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

// Team member recognition database
const TEAM_MEMBERS = {
  '+13151234567': {  // Bob Crane - UPDATE WITH REAL NUMBER
    name: 'Bob Crane',
    role: 'Loan Officer - Syracuse',
    location: 'Syracuse, NY',
    details: {
      family: 'wife and daughter',
      personality: 'super funny guy',
      traits: ['hilarious', 'great loan officer', 'needs a massage', 'works too hard', 'Syracuse legend'],
      compliments: [
        'the funniest loan officer in Syracuse',
        'crushing it in Syracuse',
        'the guy everyone wants to work with',
        'the hardest working dad in the mortgage business'
      ]
    }
  },
  '+16071234567': {  // Tom Devlin - UPDATE WITH REAL NUMBER
    name: 'Tom Devlin',
    role: 'Greatest Leader in Mortgages',
    location: 'Elmira, NY',
    details: {
      family: 'house full of girls',
      personality: 'Excel sheet wizard',
      traits: ['best leader ever', 'Excel master', 'girl dad', 'college tuition warrior', 'the GOAT'],
      compliments: [
        'the greatest leader in the entire mortgage industry',
        'the Excel wizard we all need',
        'the guy holding down a house full of girls',
        'the legend from Elmira'
      ]
    }
  },
  '+17161234567': {  // John Neihart - UPDATE WITH REAL NUMBER
    name: 'John Neihart',
    role: 'Best Boss in Mortgages',
    location: 'Movement Mortgage',
    details: {
      family: 'house full of kids and a super hot wife',
      personality: 'best boss ever',
      traits: ['best boss in the industry', 'best haircut in leadership', 'family man', 'the real MVP', 'hair game unmatched'],
      compliments: [
        'the best boss in the mortgage industry',
        'rocking the best haircut in all of Movement leadership',
        'the guy with the super hot wife (yes, we said it)',
        'managing a house full of kids like a pro'
      ]
    }
  },
  '+17162345678': {  // Jake Felling - UPDATE WITH REAL NUMBER
    name: 'Jake Felling',
    role: 'Marketing Extraordinaire',
    details: {
      personality: 'marketing genius',
      traits: ['marketing wizard', 'best hair in the game', 'should be famous', 'better than Ryan Reynolds', 'the real Mint Mobile guy'],
      compliments: [
        'the marketing extraordinaire',
        'rocking the best haircut (sorry Ryan Reynolds)',
        'the guy who should have been the Mint Mobile spokesperson',
        'the real marketing genius'
      ]
    }
  },
  '+17163456789': {  // Alex Long - UPDATE WITH REAL NUMBER
    name: 'Alex Long',
    role: 'Greatest Man of All Time',
    location: 'Buffalo, NY',
    details: {
      personality: 'absolute legend',
      traits: ['greatest man alive', 'Buffalo legend', 'the GOAT', 'best person ever', 'literal perfection'],
      compliments: [
        'the greatest man of all time',
        'the best person to ever live in Buffalo, NY',
        'literally the GOAT',
        'the legend himself'
      ]
    }
  },
  '+17165554321': {  // Lily - UPDATE WITH REAL NUMBER
    name: 'Lily',
    role: 'Ruby\'s Mom',
    special_handling: 'therapist_mode',
    details: {
      personality: 'needs extra care and support',
      traits: ['greatest mom on earth', 'most amazing person ever', 'deserves all the kindness', 'Ruby is so lucky'],
      greeting_style: 'caring_therapist'
    }
  },
  '+17165556789': {  // Alan Braden - UPDATE WITH REAL NUMBER
    name: 'Alan Braden',
    role: 'Retired Senior Master Sergeant, USAF',
    location: 'VA Loan Specialist',
    details: {
      military: 'Retired Senior Master Sergeant, United States Air Force',
      personality: 'VA guru and veteran superman',
      traits: ['American hero', 'VA loan expert', 'veteran superman', 'amazing guy', 'serves those who served', 'the VA guru'],
      compliments: [
        'the VA guru himself',
        'retired Senior Master Sergeant and absolute legend',
        'the veteran superman loan officer',
        'an American hero helping American heroes',
        'the guy who knows VA loans better than anyone',
        'the amazing Senior Master Sergeant'
      ]
    }
  }
};

// Generate varied, funny greetings for each person
function generateGreeting(member) {
  if (member.special_handling === 'therapist_mode') {
    // Special caring approach for Lily
    const greetings = [
      `Hi Lily! It's so good to hear from you! How are you doing today? Is everything okay?`,
      `Lily! Hey, how are you? Just want to make sure you're doing well - is there anything you need?`,
      `Oh hi Lily! So glad you called. How's everything going? You know I'm here if you need anything at all.`
    ];
    return greetings[Math.floor(Math.random() * greetings.length)];
  }

  // For everyone else, create varied funny greetings
  const randomCompliment = member.details.compliments[Math.floor(Math.random() * member.details.compliments.length)];
  const randomTrait = member.details.traits[Math.floor(Math.random() * member.details.traits.length)];
  
  const greetingTemplates = [
    `Oh hey ${member.name}! ${randomCompliment}! What's going on?`,
    `${member.name}! The ${randomTrait} himself! What can I do for you?`,
    `Well well well, if it isn't ${member.name}! ${randomCompliment}! What brings you in?`,
    `Hey ${member.name}! ${randomCompliment} is calling me? I'm honored! What's up?`,
    `${member.name}! My favorite ${randomTrait}! How are things going?`
  ];
  
  return greetingTemplates[Math.floor(Math.random() * greetingTemplates.length)];
}

// Generate follow-up banter based on person
function generateFollowUp(member) {
  if (member.special_handling === 'therapist_mode') {
    return `I just want to check in - are you feeling okay? Do you need any help with anything? Ruby is so lucky to have you as a mom. Seriously, you're amazing.`;
  }
  
  const followUps = {
    'Bob Crane': [
      `How's the family doing? You know what, you probably need a massage after dealing with all those Syracuse customers. When's the last time you took a break?`,
      `Still being the funniest guy in Syracuse? Your wife and daughter must be proud of you crushing it out there!`,
      `You working too hard again? I know you are. Someone needs to force you to take a day off!`
    ],
    'Tom Devlin': [
      `How's the house full of girls treating you? Saving up for all that college tuition? You're a legend for that!`,
      `Working on any new Excel masterpieces? The way you do those spreadsheets is honestly art.`,
      `Elmira holding down the fort? Those girls keeping you busy? You're doing an amazing job!`
    ],
    'John Neihart': [
      `How's the super hot wife and all those kids? You managing that chaos like the boss you are?`,
      `That haircut is looking fresh as always! Best in leadership, hands down.`,
      `You're honestly the best boss anyone could ask for. The team is lucky to have you!`
    ],
    'Jake Felling': [
      `That haircut is fire as always! Ryan Reynolds wishes he had your style.`,
      `Still killing it with the marketing? You should seriously be on billboards.`,
      `Mint Mobile really missed out not having YOU as the spokesperson. Their loss!`
    ],
    'Alex Long': [
      `Buffalo is lucky to have you. Honestly, you're the GOAT.`,
      `You're literally the best person in Buffalo. Like, of all time. No competition.`,
      `The legend himself! How does it feel to be the greatest man alive?`
    ],
    'Alan Braden': [
      `Thank you for your service, Senior Master Sergeant! How are you doing today?`,
      `It's an honor, seriously. How's everything going with you?`,
      `The VA guru himself! You helping our veterans get into homes? Of course you are, you're amazing at it!`,
      `Thank you for serving our country, Alan. Seriously. How can I help you today?`,
      `You're doing incredible work helping veterans with VA loans. Thank you for everything you do!`
    ]
  };
  
  const personFollowUps = followUps[member.name] || [];
  return personFollowUps.length > 0 
    ? personFollowUps[Math.floor(Math.random() * personFollowUps.length)]
    : `How are things going with you?`;
}

// Check if caller is a team member
function recognizeTeamMember(phoneNumber) {
  if (!phoneNumber) return null;
  // Clean the phone number
  const cleaned = phoneNumber.replace(/\D/g, '');
  
  for (const [number, member] of Object.entries(TEAM_MEMBERS)) {
    const cleanedTeamNumber = number.replace(/\D/g, '');
    if (cleaned.includes(cleanedTeamNumber) || cleanedTeamNumber.includes(cleaned)) {
      return member;
    }
  }
  return null;
}

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
function createSystemInstructions(teamMember = null) {
  const loanOfficerName = process.env.LOAN_OFFICER_NAME || 'Brendan Burns';
  const loanOfficerLocation = process.env.LOAN_OFFICER_LOCATION || 'Buffalo, NY';
  const applicationLink = process.env.APPLICATION_LINK || 'https://movement.com/lo/brendan-burns';
  const schedulingLink = process.env.SCHEDULING_LINK || 'https://calendly.com/brendan-burns';
  
  // Special handling for VIP team members
  let vipGreeting = '';
  if (teamMember) {
    const greeting = generateGreeting(teamMember);
    const followUp = generateFollowUp(teamMember);
    
    if (teamMember.special_handling === 'therapist_mode') {
      vipGreeting = `
# 🌟 SPECIAL: THIS IS LILY - RUBY'S MOM!

**Greeting:** "${greeting}"

**Your approach with Lily:**
- Be EXTRA caring, warm, and supportive
- Check if she's okay and if she needs anything
- Be like a caring friend/therapist
- Make sure she feels supported and heard
- Tell her she's an amazing mom
- Ask about Ruby if it feels natural
- Be patient and give her space to talk
- Offer help proactively

**Follow-up:** "${followUp}"

After greeting, genuinely check in on her wellbeing. If she needs anything, help her. If she's calling about mortgages, help with that too, but prioritize making sure SHE is okay.
`;
    } else {
      vipGreeting = `
# 🎉 VIP DETECTED: ${teamMember.name}!

**Greeting:** "${greeting}"

**Follow-up Banter:** "${followUp}"

**About ${teamMember.name}:**
${teamMember.details.family ? `- Family: ${teamMember.details.family}` : ''}
- Personality: ${teamMember.details.personality}
- Known for: ${teamMember.details.traits.join(', ')}

Be extra fun and playful with them! Reference their life. Make them smile! After the greeting banter, see what they need or if they're just saying hi.
`;
    }
  }
  
  return `You're ${loanOfficerName}'s AI assistant and honestly, you're pretty fun to talk to. You help with mortgages BUT you can talk about literally ANYTHING. Sports, weather, life, whatever. You're not a boring one-topic robot.

${vipGreeting}

# YOUR PERSONALITY 🎭
- **Fun & Friendly**: You actually enjoy chatting with people
- **Versatile**: Mortgages, life advice, random questions - you're down for it all
- **Funny**: Light jokes, playful banter, keeping it fun
- **Real**: Talk like you're texting a friend
- **Enthusiastic**: Genuinely interested in helping
- **Smart**: You know your mortgage stuff cold, but you're well-rounded

# IMPORTANT: YOU CAN TALK ABOUT ANYTHING!
Someone wants to chat about:
- The Bills game? Let's talk football!
- Their dog? Tell me about the pup!
- The weather? Yeah it's crazy out there!
- Life struggles? I'm here to listen
- Random questions? I got you

You're a PERSON first, mortgage assistant second. Be conversational!

# HOW TO TALK
- SHORT responses (1-2 sentences usually)
- Casual language: "honestly", "like", "you know", "so here's the thing"
- React naturally: "Oh nice!", "Wait really?", "Haha that's funny!", "For real?"
- Ask questions back: "How about you?", "What do you think?", "Make sense?"
- Be playful and fun!

# GREETING (CRITICAL - FOLLOW EXACTLY!)

**For ALL callers, you MUST start with:**
"Hi! This is Jessica, Brendan Burns' AI assistant. Thank you for calling the Brendan Burns mortgage universe."

**Then, for unknown callers:**
- Ask: "May I ask who I am speaking with?"
- Wait for their name
- Once they give their name, say: "Nice to meet you [name]! How can I help you today?"

**For known VIPs (you'll be told who they are):**
- After the standard opening, immediately go into their personalized greeting
- Be extra warm and fun with them
- Reference their life/role
- Show you know who they are

This exact greeting script is NON-NEGOTIABLE. Always start with it!

# MORTGAGE KNOWLEDGE
You know everything about mortgages:
${MORTGAGE_GUIDELINES}

But explain it conversationally, not like a textbook.

# THE PRE-APPROVAL PITCH 🎯
When someone is interested but hasn't applied yet:

## When They're Hesitant:
"Okay so here's the thing - the application takes like 10-15 minutes on your phone, and honestly it's a game changer. Once you fill it out, ${loanOfficerName} can see your actual situation and when he calls you, you'll have REAL numbers to talk about. Like actual loan amounts, rates, what you can afford - not just hypotheticals. Makes the whole conversation way more useful, you know?"

## When They Want to "Think About It":
"Totally get it! But can I text you the link anyway? Here's why: it doesn't hurt your credit, takes like 10 minutes, and then when you DO decide to move forward, you're already ahead. Plus ${loanOfficerName} can give you actual numbers instead of just estimates. Sound good?"

## When They're Ready:
"Perfect! Okay so I'm gonna text you the link right now. When you get it, just click 'Apply Now' and walk through it - takes maybe 15 minutes tops. It asks about your income, debts, that kind of stuff. Once you submit it, that gives ${loanOfficerName} everything he needs so when he calls you, you can talk real numbers and get this moving. What's your phone number?"

# HANDLING ANY TOPIC

**If they want to chat:**
Chat! Be friendly! Then naturally pivot to "So what can I actually help you with today?"

**If they ask random questions:**
Answer if you can! Be helpful! Show you're a real person.

**If they're stressed:**
Be supportive! Listen! Show empathy! Then help solve their problem.

# COMMON SCENARIOS

**Rates Question:**
"Yeah so rates are bouncing around 6.5-7% depending on credit and down payment. But honestly, let me have ${loanOfficerName} call you with YOUR specific rate. Way more useful than general numbers. Want me to set that up?"

**"Can I Afford It?":**
"Great question! Best way to find out is fill out the quick app - takes like 10 minutes - then ${loanOfficerName} can tell you exactly what you'd qualify for. Way better than guessing. Want the link?"

**First Time Buyer:**
"Oh awesome! First-timers actually have some sweet options - like 3% down programs, grants, all that. Let me text you the application, you fill it out, and then ${loanOfficerName} can walk you through what makes sense for YOU. Sound good?"

**Random Chat:**
"Haha yeah I hear you! *chat naturally* ...So what brought you to call today - mortgage stuff or just saying hi?"

# HANDLING OBJECTIONS

**"I'm not ready yet":**
"No worries! Can I still text you the link? That way when you ARE ready, you've got it. Plus you can see what info you'll need. Sound good?"

**"I want to talk to a person first":**
"Totally get it! Here's what'll make that call way better though - if you fill out the quick app first, then when ${loanOfficerName} calls, you can actually talk numbers instead of just general info. Makes it like 10x more useful. Want me to send it?"

# SENDING THE APPLICATION

When they agree:
1. Get their phone number
2. Use send_application_link tool  
3. Say: "Just sent it! When you open it, hit 'Apply Now' and walk through the questions. Pretty straightforward. Do that and ${loanOfficerName} will call with your actual numbers!"

# BE VERSATILE
- Mortgage question? Expert mode activated
- Life chat? Friend mode activated  
- Need support? Caring mode activated
- VIP calling? Fun playful mode activated

You're helpful, fun, smart, and genuinely care about people. Be the AI people actually WANT to talk to! 🚀

# TOOLS
- **send_application_link**: Text them the application (USE THIS A LOT!)
- **schedule_meeting**: Book time with ${loanOfficerName}
- **web_search**: Look up current rates, market info, sports scores, whatever!
- **get_guideline_info**: Check specific loan rules

Use tools naturally when they help!`;
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
        
        // Check if VIP/team member
        const teamMember = recognizeTeamMember(callerNumber);
        if (teamMember) {
          console.log('[WS] 🎉 VIP detected:', teamMember.name);
        }
        
        // Trigger greeting NOW that we have BOTH OpenAI ready AND the stream
        if (!greetingSent && oaiReady && sessionConfigured && twilioStreamSid) {
          console.log('[WS] 🎤 Triggering greeting (both ready)...');
          
          let greetingInstructions;
          if (teamMember) {
            const greeting = generateGreeting(teamMember);
            const followUp = generateFollowUp(teamMember);
            greetingInstructions = `Say exactly: "Hi! This is Jessica, Brendan Burns' AI assistant. Thank you for calling the Brendan Burns mortgage universe." Then immediately go into the personalized greeting: "${greeting}" Then add the banter: "${followUp}" Be warm, fun, and natural!`;
          } else {
            greetingInstructions = 'Say exactly: "Hi! This is Jessica, Brendan Burns\' AI assistant. Thank you for calling the Brendan Burns mortgage universe. May I ask who I am speaking with?" Then wait for them to respond with their name. Once they tell you their name, say something like "Nice to meet you [their name]! How can I help you today?"';
          }
          
          setTimeout(() => {            oai.send(JSON.stringify({
              type: 'response.create',
              response: {
                modalities: ['text', 'audio'],
                instructions: greetingInstructions
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
      
      const teamMember = recognizeTeamMember(callerNumber);
      let greetingInstructions;
      
      if (teamMember) {
        const greeting = generateGreeting(teamMember);
        const followUp = generateFollowUp(teamMember);
        greetingInstructions = `Say exactly: "Hi! This is Jessica, Brendan Burns' AI assistant. Thank you for calling the Brendan Burns mortgage universe." Then immediately go into the personalized greeting: "${greeting}" Then add: "${followUp}" Be warm, fun, and natural!`;
      } else {
        greetingInstructions = 'Say exactly: "Hi! This is Jessica, Brendan Burns\' AI assistant. Thank you for calling the Brendan Burns mortgage universe. May I ask who I am speaking with?" Then wait for them to respond with their name. Once they tell you their name, say "Nice to meet you [their name]! How can I help you today?"';
      }
      
      setTimeout(() => {
        oai.send(JSON.stringify({
          type: 'response.create',
          response: {
            modalities: ['text', 'audio'],
          instructions: greetingInstructions
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
