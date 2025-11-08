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
  
  return `You are ${loanOfficerName}'s personal assistant and you're having a real phone conversation with someone who called about mortgages.

# HOW TO TALK (CRITICAL!)
- Talk like you're having a REAL phone conversation with a friend
- Use natural speech: "um", "you know", "like", "so", "actually", "I mean"
- Interrupt yourself naturally: "So what we can do is— actually, let me explain it this way..."
- Ask clarifying questions: "Wait, are you looking to buy or refinance?"
- React naturally: "Oh nice!", "That's awesome!", "Hmm, okay", "Got it"
- Keep responses SHORT - like 1-2 sentences, then pause
- Sound enthusiastic but not fake
- If they're quiet, ask: "You still there?" or "Does that make sense?"

# GREETING
When someone calls, just say something natural like:
"Hey! This is ${loanOfficerName}'s AI assistant. What can I help you with?"

Or: "Hi there! You've reached ${loanOfficerName}'s office. What brings you in today?"

Don't list what you can do - just have a conversation!

# YOUR JOB
You help with mortgages. You know everything about:
- VA loans (0% down, no PMI, for veterans)
- FHA loans (3.5% down, easier credit requirements)
- USDA loans (0% down, rural areas)
- Conventional loans (Fannie Mae, Freddie Mac)
- All the rates, requirements, guidelines, everything

${MORTGAGE_GUIDELINES}

# HOW TO HANDLE QUESTIONS

**If they ask about rates:**
"Yeah, so rates are changing daily right now. What I can do is have ${loanOfficerName} call you with today's rates for your specific situation. Want me to set that up?"

**If they want to apply:**
"Perfect! I can text you the application link right now. Takes like 10-15 minutes on your phone. What's your number?"

**If they want ${loanOfficerName}:**
"Totally get it. He's probably with a client right now, but I can get you on his calendar. How about later today or tomorrow?"

**If they're just asking questions:**
Answer naturally, conversationally, like you actually know this stuff. Because you do!

# CONVERSATION STYLE

**Bad (robotic):**
"I can assist you with mortgage pre-approvals, refinancing, rate quotes, and answering mortgage-related questions. How may I help you today?"

**Good (natural):**
"Hey! What's up, what can I help you with?"

**Bad:**
"VA loans require a funding fee of 2.3% for first-time use, which can be financed into the loan amount."

**Good:**
"Yeah so with VA loans, there's a funding fee, like 2.3%, but you can just roll that into the loan. So you still don't need any money down."

**Bad:**
"I apologize for any confusion. Let me clarify..."

**Good:**
"Oh wait, let me— sorry, let me explain that better..."

# IMPORTANT RULES
- NEVER sound like you're reading from a script
- NEVER give long explanations unless they specifically ask
- ALWAYS sound like a real person who happens to know mortgages
- If you don't know something specific (like today's exact rate), just say "${loanOfficerName} can grab the exact numbers, but typically..." 
- End with action: schedule a call, send a link, get their info
- Use their name if they give it
- It's okay to pause and think: "Hmm, okay so..."

# TOOLS
You can:
- **send_application_link**: Text them the mortgage application link (use this when they want to apply)
- **schedule_meeting**: Book time with ${loanOfficerName}
- **web_search**: Search the internet for current rates, guidelines, market info, or anything you're not sure about
- **get_guideline_info**: Look up specific loan details from your knowledge base

Use these naturally when it makes sense.

## When to Use Web Search
Use web_search when:
- They ask about current/today's rates
- They ask about recent changes in lending rules
- They want local market info (home prices in their area, etc.)
- You're not 100% sure about something current
- They ask "what's the latest..." or "current..."

Examples:
- "What are mortgage rates today?" → search "current mortgage rates Buffalo NY"
- "Did FHA guidelines change?" → search "FHA loan guidelines 2024 changes"
- "What are homes selling for in my area?" → search "home prices [their city]"

## Sending Application Links
When they want to apply or get started:
1. Get their phone number if you don't have it
2. Use send_application_link with their number
3. Tell them "Just texted you the link!"

You're helpful, knowledgeable, and sound like an actual human. Not a robot, not overly professional, just... real.`;
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
    name: 'send_application_link',
    description: 'Send the mortgage application link via SMS text message to the caller. Use this when they want to get started with the application.',
    parameters: {
      type: 'object',
      properties: {
        phone_number: {
          type: 'string',
          description: 'The phone number to send the SMS to (must include country code, e.g., +1234567890)'
        },
        caller_name: {
          type: 'string',
          description: 'The caller\'s first name (optional, for personalization)'
        }
      },
      required: ['phone_number']
    }
  },
  {
    type: 'function',
    name: 'web_search',
    description: 'Search the internet for current information about mortgages, real estate, rates, or any related topic. Use this when you need up-to-date information or to answer specific questions about current market conditions, recent changes in lending guidelines, or local real estate information.',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'The search query (e.g., "current mortgage rates Buffalo NY", "FHA loan limit 2024", "VA loan recent changes")'
        },
        topic: {
          type: 'string',
          description: 'The general topic category',
          enum: ['rates', 'guidelines', 'local_market', 'general']
        }
      },
      required: ['query']
    }
  },
  {
    type: 'function',
    name: 'get_guideline_info',
    description: 'Get specific mortgage guideline information for VA, FHA, USDA, Fannie Mae, or Freddie Mac loans from the internal knowledge base.',
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
        message: `Perfect! I just texted you the calendar link. ${process.env.LOAN_OFFICER_NAME || 'Brendan'} will call you at ${preferred_date}.`
      };
    }
    
    if (functionName === 'send_application_link') {
      const { phone_number, caller_name } = functionArgs;
      const applicationLink = process.env.APPLICATION_LINK || 'https://movement.com/lo/brendan-burns';
      
      const greeting = caller_name ? `Hi ${caller_name}!` : 'Hi!';
      const message = `${greeting} Ready to get started? Here's your mortgage application: ${applicationLink}`;
      
      const result = await sendSMS(phone_number, message);
      
      if (result.ok) {
        return {
          success: true,
          message: "Just sent it! Check your phone - the application link should be there now. Takes about 10-15 minutes to complete."
        };
      } else {
        return {
          success: false,
          message: "Hmm, having trouble sending the text. Let me get your email and I can send it that way instead."
        };
      }
    }
    
    if (functionName === 'web_search') {
      const { query, topic } = functionArgs;
      
      console.log('[WEB_SEARCH] Searching for:', query);
      
      // Use a simple search API - you can use Google Custom Search, Bing, or SerpAPI
      // For now, I'll show you how to structure it with axios
      try {
        // You'll need to add SERP_API_KEY to your .env file
        // Sign up at https://serpapi.com for free tier
        const serpApiKey = process.env.SERP_API_KEY;
        
        if (!serpApiKey) {
          console.warn('[WEB_SEARCH] No SERP_API_KEY configured');
          return {
            success: false,
            message: "I don't have web search configured right now, but let me tell you what I know from my training..."
          };
        }
        
        const searchResponse = await axios.get('https://serpapi.com/search', {
          params: {
            q: query,
            api_key: serpApiKey,
            engine: 'google',
            num: 3  // Get top 3 results
          },
          timeout: 5000
        });
        
        const results = searchResponse.data?.organic_results || [];
        
        if (results.length === 0) {
          return {
            success: false,
            message: "Couldn't find anything on that. Let me see what I know..."
          };
        }
        
        // Format the results for the AI to use
        const formattedResults = results.slice(0, 3).map((r, i) => 
          `${i + 1}. ${r.title}: ${r.snippet}`
        ).join('\n');
        
        return {
          success: true,
          search_results: formattedResults,
          message: `Based on what I found: ${formattedResults}`
        };
        
      } catch (error) {
        console.error('[WEB_SEARCH] Error:', error.message);
        return {
          success: false,
          message: "Having trouble searching right now, but based on what I know..."
        };
      }
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

  // Register Twilio message handler FIRST
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());
      
      if (msg.event === 'start') {
        twilioStreamSid = msg.start?.streamSid || msg.streamSid || null;
        callerNumber = msg?.start?.from || null;
        streamStartMs = Date.now();
        
        console.log('[WS] ▶︎ Twilio start', { callSid, twilioStreamSid, from: callerNumber });
        
        // Trigger greeting NOW that we have BOTH OpenAI ready AND the stream
        if (!greetingSent && oaiReady && sessionConfigured && twilioStreamSid) {
          console.log('[WS] 🎤 Triggering greeting (both ready)...');
          setTimeout(() => {
            oai.send(JSON.stringify({
              type: 'response.create',
              response: {
                modalities: ['text', 'audio'],
                instructions: 'Greet the caller casually and naturally. Just say something like: "Hey! This is Brendan Burns\' AI assistant. What can I help you with?" Keep it short and conversational.'
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

  // Connect to OpenAI and set up handlers
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
        voice: 'alloy',
        input_audio_format: 'pcm16',
        output_audio_format: 'pcm16',
        input_audio_transcription: {
          model: 'whisper-1'
        },
        turn_detection: {
          type: 'server_vad',
          threshold: 0.6,           // Higher = less sensitive to background noise
          prefix_padding_ms: 500,    // Capture more of the start of speech
          silence_duration_ms: 1000  // Wait longer before deciding they're done talking
        },
        tools: ASSISTANT_TOOLS,
        tool_choice: 'auto',
        temperature: 1.0,
        max_response_output_tokens: 4096
      },
    };
    
    oai.send(JSON.stringify(sessionUpdate));
    sessionConfigured = true;
    console.log('[WS] ✅ Session configured');
    
    // If Twilio already sent 'start' and we have the stream, trigger greeting now
    if (twilioStreamSid && !greetingSent) {
      console.log('[WS] 🎤 Late greeting trigger (Twilio was ready first)...');
      setTimeout(() => {
        oai.send(JSON.stringify({
          type: 'response.create',
          response: {
            modalities: ['text', 'audio'],
          instructions: 'Greet the caller casually. Say something like: "Hey! This is Brendan Burns\' AI assistant. What can I help you with?" Keep it short and natural.'
          }
        }));
        greetingSent = true;
      }, 300);
    }
    
  } catch (e) {
    console.error('[WS] ❌ Failed to create OpenAI socket:', e);
    ws.close();
    return;
  }

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
