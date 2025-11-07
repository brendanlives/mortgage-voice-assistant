import 'dotenv/config';
import express from 'express';
import bodyParser from 'body-parser';
import { WebSocketServer } from 'ws';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import nodemailer from 'nodemailer';
import twilio from 'twilio';
import pkg from 'alawmulaw'; // CommonJS package, expose .mulaw object

// ---- Extract μ-law codec (encode/decode PCM16 <-> μ-law) --------------------
const { mulaw } = pkg;
const { decode: mulawToPcm, encode: pcmToMulaw } = mulaw;

// ---- Minimal PCM16 resampler (linear) to go 24 kHz <-> 8 kHz ----------------
// NOTE: This keeps us independent of pcm-util to avoid CJS/ESM friction.
// For telephony (8 kHz) this is adequate; we can upgrade to a higher-quality
// resampler later (e.g. speex/soxr wasm) without changing call sites.
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

// ---- Express app & body parsing ---------------------------------------------
const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json({ limit: '2mb' }));

const PORT = process.env.PORT || 8080;

// ---- Startup env validation --------------------------------------------------
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

// ---- Simple health probe ----------------------------------------------------
app.get('/', (_req, res) => {
  res.json({
    ok: true,
    service: 'Mortgage Voice Assistant',
    time: new Date().toISOString(),
    publicBaseUrl: process.env.PUBLIC_BASE_URL || null,
  });
});

// ---- Utilities --------------------------------------------------------------
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

// ---- Twilio: inbound call -> start media stream -----------------------------
app.post('/twilio/voice', (req, res) => {
  const callSid = req.body?.CallSid || uuidv4();
  try {
    const base = (process.env.PUBLIC_BASE_URL || '').trim();
    if (!base || !/^https?:\/\//i.test(base)) {
      console.error('[VOICE] ❌ Invalid/missing PUBLIC_BASE_URL:', base);
      res.set('Content-Type', 'text/xml').status(200).send(
        twimlSay(
          'We are sorry. The service configuration is incomplete. Please try again later.'
        )
      );
      return;
    }
    const wsBase = base.replace(/\/+$/, '');
    const wsUrl = `${wsBase.replace(/^http/, 'ws')}/twilio-stream?callSid=${encodeURIComponent(
      callSid
    )}`;
    console.log('[VOICE] ▶︎ Incoming call', { callSid, wsUrl });
    res.set('Content-Type', 'text/xml').status(200).send(twimlStream(wsUrl));
  } catch (e) {
    console.error('[VOICE] ❌ Exception preparing TwiML:', e);
    res
      .status(200)
      .set('Content-Type', 'text/xml')
      .send(twimlSay('We are sorry, an application error has occurred.'));
  }
});

// ---- Notifications (Twilio SMS + email) -------------------------------------
const twilioClient =
  process.env.TWILIO_ACCOUNT_SID && process.env.TWILIO_AUTH_TOKEN
    ? twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN)
    : null;

async function sendSMS(to, body) {
  if (!twilioClient || !process.env.TWILIO_MESSAGING_NUMBER) {
    console.warn('[SMS] ⚠️ SMS not configured; skipping.', { to, preview: body?.slice(0, 80) });
    return { ok: false, disabled: true };
  }
  const msg = await twilioClient.messages.create({
    from: process.env.TWILIO_MESSAGING_NUMBER,
    to,
    body,
  });
  return { ok: true, sid: msg.sid };
}

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
  if (!mailer || !process.env.SMTP_USER) {
    console.warn('[MAIL] ⚠️ Mailer not configured; skipping.', { subject });
    return { ok: false, disabled: true };
  }
  const info = await mailer.sendMail({
    from: 'assistant@voicebot.local',
    to: process.env.NOTIFY_EMAIL,
    subject,
    html,
  });
  return { ok: true, id: info.messageId };
}

// ---- Start HTTP server & WS upgrade ----------------------------------------
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

// ---- OpenAI Realtime socket factory ----------------------------------------
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

  ws.on('open', () => console.log('[OAI] ✅ Realtime connected'));
  ws.on('error', (err) => console.error('[OAI] ❌ WS error:', err?.message || err));
  ws.on('close', (code, reason) =>
    console.log('[OAI] ✖︎ Realtime closed', code, String(reason || ''))
  );

  return ws;
}

// ---- Twilio media bridge ----------------------------------------------------
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

  let oai;
  try {
    oai = await createOpenAIRealtimeSocket();
  } catch (e) {
    console.error('[WS] ❌ Failed to create OpenAI socket:', e);
    ws.close();
    return;
  }

  // OpenAI → Twilio (speak back)
  oexion(oai, 'message', (message) => {
    try {
      const evt = JSON.parse(message.toString());
      if (evt.type === 'response.output_text.delta' && evt?.delta) {
        transcriptParts.push(`[AI] ${evt.delta}`);
      }
      if (evt.type === 'response.audio.delta' && evt?.delta) {
        const pcm24 = Buffer.from(evt.delta, 'base64');
        const pcm8 = resamplePCM16(pcm24, 24000, 8000);
        const pcm8Int16 = new Int16Array(pcm8.buffer, pcm8.byteOffset, pcm8.length / 2);
        const mu = pcmToMulaw(pcm8Int16); // Uint8Array
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
        ws.send(JSON.stringify(media));
      }
    } catch (err) {
      console.error('[WS] ❌ handle OAI message error:', err);
    }
  });

  oexon(ws, 'message', (data) => {
    try {
      const msg = JSON.parse(data.toString());
      if (msg.event === 'start') {
        twilioStreamSid = msg.start?.streamSid || msg.streamSid || null;
        callerNumber = msg?.start?.from || null;
        streamStartMs = Date.now();

        const sessionUpdate = {
          type: 'session.update',
          session: {
            instructions: `
You are a professional, helpful mortgage assistant for Brendan's team in Buffalo, NY.
Speak clearly, concise, friendly, and confident. Offer to send the loan application link when appropriate.
Avoid any discriminatory criteria. Clarify you are an AI assistant for the team.`,
            modalities: ['text', 'audio'],
            voice: process.env.OPENAI_VOICE || 'alloy',
            input_audio_format: 'pcm16',
            output_audio_format: 'pcm16',
            turn_detection: { type: 'server_vad', threshold: 0.5, prefix_padding_ms: 300, silence_duration_ms: 600 },
          },
        };
        oai.send(JSON.stringify(sessionUpdate));
        console.log('[WS] ▶︎ Twilio start', { callSid, twilioStreamSid, from: callerNumber });
      } else if (msg.event === 'media' && msg.media?.payload) {
        // Twilio: μ-law 8 kHz -> PCM16 24 kHz
        const muBuf = Buffer.from(msg.media.payload, 'base64');
        const pcm8 = mulawToPcm(muBuf); // Int16Array (8 kHz)
        const pcm8Buf = Buffer.from(pcm8.buffer, pcm8.byteOffset, pcm8.byteLength);
        const pcm24 = resamplePCM16(pcm8Buf, 8000, 24000);
        const audio = pcm24.toString('base64');

        oai.send(JSON.stringify({ type: 'input_audio_buffer.append', audio }));
        if (!commitPending) {
          commitPending = true;
          setTimeout(() => {
            oai.send(JSON.stringify({ type: 'input_audio_buffer.commit' }));
            commitPending = false;
          }, 100);
        }
      } else if (msg.event === 'stop') {
        oai.send(JSON.stringify({ type: 'input_audio_buffer.commit' }));
        oai.send(JSON.stringify({ type: 'response.create', response: { modalities: ['audio', 'text'] } }));
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
            console.error('[WS] ❗ follow-up error:', err);
          }
        }, 1200);
      }
    } catch (err) {
      console.error('[WS] ❌ handle Twilio message error:', err, { raw: data?.toString?.() });
    }
  });

  oexon(ws, 'close', () => {
    console.log('[WS] ✖︎ Twilio stream closed', { callSid });
    try { oai?.close(); } catch {}
  });
});

// ---- TLDR helper ------------------------------------------------------------
async function summarizeTLDR(transcript) {
  try {
    const key = process.env.OPENAI_API_KEY;
    if (!key) return 'No summary (no OPENAI_API_KEY).';
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

// ---- small helpers for robust event handling with ws ------------------------
function oexion(emitter, event, handler) {
  emitter.on(event, (msg, ...rest) => {
    try { handler(msg, ...rest); } catch (e) { console.error(`[WS] handler error (${event})`, e); }
  });
}
function oexon(emitter, event, handler) { oexion(emitter, event, handler); }
