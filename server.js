import 'dotenv/config';
import express from 'express';
import bodyParser from 'body-parser';
import { WebSocketServer } from 'ws';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import nodemailer from 'nodemailer';
import twilio from 'twilio';
import pkg from 'alawmulaw';

// Extract μ-law codec
const { mulaw } = pkg;
const { decode: mulawToPcm, encode: pcmToMulaw } = mulaw;

// Minimal PCM16 resampler (linear interpolation)
function resamplePCM16(buffer, fromRate, toRate) {
  if (fromRate === toRate) return buffer;
  const inSamp = new Int16Array(buffer.buffer, buffer.byteOffset, buffer.length / 2);
  const ratio = fromRate / toRate;
  const outCount = Math.max(1, Math.floor(inSamp.length / ratio));
  const out = new Int16Array(outCount);
  for (let i = 0; i < outCount; i++) {
    const pos = i * ratio;
    const i0 = Math.min(Math.floor(pos), inSamp.length - 1);
    const i1 = Math.min(i0 + 1, inSamp.length - 1);
    const frac = pos - i0;
    const s = (1 - frac) * inSamp[i0] + frac * inSamp[i1];
    out[i] = Math.max(-32768, Math.min(32767, Math.round(s)));
  }
  return Buffer.from(out.buffer);
}

// Express app setup
const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json({ limit: '2mb' }));

const PORT = process.env.PORT || 8080;

// Startup validation
(function validateEnv() {
  const required = ['OPENAI_API_KEY', 'PUBLIC_BASE_URL'];
  const missing = required.filter((k) => !process.env[k]);
  if (missing.length) {
    console.error('[BOOT] ❌ Missing required env vars:', missing.join(', '));
  } else {
    console.log('[BOOT] ✅ Required env OK');
  }
  const pbu = process.env.PUBLIC_BASE_URL;
  if (!pbu || !/^https?:\/\//i.test(pbu)) {
    console.error(
      `[BOOT] ⚠️  PUBLIC_BASE_URL is not set to a full URL. Current: "${pbu ?? ''}". Example: https://mortgage-voice-assistant.onrender.com`
    );
  } else {
    console.log('[BOOT] PUBLIC_BASE_URL =', pbu);
  }
})();

// Health check
app.get('/', (_req, res) => {
  res.json({
    ok: true,
    service: 'Mortgage Voice Assistant',
    time: new Date().toISOString(),
    publicBaseUrl: process.env.PUBLIC_BASE_URL || null,
  });
});

// Utilities
function twimlStream(connectStreamUrl) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="${connectStreamUrl}" />
  </Connect>
</Response>`;
}

function twimlSay(text) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>${escapeXml(text)}</Say>
</Response>`;
}

function escapeXml(s) {
  return String(s).replace(/[<>&'"]/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[c])
  );
}

// Twilio voice webhook
app.post('/twilio/voice', (req, res) => {
  const callSid = req.body?.CallSid || uuidv4();
  try {
    const base = (process.env.PUBLIC_BASE_URL || '').trim();
    if (!base || !/^https?:\/\//i.test(base)) {
      console.error('[VOICE] ❌ Invalid/missing PUBLIC_BASE_URL:', base);
      res.set('Content-Type', 'text/xml').status(200).send(
        twimlSay('We are sorry. The service configuration is incomplete. Please try again later.')
      );
      return;
    }
    const wsBase = base.replace(/\/+$/, '');
    const wsUrl = `${wsBase.replace(/^http/, 'ws')}/twilio-stream?callSid=${encodeURIComponent(callSid)}`;
    console.log('[VOICE] ▶︎ Incoming call', { callSid, wsUrl });
    res.set('Content-Type', 'text/xml').status(200).send(twimlStream(wsUrl));
  } catch (e) {
    console.error('[VOICE] ❌ Exception preparing TwiML:', e);
    res.status(200).set('Content-Type', 'text/xml').send(twimlSay('We are sorry, an application error has occurred.'));
  }
});

// Twilio SMS
const twilioClient =
  process.env.TWILIO_ACCOUNT_SID && process.env.TWILIO_AUTH_TOKEN
    ? twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN)
    : null;

async function sendSMS(to, body) {
  if (!twilioClient || !process.env.TWILIO_MESSAGING_NUMBER) {
    console.warn('[SMS] ⚠️ SMS not configured; skipping.', { to, preview: body?.slice(0, 80) });
    return { ok: false, disabled: true };
  }
  try {
    const msg = await twilioClient.messages.create({
      from: process.env.TWILIO_MESSAGING_NUMBER,
      to,
      body,
    });
    return { ok: true, sid: msg.sid };
  } catch (e) {
    console.error('[SMS] Error:', e?.message);
    return { ok: false, error: e?.message };
  }
}

// Email
const mailer =
  process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASS
    ? nodemailer.createTransport({
        host: process.env.SMTP_HOST,
        port: Number(process.env.SMTP_PORT || 587),
        secure: String(process.env.SMTP_SECURE || 'false') === 'true',
        auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
      })
    : null;

async function sendEmail({ subject, html }) {
  if (!mailer || !process.env.SMTP_USER || !process.env.NOTIFY_EMAIL) {
    console.warn('[MAIL] ⚠️ Mailer not configured; skipping.', { subject });
    return { ok: false, disabled: true };
  }
  try {
    const info = await mailer.sendMail({
      from: process.env.SMTP_USER,
      to: process.env.NOTIFY_EMAIL,
      subject,
      html,
    });
    return { ok: true, id: info.messageId };
  } catch (e) {
    console.error('[MAIL] Error:', e?.message);
    return { ok: false, error: e?.message };
  }
}

// Start server
const server = app.listen(PORT, () => {
  console.log(`[HTTP] ✅ Listening on :${PORT}`);
});

const wss = new WebSocketServer({ noServer: true });

server.on('upgrade', (req, socket, head) => {
  const u = new URL(req.url, 'http://localhost');
  if (u.pathname === '/twilio-stream') {
    wss.handleUpgrade(req, socket, head, (ws) => {
      wss.emit('connection', ws, req);
    });
  } else {
    socket.destroy();
  }
});

// OpenAI Realtime socket
async function createOpenAIRealtimeSocket() {
  const { default: WS } = await import('ws');
  const model = process.env.OPENAI_REALTIME_MODEL || 'gpt-4o-realtime-preview-2024-10-01';
  const key = process.env.OPENAI_API_KEY;
  if (!key) throw new Error('OPENAI_API_KEY missing');

  const url = `wss://api.openai.com/v1/realtime?model=${encodeURIComponent(model)}`;
  const ws = new WS(url, {
    headers: { Authorization: `Bearer ${key}`, 'OpenAI-Beta': 'realtime=v1' },
    perMessageDeflate: false,
  });

  // Return a promise that resolves when connection is open
  return new Promise((resolve, reject) => {
    ws.on('open', () => {
      console.log('[OAI] ✅ Realtime connected');
      resolve(ws);
    });
    ws.on('error', (err) => {
      console.error('[OAI] ❌ WS error:', err?.message || err);
      reject(err);
    });
  });
}

// Twilio WebSocket bridge
wss.on('connection', async (ws, req) => {
  const u = new URL(req.url, 'http://localhost');
  const callSid = u.searchParams.get('callSid') || uuidv4();

  console.log('[WS] ▶︎ Twilio stream connected', { callSid });

  let transcriptParts = [];
  let callerNumber = null;
  let twilioStreamSid = null;
  let outboundSeq = 1;
  let outboundChunk = 1;
  let streamStartMs = Date.now();
  let commitPending = false;
  let messageQueue = [];
  let oaiReady = false;

  let oai;
  try {
    oai = await createOpenAIRealtimeSocket();
    oaiReady = true;
    console.log('[WS] OpenAI socket ready for', callSid);
  } catch (e) {
    console.error('[WS] ❌ Failed to create OpenAI socket:', e);
    ws.close();
    return;
  }

  oai.on('close', (code, reason) => {
    console.log('[OAI] ✖︎ Realtime closed', code, String(reason || ''));
    oaiReady = false;
  });

  // OpenAI to Twilio  
  oai.on('message', (message) => {
    try {
      const evt = JSON.parse(message.toString());
      
      console.log('[OAI] Event:', evt.type); // Debug logging
      
      if (evt.type === 'response.output_text.delta' && evt?.delta) {
        transcriptParts.push(`[AI] ${evt.delta}`);
      }
      
      if (evt.type === 'response.audio.delta' && evt?.delta) {
        if (!twilioStreamSid) {
          console.error('[OAI] ❌ Cannot send audio - twilioStreamSid is null!');
          return;
        }
        
        const pcm24 = Buffer.from(evt.delta, 'base64');
        const pcm8 = resamplePCM16(pcm24, 24000, 8000);
        const pcm8Int16 = new Int16Array(pcm8.buffer, pcm8.byteOffset, pcm8.length / 2);
        const mu = pcmToMulaw(pcm8Int16);
        const muBuf = Buffer.from(mu.buffer);
        const payload = muBuf.toString('base64');

        const media = {
          event: 'media',
          streamSid: twilioStreamSid,
          sequenceNumber: String(outboundSeq++),
          media: {
            track: 'outbound',
            chunk: String(outboundChunk++),
            timestamp: String(Date.now() - streamStartMs),
            payload,
          },
        };
        
        console.log('[OAI->Twilio] Sending audio chunk', outboundChunk - 1);
        ws.send(JSON.stringify(media));
      }
      
      if (evt.type === 'error') {
        console.error('[OAI] ❌ Error event:', evt);
      }
    } catch (err) {
      console.error('[WS] ❌ handle OAI message error:', err);
    }
  });

  // Twilio to OpenAI
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());
      
      if (msg.event === 'start') {
        twilioStreamSid = msg.start?.streamSid || msg.streamSid || null;
        callerNumber = msg?.start?.from || null;
        streamStartMs = Date.now();
        
        console.log('[WS] ▶︎ Twilio start', { callSid, twilioStreamSid, from: callerNumber });
        console.log('[WS] Configuring OpenAI session...');

        const sessionUpdate = {
          type: 'session.update',
          session: {
            instructions: `You are Brendan's AI assistant for mortgages in Buffalo, NY.

FIRST MESSAGE: Immediately greet the caller by saying "Hello! I'm Brendan's AI assistant. I help with mortgage pre-approvals, refinancing, and answering mortgage questions. How can I help you today?"

Always speak in English only. Be natural, warm, and conversational.`,
            modalities: ['text', 'audio'],
            voice: 'shimmer',
            input_audio_format: 'pcm16',
            output_audio_format: 'pcm16',
            turn_detection: {
              type: 'server_vad',
              threshold: 0.5,
              prefix_padding_ms: 300,
              silence_duration_ms: 700
            },
            temperature: 0.8
          },
        };
        
        console.log('[WS] Sending session.update to OpenAI');
        oai.send(JSON.stringify(sessionUpdate));
        
        // Give OpenAI a moment, then trigger greeting
        setTimeout(() => {
          console.log('[WS] Triggering initial greeting');
          oai.send(JSON.stringify({
            type: 'response.create',
          }));
        }, 1000);
        
      } else if (msg.event === 'media' && msg.media?.payload) {
        // Only process actual audio, not silence
        const muBuf = Buffer.from(msg.media.payload, 'base64');
        
        // Check if this is actual audio (not all zeros/silence)
        const hasAudio = Array.from(muBuf).some(byte => byte !== 127 && byte !== 255);
        
        if (hasAudio && oaiReady) {
          const pcm8 = mulawToPcm(muBuf);
          const pcm8Buf = Buffer.from(pcm8.buffer, pcm8.byteOffset, pcm8.byteLength);
          const pcm24 = resamplePCM16(pcm8Buf, 8000, 24000);
          const audio = pcm24.toString('base64');

          oai.send(JSON.stringify({ type: 'input_audio_buffer.append', audio }));
        }
        
      } else if (msg.event === 'stop') {
        console.log('[WS] ◀︎ Twilio stop', { callSid });
        
        setTimeout(async () => {
          try {
            const tldr = await summarizeTLDR(transcriptParts.join('\n'));
            if (process.env.AUTO_FOLLOW_UP === 'true' && callerNumber) {
              const appLink = process.env.APPLICATION_LINK || 'https://movement.com/lo/brendan-burns';
              await sendSMS(callerNumber, `Thanks for calling Brendan's team. Start your application here: ${appLink}`);
            }
            await sendEmail({
              subject: `New Call – ${callerNumber ?? ''} (${callSid})`,
              html: `<h2>Call Summary (Auto TLDR)</h2><pre>${tldr}</pre><hr/><pre>${transcriptParts.join('<br/>')}</pre>`,
            });
          } catch (err) {
            console.error('[WS] ❗ follow-up error:', err?.message);
          }
        }, 1200);
      }
    } catch (err) {
      console.error('[WS] ❌ handle Twilio message error:', err?.message);
    }
  });

  ws.on('close', () => {
    console.log('[WS] ✖︎ Twilio stream closed', { callSid });
    try { oai?.close(); } catch {}
  });
});

// TLDR summarizer
async function summarizeTLDR(transcript) {
  try {
    const key = process.env.OPENAI_API_KEY;
    if (!key || !transcript) return 'No summary available.';
    const r = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: 'You write crisp 3–6 bullet TLDRs for mortgage calls.' },
          { role: 'user', content: `Summarize this call:\n\n${transcript}` },
        ],
        max_tokens: 240,
        temperature: 0.2,
      },
      { headers: { Authorization: `Bearer ${key}` } }
    );
    return r.data?.choices?.[0]?.message?.content?.trim?.() ?? '—';
  } catch (e) {
    console.error('[TLDR] error:', e?.message || e);
    return '—';
  }
}
