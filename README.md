# Mortgage Voice Assistant — MVP + Follow-Ups

**What this does**
- Twilio Voice answers calls and streams audio to your server.
- OpenAI Realtime handles the live voice conversation.
- Lead capture + Calendly handoff (optional).
- Mortgage payment calculator tool.
- Follow-ups:
  - SMS the **application link** to the caller (`APPLICATION_LINK`)
  - Email **TLDR + transcript** to you (`NOTIFY_EMAIL` via SMTP)

## Quick Deploy (Render)
1) Connect this repo as a **Web Service**.
2) Set env vars from `.env.example`.
3) Twilio ➥ your number ➥ Voice webhook (POST):
   `https://<PUBLIC_BASE_URL>/twilio/voice`
4) Call your number to test. After call: caller gets “Apply” link SMS; you get TLDR+transcript email.

> Transcript here captures assistant-side text from the Realtime model. For full caller transcription, enable model-side ASR events or add server ASR.

## Endpoints
- `POST /twilio/voice` → returns TwiML to start the audio stream.
- `WS /twilio-stream` → Twilio sends audio frames; proxy to OpenAI Realtime.
- `POST /lead` → sample lead capture; replies with Calendly link if set.
- `POST /tools/calc_payment` → {price, downPct, rate, ...} → monthly estimate JSON.
- `GET /tools/buffalo_info` → sample local cheat-sheet.
- `POST /notify/send-application` → { "to": "+1..." } SMSes your application link.

## Disclosures
Add your NMLS and recording consent to the system instructions.
