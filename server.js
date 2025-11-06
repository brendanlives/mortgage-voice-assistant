import 'dotenv/config';
import express from 'express';
import bodyParser from 'body-parser';
import { WebSocketServer } from 'ws';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import nodemailer from 'nodemailer';
import twilio from 'twilio';

const app = express();
app.use(bodyParser.json({ limit: '2mb' }));
app.use(bodyParser.urlencoded({ extended: true }));

const PORT = process.env.PORT || 8080;

// --- Utilities ---
function twimlResponse(connectStreamUrl) {
  return `<?xml version="1.0" encoding="UTF-8"?><Response><Connect><Stream url="${connectStreamUrl}"/></Connect></Response>`;
}

// --- Voice webhook: returns TwiML to start Twilio <Stream> ---
app.post('/twilio/voice', (req, res) => {
  const callSid = req.body.CallSid || uuidv4();
  const publicBase = process.env.PUBLIC_BASE_URL || `https://example.com`;
  // convert http(s) to ws(s) for Twilio Media Streams
  const wsBase = publicBase.replace(/^http/, 'ws');
  const wsUrl = `${wsBase.replace(/\/$/, '')}/twilio-stream?callSid=${callSid}`;
  const twiml = twimlResponse(wsUrl);
  res.set('Content-Type', 'text/xml');
  res.send(twiml);
});

// --- Lead capture + Calendly handoff (sample) ---
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

// --- Notifications (SMS + Email) ---
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
  auth: { user: process.env.SMPP_USER || process.env.SMTP_USER, pass: process.env.SMTP_PASS }
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

// --- TLDR summarizer (OpenAI chat) ---
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

// --- “Apply Now” link: on-demand SMS endpoint ---
app.post('/notify/send-application', async (req, res) => {
  const { to } = req.body || {};
  const link = process.env.APPLICATION_LINK || 'https://movement.com/lo/brendan-burns';
  if (!to) return res.status(400).json({ ok: false, error: 'Missing "to" number' });
  const text = `Here is the application link to get started: ${link}`;
  const r = await sendSMS(to, text);
  res.json({ ok: true, result: r });
});

// --- HTTP server + WS upgrade for Twilio stream ---
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

// --- OpenAI Realtime WebSocket connection ---
async function createOpenAIRealtimeSocket() {
  const { WebSocket } = await import('ws');
  const model = 'gpt-4o-realtime-preview'; // verify latest model name
  const url = `wss://api.openai.com/v1/realtime?model=${model}`;
  const headers = {
    'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
    'OpenAI-Beta': 'realtime=v1'
  };
  return new WebSocket(url, { headers });
}

// --- Mortgage math + simple local info ---
function calcMonthlyPayment({ price, downPct = 0.05, rate = 0.07, termYears = 30, tax = 0, insurance = 0, mi = 0 }) {
  const loan = price * (1 - downPct);
  const n = termYears * 12;
  const r = rate / 12;
  const pAndI = (r === 0) ? (loan / n)
    : (loan * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
  return Math.round((pAndI + tax/12 + insurance/12 + mi) * 100) / 100;
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

// --- Twilio stream <-> OpenAI Realtime bridge (simplified) ---
wss.on('connection', async (ws, req) => {
  const url = new URL(req.url, 'http://localhost');
  const callSid = url.searchParams.get('callSid') || uuidv4();
  console.log('Twilio stream connected', callSid);

  let transcriptParts = [];
  let callerNumber = null; // populate if available
  // Store the Twilio Media Stream SID from the 'start' event. This is required
  // when sending synthesized audio back to Twilio. If not set, audio messages
  // will be rejected as invalid.
  let twilioStreamSid = null;
  // Track outbound media sequence and chunk numbers and the time the stream
  // started so we can construct valid media messages for Twilio.  Twilio
  // requires sequenceNumber, chunk, timestamp and track on each outbound
  // media message.  These counters are initialized once a call begins.
  let outboundSequence = 1;
  let outboundChunk = 1;
  let streamStartTime = null;

  const oai = await createOpenAIRealtimeSocket();

  oai.on('message', (message) => {
    try {
      const evt = JSON.parse(message.toString());

      // Capture assistant text (for TLDR/transcript)
      if (evt.type === 'response.output_text.delta' && evt.delta) {
        transcriptParts.push(`[AI] ${evt.delta}`);
      }

      // Forward synthesized audio to Twilio. Twilio requires a valid streamSid
      // and specific fields (sequenceNumber, media.track, media.chunk, media.timestamp)
      // on each outbound media message. If the stream SID has not been set yet
      // (we haven't received the 'start' message), skip sending audio.
      if (evt.type === 'response.audio.delta') {
        if (!twilioStreamSid) {
          // Skip sending audio until we have a valid stream SID from Twilio.
          return;
        }
        // Compute timestamp relative to when the stream started.  If we haven't
        // recorded a start time, fall back to 0.  Note: Twilio expects this
        // value in milliseconds.
        const now = Date.now();
        const ts = streamStartTime ? Math.floor(now - streamStartTime) : 0;
        // Build a Twilio media message compliant with the protocol.  See
        // https://www.twilio.com/docs/voice/media-streams/websocket-messages for details.
        const twilioMsgObj = {
          event: 'media',
          sequenceNumber: String(outboundSequence++),
          media: {
            track: 'outbound',
            chunk: String(outboundChunk++),
            timestamp: String(ts),
            payload: evt.audio
          },
          streamSid: twilioStreamSid
        };
        ws.send(JSON.stringify(twilioMsgObj));
      }
    } catch (e) {
      console.error('Error parsing OAI message', e);
    }
  });

  oai.on('close', () => console.log('Realtime socket closed for', callSid));

  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());

      if (msg.event === 'start') {
        // Extract the media stream SID from the start message. This will be
        // used when sending audio back to Twilio via the media event. Without
        // a valid streamSid, Twilio will reject the message.
        try {
          twilioStreamSid = (msg.start && msg.start.streamSid) || msg.streamSid || null;
        } catch (e) {
          console.warn('Unable to extract streamSid from start message', e);
        }
        // Record the time when the stream starts so outbound timestamps can be
        // computed relative to this moment.  This will be used to populate
        // the media.timestamp field on outbound messages.
        streamStartTime = Date.now();
        try { callerNumber = msg?.start?.from || null; } catch {}
        
        const sys = {
          type: 'session.update',
          session: {
            instructions: `
        You are Brendan's AI assistant for mortgages and real estate in Buffalo, NY. You have a gay male super-bright, chirpy, upbeat personality and speak with a friendly, cheerful tone. Always introduce yourself as Brendan's AI assistant.

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
            modalities: ['text','audio']
          }
        };

        oai.send(JSON.stringify(sys));

      } else if (msg.event === 'media' && msg.media && msg.media.payload) {
        // Forward incoming audio frame to OpenAI
        const frame = {
          type: 'input_audio_buffer.append',
          audio: msg.media.payload // base64 mu-law 8k from Twilio
        };
        oai.send(JSON.stringify(frame));

      } else if (msg.event === 'stop') {
        // Ask OpenAI to respond and then do follow-up notifications
        oai.send(JSON.stringify({ type: 'input_audio_buffer.commit' }));
        oai.send(JSON.stringify({ type: 'response.create', response: { modalities: ['audio','text'] } }));

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
              <pre style="white-space:pre-wrap;">${transcript}</pre>
            `;
            await sendEmail({ subject: 'New Call — TLDR + Transcript', html });
          } catch (e) {
            console.error('Follow-up error', e?.message);
          }
        }, 1000);
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
