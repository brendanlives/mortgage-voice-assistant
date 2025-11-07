import 'dotenv/config';
import express from 'express';
import bodyParser from 'body-parser';
import { WebSocketServer } from 'ws';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import nodemailer from 'nodemailer';
import twilio from 'twilio';
import { decode as mulawToPcm, encode as pcmToMulaw } from 'alawmulaw/mulaw';
import { resample } from 'pcm-util'; // Resample 8kHz ↔ 24kHz

const app = express();
app.use(bodyParser.json({ limit: '2mb' }));
app.use(bodyParser.urlencoded({ extended: true }));

const PORT = process.env.PORT || 8080;

// --- Utilities ---
function twimlResponse(connectStreamUrl) {
  return `<?xml version="1.0" encoding="UTF-8"?><Response><Connect><Stream url="${connectStreamUrl}"/></Connect></Response>`;
}

// --- Voice webhook ---
app.post('/twilio/voice', (req, res) => {
  const callSid = req.body.CallSid || uuidv4();
  const publicBase = process.env.PUBLIC_BASE_URL || `https://example.com`;
  const wsBase = publicBase.replace(/^http/, 'ws');
  const wsUrl = `${wsBase.replace(/\/$/, '')}/twilio-stream?callSid=${callSid}`;
  const twiml = twimlResponse(wsUrl);
  res.set('Content-Type', 'text/xml');
  res.send(twiml);
});

// --- Lead capture ---
app.post('/lead', async (req, res) => {
  const { name, phone, email, topic } = req.body || {};
  console.log('Lead received:', { name, phone, email, topic });
  const calendly = process.env.CALENDLY_LINK;
  const reply = {
    ok: true,
    next: calendly ? `Please pick a time here: ${calendly}` : 'We will contact you to schedule.',
  };
  res.json(reply);
});

// --- Health check ---
app.get('/', (req, res) => {
  res.json({ ok: true, service: 'Mortgage Voice Assistant', time: new Date().toISOString() });
});

// --- Notifications ---
const twilioClient = (process.env.TWILIO_ACCOUNT_SID && process.env.TWILIO_AUTH_TOKEN)
  ? twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN)
  : null;

async function sendSMS(to, body) {
  if (!twilioClient || !process.env.TWILIO_MESSAGING_NUMBER) {
    console.log('[SMS disabled]', { to, preview: body?.slice(0, 120) });
    return { ok: false, disabled: true };
  }
  try {
    const msg = await twilioClient.messages.create({
      from: process.env.TWILIO_MESSAGING_NUMBER,
      to, body
    });
    return { ok: true, sid: msg.sid };
  } catch (e) {
    console.error('SMS error', e?.message);
    return { ok: false, error: e?.message };
  }
}

const mailer = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT || 587),
  secure: String(process.env.SMTP_SECURE || 'false') === 'true',
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
});

async function sendEmail({ subject, html }) {
  if (!process.env.NOTIFY_EMAIL) {
    console.log('[Email disabled]', subject);
    return { ok: false, disabled: true };
  }
  try {
    const info = await mailer.sendMail({
      from: 'assistant@voicebot.local',
      to: process.env.NOTIFY_EMAIL,
      subject, html
    });
    return { ok: true, id: info.messageId };
  } catch (e) {
    console.error('Email error', e?.message);
    return { ok: false, error: e?.message };
  }
}

// --- TLDR summarizer ---
async function summarizeTLDR(transcript) {
  try {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) return 'No summary (no OPENAI_API_KEY).';
    const resp = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You write crisp 3–6 bullet TLDRs for phone call transcripts.' },
        { role: 'user', content: `Summarize this call for a loan officer. Include borrower basics and next steps:\n\n${transcript}` }
      ],
      temperature: 0.2,
      max_tokens: 240
    }, { headers: { Authorization: `Bearer ${apiKey}` }});
    return resp.data?.choices?.[0]?.message?.content?.trim() || 'Summary unavailable.';
  } catch (e) {
    console.error('TLDR error', e?.message);
    return 'Summary unavailable.';
  }
}

// --- Apply Now SMS ---
app.post('/notify/send-application', async (req, res) => {
  const { to } = req.body || {};
  const link = process.env.APPLICATION_LINK || 'https://movement.com/lo/brendan-burns';
  if (!to) return res.status(400).json({ ok: false, error: 'Missing "to" number' });
  const text = `Here is the application link to get started: ${link}`;
  const r = await sendSMS(to, text);
  res.json({ ok: true, result: r });
});

// --- Mortgage math ---
function calcMonthlyPayment({ price, downPct = 0.05, rate = 0.07, termYears = 30, tax = 0, insurance = 0, mi = 0 }) {
  const loan = price * (1 - downPct);
  const n = termYears * 12;
  const r = rate / 12;
  const pAndI = (r === 0)
    ? (loan / n)
    : (loan * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
  return Math.round((pAndI + tax / 12 + insurance / 12 + mi) * 100) / 100;
}

const buffaloCheat = {
  taxes_per_1000: 29.0,
  typical_attorney_fee: 900,
  transfer_tax_seller: "NY State + County, varies; budget 0.4%–0.65% total",
  seller_concession_caps: {
    fha: "Up to 6% of price",
    conventional_primary: "3% at 90–95% LTV; 6% at 75–90%; 9% at <=75%"
  }
};

app.post('/tools/calc_payment', (req, res) => {
  const { price, downPct, rate, termYears, tax, insurance, mi } = req.body || {};
  const monthly = calcMonthlyPayment({ price, downPct, rate, termYears, tax, insurance, mi });
  res.json({ ok: true, monthly });
});

app.get('/tools/buffalo_info', (req, res) => {
  res.json({ ok: true, buffalo: buffaloCheat });
});

// --- HTTP + WS server ---
const server = app.listen(PORT, () => {
  console.log(`Server listening on :${PORT}`);
});

const wss = new WebSocketServer({ noServer: true });

server.on('upgrade', (req, socket, head) => {
  const url = new URL(req.url, 'http://localhost');
  if (url.pathname === '/twilio-stream') {
    wss.handleUpgrade(req, socket, head, (ws) => {
      wss.emit('connection', ws, req);
    });
  } else {
    socket.destroy();
  }
});

// --- OpenAI Realtime WS ---
async function createOpenAIRealtimeSocket() {
  const { default: WebSocket } = await import('ws');
  const model = 'gpt-4o-realtime-preview-2024-10-01';
  const url = `wss://api.openai.com/v1/realtime?model=${model}`;
  const oai = new WebSocket(url, {
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      'OpenAI-Beta': 'realtime=v1'
    },
    perMessageDeflate: false
  });

  oai.on('error', (err) => console.error('OpenAI WS error:', err.message));
  oai.on('open', () => console.log('OpenAI Realtime connected'));

  return oai;
}

// --- Twilio ↔ OpenAI Bridge ---
wss.on('connection', async (ws, req) => {
  const url = new URL(req.url, 'http://localhost');
  const callSid = url.searchParams.get('callSid') || uuidv4();
  console.log('Twilio stream connected', callSid);

  let transcriptParts = [];
  let callerNumber = null;
  let twilioStreamSid = null;
  let outboundSequence = 1;
  let outboundChunk = 1;
  let streamStartTime = null;
  let commitPending = false;

  const oai = await createOpenAIRealtimeSocket();

  // --- OpenAI → Twilio (audio + text) ---
  oai.on('message', (message) => {
    try {
      const evt = JSON.parse(message.toString());

      if (evt.type === 'response.output_text.delta' && evt.delta) {
        transcriptParts.push(`[AI] ${evt.delta}`);
      }

      if (evt.type === 'response.audio.delta' && evt.delta && twilioStreamSid) {
        const now = Date.now();
        const ts = streamStartTime ? Math.floor(now - streamStartTime) : 0;

        // OpenAI: PCM16 24kHz → Twilio: mulaw 8kHz
        const pcm24kBuffer = Buffer.from(evt.delta, 'base64');
        const pcm8kBuffer = resample(pcm24kBuffer, 24000, 8000, { method: 'sinc' });
            // Convert the 8 kHz PCM buffer to an Int16Array for encoding
    const pcm8kInt16 = new Int16Array(
      pcm8kBuffer.buffer,
      pcm8kBuffer.byteOffset,
      pcm8kBuffer.length / 2
    );
    const mulawUint8 = pcmToMulaw(pcm8kInt16);        // Returns a Uint8Array
    const mulawBuffer = Buffer.from(mulawUint8.buffer);
    const payload = mulawBuffer.toString('base64');


        const twilioMsgObj = {
          event: 'media',
          streamSid: twilioStreamSid,
          sequenceNumber: String(outboundSequence++),
          media: {
            track: 'outbound',
            chunk: String(outboundChunk++),
            timestamp: String(ts),
            payload
          }
        };
        ws.send(JSON.stringify(twilioMsgObj));
      }
    } catch (e) {
      console.error('Error parsing OAI message', e);
    }
  });

  oai.on('close', () => console.log('Realtime socket closed for', callSid));

  // --- Twilio → OpenAI ---
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());

      if (msg.event === 'start') {
        twilioStreamSid = msg.start?.streamSid || msg.streamSid || null;
        streamStartTime = Date.now();
        callerNumber = msg?.start?.from || null;

        const sys = {
          type: 'session.update',
          session: {
            instructions: `
You are Brendan's AI assistant for mortgages and real estate in Buffalo, NY. 
You have a bright, upbeat, professional tone and always introduce yourself as Brendan's AI assistant.

Capabilities:
- Hold a conversation and answer any mortgage or real estate question, including complex mortgage guideline questions about Fannie Mae, Freddie Mac, VA, FHA, and USDA.
- Qualify callers (purchase/refi/VA/FHA/USDA/Conventional; price/down/credit band/DTI guess).
- Estimate payments using the calc tool when asked.
- Offer to text the loan application link when appropriate.
- Take messages and let callers know they can ask for anything.
- Book meetings using CALENDLY_LINK if provided.
- Provide Buffalo-local context (taxes, attorney fees, typical closing costs).

Compliance:
- Not a commitment to lend. Estimates only. Terms subject to underwriting.
- Avoid any prohibited-basis discussions. Offer to connect with a licensed loan officer for specifics.
- Always be respectful and inclusive.
`.trim(),
            modalities: ['text', 'audio'],
            voice: 'alloy',
            input_audio_format: 'pcm16',
            output_audio_format: 'pcm16',
            turn_detection: {
              type: 'server_vad',
              threshold: 0.5,
              prefix_padding_ms: 300,
              silence_duration_ms: 600
            }
          }
        };
        oai.send(JSON.stringify(sys));
      }

      else if (msg.event === 'media' && msg.media?.payload) {
        // Twilio: mulaw 8kHz → OpenAI: PCM16 24kHz
        const mulawBuffer = Buffer.from(msg.media.payload, 'base64');
        const pcm8k = mulawToPcm(mulawBuffer); // Int16Array
        const pcm8kBuffer = Buffer.from(pcm8k.buffer, pcm8k.byteOffset, pcm8k.byteLength);
        const pcm24kBuffer = resample(pcm8kBuffer, 8000, 24000, { method: 'sinc' });
        const base64Pcm = pcm24kBuffer.toString('base64');

        oai.send(JSON.stringify({
          type: 'input_audio_buffer.append',
          audio: base64Pcm
        }));

        // Throttle commits to avoid overload
        if (!commitPending) {
          commitPending = true;
          setTimeout(() => {
            oai.send(JSON.stringify({ type: 'input_audio_buffer.commit' }));
            commitPending = false;
          }, 100);
        }
      }

      else if (msg.event === 'stop') {
        oai.send(JSON.stringify({ type: 'input_audio_buffer.commit' }));
        oai.send(JSON.stringify({ type: 'response.create', response: { modalities: ['audio', 'text'] } }));

        setTimeout(async () => {
          try {
            const transcript = transcriptParts.join('\n').trim();
            const tldr = await summarizeTLDR(transcript);
            const appLink = process.env.APPLICATION_LINK || 'https://movement.com/lo/brendan-burns';
            if (process.env.AUTO_FOLLOW_UP === 'true' && callerNumber) {
              await sendSMS(callerNumber, `Thanks for calling Brendan's team. Start your application here: ${appLink}`);
            }
            const html = `
<h2>Call Summary (Auto TLDR)</h2>
<pre style="white-space:pre-wrap;">${tldr}</pre>
<hr/>
<h3>Full Transcript (assistant side)</h3>
<pre style="white-space:pre-wrap;">${transcript}</pre>`;
            await sendEmail({ subject: 'New Call — TLDR + Transcript', html });
          } catch (e) {
            console.error('Follow-up error', e?.message);
          }
        }, 1500);
      }
    } catch (e) {
      console.error('Bad WS message', e);
    }
  });

  ws.on('close', () => {
    console.log('Twilio stream closed', callSid);
    try { oai.close(); } catch {}
  });
});
