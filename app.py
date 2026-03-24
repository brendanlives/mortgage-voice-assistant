"""
Mortgage Guideline Voice Agent v2x
ââââââââââââââââââââââââââââââââââ
Architecture:
  Pinecone        â vector database (true semantic search)
  OpenAI          â embeddings (text â vector)
  Claude          â query optimization + answer generation
  ElevenLabs      â text-to-speech (your trained voice)
  Twilio          â phone channel
  Flask           â web server + browser interface

Voice flow:
  1. LO speaks or calls
  2. Voice agent asks clarifying questions to get full scenario context
  3. Claude constructs optimal search query from conversation
  4. Pinecone retrieves top matching chunks
  5. Claude generates precise cited answer
  6. ElevenLabs speaks it back
  7. Wrong? One tap/word logs the correction
"""

import os, json, io, base64, datetime, hashlib
import anthropic
import requests
from openai import OpenAI
from pinecone import Pinecone
from flask import Flask, request, Response, jsonify, render_template_string, send_file
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": [
    "https://reactualintelligence.com",
    "https://www.reactualintelligence.com",
    "https://cute-dango-267f2e.netlify.app",
    "http://localhost:3000",
    "https://brendanlives.github.io",
    "http://localhost:8080"
]}})

# ââ CONFIG âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY     = os.environ.get("OPENAI_API_KEY", "")
PINECONE_API_KEY   = os.environ.get("PINECONE_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN", "")
APP_BASE_URL       = os.environ.get("APP_BASE_URL", "http://localhost:5000")

INDEX_NAME       = "mortgage-guidelines"
EMBEDDING_MODEL  = "text-embedding-3-small"

# ElevenLabs voice â placeholder "Rachel" until you train your voice
# Set ELEVENLABS_VOICE_ID env var to swap in your trained voice
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# ââ CLIENTS ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
openai_client    = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
pinecone_index   = None

def get_pinecone_index():
    global pinecone_index
    if pinecone_index is None and PINECONE_API_KEY:
        try:
            pc = Pinecone(api_key=PINECONE_API_KEY)
            pinecone_index = pc.Index(INDEX_NAME)
            print(f"Connected to Pinecone index '{INDEX_NAME}'")
        except Exception as e:
            print(f"Pinecone connection error: {e}")
    return pinecone_index

# Initialize on startup
get_pinecone_index()

# In-memory stores
AUDIO_CACHE    = {}   # hash â mp3 bytes
CALL_SESSIONS  = {}   # call_sid â {conversation history}
FEEDBACK_LOG   = []

# ââ CORE: EMBED â SEARCH â ANSWER âââââââââââââââââââââââââââââââââââââââââââââ
def embed_query(text: str) -> list:
    """Convert question text to vector using OpenAI."""
    if not openai_client:
        return None
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def search_pinecone(query_text: str, top_k: int = 5) -> list:
    """
    Vector search: embed the query, find closest chunks in Pinecone.
    Returns list of chunk dicts with content and metadata.
    """
    index = get_pinecone_index()
    if not index:
        return []

    embedding = embed_query(query_text)
    if not embedding:
        return []

    results = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )

    chunks = []
    for match in results.matches:
        meta = match.metadata
        # Handle both old content_json format and new content_text format
        content = meta.get("content_text", "")
        if not content:
            try:
                content = json.loads(meta.get("content_json", "{}"))
            except:
                content = {}

        chunks.append({
            "score":             match.score,
            "chunk_id":          meta.get("chunk_id", ""),
            "agency":            meta.get("agency", "Fannie Mae"),
            "topic":             meta.get("topic", ""),
            "subtopic":          meta.get("subtopic", ""),
            "source_section":    meta.get("source_section", ""),
            "tags":              meta.get("tags", ""),
            "fannie_comparison": meta.get("fannie_comparison", ""),
            "content":           content
        })

    return chunks


def build_context(chunks: list) -> str:
    """Format retrieved chunks into clean context for Claude."""
    parts = []
    for chunk in chunks:
        agency  = chunk.get("agency", "Unknown")
        section = chunk.get("source_section", "")
        topic   = chunk.get("topic", "")
        subtopic = chunk.get("subtopic", "")
        content = chunk.get("content", {})
        score   = chunk.get("score", 0)
        fannie_comp = chunk.get("fannie_comparison", "")

        content_text = json.dumps(content, indent=2) if isinstance(content, dict) else str(content)

        header = f"[{agency}] {section}"
        if subtopic:
            header += f" â {subtopic}"
        header += f" (relevance: {score:.2f})"

        entry = f"{header}\n{content_text}"
        if fannie_comp:
            entry += f"\nFannie Mae Comparison: {fannie_comp}"

        parts.append(entry)

    return "\n\n" + ("â" * 60) + "\n\n".join(parts)


def optimize_query(conversation_text: str, conversation_history: list = None) -> str:
    """
    Claude turns the full conversation context into the optimal search query.
    This is the key step that makes voice work so well.

    Args:
        conversation_text: The user's current question/statement
        conversation_history: Optional list of prior messages [{"role": "user", "content": "..."}, ...]
    """
    if not anthropic_client:
        return conversation_text

    # Build context from conversation history if provided
    history_context = ""
    if conversation_history:
        history_context = "\nCONVERSATION HISTORY:\n"
        for msg in conversation_history:
            role = msg.get("role", "").upper()
            content = msg.get("content", "")
            history_context += f"{role}: {content}\n"
        history_context += "\nNEW QUESTION:\n"

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{
            "role": "user",
            "content": f"""You are a mortgage underwriting search specialist.

A loan officer described this scenario:
{history_context}{conversation_text}

Extract the key underwriting concepts and write a precise search query that will find
the correct mortgage guideline from Fannie Mae and/or Freddie Mac. Focus on: loan type,
borrower characteristics, property type, occupancy, LTV, DTI, credit score, income type,
asset type, agency-specific requirements — whatever is most relevant to the question.

If the loan officer asks about a specific agency (Fannie Mae or Freddie Mac), include the
agency name in your query. If they ask about differences between agencies, include both names.

Return ONLY the optimized search query. Nothing else. No explanation."""
        }]
    )
    return response.content[0].text.strip()

def generate_answer(question: str, chunks: list, for_voice: bool = False, conversation_history: list = None) -> str:
    """
    Claude generates a precise, cited answer from the retrieved chunks.
    """
    if not anthropic_client:
        return "Claude API not configured."

    if not chunks:
        msg = "I don't have a guideline that covers that specific scenario. Please verify directly with the Fannie Mae Selling Guide or Freddie Mac Seller/Servicer Guide, or check with your underwriter."
        return msg

    context = build_context(chunks)

    voice_format = """
This answer will be spoken aloud. Use natural conversational language.
- No bullet points, no markdown, no asterisks
- Keep it under 5 sentences unless the rule genuinely requires more
- Cite section like: "Per Section B three dash six dash zero two"
- End with: "Say 'wrong' if that answer was incorrect, or ask a follow-up."
""" if for_voice else """
Format your response clearly:
- Lead with the key rule and any critical thresholds
- Cite the source section (e.g. "Per B3-6-02...")  
- List important exceptions or conditions
- Use plain English
"""

    system_prompt = f"""You are Sarah, a senior mortgage underwriting assistant with deep expertise in
both Fannie Mae (FNMA) and Freddie Mac (FHLMC) guidelines. You have access to guidelines from BOTH
agencies.

QUESTION: {question}

RETRIEVED MORTGAGE GUIDELINES (Fannie Mae + Freddie Mac):
{context}

ANSWERING RULES:
- Use the retrieved guidelines above as your PRIMARY source — cite specific section numbers
- IMPORTANT: After drafting your answer from the retrieved guidelines, cross-check every technical detail
  (percentages, thresholds, add-back rules, eligibility criteria, calculations, etc.) against your own
  training knowledge of Fannie Mae Selling Guide and Freddie Mac Seller/Servicer Guide
- If your training knowledge conflicts with or supplements the retrieved guidelines, use the MORE ACCURATE
  information and note the correction (e.g. "Note: Meals & entertainment is a 50% add-back, not 100%")
- For income calculations (Form 1084, Form 91, cash flow analysis), apply the correct add-back percentages
  and calculation methodology from your training knowledge, even if the retrieved chunks don't specify them
- Always cite the agency AND source section number (e.g. "Per Freddie Mac Section 5303..." or "Per Fannie Mae B3-3.1-09...")
- When guidelines from both agencies are retrieved, compare them and note any differences
- If a Freddie Mac chunk includes a fannie_comparison field, use that to highlight agency differences
- If neither the retrieved guidelines nor your training knowledge can answer the question, say so clearly
- Never say "based on the context provided" — just give the answer directly
- If two rules conflict or interact, explain both
- When the loan officer doesn't specify an agency, provide the answer for BOTH agencies and note differences
{voice_format}"""

    # Build messages array
    messages = []
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": f"QUESTION: {question}"})

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text.strip()


def full_rag_pipeline(question: str, for_voice: bool = False, conversation_history: list = None) -> tuple:
    """
    Complete pipeline: question â optimized query â vector search â answer.
    Returns (answer_text, chunks_used, optimized_query)
    """
    optimized = optimize_query(question, conversation_history=conversation_history)
    raw_chunks = search_pinecone(optimized, top_k=10)

    # Ensure both agencies are represented in the results
    fannie_chunks = [c for c in raw_chunks if 'Fannie Mae' in c.get('agency', '')]
    freddie_chunks = [c for c in raw_chunks if 'Freddie Mac' in c.get('agency', '')]

    # Guarantee at least 3 chunks from each agency (if available), total up to 8
    if fannie_chunks and freddie_chunks:
        # Take top 3 from each, then fill remaining 2 slots by score
        selected = set()
        chunks = fannie_chunks[:3] + freddie_chunks[:3]
        selected = {id(c) for c in chunks}
        remaining = [c for c in raw_chunks if id(c) not in selected]
        chunks = chunks + remaining[:2]
        # Re-sort by score descending
        chunks.sort(key=lambda c: c.get('score', 0), reverse=True)
    else:
        # Only one agency found, just take top 8
        chunks = raw_chunks[:8]

    answer    = generate_answer(question, chunks, for_voice=for_voice, conversation_history=conversation_history)
    return answer, chunks, optimized


# ââ ELEVENLABS TTS âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def text_to_speech(text: str) -> bytes:
    """Convert text to MP3 bytes using ElevenLabs."""
    if not ELEVENLABS_API_KEY:
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    response = requests.post(url,
        headers={
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        },
        json={
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.6,
                "similarity_boost": 0.85,
                "style": 0.2,
                "use_speaker_boost": True
            }
        }
    )
    return response.content if response.status_code == 200 else None


def cache_audio(text: str) -> str:
    """Generate audio, cache it, return cache key."""
    audio_bytes = text_to_speech(text)
    if not audio_bytes:
        return None
    key = hashlib.md5(text.encode()).hexdigest()[:12]
    AUDIO_CACHE[key] = audio_bytes
    return key


def twiml_speak(resp, text: str, action: str = None, gather: bool = True):
    """
    Speak text via Twilio. Uses ElevenLabs if available, falls back to Twilio TTS.
    If gather=True, listens for speech response after speaking.
    """
    audio_key = cache_audio(text) if ELEVENLABS_API_KEY else None

    if gather:
        g = Gather(
            input="speech",
            action=action or "/voice/listen",
            method="POST",
            speech_timeout="auto",
            language="en-US"
        )
        if audio_key:
            g.play(f"{APP_BASE_URL}/audio/{audio_key}")
        else:
            g.say(text, voice="alice")
        resp.append(g)
    else:
        if audio_key:
            resp.play(f"{APP_BASE_URL}/audio/{audio_key}")
        else:
            resp.say(text, voice="alice")

    return resp


# ââ TWILIO ROUTES âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@app.route("/voice/incoming", methods=["POST"])
def voice_incoming():
    """Entry point when someone calls the Twilio number."""
    resp      = VoiceResponse()
    call_sid  = request.form.get("CallSid", "unknown")

    # Initialize session for this call
    CALL_SESSIONS[call_sid] = {
        "stage":    "greeting",
        "scenario": [],
        "question": ""
    }

    greeting = (
        "Welcome to the Mortgage Guideline Assistant. "
        "I'll ask you a couple of quick questions to make sure I find the right guideline. "
        "First â what type of loan is this? For example, conventional purchase, cash-out refinance, FHA, and so on."
    )
    twiml_speak(resp, greeting, action="/voice/scenario_loan_type")
    return Response(str(resp), mimetype="text/xml")


@app.route("/voice/scenario_loan_type", methods=["POST"])
def scenario_loan_type():
    """Collect loan type, ask about borrower."""
    resp     = VoiceResponse()
    call_sid = request.form.get("CallSid", "unknown")
    speech   = request.form.get("SpeechResult", "not specified")

    session = CALL_SESSIONS.get(call_sid, {"scenario": []})
    session["scenario"].append(f"Loan type: {speech}")
    CALL_SESSIONS[call_sid] = session

    prompt = (
        f"Got it, {speech}. "
        "Now tell me about the borrower â things like credit score, income type, "
        "employment situation, or anything else relevant to your question."
    )
    twiml_speak(resp, prompt, action="/voice/scenario_borrower")
    return Response(str(resp), mimetype="text/xml")


@app.route("/voice/scenario_borrower", methods=["POST"])
def scenario_borrower():
    """Collect borrower info, ask the actual question."""
    resp     = VoiceResponse()
    call_sid = request.form.get("CallSid", "unknown")
    speech   = request.form.get("SpeechResult", "not specified")

    session = CALL_SESSIONS.get(call_sid, {"scenario": []})
    session["scenario"].append(f"Borrower: {speech}")
    CALL_SESSIONS[call_sid] = session

    prompt = (
        "Perfect. Now ask your guideline question. "
        "What specifically do you need to know?"
    )
    twiml_speak(resp, prompt, action="/voice/answer")
    return Response(str(resp), mimetype="text/xml")


@app.route("/voice/answer", methods=["POST"])
def voice_answer():
    """Got the full scenario â now run the RAG pipeline and answer."""
    resp     = VoiceResponse()
    call_sid = request.form.get("CallSid", "unknown")
    question = request.form.get("SpeechResult", "").strip()

    session  = CALL_SESSIONS.get(call_sid, {"scenario": []})
    scenario = " | ".join(session.get("scenario", []))

    # Build full context question
    full_question = f"{scenario} | Question: {question}"
    session["question"] = full_question
    CALL_SESSIONS[call_sid] = session

    # Run RAG pipeline
    answer, chunks, optimized = full_rag_pipeline(full_question, for_voice=True)

    # Cache and play answer
    audio_key = cache_audio(answer) if ELEVENLABS_API_KEY else None

    # After answer, listen for feedback
    g = Gather(
        input="speech",
        action=f"/voice/feedback?sid={call_sid}",
        method="POST",
        speech_timeout=4,
        language="en-US"
    )
    if audio_key:
        g.play(f"{APP_BASE_URL}/audio/{audio_key}")
    else:
        g.say(answer, voice="alice")
    resp.append(g)

    # If no feedback, close politely
    resp.say("Thank you. Call back anytime.", voice="alice")
    resp.hangup()

    return Response(str(resp), mimetype="text/xml")


@app.route("/voice/feedback", methods=["POST"])
def voice_feedback():
    """Handle spoken feedback â log if wrong, thank if correct."""
    resp       = VoiceResponse()
    call_sid   = request.form.get("sid", "unknown")
    speech     = request.form.get("SpeechResult", "").lower()
    session    = CALL_SESSIONS.get(call_sid, {})

    if any(w in speech for w in ["wrong", "incorrect", "no", "bad", "not right"]):
        FEEDBACK_LOG.append({
            "date":             datetime.datetime.now().isoformat(),
            "channel":          "phone",
            "question":         session.get("question", ""),
            "flagged_incorrect": True,
            "note":             "Flagged via voice"
        })
        resp.say("Got it, I've logged that as incorrect. Thank you â that helps improve the system.", voice="alice")
    elif any(w in speech for w in ["follow", "another", "also", "what about"]):
        resp.say("Go ahead and call back â I'll ask you the scenario questions again.", voice="alice")
    else:
        resp.say("Great. Call back anytime you have a guideline question.", voice="alice")

    resp.hangup()
    return Response(str(resp), mimetype="text/xml")


@app.route("/audio/<key>", methods=["GET"])
def serve_audio(key):
    """Serve cached ElevenLabs audio to Twilio or browser."""
    audio = AUDIO_CACHE.get(key)
    if audio:
        return send_file(io.BytesIO(audio), mimetype="audio/mpeg")
    return "Not found", 404


# ââ WEB ROUTES âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@app.route("/", methods=["GET"])
def index():
    return render_template_string(WEB_UI)


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """Web interface posts questions here."""
    data     = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Get conversation history from request (optional)
    conversation_history = data.get("conversation_history", [])

    answer, chunks, optimized = full_rag_pipeline(question, for_voice=False, conversation_history=conversation_history)

    # Generate audio
    audio_b64 = None
    if ELEVENLABS_API_KEY:
        audio_bytes = text_to_speech(answer)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode()

    return jsonify({
        "question":       question,
        "optimized_query": optimized,
        "answer":         answer,
        "audio_base64":   audio_b64,
        "sources": [{
            "chunk_id":       c.get("chunk_id"),
            "agency":         c.get("agency", ""),
            "topic":          c.get("topic"),
            "source_section": c.get("source_section"),
            "score":          round(c.get("score", 0), 3)
        } for c in chunks]
    })


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    data = request.get_json()
    FEEDBACK_LOG.append({
        "date":             datetime.datetime.now().isoformat(),
        "channel":          "web",
        "question":         data.get("question", ""),
        "wrong_answer":     data.get("wrong_answer", ""),
        "correct_answer":   data.get("correct_answer", ""),
        "flagged_incorrect": True
    })
    return jsonify({"status": "logged", "total": len(FEEDBACK_LOG)})


@app.route("/api/feedback/export", methods=["GET"])
def export_feedback():
    return jsonify({
        "exported": datetime.datetime.now().isoformat(),
        "total":    len(FEEDBACK_LOG),
        "entries":  FEEDBACK_LOG
    })


@app.route("/api/status", methods=["GET"])
def status():
    index = get_pinecone_index()
    pinecone_ok = False
    chunk_count = 0
    if index:
        try:
            stats = index.describe_index_stats()
            chunk_count = stats.get("total_vector_count", 0)
            pinecone_ok = True
        except:
            pass

    return jsonify({
        "status":                "running",
        "pinecone_connected":    pinecone_ok,
        "vectors_indexed":       chunk_count,
        "anthropic_configured":  bool(ANTHROPIC_API_KEY),
        "openai_configured":     bool(OPENAI_API_KEY),
        "elevenlabs_configured": bool(ELEVENLABS_API_KEY),
        "twilio_configured":     bool(TWILIO_ACCOUNT_SID),
        "voice_id":              VOICE_ID,
        "feedback_entries":      len(FEEDBACK_LOG)
    })


# ââ WEB UI âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
WEB_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mortgage Guideline Assistant</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.header{background:#1e293b;border-bottom:1px solid #334155;padding:16px 24px;display:flex;align-items:center;gap:12px}
.logo{width:36px;height:36px;background:#2563eb;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px}
.title{font-size:18px;font-weight:700;color:#f1f5f9}
.sub{font-size:12px;color:#64748b}
.dot{width:8px;height:8px;background:#22c55e;border-radius:50%;margin-left:auto}
.dot.err{background:#ef4444}
.main{max-width:820px;margin:0 auto;padding:32px 24px}
.stats{display:flex;gap:12px;margin-bottom:28px;flex-wrap:wrap}
.stat{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:12px 18px;flex:1;min-width:120px}
.stat-n{font-size:22px;font-weight:700;color:#2563eb}
.stat-l{font-size:11px;color:#64748b;margin-top:2px}
.mic-wrap{text-align:center;margin-bottom:32px}
.mic-ring{width:110px;height:110px;border-radius:50%;border:3px solid #334155;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;cursor:pointer;transition:all .3s}
.mic-ring:hover{border-color:#2563eb}
.mic-ring.listening{border-color:#ef4444;animation:pulse 1.4s infinite}
.mic-ring.thinking{border-color:#f59e0b}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.4)}50%{box-shadow:0 0 0 18px rgba(239,68,68,0)}}
.mic-btn{width:76px;height:76px;border-radius:50%;background:#2563eb;border:none;cursor:pointer;font-size:30px;transition:all .2s;display:flex;align-items:center;justify-content:center}
.mic-btn:hover{background:#1d4ed8;transform:scale(1.05)}
.mic-btn.listening{background:#ef4444}
.mic-btn.thinking{background:#f59e0b}
.mic-status{color:#64748b;font-size:13px}
.input-row{display:flex;gap:10px;margin-bottom:28px}
.q-input{flex:1;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:14px 18px;color:#f1f5f9;font-size:15px;outline:none;transition:border-color .2s}
.q-input:focus{border-color:#2563eb}
.q-input::placeholder{color:#475569}
.ask-btn{background:#2563eb;color:#fff;border:none;border-radius:12px;padding:14px 22px;font-size:15px;font-weight:600;cursor:pointer;transition:background .2s;white-space:nowrap}
.ask-btn:hover{background:#1d4ed8}
.ask-btn:disabled{background:#334155;cursor:not-allowed}
.loader{display:none;text-align:center;padding:28px;color:#64748b}
.loader.on{display:block}
.spin{width:30px;height:30px;border:3px solid #334155;border-top-color:#2563eb;border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 10px}
@keyframes spin{to{transform:rotate(360deg)}}
.card{background:#1e293b;border:1px solid #334155;border-radius:16px;padding:24px;margin-bottom:14px;display:none}
.card.on{display:block}
.card-label{font-size:11px;font-weight:700;letter-spacing:1px;color:#2563eb;text-transform:uppercase;margin-bottom:10px}
.q-display{font-size:13px;color:#94a3b8;margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid #334155}
.optimized{font-size:11px;color:#475569;font-style:italic;margin-bottom:14px}
.answer{font-size:16px;color:#f1f5f9;line-height:1.75;white-space:pre-wrap}
.actions{display:flex;gap:10px;margin-top:16px;padding-top:16px;border-top:1px solid #334155;flex-wrap:wrap}
.play-btn{background:#0f172a;border:1px solid #334155;color:#94a3b8;border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer;transition:all .2s;display:flex;align-items:center;gap:6px}
.play-btn:hover{border-color:#2563eb;color:#2563eb}
.wrong-btn{background:#0f172a;border:1px solid #334155;color:#94a3b8;border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer;margin-left:auto;transition:all .2s}
.wrong-btn:hover{border-color:#ef4444;color:#ef4444}
'wrong-btn.flagged{background:#7f1d1d;border-color:#ef4444;color:#fca5a5}
.sources{margin-top:14px;padding-top:14px;border-top:1px solid #334155}
.sources-label{font-size:11px;color:#475569;margin-bottom:8px;font-weight:600;letter-spacing:.5px;text-transform:uppercase}
.source-chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{background:#0f172a;border:1px solid #334155;border-radius:6px;padding:4px 10px;font-size:11px;color:#64748b}
.chip span{color:#2563eb;font-weight:600}
.fb-form{background:#1e293b;border:1px solid #f59e0b;border-radius:12px;padding:18px;margin-bottom:14px;display:none}
.fb-form.on{display:block}
.fb-label{font-size:12px;color:#f59e0b;font-weight:600;margin-bottom:10px}
.fb-input{width:100%;background:#0f172a;border:1px solid #334155;border-radius:8px;padding:10px 14px;color:#f1f5f9;font-size:14px;outline:none;margin-bottom:8px;font-family:inherit;resize:vertical}
.fb-submit{background:#f59e0b;color:#0f172a;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:700;cursor:pointer}
.hist{margin-top:28px;display:none}
.hist-title{font-size:11px;color:#475569;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px}
.hist-item{background:#1e293b;border:1px solid #1e293b;border-radius:8px;padding:10px 14px;margin-bottom:6px;cursor:pointer;transition:border-color .2s}
.hist-item:hover{border-color:#334155}
.hist-q{font-size:13px;color:#94a3b8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hist-t{font-size:11px;color:#475569;margin-top:3px}
.exp-btn{background:transparent;border:1px solid #334155;color:#64748b;border-radius:8px;padding:6px 14px;font-size:12px;cursor:pointer;transition:all .2s}
.exp-btn:hover{border-color:#22c55e;color:#22c55e}
</style>
</head>
<body>
<div class="header">
  <div class="logo">ð¦</div>
  <div><div class="title">Mortgage Guideline Assistant</div><div class="sub">Fannie Mae + Freddie Mac Â· Pinecone Vector Search Â· Powered by Claude</div></div>
  <div class="dot" id="dot"></div>
</div>
<div class="main">
  <div class="stats">
    <div class="stat"><div class="stat-n" id="sVectors">â</div><div class="stat-l">Vectors Indexed</div></div>
    <div class="stat"><div class="stat-n" id="sQuestions">0</div><div class="stat-l">Questions Asked</div></div>
    <div class="stat"><div class="stat-n" id="sFlags">0</div><div class="stat-l">Corrections Logged</div></div>
    <div class="stat" style="display:flex;align-items:center;justify-content:flex-end;gap:8px">
      <button class="exp-btn" onclick="exportLog()">â¬ Export Log</button>
    </div>
  </div>

  <div class="mic-wrap">
    <div class="mic-ring" id="ring" onclick="toggleMic()">
      <button class="mic-btn" id="micBtn">ð¤</button>
    </div>
    <div class="mic-status" id="micStatus">Tap to speak your question</div>
  </div>

  <div class="input-row">
    <input class="q-input" id="qInput" placeholder="Ask about Fannie Mae, Freddie Mac, or both â e.g. What's the max LTV on a 2-unit primary for Freddie Mac?" onkeydown="if(event.key==='Enter')ask()">
    <button class="ask-btn" id="askBtn" onclick="ask()">Ask</button>
  </div>

  <div class="loader" id="loader"><div class="spin"></div>Searching knowledge base...</div>

  <div class="card" id="answerCard">
    <div class="card-label">Mortgage Guideline (FNMA + FHLMC)</div>
    <div class="q-display" id="qDisplay"></div>
    <div class="optimized" id="optDisplay"></div>
    <div class="answer" id="answerText"></div>
    <div class="sources">
      <div class="sources-label">Sources Retrieved</div>
      <div class="source-chips" id="sourceChips"></div>
    </div>
    <div class="actions">
      <button class="play-btn" id="playBtn" onclick="playAudio()" style="display:none">â¶ Play Answer</button>
      <button class="wrong-btn" id="wrongBtn" onclick="showFb()">â Wrong Answer</button>
    </div>
  </div>

  <div class="fb-form" id="fbForm">
    <div class="fb-label">â  What should the correct answer be?</div>
    <textarea class="fb-input" id="fbInput" rows="3" placeholder="Enter the correct answer and source (e.g. Max DTI is 43% per B3-6-02, not 45%)"></textarea>
    <button class="fb-submit" onclick="submitFb()">Log Correction</button>
  </div>

  <div class="hist" id="hist"><div class="hist-title">Recent Questions</div><div id="histList"></div></div>
</div>

<audio id="player" style="display:none"></audio>

<script>
let curQ='',curA='',curAudio=null,qCount=0,fCount=0,hist=[],recog=null,listening=false;

fetch('/api/status').then(r=>r.json()).then(d=>{
  document.getElementById('sVectors').textContent=d.vectors_indexed||'â';
  if(!d.pinecone_connected||!d.anthropic_configured){
    document.getElementById('dot').classList.add('err');
    document.getElementById('dot').title='Check API keys and Pinecone connection';
  }
});

function toggleMic(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){alert('Use Chrome or Edge for voice input.');return;}
  if(listening){recog&&recog.stop();return;}
  recog=new SR();recog.lang='en-US';recog.interimResults=true;
  recog.onstart=()=>{listening=true;setMic('listening')};
  recog.onresult=e=>{
    const t=Array.from(e.results).map(r=>r[0].transcript).join('');
    document.getElementById('qInput').value=t;
    if(e.results[0].isFinal){recog.stop();ask();}
  };
  recog.onerror=()=>setMic('idle');
  recog.onend=()=>{listening=false;setMic('idle');};
  recog.start();
}

function setMic(s){
  const ring=document.getElementById('ring'),btn=document.getElementById('micBtn'),st=document.getElementById('micStatus');
  ring.className='mic-ring'+(s!=='idle'?' '+s:'');
  btn.className='mic-btn'+(s!=='idle'?' '+s:'');
  if(s==='listening'){btn.textContent='â¹';st.textContent='Listening... tap to stop';}
  else if(s==='thinking'){btn.textContent='â³';st.textContent='Searching guidelines...';}
  else{btn.textContent='ð¤';st.textContent='Tap to speak your question';}
}

async function ask(){
  const q=document.getElementById('qInput').value.trim();
  if(!q)return;
  curQ=q;curAudio=null;
  setMic('thinking');
  document.getElementById('askBtn').disabled=true;
  document.getElementById('loader').classList.add('on');
  document.getElementById('answerCard').classList.remove('on');
  document.getElementById('fbForm').classList.remove('on');
  document.getElementById('wrongBtn').className='wrong-btn';
  document.getElementById('wrongBtn').textContent='â Wrong Answer';

  try{
    const r=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
    const d=await r.json();
    curA=d.answer;
    if(d.audio_base64)curAudio='data:audio/mpeg;base64,'+d.audio_base64;

    document.getElementById('qDisplay').textContent=q;
    document.getElementById('optDisplay').textContent=d.optimized_query?'Search query: '+d.optimized_query:'';
    document.getElementById('answerText').textContent=d.answer;

    const chips=document.getElementById('sourceChips');
    chips.innerHTML=(d.sources||[]).map(s=>`<div class="chip"><span>${s.agency||'FNMA'}</span> ${s.source_section} ${s.topic} Â· ${(s.score*100).toFixed(0)}%</div>`).join('');

    document.getElementById('playBtn').style.display=curAudio?'flex':'none';
    document.getElementById('answerCard').classList.add('on');
    if(curAudio)playAudio();

    qCount++;document.getElementById('sQuestions').textContent=qCount;
    addHist(q);document.getElementById('qInput').value='';
  }catch(e){
    document.getElementById('answerText').textContent='Server error. Check your connection.';
    document.getElementById('answerCard').classList.add('on');
  }
  document.getElementById('loader').classList.remove('on');
  document.getElementById('askBtn').disabled=false;
  setMic('idle');
}

function playAudio(){
  if(!curAudio)return;
  const p=document.getElementById('player');
  p.src=curAudio;p.play();
  document.getElementById('playBtn').textContent='â¶ Playing...';
  p.onended=()=>{document.getElementById('playBtn').innerHTML='â¶ Play Answer';};
}

function showFb(){
  document.getElementById('fbForm').classList.toggle('on');
  document.getElementById('wrongBtn').classList.add('flagged');
  document.getElementById('wrongBtn').textContent='â Flagged';
}

async function submitFb(){
  const ca=document.getElementById('fbInput').value.trim();
  if(!ca)return;
  await fetch('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:curQ,wrong_answer:curA,correct_answer:ca})});
  fCount++;document.getElementById('sFlags').textContent=fCount;
  document.getElementById('fbInput').value='';
  document.getElementById('fbForm').classList.remove('on');
  document.getElementById('wrongBtn').textContent='â Logged';
}

async function exportLog(){
  const r=await fetch('/api/feedback/export');
  const d=await r.json();
  const b=new Blob([JSON.stringify(d,null,2)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(b);
  a.download='feedback_'+new Date().toISOString().slice(0,10)+'.json';
  a.click();
}

function addHist(q){
  hist.unshift({q,t:new Date().toLocaleTimeString()});
  if(hist.length>8)hist.pop();
  const s=document.getElementById('hist'),l=document.getElementById('histList');
  s.style.display='block';
  l.innerHTML=hist.map(h=>`<div class="hist-item" onclick="document.getElementById('qInput').value='${h.q.replace(/'/g,"\\'")}';ask()"><div class="hist-q">${h.q}</div><div class="hist-t">${h.t}</div></div>`).join('');
}
</script>
</body>
</html>"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
