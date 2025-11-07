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

// Mortgage Guidelines Knowledge Base
const MORTGAGE_GUIDELINES = `
# MORTGAGE GUIDELINES KNOWLEDGE BASE

## VA LOANS
- **Down Payment**: 0% down payment required
- **Credit Score**: Minimum 580-620 (varies by lender)
- **Funding Fee**: 2.3% for first-time use, 3.6% for subsequent use (can be financed)
- **DTI Ratio**: Up to 41% (residual income is key factor)
- **Property Requirements**: Must be primary residence, VA appraisal required
- **Eligibility**: Veterans, active military, qualifying spouses
- **Benefits**: No PMI, competitive rates, easier qualification

## USDA LOANS
- **Down Payment**: 0% down payment
- **Credit Score**: Minimum 640 for automated underwriting
- **Guarantee Fee**: 1% upfront + 0.35% annual (can be financed)
- **DTI Ratio**: 29% front-end, 41% back-end
- **Income Limits**: Must not exceed 115% of area median income
- **Location**: Property must be in eligible rural area
- **Property**: Primary residence only, modest size/value

## FHA LOANS
- **Down Payment**: 3.5% with 580+ credit score, 10% with 500-579
- **Credit Score**: Minimum 500 (580 for 3.5% down)
- **MIP**: 1.75% upfront + 0.55%-0.85% annual
- **DTI Ratio**: Up to 43% (50% with compensating factors)
- **Property Standards**: Must meet HUD minimum property standards
- **Loan Limits**: Varies by county ($498,257-$1,149,825 in 2024)
- **Best For**: First-time buyers, lower credit scores

## FANNIE MAE CONVENTIONAL
- **Down Payment**: As low as 3% (first-time buyers)
- **Credit Score**: Minimum 620
- **PMI**: Required if less than 20% down (cancellable at 78% LTV)
- **DTI Ratio**: Up to 50%
- **Reserves**: Typically 2 months PITI
- **Loan Limits**: $766,550 (2024 standard), higher in high-cost areas
- **Programs**: HomeReady (97% LTV for low-moderate income)

## FREDDIE MAC CONVENTIONAL
- **Down Payment**: As low as 3%
- **Credit Score**: Minimum 620
- **PMI**: Required if less than 20% down
- **DTI Ratio**: Up to 50%
- **Loan Limits**: Same as Fannie Mae
- **Programs**: Home Possible (similar to HomeReady)
- **Special**: More flexible on rental income calculations

## GENERAL MORTGAGE INFO
- **Debt-to-Income (DTI)**: Monthly debt payments ÷ gross monthly income
- **Loan-to-Value (LTV)**: Loan amount ÷ property value
- **PITI**: Principal, Interest, Taxes, Insurance
- **Rate Lock**: Typically 30-60 days
- **Closing Costs**: Usually 2-5% of loan amount
- **Pre-Approval**: Valid for 60-90 days typically
`;

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
    service: 'Mortgage Voice Assistant - Enhanced',
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
    console.log('[SMS] ✅ Sent to', to, '| SID:', msg.sid);
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
    console.log('[MAIL] ✅ Sent:', subject);
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
  const model = process.env.OPENAI_REALTIME_MODEL || 'gpt-4o-realtime-preview-2024-12-17';
  const key = process.env.OPENAI_API_KEY;
  if (!key) throw new Error('OPENAI_API_KEY missing');

  const url = `wss://api.openai.com/v1/realtime?model=${encodeURIComponent(model)}`;
  const ws = new WS(url, {
    headers: { Authorization: `Bearer ${key}`, 'OpenAI-Beta': 'realtime=v1' },
    perMessageDeflate: false,
  });

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

// Create natural, conversational system instructions
function createSystemInstructions() {
  const loanOfficerName = process.env.LOAN_OFFICER_NAME || 'Brendan Burns';
  const loanOfficerLocation = process.env.LOAN_OFFICER_LOCATION || 'Buffalo, NY';
  const applicationLink = process.env.APPLICATION_LINK || 'https://movement.com/lo/brendan-burns';
  const schedulingLink = process.env.SCHEDULING_LINK || 'https://calendly.com/brendan-burns';
  
  return `You are ${loanOfficerName}'s personal AI assistant and you help people with mortgages in ${loanOfficerLocation}.

# YOUR PERSONALITY
- Talk like a real person, not a robot. Be warm, friendly, and conversational
- Use natural filler words occasionally like "um", "you know", "actually", "so", "well"
- You can laugh (use "haha" naturally), say "great question!", show enthusiasm
- Keep responses SHORT and conversational - think 1-2 sentences max for most replies
- Mirror the caller's energy and tone
- Don't be overly formal - you're helpful but casual, like a friend in the business

# GREETING (IMPORTANT!)
When someone calls, you MUST greet them with a proper introduction. Start with:

"Hi! This is ${loanOfficerName}'s AI assistant. I can help answer questions about mortgages, including mortgage guidelines like VA, FHA, USDA, Fannie Mae, and Freddie Mac loans. I can also schedule meetings with ${loanOfficerName} and answer any real estate or mortgage-related questions you have. What can I help you with today?"

Or a natural variation like:
"Hey! You've reached ${loanOfficerName}'s AI assistant. I help with all things mortgages - guidelines, loan programs like VA and FHA, scheduling time with ${loanOfficerName}, really anything real estate or mortgage related. What brings you in today?"

Always introduce yourself as ${loanOfficerName}'s AI assistant and briefly mention your capabilities in the greeting.

# WHAT YOU DO
1. **Answer Mortgage Questions** - You know VA, FHA, USDA, Fannie Mae, Freddie Mac guidelines inside and out
2. **Schedule Meetings** - You can book time with ${loanOfficerName}
3. **Send Application Links** - You can text or email the mortgage application
4. **Take Messages** - If someone wants to talk to ${loanOfficerName} directly, you'll make sure he gets the message
5. **Pre-qualify Discussions** - Help them understand what they might qualify for

# YOUR KNOWLEDGE
You have complete knowledge of:
${MORTGAGE_GUIDELINES}

Use this knowledge naturally in conversation. Don't recite it like a textbook - explain it conversationally.

# HANDLING COMMON SCENARIOS

**If they ask about rates:**
"Great question! Rates change daily based on the market. Right now we're seeing really competitive rates. Want me to have ${loanOfficerName} give you a personalized quote? I can schedule a quick call or text you to get started."

**If they want to apply:**
"Awesome! I can text you the application link right now and you can get started on your phone. It takes about 10-15 minutes. Want me to send that over?"

**If they want to talk to ${loanOfficerName}:**
"I totally get it! ${loanOfficerName} is probably with another client right now, but I can schedule you for a call. What works better for you - today after 4pm or sometime tomorrow?"

**If they ask what you can help with:**
"I can help with pretty much anything mortgage-related! Pre-approvals, refinancing, questions about VA, FHA, conventional loans, you name it. I can also get you scheduled with ${loanOfficerName} if you want to chat with him directly. What brings you in today?"

**If they seem confused or frustrated:**
Slow down, be extra patient, use simpler language. Say things like "No worries, let me break this down super simple..."

# SCHEDULING MEETINGS
When someone wants to meet with ${loanOfficerName}:
1. Offer specific time slots: "How about tomorrow at 2pm or Thursday at 10am?"
2. Get their contact info: "Perfect! Can I grab your phone number and email so ${loanOfficerName} can reach you?"
3. Confirm: "Great, I've got you scheduled for [time]. ${loanOfficerName} will call you then. I'll text you a calendar invite too."
4. Use the scheduling link: ${schedulingLink}

# SENDING APPLICATION LINKS
Application link to send: ${applicationLink}

When sending the link via text: "Just sent it! Check your phone in a sec. The link should be there and you can start right away."

# KEY RULES
- NEVER say you're "just an AI" or apologize for being an AI - you're ${loanOfficerName}'s assistant, period
- NEVER sound scripted or robotic
- Keep answers SHORT unless they specifically ask for details
- Ask follow-up questions to keep the conversation going naturally
- If you don't know something specific (like today's exact rate), say "${loanOfficerName} can get you the exact numbers, but generally..." and give helpful context
- Always end with a next step: schedule a call, send a link, or take their info
- Use their name if they give it to you
- Be proactive: "While I have you, is this for buying a new home or refinancing?"

# TOOLS YOU CAN USE
- **schedule_meeting**: When someone wants to meet with ${loanOfficerName}, use this to book a time slot
- **send_application**: When someone wants the application link via text or email
- **transfer_to_loan_officer**: For urgent matters that need ${loanOfficerName} immediately (rarely needed)

You sound natural, knowledgeable, and actually helpful. You're not reading from a script - you're having a real conversation about helping them with their mortgage.`;
}

// Function calling tools for the assistant
const ASSISTANT_TOOLS = [
  {
    type: 'function',
    name: 'schedule_meeting',
    description: 'Schedule a meeting between the caller and the loan officer. Use this when someone wants to talk to the loan officer or schedule a consultation.',
    parameters: {
      type: 'object',
      properties: {
        caller_name: {
          type: 'string',
          description: 'The caller\'s full name'
        },
        caller_phone: {
          type: 'string',
          description: 'The caller\'s phone number'
        },
        caller_email: {
          type: 'string',
          description: 'The caller\'s email address (optional)'
        },
        preferred_date: {
          type: 'string',
          description: 'Preferred date/time mentioned by caller (e.g., "tomorrow at 2pm", "Thursday morning")'
        },
        meeting_reason: {
          type: 'string',
          description: 'Brief reason for the meeting (e.g., "pre-approval", "refinance", "rate quote")'
        }
      },
      required: ['caller_name', 'caller_phone', 'preferred_date', 'meeting_reason']
    }
  },
  {
    type: 'function',
    name: 'send_application',
    description: 'Send the mortgage application link via SMS or email to the caller.',
    parameters: {
      type: 'object',
      properties: {
        phone: {
          type: 'string',
          description: 'Phone number to send SMS (include country code)'
        },
        email: {
          type: 'string',
          description: 'Email address to send link (optional)'
        },
        application_type: {
          type: 'string',
          enum: ['purchase', 'refinance', 'general'],
          description: 'Type of mortgage application'
        }
      },
      required: ['phone', 'application_type']
    }
  },
  {
    type: 'function',
    name: 'get_guideline_info',
    description: 'Get specific mortgage guideline information for VA, FHA, USDA, Fannie Mae, or Freddie Mac loans.',
    parameters: {
      type: 'object',
      properties: {
        loan_type: {
          type: 'string',
          enum: ['VA', 'FHA', 'USDA', 'FANNIE_MAE', 'FREDDIE_MAC', 'CONVENTIONAL'],
          description: 'The type of loan to get guidelines for'
        },
        specific_question: {
          type: 'string',
          description: 'Specific aspect (e.g., "down payment", "credit score", "DTI ratio")'
        }
      },
      required: ['loan_type']
    }
  }
];

// Handle function calls from OpenAI
async function handleFunctionCall(functionName, functionArgs, callerNumber, callSid) {
  console.log('[FUNCTION] Calling:', functionName, 'with args:', functionArgs);
  
  try {
    if (functionName === 'schedule_meeting') {
      const { caller_name, caller_phone, caller_email, preferred_date, meeting_reason } = functionArgs;
      
      // Send confirmation SMS
      const schedulingLink = process.env.SCHEDULING_LINK || 'https://calendly.com/brendan-burns';
      await sendSMS(
        caller_phone,
        `Hi ${caller_name}! Here's the link to schedule your ${meeting_reason} consultation: ${schedulingLink}`
      );
      
      // Email notification to loan officer
      await sendEmail({
        subject: `New Meeting Request: ${caller_name} - ${meeting_reason}`,
        html: `
          <h2>New Meeting Scheduled</h2>
          <p><strong>Name:</strong> ${caller_name}</p>
          <p><strong>Phone:</strong> ${caller_phone}</p>
          <p><strong>Email:</strong> ${caller_email || 'Not provided'}</p>
          <p><strong>Preferred Time:</strong> ${preferred_date}</p>
          <p><strong>Reason:</strong> ${meeting_reason}</p>
          <p><strong>Call SID:</strong> ${callSid}</p>
        `
      });
      
      return {
        success: true,
        message: `Great! I've sent you a calendar link via text. I also let ${process.env.LOAN_OFFICER_NAME || 'Brendan'} know you want to schedule for ${preferred_date}.`
      };
    }
    
    if (functionName === 'send_application') {
      const { phone, email, application_type } = functionArgs;
      const applicationLink = process.env.APPLICATION_LINK || 'https://movement.com/lo/brendan-burns';
      
      const messageMap = {
        purchase: `Ready to buy? Start your mortgage application here: ${applicationLink}`,
        refinance: `Let's refinance! Start your application here: ${applicationLink}`,
        general: `Start your mortgage application here: ${applicationLink}`
      };
      
      await sendSMS(phone, messageMap[application_type]);
      
      if (email) {
        await sendEmail({
          subject: 'Your Mortgage Application Link',
          html: `
            <p>Thank you for your interest! You can start your mortgage application here:</p>
            <p><a href="${applicationLink}">${applicationLink}</a></p>
            <p>Questions? Call us anytime!</p>
          `
        });
      }
      
      return {
        success: true,
        message: "Perfect! Just sent the application link to your phone. Should be there any second now!"
      };
    }
    
    if (functionName === 'get_guideline_info') {
      // This function returns the guidelines - OpenAI will use them in its knowledge
      return {
        success: true,
        guidelines: MORTGAGE_GUIDELINES
      };
    }
    
  } catch (error) {
    console.error('[FUNCTION] Error:', error);
    return {
      success: false,
      message: "I had a small technical issue with that. Let me take down your info and have the loan officer call you back directly."
    };
  }
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
  let oaiReady = false;
  let oai = null;
  let sessionConfigured = false;
  let greetingSent = false;

  // Connect to OpenAI FIRST, before setting up Twilio handlers
  console.log('[WS] Connecting to OpenAI...');
  try {
    oai = await createOpenAIRealtimeSocket();
    oaiReady = true;
    console.log('[WS] ✅ OpenAI connected for', callSid);
    
    // Configure session immediately
    console.log('[WS] 🔧 Configuring OpenAI session...');
    const sessionUpdate = {
      type: 'session.update',
      session: {
        instructions: createSystemInstructions(),
        modalities: ['text', 'audio'],
        voice: 'shimmer',
        input_audio_format: 'pcm16',
        output_audio_format: 'pcm16',
        input_audio_transcription: {
          model: 'whisper-1'
        },
        turn_detection: {
          type: 'server_vad',
          threshold: 0.5,
          prefix_padding_ms: 300,
          silence_duration_ms: 500
        },
        tools: ASSISTANT_TOOLS,
        tool_choice: 'auto',
        temperature: 0.9,
        max_response_output_tokens: 4096
      },
    };
    
    oai.send(JSON.stringify(sessionUpdate));
    sessionConfigured = true;
    console.log('[WS] ✅ Session configured');
    
  } catch (e) {
    console.error('[WS] ❌ Failed to create OpenAI socket:', e);
    ws.close();
    return;
  }

  // Register Twilio message handler
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());
      
      if (msg.event === 'start') {
        twilioStreamSid = msg.start?.streamSid || msg.streamSid || null;
        callerNumber = msg?.start?.from || null;
        streamStartMs = Date.now();
        
        console.log('[WS] ▶︎ Twilio start', { callSid, twilioStreamSid, from: callerNumber });
        
        // Trigger greeting NOW that we have the stream
        if (!greetingSent && oaiReady && sessionConfigured) {
          console.log('[WS] 🎤 Triggering greeting...');
          setTimeout(() => {
            oai.send(JSON.stringify({
              type: 'response.create',
              response: {
                modalities: ['text', 'audio'],
                instructions: 'Immediately greet the caller. Say: "Hi! This is Brendan Burns\' AI assistant. I can help answer questions about mortgages, including mortgage guidelines like VA, FHA, USDA, Fannie Mae, and Freddie Mac loans. I can also schedule meetings with Brendan and answer any real estate or mortgage-related questions you have. What can I help you with today?"'
              }
            }));
            greetingSent = true;
          }, 300);
        }
        
      } else if (msg.event === 'media' && msg.media?.payload) {
        const muBuf = Buffer.from(msg.media.payload, 'base64');
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
            const fullTranscript = transcriptParts.join('\n');
            const tldr = await summarizeTLDR(fullTranscript);
            
            // Send follow-up if enabled
            if (process.env.AUTO_FOLLOW_UP === 'true' && callerNumber) {
              const appLink = process.env.APPLICATION_LINK || 'https://movement.com/lo/brendan-burns';
              await sendSMS(
                callerNumber,
                `Thanks for calling! If you'd like to get started, here's the application link: ${appLink}`
              );
            }
            
            await sendEmail({
              subject: `Call Summary – ${callerNumber ?? 'Unknown'} (${callSid})`,
              html: `
                <h2>Call Summary</h2>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                  <strong>Quick Summary:</strong>
                  <p>${tldr}</p>
                </div>
                <hr/>
                <h3>Full Transcript</h3>
                <pre style="white-space: pre-wrap;">${fullTranscript}</pre>
              `,
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

  // Set up OpenAI event handlers
  oai.on('close', (code, reason) => {
    console.log('[OAI] ✖︎ Realtime closed', code, String(reason || ''));
    oaiReady = false;
  });

  // OpenAI to Twilio  
  oai.on('message', async (message) => {
    try {
      const evt = JSON.parse(message.toString());
      
      // Log conversation transcripts
      if (evt.type === 'conversation.item.input_audio_transcription.completed') {
        const transcript = evt?.transcript || '';
        if (transcript) {
          transcriptParts.push(`[Caller] ${transcript}`);
          console.log('[Transcript] Caller:', transcript);
        }
      }
      
      if (evt.type === 'response.audio_transcript.delta') {
        const delta = evt?.delta || '';
        if (delta) {
          transcriptParts.push(`[Assistant] ${delta}`);
        }
      }
      
      // Handle function calls
      if (evt.type === 'response.function_call_arguments.done') {
        const funcName = evt?.name;
        const funcArgs = evt?.arguments ? JSON.parse(evt.arguments) : {};
        
        const result = await handleFunctionCall(funcName, funcArgs, callerNumber, callSid);
        
        // Send function result back to OpenAI
        oai.send(JSON.stringify({
          type: 'conversation.item.create',
          item: {
            type: 'function_call_output',
            call_id: evt?.call_id,
            output: JSON.stringify(result)
          }
        }));
        
        // Trigger response generation
        oai.send(JSON.stringify({ type: 'response.create' }));
      }
      
      // Stream audio to Twilio
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
        
        ws.send(JSON.stringify(media));
      }
      
      if (evt.type === 'error') {
        console.error('[OAI] ❌ Error event:', evt);
      }
    } catch (err) {
      console.error('[WS] ❌ handle OAI message error:', err);
    }
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
          { 
            role: 'system', 
            content: 'You create concise, actionable summaries of mortgage consultation calls. Focus on: what they want, their situation, next steps needed, and urgency level.'
          },
          { 
            role: 'user', 
            content: `Summarize this mortgage call in 3-5 bullet points:\n\n${transcript}` 
          },
        ],
        max_tokens: 300,
        temperature: 0.3,
      },
      { headers: { Authorization: `Bearer ${key}` } }
    );
    return r.data?.choices?.[0]?.message?.content?.trim?.() ?? '—';
  } catch (e) {
    console.error('[TLDR] error:', e?.message || e);
    return '—';
  }
}
