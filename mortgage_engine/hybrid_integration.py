"""
HYBRID ENGINE INTEGRATION LAYER
=================================
Bridges the deterministic rule engine with the existing Flask RAG pipeline.

This module provides:
1. hybrid_pipeline() — Drop-in replacement for full_rag_pipeline()
2. hybrid_stream() — Streaming variant for SSE endpoints
3. inject_rule_context() — Prepends rule engine results to RAG context
4. format_for_voice() — Converts rule engine results to natural speech
5. format_for_web() — Converts rule engine results to rich web display

Architecture:
  Question → Router classifies → Rule Engine and/or RAG → Merged Answer
"""

import json
import time
from typing import Optional, Dict, Any, Tuple, List, Callable, Generator

from router import (
    classify_query, route_and_answer, extract_parameters,
    ROUTE_RULE_ENGINE, ROUTE_RAG, ROUTE_HYBRID, ROUTE_COMPARISON
)
from rule_engine import (
    LoanScenario, evaluate_scenario, compare_agencies,
    lookup_ltv, lookup_dti, lookup_credit_score, lookup_mi, lookup_mip,
    lookup_funding_fee, lookup_reserves, lookup_loan_limits,
    lookup_va_residual_income, ScenarioResult, RuleResult,
)
from rules_database import resolve_agency


# =============================================================================
# MAIN HYBRID PIPELINE
# =============================================================================

def hybrid_pipeline(
    question: str,
    rag_pipeline_fn: Optional[Callable] = None,
    for_voice: bool = False,
    conversation_history: Optional[list] = None,
) -> Tuple[str, list, str, Dict[str, Any]]:
    """
    The hybrid pipeline — drop-in replacement for full_rag_pipeline().

    Args:
        question: User's natural language question
        rag_pipeline_fn: The existing full_rag_pipeline function
        for_voice: Whether response is for voice (ElevenLabs TTS)
        conversation_history: Prior conversation messages

    Returns:
        (answer_text, chunks_used, optimized_query, metadata)
        metadata includes: route, classification, rule_engine_data, timing
    """
    start = time.time()

    # Step 1: Classify the query
    classification = classify_query(question)
    route = classification["route"]
    params = classification["parameters"]
    rule_type = classification["rule_type"]

    metadata = {
        "route": route,
        "classification": classification,
        "rule_engine_data": None,
        "timing_ms": 0,
    }

    # Step 2: Route execution
    if route == ROUTE_RULE_ENGINE or route == ROUTE_COMPARISON:
        # Pure deterministic — no RAG needed
        rule_result = route_and_answer(question)
        rule_answer = rule_result["combined_answer"]
        metadata["rule_engine_data"] = rule_result

        if for_voice:
            answer = format_rule_answer_for_voice(rule_answer, rule_type, params)
        else:
            answer = format_rule_answer_for_web(rule_answer, rule_type, params,
                                                 classification)

        metadata["timing_ms"] = round((time.time() - start) * 1000)
        return (answer, [], question, metadata)

    elif route == ROUTE_RAG:
        # Pure RAG — use existing pipeline
        if rag_pipeline_fn:
            answer, chunks, opt_query = rag_pipeline_fn(
                question, for_voice, conversation_history
            )
            metadata["timing_ms"] = round((time.time() - start) * 1000)
            return (answer, chunks, opt_query, metadata)
        else:
            metadata["timing_ms"] = round((time.time() - start) * 1000)
            return (
                "I'd need to search the guidelines for that. The RAG pipeline is processing your question.",
                [], question, metadata
            )

    elif route == ROUTE_HYBRID:
        # Both: Rule engine for hard facts + RAG for context
        rule_result = route_and_answer(question)
        rule_answer = rule_result["combined_answer"]
        metadata["rule_engine_data"] = rule_result

        if rag_pipeline_fn:
            rag_answer, chunks, opt_query = rag_pipeline_fn(
                question, for_voice, conversation_history
            )

            if for_voice:
                # For voice: lead with rule engine facts, then brief RAG context
                rule_voice = format_rule_answer_for_voice(rule_answer, rule_type, params)
                answer = f"{rule_voice} Additionally, {_truncate_for_voice(rag_answer)}"
            else:
                # For web: structured hybrid response
                answer = format_hybrid_answer_for_web(
                    rule_answer, rag_answer, rule_type, params, classification
                )

            metadata["timing_ms"] = round((time.time() - start) * 1000)
            return (answer, chunks, opt_query, metadata)
        else:
            # No RAG available — fall back to rule engine only
            if for_voice:
                answer = format_rule_answer_for_voice(rule_answer, rule_type, params)
            else:
                answer = format_rule_answer_for_web(rule_answer, rule_type, params,
                                                     classification)
            metadata["timing_ms"] = round((time.time() - start) * 1000)
            return (answer, [], question, metadata)

    # Fallback
    metadata["timing_ms"] = round((time.time() - start) * 1000)
    return ("I couldn't process that question. Please try rephrasing.", [], question, metadata)


# =============================================================================
# RULE CONTEXT INJECTION (for hybrid mode)
# =============================================================================

def build_rule_engine_context_block(question: str) -> Optional[str]:
    """
    Run the rule engine and format its output as a context block
    that can be prepended to the RAG context for Claude.

    For complex multi-topic questions, runs a FULL scenario evaluation
    (LTV + DTI + credit score + fees for all agencies) instead of just
    the single rule type the router picked. This ensures the LLM has
    all deterministic data available.

    Returns None if the question doesn't trigger rule engine,
    otherwise returns a formatted context block string.
    """
    classification = classify_query(question)
    if classification["route"] in (ROUTE_RAG,):
        return None

    complexity = classification.get("complexity", {})
    is_complex = complexity.get("is_complex", False)

    # For complex questions, run full scenario evaluation instead of
    # single-type lookup. This covers LTV, DTI, credit, fees, etc.
    if is_complex:
        params = classification.get("parameters", {})
        scenario_kwargs = {}
        for key in ["agency", "transaction_type", "occupancy", "units",
                     "rate_type", "credit_score", "ltv", "dti",
                     "loan_amount", "down_payment_pct", "loan_term_years",
                     "va_first_use", "va_disability_exempt",
                     "underwriting_method", "state"]:
            if key in params:
                scenario_kwargs[key] = params[key]
        try:
            scenario = LoanScenario(**scenario_kwargs)
            result = evaluate_scenario(scenario)
            rule_data = result.to_text()
            citations = [r.citation for results in result.results.values()
                         for r in results if r.citation]
        except Exception:
            # Fallback to single lookup
            result = route_and_answer(question)
            if not result.get("rule_engine_answer"):
                return None
            rule_data = result["rule_engine_answer"]
            citations = result.get("citations", [])
    else:
        result = route_and_answer(question)
        if not result.get("rule_engine_answer"):
            return None
        rule_data = result["rule_engine_answer"]
        citations = result.get("citations", [])

    block = [
        "╔══════════════════════════════════════════════════════════════════╗",
        "║  DETERMINISTIC RULE ENGINE RESULTS (verified, zero-hallucination)  ║",
        "╚══════════════════════════════════════════════════════════════════╝",
        "",
        rule_data,
        "",
        "IMPORTANT: The above values are from the official agency guidelines.",
        "Use these exact numbers in your answer. Do NOT contradict them.",
        "You may add explanatory context from the retrieved passages below,",
        "but the numerical values above are authoritative.",
    ]
    if citations:
        block.append(f"\nRule Engine Citations: {', '.join(c for c in citations if c)}")

    return "\n".join(block)


def inject_rule_context_into_rag(existing_context: str, question: str) -> str:
    """
    Inject rule engine results into existing RAG context.
    Call this between build_context() and generate_answer() in the existing pipeline.
    """
    rule_block = build_rule_engine_context_block(question)
    if rule_block:
        return f"{rule_block}\n\n{'═' * 70}\nRETRIEVED GUIDELINE PASSAGES:\n{'═' * 70}\n\n{existing_context}"
    return existing_context


# =============================================================================
# FORMATTING — VOICE
# =============================================================================

def format_rule_answer_for_voice(raw_answer: str, rule_type: str,
                                  params: dict) -> str:
    """
    Convert rule engine output to natural conversational language for TTS.
    Max 4-5 sentences. No symbols, abbreviations spoken out.
    """
    # Parse the raw answer to extract key values
    lines = raw_answer.strip().split("\n")
    agency = params.get("agency", "")

    # For simple single-agency answers
    if rule_type == "ltv":
        # Extract max LTV value
        for line in lines:
            if "max_ltv:" in line:
                val = _extract_value_from_line(line, "max_ltv:")
                if val:
                    tx = params.get("transaction_type", "purchase").replace("_", " ")
                    occ = params.get("occupancy", "primary").replace("_", " ")
                    units = params.get("units", "1 unit")
                    return (f"The maximum loan-to-value ratio for {agency} "
                            f"on a {tx}, {occ} residence, {units} property "
                            f"is {val} percent.")
        return _generic_voice_answer(raw_answer)

    elif rule_type == "dti":
        for line in lines:
            if "max_dti:" in line:
                val = _extract_value_from_line(line, "max_dti:")
                if val:
                    method = params.get("underwriting_method", "automated")
                    return (f"The maximum debt-to-income ratio for {agency} "
                            f"with {method} underwriting is {val} percent.")
        # Multiple agencies
        if len(lines) > 1:
            parts = []
            for line in lines:
                if "|" in line:
                    ag = line.split("|")[0].strip().replace("[✓]", "").replace("[✗]", "").strip()
                    val = _extract_value_from_line(line, "max_dti:")
                    if val:
                        parts.append(f"{ag} allows up to {val} percent")
            if parts:
                return "For maximum debt-to-income ratios: " + ". ".join(parts) + "."
        return _generic_voice_answer(raw_answer)

    elif rule_type == "credit_score":
        for line in lines:
            if "min_credit_score:" in line:
                val = _extract_value_from_line(line, "min_credit_score:")
                if val:
                    return f"The minimum credit score for {agency} is {val}."
        return _generic_voice_answer(raw_answer)

    elif rule_type == "funding_fee":
        for line in lines:
            if "fee_pct" in line:
                # Extract fee percentage
                import re
                pct = re.search(r"(\d+\.?\d*)%", line)
                if pct:
                    dp = params.get("down_payment_pct", 0)
                    use = "first" if params.get("va_first_use", True) else "subsequent"
                    return (f"The VA funding fee for {use} use with "
                            f"{dp} percent down is {pct.group(1)} percent of the loan amount.")
        return _generic_voice_answer(raw_answer)

    elif rule_type == "mip":
        parts = []
        for line in lines:
            if "upfront_mip_rate" in line:
                import re
                rate = re.search(r"upfront_mip_rate.*?(\d+\.?\d*)%", line)
                if rate:
                    parts.append(f"The upfront M I P is {rate.group(1)} percent of the base loan amount")
            if "annual_mip_rate" in line:
                import re
                rate = re.search(r"annual_mip_rate.*?(\d+\.?\d*)%", line)
                monthly = re.search(r"monthly_mip.*?\$([\d,.]+)", line)
                if rate:
                    parts.append(f"and the annual M I P is {rate.group(1)} percent")
                if monthly:
                    parts.append(f"which comes to about {monthly.group(1)} dollars per month")
        if parts:
            return "For FHA mortgage insurance: " + ", ".join(parts) + "."
        return _generic_voice_answer(raw_answer)

    elif rule_type == "comparison":
        # Simplify comparison for voice
        eligible = []
        for line in lines:
            if "ELIGIBLE:" in line:
                eligible = line.split("ELIGIBLE:")[-1].strip().split(",")
                eligible = [a.strip() for a in eligible if a.strip()]
        if eligible:
            return (f"Based on your scenario, you're eligible with "
                    f"{', '.join(eligible[:-1])} and {eligible[-1]}." if len(eligible) > 1
                    else f"Based on your scenario, you're eligible with {eligible[0]}.")
        return _generic_voice_answer(raw_answer)

    return _generic_voice_answer(raw_answer)


def _generic_voice_answer(raw: str) -> str:
    """Fallback: clean up raw text for voice."""
    # Remove symbols and formatting
    clean = raw.replace("[✓]", "").replace("[✗]", "").replace("|", ",")
    clean = clean.replace("{", "").replace("}", "").replace("'", "")
    # Truncate
    sentences = clean.split(".")
    return ". ".join(s.strip() for s in sentences[:4] if s.strip()) + "."


def _truncate_for_voice(text: str, max_sentences: int = 2) -> str:
    """Truncate text to max sentences for voice."""
    sentences = text.split(".")
    return ". ".join(s.strip() for s in sentences[:max_sentences] if s.strip()) + "."


def _extract_value_from_line(line: str, key: str) -> Optional[str]:
    """Extract a value after a key in a line like 'max_ltv: 97'."""
    if key in line:
        after = line.split(key)[-1].strip()
        # Get first word/number
        val = after.split()[0].strip().rstrip(",").rstrip(")")
        return val
    return None


# =============================================================================
# FORMATTING — WEB
# =============================================================================

def format_rule_answer_for_web(raw_answer: str, rule_type: str, params: dict,
                                classification: dict) -> str:
    """
    Format rule engine output as rich markdown for the web UI.
    """
    route = classification["route"]
    confidence = classification["confidence"]

    header = "## 📊 Deterministic Rule Engine Answer\n"
    header += f"*Route: {route} | Confidence: {confidence:.0%} | Source: Official Agency Guidelines*\n\n"

    if route == ROUTE_COMPARISON:
        return header + _format_comparison_for_web(raw_answer)

    # Clean up the raw answer for web display
    formatted = raw_answer.replace("[✓]", "✅").replace("[✗]", "❌")

    # Add parameter summary
    param_summary = ""
    if params:
        parts = []
        if params.get("agency"): parts.append(f"**Agency:** {params['agency']}")
        if params.get("transaction_type"): parts.append(f"**Transaction:** {params['transaction_type'].replace('_', ' ').title()}")
        if params.get("occupancy"): parts.append(f"**Occupancy:** {params['occupancy'].replace('_', ' ').title()}")
        if params.get("credit_score"): parts.append(f"**Credit Score:** {params['credit_score']}")
        if params.get("ltv"): parts.append(f"**LTV:** {params['ltv']}%")
        if params.get("loan_amount"): parts.append(f"**Loan:** ${params['loan_amount']:,.0f}")
        if parts:
            param_summary = "**Your Scenario:** " + " | ".join(parts) + "\n\n"

    return header + param_summary + "```\n" + formatted + "\n```"


def _format_comparison_for_web(raw_answer: str) -> str:
    """Format cross-agency comparison nicely for web."""
    # Already well-formatted, just clean up
    formatted = raw_answer.replace("[✓]", "✅").replace("[✗]", "❌")
    return "```\n" + formatted + "\n```"


def format_hybrid_answer_for_web(rule_answer: str, rag_answer: str,
                                  rule_type: str, params: dict,
                                  classification: dict) -> str:
    """Format combined rule engine + RAG answer for web."""
    rule_section = format_rule_answer_for_web(rule_answer, rule_type, params, classification)
    rag_section = f"\n\n## 📖 Additional Guideline Context\n\n{rag_answer}"
    return rule_section + rag_section


# =============================================================================
# FLASK INTEGRATION HELPERS
# =============================================================================

def get_hybrid_system_prompt_addition() -> str:
    """
    Additional system prompt text to inject into the existing generate_answer()
    system prompt, making Claude aware of the rule engine layer.
    """
    return """
IMPORTANT — HYBRID ENGINE INTEGRATION:
You now have access to a deterministic rule engine that provides exact,
citation-backed answers for numerical mortgage rules (LTV limits, DTI caps,
credit score minimums, MI/MIP/funding fee calculations, loan limits, etc.).

When rule engine results are prepended to the context (marked with
"DETERMINISTIC RULE ENGINE RESULTS"), treat those values as AUTHORITATIVE.
Do NOT change or round the numbers. Do NOT contradict them.

You may:
- Explain the rule engine's numbers in plain language
- Add context from the retrieved guideline passages
- Note exceptions, compensating factors, or special circumstances
- Suggest alternatives if the borrower doesn't qualify

You must NOT:
- Override rule engine numbers with different values
- Hallucinate percentages that differ from the rule engine
- Ignore the rule engine results in favor of your training data
"""


def build_hybrid_metadata_event(classification: dict) -> dict:
    """Build metadata for SSE streaming that includes routing info."""
    return {
        "route": classification["route"],
        "rule_type": classification.get("rule_type"),
        "confidence": classification.get("confidence", 0),
        "parameters_extracted": classification.get("parameters", {}),
    }


# =============================================================================
# STREAMING HELPER (for /api/ask-stream)
# =============================================================================

def hybrid_stream_preprocess(question: str) -> Dict[str, Any]:
    """
    Pre-process a question for the streaming endpoint.
    Returns rule engine results if applicable, so they can be
    sent as the first SSE event before RAG streaming begins.

    Returns:
        {
            "classification": dict,
            "rule_engine_answer": str or None,
            "use_rag": bool,
            "rule_context_block": str or None,  # For injection into RAG context
        }
    """
    classification = classify_query(question)
    route = classification["route"]
    force_rag = classification.get("force_rag", False)

    result = {
        "classification": classification,
        "rule_engine_answer": None,
        "rule_citations": [],
        "use_rag": route in (ROUTE_RAG, ROUTE_HYBRID) or force_rag,
        "rule_context_block": None,
    }

    if route in (ROUTE_RULE_ENGINE, ROUTE_COMPARISON, ROUTE_HYBRID):
        rule_result = route_and_answer(question)
        result["rule_engine_answer"] = rule_result.get("combined_answer")
        result["rule_citations"] = [c for c in rule_result.get("citations", []) if c]

        # Build context block for HYBRID or force_rag (complex questions
        # that route to RULE_ENGINE/COMPARISON but need RAG supplementation)
        if route == ROUTE_HYBRID or force_rag:
            result["rule_context_block"] = build_rule_engine_context_block(question)

    return result


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("HYBRID INTEGRATION — TEST SUITE")
    print("=" * 70)

    # Mock RAG pipeline
    def mock_rag_pipeline(q, for_voice=False, history=None):
        return (
            "Based on Fannie Mae Selling Guide B2-1.1-01, the maximum LTV for a "
            "purchase transaction on a primary residence single-family home is 97% "
            "with DU approval. Manual underwriting caps at 95%. The 97% option requires "
            "a fixed-rate mortgage and at least 3% borrower contribution from own funds.",
            [{"chunk_id": "FNMA_001", "agency": "Fannie Mae", "score": 0.95}],
            "fannie mae max LTV purchase primary 1-unit fixed"
        )

    test_questions = [
        ("What's the max LTV for Fannie Mae purchase?", False),
        ("Compare FHA vs VA for a 720 credit score purchase", False),
        ("Explain the FHA streamline refinance requirements", False),
        ("VA funding fee with 0% down, first use, $400,000 loan", True),  # voice
        ("What's the max DTI for all agencies?", False),
    ]

    for question, voice in test_questions:
        print(f"\n{'━' * 60}")
        print(f"Q: {question} {'(voice)' if voice else '(web)'}")
        answer, chunks, opt_q, meta = hybrid_pipeline(
            question, mock_rag_pipeline, voice
        )
        print(f"Route: {meta['route']} ({meta['timing_ms']}ms)")
        print(f"Answer preview: {answer[:300]}...")
        print(f"Chunks used: {len(chunks)}")

    # Test context injection
    print(f"\n{'━' * 60}")
    print("Testing rule context injection:")
    context = inject_rule_context_into_rag(
        "Some RAG context about Fannie Mae guidelines...",
        "What's the max LTV for Fannie Mae purchase?"
    )
    print(context[:500])

    # Test streaming preprocess
    print(f"\n{'━' * 60}")
    print("Testing streaming preprocess:")
    prep = hybrid_stream_preprocess("FHA MIP on a $350,000 loan at 96.5% LTV")
    print(f"Route: {prep['classification']['route']}")
    print(f"Use RAG: {prep['use_rag']}")
    print(f"Rule answer: {prep['rule_engine_answer'][:200] if prep['rule_engine_answer'] else 'None'}...")
