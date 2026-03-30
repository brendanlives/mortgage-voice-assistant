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

import os, sys, json, io, base64, datetime, hashlib, threading
import anthropic
import requests
from openai import OpenAI
from pinecone import Pinecone
from flask import Flask, request, Response, jsonify, render_template_string, send_file
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client as TwilioClient

# ── HYBRID RULE ENGINE ─────────────────────────────────────────────────────────
# Import the deterministic rule engine for instant, citation-backed answers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mortgage_engine'))
from mortgage_engine.router import classify_query, route_and_answer, extract_parameters
from mortgage_engine.hybrid_integration import (
    hybrid_pipeline, hybrid_stream_preprocess,
    inject_rule_context_into_rag, build_rule_engine_context_block,
    format_rule_answer_for_voice, format_rule_answer_for_web,
    get_hybrid_system_prompt_addition,
)
from mortgage_engine.rule_engine import (
    LoanScenario, evaluate_scenario, compare_agencies,
    lookup_ltv, lookup_dti, lookup_credit_score,
)

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
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")
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


# ── AI INSTRUCTIONS — POLICY OVERRIDES & SCENARIO GUIDANCE ───────────────────
# Load AI_INSTRUCTIONS.md at startup and extract the critical policy sections
# that help Claude synthesize multi-topic answers correctly. These override
# stale RAG data and provide guidance for common complex scenarios.
# ─────────────────────────────────────────────────────────────────────────────
def _load_ai_instructions() -> str:
    """Load AI_INSTRUCTIONS.md and extract sections 8-9 as a policy override block."""
    instructions_path = os.path.join(os.path.dirname(__file__), "AI_INSTRUCTIONS.md")
    try:
        with open(instructions_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("WARNING: AI_INSTRUCTIONS.md not found — policy overrides will not be injected")
        return ""

    # Extract sections 8 (Critical Policy Updates) through 9 (Common Scenarios)
    # These are the sections that override stale RAG data and guide multi-topic synthesis
    import re
    sections = []

    # Section 8: Critical Policy Updates
    m8 = re.search(r"(## 8\. CRITICAL POLICY UPDATES.*?)(?=\n## \d+\.|\Z)", content, re.DOTALL)
    if m8:
        sections.append(m8.group(1).strip())

    # Section 9: Common Scenarios (first instance — the scenario guidance, not parameter extraction)
    m9 = re.search(r"(## 9\. COMMON SCENARIOS AND HOW TO HANDLE THEM.*?)(?=\n## 9\. PARAMETER|\n## \d+\.|\Z)", content, re.DOTALL)
    if m9:
        sections.append(m9.group(1).strip())

    if sections:
        block = "\n\n".join(sections)
        print(f"Loaded AI_INSTRUCTIONS.md policy overrides ({len(block)} chars, {len(sections)} sections)")
        return block
    else:
        print("WARNING: Could not extract policy sections from AI_INSTRUCTIONS.md")
        return ""


AI_POLICY_OVERRIDES = _load_ai_instructions()

# Initialize on startup
get_pinecone_index()

# In-memory stores
AUDIO_CACHE    = {}   # hash â mp3 bytes
CALL_SESSIONS  = {}   # call_sid â {conversation history}
PENDING_ANSWERS = {}  # call_sid -> {"status": "processing"|"ready", "answer": str, "audio_key": str|None}
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
        # Handle multiple content field formats across agencies:
        # - Fannie/Freddie chunks use "content_text"
        # - FHA/TOTAL chunks use "content"
        # - Legacy format uses "content_json" (JSON string)
        content = meta.get("content_text") or meta.get("content") or ""
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


def search_pinecone_debug(query_text: str, top_k: int = 3) -> list:
    """Debug version: returns raw metadata keys and content field info."""
    index = get_pinecone_index()
    if not index:
        return []
    embedding = embed_query(query_text)
    if not embedding:
        return []
    results = index.query(vector=embedding, top_k=top_k, include_metadata=True)
    debug = []
    for match in results.matches:
        meta = match.metadata
        entry = {
            "chunk_id": meta.get("chunk_id", "?"),
            "score": match.score,
            "metadata_keys": sorted(list(meta.keys())),
        }
        # Show which content fields exist and their lengths
        for key in meta.keys():
            val = meta[key]
            if isinstance(val, str) and len(val) > 50:
                entry[f"field_{key}_len"] = len(val)
                entry[f"field_{key}_preview"] = val[:100]
            elif isinstance(val, str):
                entry[f"field_{key}"] = val
        debug.append(entry)
    return debug


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
the correct mortgage guideline from Fannie Mae, Freddie Mac, FHA (HUD Handbook 4000.1),
and/or VA (VA Pamphlet 26-7).
Focus on: loan type, borrower characteristics, property type, occupancy, LTV, DTI, credit score,
income type, asset type, agency-specific requirements — whatever is most relevant to the question.

If the loan officer asks about a specific agency, include the agency name in your query.
If they ask about differences between agencies, include all relevant names.

Return ONLY the optimized search query. Nothing else. No explanation."""
        }]
    )
    return response.content[0].text.strip()


def decompose_into_subtopics(question: str) -> list:
    """
    For complex multi-topic questions, break them into distinct sub-queries
    so each topic gets its own targeted Pinecone search.

    Returns a list of focused search queries, one per topic.
    For simple single-topic questions, returns an empty list (use standard flow).
    """
    if not anthropic_client:
        return []

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""You are a mortgage underwriting search specialist.

A loan officer asked this question:
{question}

Count the DISTINCT mortgage guideline topics in this question. Topics are separate
underwriting issues that would be found in DIFFERENT sections of the guideline handbooks.

Examples of distinct topics:
- Borrower eligibility (citizenship, visa, ITIN, foreign national)
- Non-occupant co-borrower / co-signer rules
- Departure residence / converting primary to rental
- Rental income from subject property
- Gift fund documentation and sourcing
- Foreign language document / asset verification requirements
- LTV/down payment for specific property types
- Credit score requirements / non-traditional credit
- DTI limits and calculation
- MI/MIP/funding fee costs
- Reserve requirements
- Waiting periods (bankruptcy, foreclosure, short sale)
- Income types (retirement, pension, Social Security, self-employment, commission)
- Reverse mortgage / HECM
- Investment property / multiple financed properties
- High-balance / jumbo / non-conforming

If the question has 3 or more distinct topics, output a JSON array of focused search
queries, one per topic. Each query should:
1. Be specific enough to find the RIGHT guideline section for that ONE topic
2. Include ALL relevant agency names (Fannie Mae, Freddie Mac, FHA, VA) when the
   question asks to compare agencies or says "all agencies"
3. Use mortgage industry terminology

If the question has 1-2 topics, output: []

Output ONLY the JSON array, no explanation. Example:
["Fannie Mae Freddie Mac FHA VA non-citizen H1B visa borrower eligibility requirements",
 "non-occupant co-borrower co-signer 2-unit primary residence FHA conventional VA",
 "departure residence converting primary to rental income documentation requirements",
 "rental income from subject 2-unit primary residence qualifying FHA conventional"]"""
            }]
        )

        text = response.content[0].text.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0].strip()
        subtopics = json.loads(text)
        if isinstance(subtopics, list) and len(subtopics) >= 2:
            return subtopics
    except Exception as e:
        print(f"[decompose_into_subtopics] Error: {e}")
    return []


def multi_topic_search(question: str, conversation_history: list = None) -> tuple:
    """
    Smart search that handles both simple and complex multi-topic questions.

    For simple questions: single optimized search (fast, 1 embedding call)
    For complex questions: decompose into sub-topics, search each, merge results

    Returns: (chunks, optimized_query_or_summary)
    """
    # Step 1: Try to decompose into sub-topics
    subtopics = decompose_into_subtopics(question)

    if not subtopics:
        # Simple question — standard single search with agency-aware filtering
        optimized = optimize_query(question, conversation_history)
        chunks = search_pinecone(optimized, top_k=15)

        # Agency-aware filtering: if the question mentions a specific agency,
        # ensure that agency's chunks are well-represented in results
        q_lower = question.lower()
        target_agency = None
        if "fha" in q_lower or "hud" in q_lower:
            target_agency = "FHA"
        elif "fannie" in q_lower or "fnma" in q_lower:
            target_agency = "Fannie Mae"
        elif "freddie" in q_lower or "fhlmc" in q_lower:
            target_agency = "Freddie Mac"
        elif "va " in q_lower or q_lower.startswith("va ") or "va loan" in q_lower:
            target_agency = "VA"

        if target_agency and chunks:
            target_chunks = [c for c in chunks if c.get("agency") == target_agency]
            other_chunks = [c for c in chunks if c.get("agency") != target_agency]
            # If the target agency has fewer than 5 chunks in results, boost them
            if len(target_chunks) < 5:
                # Keep all target agency chunks first, then fill with others, max 12
                balanced = target_chunks + other_chunks
                chunks = balanced[:12]
            else:
                chunks = chunks[:12]
        else:
            chunks = chunks[:12]

        return chunks, optimized

    # Step 2: Complex question — search each sub-topic separately
    all_chunks = {}  # chunk_id -> chunk (dedup)
    for subtopic_query in subtopics:
        sub_chunks = search_pinecone(subtopic_query, top_k=5)
        for c in sub_chunks:
            cid = c.get("chunk_id", "")
            if cid not in all_chunks or c.get("score", 0) > all_chunks[cid].get("score", 0):
                all_chunks[cid] = c

    # Step 3: Sort by score, take top chunks with agency balancing
    merged = sorted(all_chunks.values(), key=lambda c: c.get("score", 0), reverse=True)

    # Agency-balance the merged results
    fannie = [c for c in merged if c.get("agency", "") == "Fannie Mae"]
    freddie = [c for c in merged if c.get("agency", "") == "Freddie Mac"]
    fha = [c for c in merged if c.get("agency", "") == "FHA"]
    va = [c for c in merged if c.get("agency", "") == "VA"]

    balanced = []
    selected_ids = set()
    # Ensure at least 3 chunks per agency that has results
    for agency_list in [fannie, freddie, fha, va]:
        for c in agency_list[:3]:
            cid = c.get("chunk_id", "")
            if cid not in selected_ids:
                balanced.append(c)
                selected_ids.add(cid)

    # Fill remaining slots with highest-scoring unselected chunks
    remaining = [c for c in merged if c.get("chunk_id", "") not in selected_ids]
    max_chunks = min(20, 5 * len(subtopics))  # Scale with complexity
    balanced = balanced + remaining[:max(0, max_chunks - len(balanced))]
    balanced.sort(key=lambda c: c.get("score", 0), reverse=True)

    summary = f"Multi-topic search: {len(subtopics)} sub-queries, {len(balanced)} chunks retrieved"
    return balanced, summary

def generate_answer(question: str, chunks: list, for_voice: bool = False, conversation_history: list = None) -> str:
    """
    Claude generates a precise, cited answer from the retrieved chunks.
    """
    if not anthropic_client:
        return "Claude API not configured."

    if not chunks:
        msg = "I don't have a guideline that covers that specific scenario. Please verify directly with the Fannie Mae Selling Guide, Freddie Mac Seller/Servicer Guide, or FHA Handbook 4000.1, or check with your underwriter."
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

    # Inject rule engine context if available
    rule_context = build_rule_engine_context_block(question)
    if rule_context:
        context = f"{rule_context}\n\n{'═' * 70}\nRETRIEVED GUIDELINE PASSAGES:\n{'═' * 70}\n\n{context}"

    hybrid_addition = get_hybrid_system_prompt_addition() if rule_context else ""

    # Build policy overrides block from AI_INSTRUCTIONS.md
    policy_block = ""
    if AI_POLICY_OVERRIDES:
        policy_block = f"""
═══════════════════════════════════════════════════════════════════════
POLICY OVERRIDES & SCENARIO GUIDANCE (from AI_INSTRUCTIONS.md)
═══════════════════════════════════════════════════════════════════════
The following policy updates and scenario guidance OVERRIDE any conflicting
information in the retrieved guideline passages. These reflect the most
recent agency changes and common LO scenarios.

{AI_POLICY_OVERRIDES}
"""

    system_prompt = f"""You are Sarah, a senior mortgage underwriting assistant. You answer ONLY from
the retrieved guideline passages below. You are a professional guideline interpreter, not a
mortgage encyclopedia.

QUESTION: {question}

RETRIEVED MORTGAGE GUIDELINES:
{context}

═══════════════════════════════════════════════════════════════════════
CRITICAL ACCURACY RULES — YOUR #1 PRIORITY IS BEING CORRECT
═══════════════════════════════════════════════════════════════════════

SOURCE OF TRUTH HIERARCHY:
1. The RETRIEVED GUIDELINE PASSAGES above are your ONLY authoritative source
2. You may use general mortgage knowledge to STRUCTURE and EXPLAIN the
   retrieved content (e.g., organizing by topic, explaining what terms mean)
3. You must NEVER invent, fabricate, or fill in specific guideline details
   (eligibility rules, percentages, documentation requirements, LTV limits,
   waiting periods, etc.) that are not stated in the retrieved passages
4. If the retrieved passages do not cover a topic the LO asked about, you
   MUST say: "The guidelines I have access to don't specifically address
   [topic]. I'd recommend verifying [specific handbook/section] or checking
   with your underwriter." DO NOT GUESS.

WHAT YOU CAN DO:
- Synthesize and organize information FROM the retrieved passages
- Explain what guideline language means in practical terms
- Compare retrieved guidelines across agencies/programs
- Flag potential issues or risks based on what the guidelines say
- Cite specific section numbers from the retrieved text
- Structure complex answers by topic for readability

WHAT YOU MUST NEVER DO:
- State a specific eligibility rule, percentage, or requirement that isn't
  in the retrieved passages (even if you "know" it from training data)
- Present your training knowledge as if it were from a specific guideline
- Blend one agency's rules with another's — keep them clearly separated
- Assume facts about the borrower that aren't stated in the question
  (e.g., don't assume someone is a veteran unless they say so)

CITATION RULES:
- Cite the agency AND source section: "Per Fannie Mae B3-3.1-09..."
- If a passage doesn't have a clear section number, cite the chunk topic
- When you CAN'T cite a specific source for a claim, that's a red flag
  that you're inventing it — stop and flag it as "verify with underwriter"

WHEN MULTIPLE AGENCIES APPLY:
- Address each agency separately with its own section
- Only state rules for an agency if you have retrieved passages from that agency
- If no passages were retrieved for an agency, say so: "No [agency] guidelines
  were retrieved for this topic" rather than inventing the agency's position

FORMAT:
- Lead with the most critical finding / answer
- Organize complex answers by issue/topic
- Be concise — loan officers need actionable answers, not essays
- Flag genuine red flags and areas requiring underwriter verification
- When the question involves a complex scenario, provide a clear recommendation
  at the end with the best path forward
{policy_block}
{hybrid_addition}
{voice_format}"""

    # Build messages array
    messages = []
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": f"QUESTION: {question}"})

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text.strip()


def full_rag_pipeline(question: str, for_voice: bool = False, conversation_history: list = None) -> tuple:
    """
    Complete pipeline: question â optimized query â vector search â answer.
    Returns (answer_text, chunks_used, optimized_query)
    """
    # Smart search: auto-detects complex multi-topic questions
    chunks, optimized = multi_topic_search(question, conversation_history)

    answer = generate_answer(question, chunks, for_voice=for_voice, conversation_history=conversation_history)
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


def _process_answer_async(call_sid, full_question):
    """Background thread: run RAG pipeline, cache audio, mark answer ready."""
    try:
        answer, chunks, optimized = full_rag_pipeline(full_question, for_voice=True)
        audio_key = cache_audio(answer) if ELEVENLABS_API_KEY else None
        PENDING_ANSWERS[call_sid] = {
            "status": "ready",
            "answer": answer,
            "audio_key": audio_key,
        }
    except Exception as e:
        PENDING_ANSWERS[call_sid] = {
            "status": "ready",
            "answer": f"I'm sorry, I ran into an issue processing that question. Could you try rephrasing it?",
            "audio_key": None,
        }
        print(f"[voice] Error processing answer for {call_sid}: {e}")


@app.route("/voice/answer", methods=["POST"])
def voice_answer():
    """Got the full scenario -- kick off RAG pipeline in background, return hold music."""
    resp     = VoiceResponse()
    call_sid = request.form.get("CallSid", "unknown")
    question = request.form.get("SpeechResult", "").strip()

    session  = CALL_SESSIONS.get(call_sid, {"scenario": []})
    scenario = " | ".join(session.get("scenario", []))

    # Build full context question
    full_question = f"{scenario} | Question: {question}"
    session["question"] = full_question
    CALL_SESSIONS[call_sid] = session

    # Start background processing
    PENDING_ANSWERS[call_sid] = {"status": "processing"}
    thread = threading.Thread(
        target=_process_answer_async,
        args=(call_sid, full_question),
        daemon=True
    )
    thread.start()

    # Return immediate response: brief hold message + redirect to polling endpoint
    resp.say("Great question. Let me look that up for you.", voice="alice")
    resp.pause(length=2)
    resp.redirect(f"/voice/poll_answer?sid={call_sid}&attempt=1", method="POST")

    return Response(str(resp), mimetype="text/xml")


@app.route("/voice/poll_answer", methods=["POST"])
def voice_poll_answer():
    """Poll for the background answer. If ready, play it. If not, wait and retry."""
    resp     = VoiceResponse()
    call_sid = request.args.get("sid", request.form.get("CallSid", "unknown"))
    attempt  = int(request.args.get("attempt", "1"))

    pending = PENDING_ANSWERS.get(call_sid, {})

    if pending.get("status") == "ready":
        # Answer is ready -- play it
        answer    = pending.get("answer", "I couldn't find an answer to that question.")
        audio_key = pending.get("audio_key")

        # Clean up
        PENDING_ANSWERS.pop(call_sid, None)

        # Play answer and listen for feedback
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
    elif attempt >= 15:
        # Timeout after ~30 seconds of polling -- give up gracefully
        PENDING_ANSWERS.pop(call_sid, None)
        resp.say(
            "I'm sorry, it's taking longer than expected to look that up. "
            "Please try calling back and I'll be ready for you.",
            voice="alice"
        )
        resp.hangup()
    else:
        # Still processing -- wait 2 seconds and poll again
        resp.pause(length=2)
        resp.redirect(
            f"/voice/poll_answer?sid={call_sid}&attempt={attempt + 1}",
            method="POST"
        )

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



# -- SMS ENDPOINT (for ElevenLabs voice agent to text breakdowns) -------------
@app.route("/api/send-sms", methods=["POST"])
def send_sms():
    """Send an SMS via Twilio. Used by ElevenLabs voice agent to text full breakdowns."""
    data = request.get_json(force=True)
    to_number = data.get("to", "").strip()
    message_body = data.get("message", "").strip()

    if not to_number or not message_body:
        return jsonify({"error": "Both 'to' and 'message' fields are required"}), 400

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        return jsonify({"error": "Twilio is not configured on the server"}), 500

    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        return jsonify({"success": True, "sid": msg.sid, "status": msg.status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ââ WEB ROUTES âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@app.route("/", methods=["GET"])
def index():
    return render_template_string(WEB_UI)


@app.route("/api/debug-chunks", methods=["POST"])
def api_debug_chunks():
    """Debug endpoint: show raw Pinecone metadata for a query."""
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400
    optimized = optimize_query(question)
    debug_results = search_pinecone_debug(optimized, top_k=5)
    return jsonify({"question": question, "optimized_query": optimized, "raw_chunks": debug_results})


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """Web interface posts questions here. Uses hybrid rule engine + RAG."""
    data     = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Get conversation history from request (optional)
    conversation_history = data.get("conversation_history", [])

    # Step 1: Classify the query via the smart router
    classification = classify_query(question)
    route = classification["route"]

    # Step 2: Use hybrid pipeline
    answer, chunks, optimized, metadata = hybrid_pipeline(
        question,
        rag_pipeline_fn=lambda q, fv=False, h=None: full_rag_pipeline(
            q, for_voice=False, conversation_history=conversation_history
        ),
        for_voice=False,
        conversation_history=conversation_history,
    )

    # Step 3: Generate audio
    audio_b64 = None
    if ELEVENLABS_API_KEY:
        # For rule engine answers, use a clean text version for TTS
        tts_text = answer[:2000]  # Limit TTS length
        audio_bytes = text_to_speech(tts_text)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode()

    # Step 4: Extract citations from rule engine results
    rule_citations = []
    if metadata.get("rule_engine_data"):
        rule_citations = metadata["rule_engine_data"].get("citations", [])
        rule_citations = [c for c in rule_citations if c]  # Filter empties

    return jsonify({
        "question":        question,
        "optimized_query": optimized,
        "answer":          answer,
        "audio_base64":    audio_b64,
        "route":           route,
        "confidence":      classification.get("confidence", 0),
        "rule_type":       classification.get("rule_type"),
        "parameters":      classification.get("parameters", {}),
        "rule_citations":  rule_citations,
        "timing_ms":       metadata.get("timing_ms", 0),
        "sources": [{
            "chunk_id":       c.get("chunk_id"),
            "agency":         c.get("agency", ""),
            "topic":          c.get("topic"),
            "source_section": c.get("source_section"),
            "score":          round(c.get("score", 0), 3),
            "content":        str(c.get("content", ""))[:200]  # First 200 chars for debugging
        } for c in chunks]
    })


@app.route("/api/ask-stream", methods=["POST"])
def api_ask_stream():
    """Streaming version of /api/ask — returns Server-Sent Events.
    Now with hybrid rule engine: sends deterministic answer instantly,
    then streams RAG explanation if needed."""
    data     = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400

    conversation_history = data.get("conversation_history", [])

    def generate():
        try:
            # Step 0: Run rule engine classification (instant, <5ms)
            preprocess = hybrid_stream_preprocess(question)
            classification = preprocess["classification"]
            route = classification["route"]
            rule_answer = preprocess.get("rule_engine_answer")
            use_rag = preprocess["use_rag"]

            # Send rule engine results immediately as first event
            rule_citations = preprocess.get("rule_citations", [])
            if rule_answer:
                yield f"event: rule_engine\ndata: {json.dumps({'route': route, 'rule_type': classification.get('rule_type'), 'confidence': classification.get('confidence', 0), 'parameters': classification.get('parameters', {}), 'answer': rule_answer, 'citations': rule_citations})}\n\n"

            # If pure rule engine, we're done — no RAG needed
            if not use_rag and rule_answer:
                yield f"event: done\ndata: {json.dumps({'route': route})}\n\n"
                return

            # Step 1+2: Smart search — auto-detects complex multi-topic questions
            # and runs multiple targeted searches to ensure full topic coverage
            chunks, optimized = multi_topic_search(question, conversation_history)

            # Send metadata (sources)
            sources = [{
                "chunk_id":       c.get("chunk_id"),
                "agency":         c.get("agency", ""),
                "topic":          c.get("topic"),
                "source_section": c.get("source_section"),
                "score":          round(c.get("score", 0), 3)
            } for c in chunks]
            yield f"event: metadata\ndata: {json.dumps({'optimized_query': optimized, 'sources': sources, 'route': route})}\n\n"

            # Step 3: Build prompt with rule engine context injection
            context = build_context(chunks)

            # Inject rule engine results into context
            rule_context_block = preprocess.get("rule_context_block")
            if rule_context_block:
                context = f"{rule_context_block}\n\n{'═' * 70}\nRETRIEVED GUIDELINE PASSAGES:\n{'═' * 70}\n\n{context}"

            hybrid_addition = get_hybrid_system_prompt_addition() if rule_context_block else ""

            # Build policy overrides block from AI_INSTRUCTIONS.md
            policy_block = ""
            if AI_POLICY_OVERRIDES:
                policy_block = f"""
═══════════════════════════════════════════════════════════════════════
POLICY OVERRIDES & SCENARIO GUIDANCE (from AI_INSTRUCTIONS.md)
═══════════════════════════════════════════════════════════════════════
The following policy updates and scenario guidance OVERRIDE any conflicting
information in the retrieved guideline passages. These reflect the most
recent agency changes and common LO scenarios.

{AI_POLICY_OVERRIDES}
"""

            voice_format = """
Format your response clearly:
- Lead with the key rule and any critical thresholds
- Cite the source section (e.g. "Per B3-6-02...")
- List important exceptions or conditions
- Use plain English
"""
            system_prompt = f"""You are Sarah, a senior mortgage underwriting assistant. You answer ONLY from
the retrieved guideline passages below. You are a professional guideline interpreter, not a
mortgage encyclopedia.

QUESTION: {question}

RETRIEVED MORTGAGE GUIDELINES:
{context}

═══════════════════════════════════════════════════════════════════════
CRITICAL ACCURACY RULES — YOUR #1 PRIORITY IS BEING CORRECT
═══════════════════════════════════════════════════════════════════════

SOURCE OF TRUTH HIERARCHY:
1. The RETRIEVED GUIDELINE PASSAGES above are your ONLY authoritative source
2. You may use general mortgage knowledge to STRUCTURE and EXPLAIN the
   retrieved content (e.g., organizing by topic, explaining what terms mean)
3. You must NEVER invent, fabricate, or fill in specific guideline details
   (eligibility rules, percentages, documentation requirements, LTV limits,
   waiting periods, etc.) that are not stated in the retrieved passages
4. If the retrieved passages do not cover a topic the LO asked about, you
   MUST say: "The guidelines I have access to don't specifically address
   [topic]. I'd recommend verifying [specific handbook/section] or checking
   with your underwriter." DO NOT GUESS.

WHAT YOU CAN DO:
- Synthesize and organize information FROM the retrieved passages
- Explain what guideline language means in practical terms
- Compare retrieved guidelines across agencies/programs
- Flag potential issues or risks based on what the guidelines say
- Cite specific section numbers from the retrieved text

WHAT YOU MUST NEVER DO:
- State a specific eligibility rule, percentage, or requirement that isn't
  in the retrieved passages
- Present your training knowledge as if it were from a specific guideline
- Blend one agency's rules with another's
- Assume facts about the borrower not stated in the question

CITATION RULES:
- Cite the agency AND source section from the retrieved text
- If you CAN'T cite a specific source for a claim, flag it as needing
  verification rather than stating it as fact

WHEN MULTIPLE AGENCIES APPLY:
- Address each agency separately
- Only state rules for an agency if you have retrieved passages from that agency
- If no passages were retrieved for an agency, say so

FORMAT:
- Lead with the most critical finding
- Organize complex answers by issue/topic
- Be concise and actionable
- Flag red flags and areas requiring underwriter verification
- Provide a clear recommendation at the end for complex scenarios

TLDR REQUIREMENT:
- At the very end of EVERY response, add a "## TLDR" section
- This should be 2-4 sentences MAX — a plain English bottom line
- Written for a busy loan officer who needs the quick answer
- Include: can they qualify? what's the biggest issue? what's the key next step?
- Example: "TLDR: This borrower can likely qualify with Fannie Mae if they increase
  the down payment to 15%. The main issue is the 2-year employment gap — you'll need
  a solid LOE. Get the VOR from the previous landlord before submitting."
{policy_block}
{hybrid_addition}
{voice_format}"""

            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": f"QUESTION: {question}"})

            # Step 4: Stream Claude response
            with anthropic_client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield f"event: token\ndata: {json.dumps({'text': text})}\n\n"

            yield f"event: done\ndata: {json.dumps({'route': route})}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive'
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




# ── ADMIN: PINECONE KNOWLEDGE BASE CLEANUP ─────────────────────────────────────
# One-time endpoint to find and replace stale/outdated chunks in Pinecone.
# Call POST /api/admin/cleanup-stale-chunks to execute.

STALE_TOPICS = [
    {
        "search_query": "FHA non-permanent resident alien eligible H1B visa EAD employment authorization",
        "stale_keywords": ["non-permanent resident", "employment authorization document", "ead", "eligible alien"],
        "reason": "ML 2025-09 removed non-permanent resident alien eligibility effective May 25, 2025",
        "replacement_text": "FHA BORROWER ELIGIBILITY UPDATE (Mortgagee Letter 2025-09, effective May 25, 2025): Non-permanent resident aliens (including H1B, L1, F1, OPT, DACA holders) are NO LONGER ELIGIBLE for FHA-insured loans. Only U.S. citizens, lawful permanent residents (green card holders), and citizens of Federated States of Micronesia, Republic of Marshall Islands, and Republic of Palau are eligible. Social Security cards alone are insufficient to prove immigration status; USCIS documentation is required. This supersedes all prior FHA guidance on non-permanent resident alien eligibility.",
        "replacement_source": "ML 2025-09; HUD 4000.1 (revised May 2025)",
        "replacement_agency": "FHA",
    },
    {
        "search_query": "FHA student loan deferred IBR income driven repayment 1% balance calculation",
        "stale_keywords": ["1% of", "one percent of", "1 percent"],
        "reason": "ML 2021-13 changed FHA student loan calc from 1% to 0.5%",
        "replacement_text": "FHA STUDENT LOAN DTI CALCULATION (Updated per ML 2021-13, effective August 16, 2021): For student loans in deferment, forbearance, or income-based repayment (IBR/IDR/PAYE): use 0.5% of the outstanding balance OR the actual documented monthly payment, whichever is greater. If the IBR/IDR payment is $0, use 0.5% of the outstanding balance (cannot use $0). For student loans in standard repayment, use the actual monthly payment from the credit report. This supersedes the prior 1% calculation rule.",
        "replacement_source": "ML 2021-13; HUD 4000.1, II.A.4.c.ii(E) (revised)",
        "replacement_agency": "FHA",
    },
    {
        "search_query": "Fannie Mae 2-unit 3-unit 4-unit multi-unit primary purchase LTV maximum 85% 75%",
        "stale_keywords": ["85%", "75%"],
        "reason": "Fannie Mae increased 2-4 unit primary LTV to 95% in Nov 2023",
        "replacement_text": "FANNIE MAE MULTI-UNIT PRIMARY RESIDENCE LTV LIMITS (Updated November 18, 2023): For purchase and rate/term refinance transactions on owner-occupied 2-4 unit properties with DU approval: Maximum LTV/CLTV is 95% for all unit counts (2-unit, 3-unit, and 4-unit). This is an increase from the prior limits of 85% (2-unit) and 75% (3-4 unit). Manual underwriting retains the prior lower limits. High-balance loans are excluded from this increase. Investment property limits unchanged (85% 1-unit, 75% 2-4 unit).",
        "replacement_source": "B2-1.1-01, Eligibility Matrix (updated Nov 2023)",
        "replacement_agency": "Fannie Mae",
    },
    {
        "search_query": "Freddie Mac 2-unit 3-unit 4-unit multi-unit primary purchase LTV maximum 85% 80% 75%",
        "stale_keywords": ["80%", "75%"],
        "reason": "Freddie Mac increased 2-4 unit primary LTV to 95% in Sep 2025",
        "replacement_text": "FREDDIE MAC MULTI-UNIT PRIMARY RESIDENCE LTV LIMITS (Updated September 29, 2025): For purchase and rate/term refinance transactions on owner-occupied 2-4 unit properties with LPA approval: Maximum LTV/CLTV is 95% for all unit counts (2-unit, 3-unit, and 4-unit). This is an increase from prior limits of 85%/95% (2-unit) and 80%/75% (3-4 unit). Investment property limits unchanged (85% 1-unit, 75% 2-4 unit).",
        "replacement_source": "Section 4201.4 (updated Sep 2025)",
        "replacement_agency": "Freddie Mac",
    },
    {
        "search_query": "Fannie Mae minimum credit score 620 required DU Desktop Underwriter",
        "stale_keywords": ["620", "minimum credit score"],
        "reason": "SEL-2025-09 removed the 620 credit score floor for DU loans",
        "replacement_text": "FANNIE MAE CREDIT SCORE REQUIREMENTS (Updated per SEL-2025-09, effective November 16, 2025): Fannie Mae NO LONGER requires a minimum 620 credit score for DU-approved loans. Desktop Underwriter now performs a comprehensive risk analysis without a hard credit score floor. Manual underwriting still requires a minimum 620 representative credit score. Individual lenders may continue to impose their own overlay minimums (commonly 620-640). This change allows DU to approve borrowers with lower scores when other risk factors are strong.",
        "replacement_source": "SEL-2025-09; B3-5.1-01 (revised Nov 2025)",
        "replacement_agency": "Fannie Mae",
    },
    {
        "search_query": "FHA 203k limited repair rehabilitation maximum cost $35,000 35000",
        "stale_keywords": ["35,000", "35000", "$35,000"],
        "reason": "ML 2024-13 increased Limited 203k max from $35k to $75k",
        "replacement_text": "FHA 203(K) REHABILITATION PROGRAM UPDATES (Per ML 2024-13, effective November 4, 2024): LIMITED 203(k): Maximum rehabilitation cost increased to $75,000 (from $35,000). Rehabilitation period extended to 9 months (from 6 months). Consultant fees may now be financed. STANDARD 203(k): Minimum repair cost remains $5,000. Maximum is the FHA loan limit for the area. Rehabilitation period extended to 12 months. HUD 203(k) consultant is required for Standard but optional for Limited.",
        "replacement_source": "ML 2024-13; HUD 4000.1, II.A.8.h (revised Nov 2024)",
        "replacement_agency": "FHA",
    },
    {
        "search_query": "conforming loan limit 2024 2025 766550 806500 Fannie Freddie conventional",
        "stale_keywords": ["766,550", "766550", "806,500", "806500", "$766,550", "$806,500"],
        "reason": "2026 conforming loan limits are now in effect",
        "replacement_text": "2026 CONFORMING LOAN LIMITS (Effective January 1, 2026, per FHFA): Fannie Mae/Freddie Mac baseline conforming limit: 1-unit $832,750, 2-unit $1,066,250, 3-unit $1,288,800, 4-unit $1,601,750. High-cost area ceiling: $1,249,125 (150% of baseline). FHA floor: $541,287 (65% of $832,750). FHA ceiling: $1,249,125. VA: $832,750 baseline (partial entitlement); no limit for full entitlement veterans. Limits vary by county/MSA for FHA.",
        "replacement_source": "FHFA 2026 Conforming Loan Limit Announcement; ML 2025-23; Circular 26-25-10",
        "replacement_agency": "All Agencies",
    },
    # --- ROUND 2: Additional corrections identified from LO review ---
    {
        "search_query": "departure residence departing primary vacating rental income lease security deposit Fannie Mae conventional",
        "stale_keywords": ["security deposit"],
        "reason": "Fannie Mae does NOT require security deposit for departure residence rental income. Requires lease + rent comp OR lease + 2 months bank statements.",
        "replacement_text": "FANNIE MAE DEPARTURE RESIDENCE RENTAL INCOME: To count rental income from a departing primary residence, Fannie Mae requires EITHER: (1) executed lease agreement + comparable rent schedule (Form 1007), OR (2) executed lease agreement + 2 months most recent bank statements showing rent deposit history. Security deposit is NOT required. No equity requirement exists for departure residence rental income (unlike FHA which requires 25% equity). If no lease documentation, full PITIA counted as liability with zero rental offset. The 75% vacancy factor applies: 75% of gross rent minus PITIA = net rental income/loss.",
        "replacement_source": "B3-3.1-08; B3-6-06",
        "replacement_agency": "Fannie Mae",
    },
    {
        "search_query": "FHA departure residence departing primary vacating rental income 25% equity requirement",
        "stale_keywords": ["security deposit"],
        "reason": "FHA departure residence rules are distinct from conventional - requires 25% equity",
        "replacement_text": "FHA DEPARTURE RESIDENCE RENTAL INCOME (CRITICAL DIFFERENCE FROM CONVENTIONAL): FHA REQUIRES 25% documented equity in the departing primary residence before rental income can be used to offset the mortgage payment. If borrower has LESS than 25% equity, the full PITIA of the departure residence must be counted as a liability in DTI with ZERO rental income offset, EVEN IF the borrower has an executed lease. Exception: if borrower is relocating for employment (new job >100 miles from current residence), the 25% equity requirement may be waived. This is the single biggest difference between FHA and conventional on departure residences. Do NOT confuse this with the rules about having two FHA loans simultaneously (which is a separate issue).",
        "replacement_source": "HUD 4000.1, II.A.4.c.ii(H); II.A.1.b.ii(B)",
        "replacement_agency": "FHA",
    },
    {
        "search_query": "gift funds donor bank statement documentation required ability to give",
        "stale_keywords": ["donor bank statement showing withdrawal"],
        "reason": "Donor bank statement is NOT always required - only when transfer cannot be verified otherwise",
        "replacement_text": "GIFT FUND DOCUMENTATION (ALL AGENCIES): A gift letter signed by the donor is ALWAYS required (stating amount, donor name, relationship, property address, no repayment expected). HOWEVER, a donor bank statement is NOT universally required. Donor bank statements are only needed when the transfer of funds cannot be verified through other means (e.g., wire confirmation, cashier's check, or closing statement). DU/LPA do not universally require donor bank statements. The key requirement is evidence of transfer to the borrower or to escrow/closing. All gift funds must be in US dollars at closing. For foreign gifts, certified English translation of any foreign-language documents is required.",
        "replacement_source": "B3-4.3-04; Section 5501.2; HUD 4000.1 II.A.4.d.iii",
        "replacement_agency": "All Agencies",
    },
    {
        "search_query": "Fannie Mae non-occupant co-borrower 2-unit maximum LTV 85%",
        "stale_keywords": ["85%", "85"],
        "reason": "Fannie Mae non-occ co-borrower LTV on 2-unit updated to 95% (Nov 2023 eligibility matrix update)",
        "replacement_text": "FANNIE MAE NON-OCCUPANT CO-BORROWER LTV (Updated Nov 2023): Non-occupant co-borrowers are permitted on primary residence loans. Max LTV: 97% for 1-unit, 95% for 2-unit, 95% for 3-4 unit (with DU approval). No family relationship is required for non-occupant co-borrowers on conventional loans — any individual can co-sign. The co-borrower must sign the Note and be obligated on the mortgage. Their income can be used to qualify and their debts are included in combined DTI.",
        "replacement_source": "B2-2-04; B2-1.1-01 (updated Nov 2023)",
        "replacement_agency": "Fannie Mae",
    },
    {
        "search_query": "FHA non-occupant co-borrower family member required cousin relationship 75%",
        "stale_keywords": ["cousin"],
        "reason": "Clarify FHA non-occ rules - both family and non-family allowed but at different LTV",
        "replacement_text": "FHA NON-OCCUPANT CO-BORROWER RULES: FHA allows BOTH family AND non-family non-occupant co-borrowers. The critical difference is LTV: (1) Family member non-occ on 1-unit = standard 96.5% LTV. (2) Non-family non-occ on 1-unit = LTV capped at 75%. (3) ANY non-occ (family or not) on 2-4 unit = LTV capped at 75%. FHA family member definition: spouse, child, parent, grandparent, sibling (including step), aunt, uncle, niece, nephew, stepchild, stepparent, in-laws, domestic partner. IMPORTANT: Cousin is NOT explicitly listed in HUD's family member definition. If a cousin is used as non-occ co-borrower on FHA, the LTV may be limited to 75%.",
        "replacement_source": "HUD 4000.1, II.A.2.a",
        "replacement_agency": "FHA",
    },
]


@app.route("/api/admin/cleanup-stale-chunks", methods=["POST"])
def cleanup_stale_chunks():
    """Find and replace outdated Pinecone chunks with corrected versions."""
    index = get_pinecone_index()
    if not index:
        return jsonify({"error": "Pinecone not connected"}), 500

    results = {"deleted": [], "upserted": [], "errors": []}

    for topic in STALE_TOPICS:
        try:
            # Search for potentially stale chunks
            embedding = embed_query(topic["search_query"])
            if not embedding:
                results["errors"].append(f"Could not embed query for: {topic['reason']}")
                continue

            matches = index.query(
                vector=embedding,
                top_k=10,
                include_metadata=True
            )

            # Check each match for stale keywords
            stale_ids = []
            for match in matches.get("matches", []):
                content = match.get("metadata", {}).get("content", "").lower()
                text = match.get("metadata", {}).get("text", "").lower()
                full_text = content + " " + text
                # Check if any stale keyword appears
                if any(kw.lower() in full_text for kw in topic["stale_keywords"]):
                    stale_ids.append(match["id"])

            # Delete stale chunks
            if stale_ids:
                index.delete(ids=stale_ids)
                results["deleted"].extend([{
                    "id": sid,
                    "reason": topic["reason"]
                } for sid in stale_ids])

            # Upsert replacement chunk
            replacement_id = f"corrected_{topic['replacement_agency'].lower().replace(' ', '_')}_{hash(topic['replacement_text']) % 100000}"
            replacement_embedding = embed_query(topic["replacement_text"])
            if replacement_embedding:
                index.upsert(vectors=[{
                    "id": replacement_id,
                    "values": replacement_embedding,
                    "metadata": {
                        "text": topic["replacement_text"],
                        "content": topic["replacement_text"],
                        "source": topic["replacement_source"],
                        "agency": topic["replacement_agency"],
                        "type": "corrected_guideline",
                        "corrected_date": "2026-03-29",
                    }
                }])
                results["upserted"].append({
                    "id": replacement_id,
                    "agency": topic["replacement_agency"],
                    "reason": topic["reason"],
                })

        except Exception as e:
            results["errors"].append(f"Error processing '{topic['reason']}': {str(e)}")

    return jsonify({
        "status": "complete",
        "deleted_count": len(results["deleted"]),
        "upserted_count": len(results["upserted"]),
        "error_count": len(results["errors"]),
        "details": results,
    })


# ── ADMIN: BULK UPLOAD VERIFIED GUIDELINE CHUNKS ────────────────────────────────
# Chunks built from verified official update letters (MLs, SELs, Bulletins, Circulars).
# These are authoritative because they come from the actual letters, not handbook scrapes.

VERIFIED_CHUNKS = [
    # ──── FANNIE MAE (from SEL-2025-08, SEL-2025-09, SEL-2025-10, SEL-2026-01, SEL-2026-02) ────
    {
        "id": "verified_fnma_adu_rental_income",
        "text": "FANNIE MAE ADU RENTAL INCOME (SEL-2025-08, effective October 8, 2025): Fannie Mae now allows rental income from an Accessory Dwelling Unit (ADU) to be used as qualifying income. Requirements: (1) Property must be a 1-unit principal residence, (2) Transaction must be purchase or limited cash-out refinance, (3) Rental income may only be derived from ONE ADU even if multiple ADUs exist on the property, (4) ADU rental income is CAPPED at 30% of the borrower's total qualifying income, (5) A Single-Family Comparable Rent Schedule (Form 1007) is required — if comparable ADU rentals cannot be found, appraiser may use similar non-ADU rental properties with adjustments, (6) DU version 12.1 (Q1 2026) will include ADU rental income eligibility — until then, manual underwriting only.",
        "source": "SEL-2025-08; B3-3.8-01 (revised 10/08/2025)",
        "agency": "Fannie Mae",
    },
    {
        "id": "verified_fnma_limited_cashout_refi",
        "text": "FANNIE MAE LIMITED CASH-OUT REFINANCE CASH BACK UPDATE (SEL-2025-08, effective October 8, 2025): The maximum cash back a borrower may receive in a limited cash-out refinance was changed from 'the lesser of 2% of the new UPB or $2,000' to 'the GREATER of 1% of the new UPB or $2,000.' This is a significant improvement for borrowers with larger loan balances. Example: on a $400,000 loan, max cash back is now $4,000 (1% of UPB) vs the old $2,000 cap.",
        "source": "SEL-2025-08; B2-1.3-02 (revised 10/08/2025)",
        "agency": "Fannie Mae",
    },
    {
        "id": "verified_fnma_credit_score_floor_removed",
        "text": "FANNIE MAE CREDIT SCORE FLOOR REMOVED (SEL-2025-09, effective November 16, 2025): Fannie Mae NO LONGER requires a minimum 620 credit score for DU-approved loans. Desktop Underwriter now performs a comprehensive risk analysis without a hard credit score floor. This means DU can approve borrowers with scores below 620 if other risk factors (reserves, LTV, DTI, etc.) are strong enough. Manual underwriting STILL requires a minimum 620 representative credit score. Individual lenders may continue to impose their own overlay minimums (commonly 620-640). IMPORTANT: Freddie Mac STILL requires a minimum 620 credit score — only Fannie Mae removed the floor.",
        "source": "SEL-2025-09; B3-5.1-01 (revised Nov 2025)",
        "agency": "Fannie Mae",
    },
    {
        "id": "verified_fnma_homestyle_renovation",
        "text": "FANNIE MAE HOMESTYLE RENOVATION UPDATES (SEL-2025-10, effective November 25, 2025): Updated HomeStyle Renovation financing policies including: expanded eligible upfront disbursements, removed outdated cost caps for manufactured homes, and enhanced guidance on limited cash-out refinancing for HomeStyle Renovation loans. These changes provide more flexibility for renovation lending.",
        "source": "SEL-2025-10; B5-3.2 HomeStyle Renovation (revised Nov 2025)",
        "agency": "Fannie Mae",
    },
    {
        "id": "verified_fnma_income_docs_simplified",
        "text": "FANNIE MAE INCOME DOCUMENTATION SIMPLIFIED (SEL-2026-02, effective March 4, 2026 — must implement by June 1, 2026): Chapter B3-3 (Income Assessment) was restructured. KEY CHANGES: (1) Fixed base income now requires only the most recent W-2 and pay stub (previously required W-2s for past 2 years plus pay stub), (2) Variable base income also now requires only the most recent W-2 and pay stub (same reduction), (3) Automobile allowance history requirement reduced from 2 years to 1 year (aligned with housing allowance). The chapter was reorganized into modular format with standard tables for each income type consolidating documentation, history, continuity, and calculation requirements.",
        "source": "SEL-2026-02; B3-3 Income Assessment (revised 03/04/2026)",
        "agency": "Fannie Mae",
    },
    {
        "id": "verified_fnma_2026_loan_limits",
        "text": "FANNIE MAE 2026 CONFORMING LOAN LIMITS (effective January 1, 2026, per FHFA): Baseline conforming limits: 1-unit $832,750, 2-unit $1,066,250, 3-unit $1,288,800, 4-unit $1,601,750. High-cost area ceiling: 1-unit $1,249,125, 2-unit $1,599,375, 3-unit $1,933,200, 4-unit $2,402,625. Alaska, Hawaii, Guam, and US Virgin Islands: 50% higher than baseline. This represents a 3.26% increase over 2025 limits ($806,500 baseline).",
        "source": "FHFA 2026 Conforming Loan Limit Announcement; Fannie Mae LL-2025",
        "agency": "Fannie Mae",
    },
    {
        "id": "verified_fnma_multiunit_ltv_95",
        "text": "FANNIE MAE 2-4 UNIT PRIMARY RESIDENCE LTV INCREASE (effective November 18, 2023): For purchase and rate/term refinance transactions on owner-occupied 2-4 unit properties with DU approval, maximum LTV/CLTV is 95% for ALL unit counts (2-unit, 3-unit, and 4-unit). This was an increase from prior limits of 85% (2-unit) and 75% (3-4 unit). Manual underwriting retains the prior lower limits. High-balance loans are excluded. Investment property limits remain unchanged (85% 1-unit, 75% 2-4 unit). Minimum 5% down payment for 2-4 unit primary with DU.",
        "source": "B2-1.1-01, Eligibility Matrix (updated Nov 2023)",
        "agency": "Fannie Mae",
    },
    {
        "id": "verified_fnma_h1b_eligible",
        "text": "FANNIE MAE H1B/NON-PERMANENT RESIDENT ELIGIBILITY: H1B visa holders ARE eligible for Fannie Mae conventional loans on the same terms as U.S. citizens per B2-2-02. Requirements: valid SSN, current verified immigration status (H1B qualifies), lender warrants legal presence at delivery. No LTV penalties based on citizenship. Income continuance documentation is NOT required solely because the borrower is a non-permanent resident for standard employment income. However, lenders should confirm the H1B is not expiring imminently and employment with the sponsoring employer is ongoing.",
        "source": "B2-2-02, Non-U.S. Citizen Borrower Eligibility",
        "agency": "Fannie Mae",
    },

    # ──── FREDDIE MAC (from Bulletins 2025-1 through 2025-16) ────
    {
        "id": "verified_fhlmc_2026_loan_limits",
        "text": "FREDDIE MAC 2026 CONFORMING LOAN LIMITS (Bulletin 2025-16, effective January 1, 2026): Baseline conforming limits: 1-unit $832,750, 2-unit $1,066,250, 3-unit $1,288,800, 4-unit $1,601,750. High-cost area ceiling: 1-unit $1,249,125, 2-unit $1,599,375, 3-unit $1,933,200, 4-unit $2,402,625. This represents a 3.26% increase over 2025. Guide sections impacted: 4203.1 and 4603.2. Loan Product Advisor and Loan Selling Advisor updated December 7, 2025.",
        "source": "Bulletin 2025-16; Sections 4203.1, 4603.2",
        "agency": "Freddie Mac",
    },
    {
        "id": "verified_fhlmc_multiunit_ltv_95",
        "text": "FREDDIE MAC 2-4 UNIT PRIMARY RESIDENCE LTV INCREASE (effective September 29, 2025): For purchase and rate/term refinance transactions on owner-occupied 2-4 unit properties with LPA approval, maximum LTV/CLTV is 95% for ALL unit counts (2-unit, 3-unit, and 4-unit). This was an increase from prior limits of 85%/95% (2-unit) and 80%/75% (3-4 unit). Investment property limits remain unchanged (85% 1-unit, 75% 2-4 unit). Minimum 5% down payment for 2-4 unit primary with LPA.",
        "source": "Section 4201.4 (updated Sep 2025)",
        "agency": "Freddie Mac",
    },
    {
        "id": "verified_fhlmc_resale_restrictions",
        "text": "FREDDIE MAC RESALE RESTRICTION VALUATION UPDATE (Bulletin 2025-16, effective March 3, 2026): Updated requirements for determining property value for mortgages secured by properties subject to resale restrictions that terminate upon foreclosure. For PURCHASE with income-based resale restrictions: use appraised value. For PURCHASE with non-income-based resale restrictions: use lesser of appraised value or purchase price. For REFINANCE (all restriction types): use appraised value. Guide sections impacted: 4203.1 and 4406.5.",
        "source": "Bulletin 2025-16; Sections 4203.1, 4406.5",
        "agency": "Freddie Mac",
    },
    {
        "id": "verified_fhlmc_h1b_eligible",
        "text": "FREDDIE MAC H1B/NON-PERMANENT RESIDENT ELIGIBILITY: H1B visa holders ARE eligible for Freddie Mac conventional loans. Non-permanent resident aliens who are legally present in the United States are eligible on the same terms as U.S. citizens. Requirements: valid SSN, documented legal presence. No LTV restrictions based on immigration status.",
        "source": "Section 4501.5, Non-U.S. Citizen Borrower Eligibility",
        "agency": "Freddie Mac",
    },

    # ──── FHA (from ML 2025-09, ML 2024-13, ML 2021-13, ML 2025-23, ML 2025-08) ────
    {
        "id": "verified_fha_h1b_ineligible",
        "text": "FHA BORROWER ELIGIBILITY UPDATE — H1B INELIGIBLE (Mortgagee Letter 2025-09, effective May 25, 2025): Non-permanent resident aliens (including H1B, L1, F1, OPT, DACA holders) are NO LONGER ELIGIBLE for FHA-insured loans. Only the following are eligible: U.S. citizens, lawful permanent residents (green card holders), and citizens of Federated States of Micronesia, Republic of Marshall Islands, and Republic of Palau. Social Security cards alone are insufficient to prove immigration status — USCIS documentation is required. This SUPERSEDES all prior FHA guidance on non-permanent resident alien eligibility. Alternatives for ineligible borrowers: conventional loans (Fannie/Freddie still accept H1B), non-QM loans, VA loans (if eligible veteran).",
        "source": "ML 2025-09; HUD 4000.1 (revised May 2025)",
        "agency": "FHA",
    },
    {
        "id": "verified_fha_203k_limits_updated",
        "text": "FHA 203(K) REHABILITATION PROGRAM UPDATES (Mortgagee Letter 2024-13, effective November 4, 2024): LIMITED 203(k): Maximum rehabilitation cost increased to $75,000 (from $35,000). Rehabilitation period extended to 9 months (from 6 months). Consultant fees may now be financed. STANDARD 203(k): Minimum repair cost remains $5,000. Maximum is the FHA loan limit for the area. Rehabilitation period extended to 12 months. HUD 203(k) consultant is required for Standard but optional for Limited.",
        "source": "ML 2024-13; HUD 4000.1, II.A.8.h (revised Nov 2024)",
        "agency": "FHA",
    },
    {
        "id": "verified_fha_student_loans_half_pct",
        "text": "FHA STUDENT LOAN DTI CALCULATION UPDATE (Mortgagee Letter 2021-13, effective August 16, 2021): For student loans in deferment, forbearance, or income-based repayment (IBR/IDR/PAYE): use 0.5% of the outstanding balance OR the actual documented monthly payment, whichever is greater. If the IBR/IDR payment is $0, use 0.5% of the outstanding balance (cannot use $0). For student loans in standard repayment, use the actual monthly payment from the credit report. This SUPERSEDES the prior 1% calculation rule. FHA now uses the same 0.5% as conventional (Fannie Mae/Freddie Mac).",
        "source": "ML 2021-13; HUD 4000.1, II.A.4.c.ii(E) (revised)",
        "agency": "FHA",
    },
    {
        "id": "verified_fha_2026_loan_limits",
        "text": "FHA 2026 LOAN LIMITS (Mortgagee Letter 2025-23, effective January 1, 2026): FHA floor (low-cost areas): $541,287 (65% of conforming $832,750). FHA ceiling (high-cost areas): $1,249,125 (150% of conforming). Limits vary by county/MSA — always verify the specific county limit on HUD's website. Special areas (Alaska, Hawaii, Guam, US Virgin Islands): ceiling is $1,873,688.",
        "source": "ML 2025-23; HUD 4000.1, II.A.2",
        "agency": "FHA",
    },
    {
        "id": "verified_fha_departure_residence_25pct",
        "text": "FHA DEPARTURE RESIDENCE — 25% EQUITY REQUIREMENT (HUD 4000.1, II.A.4.c.ii(H)): FHA REQUIRES at least 25% documented equity in a departing primary residence before rental income can be used to offset the mortgage payment. If borrower has LESS than 25% equity, the full PITIA is counted as a DTI liability with ZERO rental income offset — even if the borrower has a signed lease. This is the CRITICAL difference from conventional (Fannie Mae and Freddie Mac have NO equity requirement). Exception: the 25% equity requirement may be waived if borrower is relocating for employment (new job more than 100 miles from current residence). Do NOT conflate this with rules about having two FHA loans simultaneously (related but separate issue under HUD 4000.1 II.A.1.b.ii(B)).",
        "source": "HUD 4000.1, II.A.4.c.ii(H); II.A.1.b.ii(B)",
        "agency": "FHA",
    },
    {
        "id": "verified_fha_appraisal_mls_rescinded",
        "text": "FHA APPRAISAL POLICY — MULTIPLE MORTGAGEE LETTERS RESCINDED (Mortgagee Letter 2025-08, effective March 19, 2025): FHA rescinded multiple appraisal-related Mortgagee Letters to streamline and consolidate appraisal policy. This simplifies the appraisal requirements by eliminating overlapping or outdated guidance. Current appraisal requirements are now consolidated in HUD 4000.1.",
        "source": "ML 2025-08; HUD 4000.1 (revised March 2025)",
        "agency": "FHA",
    },

    # ──── VA (from Circulars 26-23-06, 26-25-7, 26-25-10, 26-24-17) ────
    {
        "id": "verified_va_funding_fee_schedule",
        "text": "VA FUNDING FEE SCHEDULE (Circular 26-23-06, effective April 7, 2023 through November 14, 2031): PURCHASE/CONSTRUCTION — First Use: 2.15% (no down payment), 1.50% (5%+ down), 1.25% (10%+ down). Subsequent Use: 3.30% (no down payment), 1.50% (5%+ down), 1.25% (10%+ down). CASH-OUT REFINANCE — First Use: 2.15%, Subsequent Use: 3.30%. IRRRL (Streamline Refinance): 0.50% for all uses. LOAN ASSUMPTIONS: 0.50%. MANUFACTURED HOME (not permanently affixed): 1.00%. Reserves/National Guard pay the SAME rates as regular military (parity established). EXEMPT from funding fee: veterans receiving VA disability compensation, veterans rated eligible for compensation but receiving retirement pay, surviving spouses of veterans who died in service or from service-connected disability, active duty Purple Heart recipients. The funding fee is tax-deductible as mortgage interest and can be financed into the loan amount.",
        "source": "Circular 26-23-06 Exhibit B; 38 USC 3729(b)(2)",
        "agency": "VA",
    },
    {
        "id": "verified_va_energy_efficiency",
        "text": "VA ENERGY EFFICIENCY UNDERWRITING (Circular 26-25-7, effective September 22, 2025): Per the Joseph Maxwell Cleland and Robert Dole Memorial Veterans Benefits and Health Care Improvement Act of 2022, lenders may use a property's energy efficiency rating as a compensating factor during VA underwriting. If a RESNET HERS report (or other approved energy efficiency report) shows potential utility expense savings, the lender may consider the cost savings as a compensating factor for residual income calculation (per VA Lenders Handbook Ch. 4 Topic 10 Section d). The lender notes this on VA Form 26-6393 in the Remarks section. Energy efficiency reports should be dated within 12 months of closing. The report validity is tied to family size vs bedrooms — cannot use this compensating factor if family size exceeds bedrooms plus one. Lenders are NOT to reduce maintenance/utilities expenses in the residual income calculation — this is purely a compensating factor.",
        "source": "Circular 26-25-7; 38 USC 3710(i)",
        "agency": "VA",
    },
    {
        "id": "verified_va_2026_loan_limits",
        "text": "VA 2026 LOAN LIMITS (Circular 26-25-10, effective January 1, 2026): For veterans with FULL entitlement (no prior VA loan default or active VA loan): there is NO loan limit — VA will guaranty any amount the lender approves. For veterans with PARTIAL (reduced) entitlement: county-level conforming loan limits apply. Baseline: $832,750. High-cost areas: up to $1,249,125. Veterans with partial entitlement borrowing above the county limit may need a down payment for the portion above the guaranty. The Blue Water Navy Vietnam Veterans Act of 2019 eliminated loan limits for full-entitlement veterans effective January 1, 2020.",
        "source": "Circular 26-25-10; FHFA 2026 CLL",
        "agency": "VA",
    },
    {
        "id": "verified_va_borrower_eligibility",
        "text": "VA LOAN BORROWER ELIGIBILITY — WHO CAN USE VA ENTITLEMENT: Only the following individuals may use VA home loan entitlement: (1) Veterans with qualifying military service and honorable/general discharge, (2) Active duty service members after minimum service requirement, (3) National Guard/Reserve members with 6+ years of service or who were called to active duty, (4) Surviving unremarried spouses of veterans who died in service or from service-connected disability (or remarried after age 57). IMPORTANT: The veteran must be ON the loan — a non-veteran spouse alone cannot use the veteran's entitlement. A Certificate of Eligibility (COE) is required. VA does NOT require U.S. citizenship — eligibility is based on military service, not immigration status.",
        "source": "VA Pamphlet 26-7, Ch. 3; 38 USC 3702",
        "agency": "VA",
    },
    {
        "id": "verified_va_non_occ_coborrower",
        "text": "VA NON-OCCUPANT CO-BORROWER RULES: VA loan co-borrower options are very limited compared to conventional and FHA. Only the veteran's SPOUSE or ANOTHER ELIGIBLE VETERAN can be a co-borrower on a VA loan. Civilian non-veterans (parents, siblings, cousins, friends) CANNOT be non-occupant co-borrowers on VA loans. VA does allow a joint loan with a non-veteran, but the VA guaranty only covers the veteran's portion, resulting in a lower guaranty percentage and potentially requiring a down payment on the non-veteran's share. This is a critical difference from FHA (which allows both family and non-family co-signers at different LTVs) and conventional (which allows any individual as co-signer).",
        "source": "VA Pamphlet 26-7, Ch. 3; 38 USC 3710",
        "agency": "VA",
    },

    # ──── CROSS-AGENCY VERIFIED CHUNKS ────
    {
        "id": "verified_cross_agency_departure_residence",
        "text": "DEPARTURE RESIDENCE RENTAL INCOME — CROSS-AGENCY COMPARISON: CONVENTIONAL (Fannie Mae/Freddie Mac): Executed lease + rent comp (Form 1007) OR executed lease + 2 months bank statements showing rent deposits. NO security deposit required. NO equity requirement. 75% of gross rent minus PITIA = net rental income/loss. FHA: REQUIRES 25% documented equity in the departing residence. If equity is below 25%, full PITIA is counted as liability with ZERO rental offset even with a lease. Exception for 100+ mile employment relocation. VA: Executed lease + rent comp. NO equity requirement. 75% of gross rent minus PITIA. ALL AGENCIES: If no lease documentation exists, the full PITIA of the departing residence must be counted as a monthly liability with zero rental income offset.",
        "source": "B3-3.1-08; Section 5306.1; HUD 4000.1 II.A.4.c.ii(H); VA Pamphlet 26-7 Ch. 4",
        "agency": "All Agencies",
    },
    {
        "id": "verified_cross_agency_gift_documentation",
        "text": "GIFT FUND DOCUMENTATION — CROSS-AGENCY RULES: ALL AGENCIES require a signed gift letter (donor name, amount, relationship, property address, no repayment expected). Donor bank statements are NOT universally required — they are only needed when the transfer of funds cannot be verified through other documentation (wire confirmation, cashier's check, closing statement). All gift funds must be in US DOLLARS at closing. Foreign currency gifts must be converted to USD with conversion documented. Non-English documents require certified English translation. ELIGIBLE DONORS vary by agency: Fannie Mae allows relatives by blood/marriage/adoption, domestic partner, fiancé, employer, government entity, nonprofit. Freddie Mac is similar. FHA allows family members, employer, close friend with LOE, government agency, nonprofit. Cousin is NOT explicitly listed in HUD's family member definition.",
        "source": "B3-4.3-04; Section 5501.2; HUD 4000.1 II.A.4.d.iii",
        "agency": "All Agencies",
    },
    {
        "id": "verified_cross_agency_non_occ_coborrower",
        "text": "NON-OCCUPANT CO-BORROWER — CROSS-AGENCY COMPARISON: FANNIE MAE: Any individual can co-sign (no family requirement). Max LTV: 97% (1-unit), 95% (2-4 unit with DU). FREDDIE MAC: Any individual can co-sign (no family requirement). Max LTV: 95% (1-unit), 95% (2-4 unit with LPA). Manual UW: occupant max 35% housing ratio, 43% DTI. FHA: Both family and non-family non-occ co-borrowers are ALLOWED. Family member on 1-unit: standard 96.5% LTV. Non-family on 1-unit: LTV capped at 75%. Any non-occ (family or not) on 2-4 unit: 75% max LTV. Cousin is NOT in HUD's family definition. VA: Only veteran's spouse or another eligible veteran. Civilian non-veterans CANNOT co-sign VA loans.",
        "source": "B2-2-04; Section 4201.17; HUD 4000.1 II.A.2.a; VA Pamphlet 26-7 Ch. 3",
        "agency": "All Agencies",
    },
]


@app.route("/api/admin/upload-verified-chunks", methods=["POST"])
def upload_verified_chunks():
    """Upload all verified guideline chunks from official update letters to Pinecone."""
    index = get_pinecone_index()
    if not index:
        return jsonify({"error": "Pinecone not connected"}), 500

    results = {"upserted": [], "errors": []}

    for chunk in VERIFIED_CHUNKS:
        try:
            embedding = embed_query(chunk["text"])
            if not embedding:
                results["errors"].append(f"Could not embed: {chunk['id']}")
                continue

            index.upsert(vectors=[{
                "id": chunk["id"],
                "values": embedding,
                "metadata": {
                    "text": chunk["text"],
                    "content": chunk["text"],
                    "source": chunk["source"],
                    "agency": chunk["agency"],
                    "type": "verified_official_update",
                    "verified_date": "2026-03-29",
                    "priority": "high",
                }
            }])
            results["upserted"].append({"id": chunk["id"], "agency": chunk["agency"]})
        except Exception as e:
            results["errors"].append(f"Error upserting {chunk['id']}: {str(e)}")

    return jsonify({
        "status": "complete",
        "upserted_count": len(results["upserted"]),
        "error_count": len(results["errors"]),
        "details": results,
    })


# -- INCOME WORKBOOK FILLER -------------------------------------------------
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'static', 'income_workbook_template.xlsm')

@app.route("/api/income-template", methods=["GET"])
def income_template():
    """Serve the pre-built Income Workbook .xlsm template."""
    if os.path.exists(TEMPLATE_PATH):
        return send_file(
            TEMPLATE_PATH,
            mimetype='application/vnd.ms-excel.sheet.macroEnabled.12',
            as_attachment=False,
            download_name='income_workbook_template.xlsm'
        )
    return jsonify({"error": "Template not found"}), 404


@app.route("/api/extract-income", methods=["POST"])
def extract_income():
    """
    Proxy endpoint for Claude vision API calls.
    Accepts: { "images": [{"data": "base64...", "mime": "image/jpeg"}], "prompt": "..." }
    Returns: Claude JSON response.
    """
    if not anthropic_client:
        return jsonify({"error": "Anthropic API not configured"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    images = data.get("images", [])
    prompt = data.get("prompt", "")
    if not images or not prompt:
        return jsonify({"error": "Missing images or prompt"}), 400

    # Build content blocks
    content = []
    for img in images:
        b64 = img.get("data", "")
        mime = img.get("mime", "image/jpeg")
        if mime == "application/pdf":
            content.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}})
        else:
            content.append({"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}})
    content.append({"type": "text", "text": prompt})

    try:
        import re as _re
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": content}]
        )
        text = "".join(block.text for block in response.content if hasattr(block, 'text'))
        clean = text.replace('```json', '').replace('```', '').strip()
        try:
            parsed = json.loads(clean)
        except json.JSONDecodeError:
            m = _re.search(r'\[[\s\S]*\]|\{[\s\S]*\}', clean)
            if m:
                parsed = json.loads(m.group(0))
            else:
                return jsonify({"error": "Could not parse AI response", "raw": clean[:500]}), 500
        return jsonify({"result": parsed})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/income-tool", methods=["GET"])
def income_tool():
    """Serve the Income Workbook Filler tool page."""
    _tmpl_path = os.path.join(os.path.dirname(__file__), 'templates', 'income_tool.html')
    if os.path.exists(_tmpl_path):
        with open(_tmpl_path, 'r') as _f:
            return _f.read()
    return "<h1>Income Tool template not found</h1>", 404


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
  <a href="/income-tool" style="margin-left:auto;padding:6px 14px;border-radius:6px;background:#1e40af;color:#93c5fd;font-size:11px;font-weight:600;text-decoration:none;letter-spacing:.3px;transition:background .2s" onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#1e40af'">Income Tool</a>
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
