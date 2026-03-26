"""
SMART QUERY ROUTER — THE BRAIN OF THE HYBRID ENGINE
=====================================================
Classifies natural language mortgage questions and routes them to:
  1. RULE_ENGINE — deterministic lookups (LTV, DTI, credit, fees, etc.)
  2. RAG — contextual/explanatory questions that need guideline passages
  3. HYBRID — needs both (rule lookup + RAG explanation)

The router extracts structured parameters from natural language so the
rule engine gets clean, typed inputs. No hallucination possible on the
deterministic path.

Architecture:
  classify_query() → { route, parameters, confidence }
  route_and_answer() → calls rule engine and/or RAG, merges results
"""

import re
import json
from typing import Optional, Dict, Any, Tuple, List
from rule_engine import (
    LoanScenario, evaluate_scenario, compare_agencies, compare_agencies_text,
    lookup_ltv, lookup_dti, lookup_credit_score, lookup_mi, lookup_mip,
    lookup_funding_fee, lookup_reserves, lookup_loan_limits,
    lookup_va_residual_income,
    quick_ltv, quick_dti, quick_credit, quick_funding_fee, quick_mip,
)
from rules_database import AGENCY_ALIASES, resolve_agency


# =============================================================================
# ROUTE TYPES
# =============================================================================

ROUTE_RULE_ENGINE = "RULE_ENGINE"
ROUTE_RAG = "RAG"
ROUTE_HYBRID = "HYBRID"
ROUTE_COMPARISON = "COMPARISON"  # Special: cross-agency comparison


# =============================================================================
# KEYWORD-BASED CLASSIFIER (fast, no LLM needed)
# =============================================================================

# Patterns that strongly indicate a deterministic rule lookup
RULE_ENGINE_PATTERNS = [
    # LTV questions (weight: 2 each)
    (r"(?:max|maximum|highest|what(?:'s| is))\s+(?:the\s+)?(?:ltv|loan.to.value|cltv)", "ltv"),
    (r"(?:ltv|loan.to.value)\s+(?:limit|cap|max|for|on)", "ltv"),
    (r"(?:how much|what).+(?:down payment|down.payment|put down)", "ltv"),
    (r"(?:minimum|min)\s+(?:down payment|down.payment)", "ltv"),
    (r"(?:\d+%?\s+(?:ltv|down))", "ltv"),
    (r"(?:100%\s+financ)", "ltv"),
    (r"(?:manufactured|condo|home|property|residence)\s+(?:ltv|loan.to.value)", "ltv"),

    # DTI questions
    (r"(?:max|maximum|highest|what(?:'s| is))\s+(?:the\s+)?(?:dti|debt.to.income)", "dti"),
    (r"(?:dti|debt.to.income)\s+(?:limit|cap|max|ratio|for|too\s+high)", "dti"),
    (r"(?:max|maximum)\s+dti", "dti"),
    (r"\b\d+%?\s*dti\b", "dti"),
    (r"dti.*(?:manual|automated|du\b|lpa)", "dti"),

    # Credit score questions
    (r"(?:min|minimum|lowest|what(?:'s| is))\s+(?:the\s+)?(?:credit\s*score|fico|score)", "credit_score"),
    (r"(?:credit\s*score|fico)\s+(?:require|need|minimum|floor|enough|eligible)", "credit_score"),
    (r"(?:\d{3})\s+(?:credit|fico|score)", "credit_score"),
    (r"(?:what|how much|what's)\s+(?:credit\s*score|score)\s+(?:do\s+(?:i|you)|is\s+needed|need)", "credit_score"),
    (r"(?:is\s+\d{3})\s+(?:enough|sufficient|ok|okay|good)\s+(?:for|to)", "credit_score"),
    (r"(?:need|require).*credit\s*score", "credit_score"),

    # MI / MIP questions
    (r"(?:mortgage\s+insurance|mi\s+|pmi|private\s+mortgage)", "mi"),
    (r"(?:mip|mortgage\s+insurance\s+premium|ufmip|upfront\s+mip|annual\s+mip)", "mip"),
    (r"(?:how\s+much\s+is\s+(?:the\s+)?(?:upfront\s+)?mip)", "mip"),

    # VA funding fee
    (r"(?:funding\s+fee|va\s+(?:funding|fee))", "funding_fee"),

    # Loan limits
    (r"(?:loan\s+limit|conforming\s+limit|max\s+loan|maximum\s+loan\s+amount)", "loan_limit"),

    # Reserves
    (r"(?:reserve|reserves|months?\s+(?:of\s+)?reserve)", "reserves"),

    # Residual income
    (r"(?:residual\s+income)", "residual_income"),

    # Eligibility checks
    (r"(?:am\s+i|is\s+(?:this|the|my)|do\s+i|can\s+i|will\s+i)\s+(?:eligible|qualify|approved)", "eligibility"),
    (r"(?:eligible|qualify|qualif)\s+(?:for|with)", "eligibility"),

    # Direct comparison requests
    (r"(?:compare|comparison|versus|vs\.?|difference|better|which\s+(?:is|agency|program))", "comparison"),
    (r"(?:fannie|freddie|fha|va).+(?:\bvs\b|\bversus\b|\bor\b|\bcompared\b|\bdiffer)", "comparison"),

    # Specific numbers / scenarios (low priority — only adds context)
    (r"(?:\d+)\s*(?:unit|bedroom|year|month)", "scenario"),
    (r"(?:purchase|refi|refinance|cash.out|streamline|irrrl)", "scenario"),
    (r"(?:primary|second\s+home|investment|rental|vacation)", "scenario"),
    (r"(?:fixed|arm|adjustable)", "scenario"),
]

# Patterns that strongly indicate RAG is needed
RAG_PATTERNS = [
    r"(?:explain|why|how\s+does|what\s+happens|what\s+if|tell\s+me\s+about)",
    r"(?:process|procedure|steps?\s+(?:for|to)|documentation|documents?\s+needed)",
    r"(?:exception|waiver|variance|compensating\s+factor)",
    r"(?:history|background|origin|purpose\s+of)",
    r"(?:guideline|handbook|section|chapter|paragraph)",
    r"(?:manual\s+(?!underwr))",  # "manual" but NOT "manual underwriting" (that's a rule lookup)
    r"(?:example|scenario.*explain|walk\s+me\s+through)",
    r"(?:gift\s+(?:fund|letter|donor|source)|asset\s+(?:verification|documentation))",
    r"(?:appraisal|inspection|title|escrow|closing\s+cost)",
    r"(?:bankruptcy|foreclosure|short\s+sale|deed.in.lieu|waiting\s+period)",
    r"(?:self.employ|commission|bonus|overtime|rental\s+income|income\s+calculation)",
    r"(?:non.traditional\s+credit|alternative\s+credit|credit\s+history)",
    r"(?:condo\s+(?:project|approval|review)|warrantable|non.warrantable)",
    r"(?:what\s+are\s+the\s+(?:rules|requirements|guidelines)\s+(?:for|regarding|about))",

    # Immigration / visa / citizenship topics
    r"(?:h1b|h-1b|h1.b|visa|green\s*card|permanent\s+resident|non.citizen|citizen|immigration|ead|opt|work\s+(?:permit|authorization)|alien)",
    r"(?:non.permanent|lawful\s+(?:resident|presence)|eligible\s+non.citizen|ineligible\s+non.citizen)",

    # Foreign language / translation / international documents
    r"(?:foreign|translat|another\s+language|different\s+language|not\s+(?:in\s+)?english|indian|chinese|spanish|korean|hindi|language)",
    r"(?:foreign\s+(?:bank|asset|income|document|statement)|overseas|international\s+(?:bank|asset|income))",

    # Gift funds / gift letter / gift donor
    r"(?:gift\s+from|gift\s+money|gifted\s+(?:fund|money|down\s*payment))",

    # Co-signer / co-borrower / non-occupant
    r"(?:co.sign|cosign|co.borrow|non.occupant|non.occupying|coborrower)",

    # Occupancy change / vacating / converting
    r"(?:vacat|converting|convert\s+(?:to|my)|current\s+(?:home|house|property).*(?:rent|vacat|move|leave))",
    r"(?:moving\s+out|rent\s+(?:out|my)|departing\s+residence|primary\s+to\s+(?:rental|investment))",

    # Retirement / pension / Social Security / asset depletion income
    r"(?:retir|pension|social\s+security|ssa\b|401k|401\(k\)|ira\b|annuity|asset\s+depletion)",
    r"(?:ss\s+(?:income|benefit|disability)|ssdi|ssi\b)",
    r"(?:income\s+(?:transition|change|switch)|switching\s+(?:to|from)\s+(?:retirement|pension|social))",

    # Reverse mortgage
    r"(?:reverse\s+mortgage|hecm|home\s+equity\s+conversion)",

    # Waiting periods / derogatory events (supplements the bankruptcy/foreclosure pattern)
    r"(?:waiting\s+period|seasoning|time\s+since|years?\s+(?:since|after|from)\s+(?:bankruptcy|foreclosure|short\s+sale))",

    # ITIN / SSN / tax ID for non-citizens
    r"(?:itin|individual\s+tax|no\s+ssn|without\s+(?:ssn|social\s+security\s+number))",

    # Investment property / multiple properties
    r"(?:investment\s+property|rental\s+property|multiple\s+(?:propert|financed)|5.10\s+(?:propert|financed))",
    r"(?:\d+\s+(?:financed\s+)?propert|\d+(?:th|st|nd|rd)\s+(?:property|home|rental))",

    # Jumbo / non-conforming / high-balance
    r"(?:jumbo|non.conforming|high.balance)",
]


def classify_query(query: str) -> Dict[str, Any]:
    """
    Classify a natural language mortgage question into a routing decision.

    Returns:
        {
            "route": "RULE_ENGINE" | "RAG" | "HYBRID" | "COMPARISON",
            "rule_type": str or None (e.g., "ltv", "dti", "credit_score"),
            "parameters": dict of extracted parameters,
            "confidence": float (0-1),
            "reasoning": str
        }
    """
    query_lower = query.lower().strip()

    # Extract parameters from the query
    params = extract_parameters(query_lower)

    # Score each route
    rule_score = 0
    rag_score = 0
    matched_rule_type = None

    # Check rule engine patterns
    # Priority: specific rule types always beat generic "scenario"
    # Among specific types, pick the most relevant (by match count)
    SPECIFIC_TYPES = {"ltv", "dti", "credit_score", "mi", "mip",
                      "funding_fee", "reserves", "residual_income",
                      "loan_limit", "eligibility", "comparison"}
    all_matched_types = []
    type_match_count = {}
    for pattern, rule_type in RULE_ENGINE_PATTERNS:
        if re.search(pattern, query_lower):
            rule_score += 2
            all_matched_types.append(rule_type)
            type_match_count[rule_type] = type_match_count.get(rule_type, 0) + 1
            if not matched_rule_type:
                matched_rule_type = rule_type

    # Pick the best specific type (most pattern hits wins, with priority tiebreaker)
    # Priority ensures that explicitly-named types (funding_fee, mip) beat
    # incidental matches (ltv from "10% down") when match counts are equal.
    TYPE_PRIORITY = {
        "funding_fee": 10, "mip": 10, "mi": 9, "residual_income": 9,
        "reserves": 8, "loan_limit": 8, "credit_score": 7, "dti": 7,
        "ltv": 5, "eligibility": 3, "comparison": 3,
    }
    if all_matched_types:
        specific_matches = {t: c for t, c in type_match_count.items() if t in SPECIFIC_TYPES}
        if specific_matches:
            # Pick by (match_count, priority) — higher priority wins on ties
            matched_rule_type = max(
                specific_matches,
                key=lambda t: (specific_matches[t], TYPE_PRIORITY.get(t, 0))
            )
        elif "scenario" in all_matched_types:
            matched_rule_type = "scenario"

    # Check RAG patterns
    for pattern in RAG_PATTERNS:
        if re.search(pattern, query_lower):
            rag_score += 2

    # Boost rule score if specific numbers are present
    if params.get("credit_score") or params.get("ltv") or params.get("loan_amount"):
        rule_score += 1

    # Boost comparison ONLY if explicit comparison intent
    agencies_mentioned = _count_agencies_mentioned(query_lower)
    has_comparison_intent = any(re.search(p, query_lower) for p in [
        r"(?:compare|comparison|versus|vs\.?|which\s+(?:is|agency|program))",
        r"(?:differ|better|worse|cheaper)",
    ])
    if (agencies_mentioned >= 2 and has_comparison_intent) or matched_rule_type == "comparison":
        matched_rule_type = "comparison"
        rule_score += 2

    # Determine route
    #
    # IMPORTANT: Complex multi-topic questions (visa + gift + co-signer + etc.)
    # that only match generic "scenario" patterns should NOT dump raw rule engine
    # output. When RAG dominates and the only rule matches are scenario-level,
    # route to RAG so the LLM can synthesize a proper answer.
    #
    only_scenario_rules = (
        matched_rule_type == "scenario" and
        not any(t in SPECIFIC_TYPES for t in all_matched_types)
    )

    if matched_rule_type == "comparison":
        route = ROUTE_COMPARISON
        confidence = min(0.95, 0.6 + rule_score * 0.1)
        reasoning = "Multiple agencies or comparison keywords detected"
    elif rag_score >= 8 and only_scenario_rules:
        # Complex multi-topic question — let the LLM handle it entirely
        # Rule engine would only dump generic numbers that don't help
        route = ROUTE_RAG
        confidence = min(0.95, 0.6 + rag_score * 0.1)
        reasoning = "Complex multi-topic question requiring guideline synthesis (visa, gift, co-signer, etc.)"
    elif rule_score > 0 and rag_score > 0 and only_scenario_rules and rag_score > rule_score:
        # RAG-dominant hybrid where rule engine is only scenario-level
        # Still route hybrid but flag that rule output should be contextual, not primary
        route = ROUTE_HYBRID
        confidence = min(0.9, 0.5 + (rule_score + rag_score) * 0.05)
        reasoning = "Hybrid with RAG-dominant: scenario context + guideline explanations"
    elif rule_score > 0 and rag_score > 0:
        route = ROUTE_HYBRID
        confidence = min(0.9, 0.5 + (rule_score + rag_score) * 0.05)
        reasoning = "Question has both deterministic and explanatory components"
    elif rule_score > rag_score:
        route = ROUTE_RULE_ENGINE
        confidence = min(0.95, 0.6 + rule_score * 0.1)
        reasoning = f"Deterministic lookup detected: {matched_rule_type}"
    elif rag_score > rule_score:
        route = ROUTE_RAG
        confidence = min(0.95, 0.6 + rag_score * 0.1)
        reasoning = "Contextual/explanatory question requiring guideline passages"
    else:
        # Default to hybrid for safety
        route = ROUTE_HYBRID
        confidence = 0.4
        reasoning = "Ambiguous query — using hybrid for best coverage"

    # ─── COMPLEXITY DETECTION ────────────────────────────────────────────
    # Complex multi-topic questions (6+ topics) often match many specific
    # rule types (credit_score, ltv, dti, comparison, etc.) and get routed
    # to RULE_ENGINE or COMPARISON. But the rule engine can only output
    # deterministic lookups — it can't explain visa eligibility, waiting
    # periods, income calculation rules, etc. Force RAG supplementation
    # for these complex questions so the LLM can synthesize a full answer.
    #
    # Criteria for "complex question needing RAG":
    #   - 3+ distinct rule types matched (multi-faceted), OR
    #   - 4+ total rule pattern matches AND rag_score >= 2 (many topics)
    #   - AND the route would otherwise skip RAG (RULE_ENGINE or COMPARISON)
    # ─────────────────────────────────────────────────────────────────────
    distinct_rule_types = len(set(all_matched_types))
    is_complex = (
        (distinct_rule_types >= 3) or
        (len(all_matched_types) >= 4 and rag_score >= 2) or
        (rag_score >= 4 and rule_score > 0)
    )
    force_rag = is_complex and route in (ROUTE_RULE_ENGINE, ROUTE_COMPARISON)

    return {
        "route": route,
        "rule_type": matched_rule_type,
        "parameters": params,
        "confidence": confidence,
        "reasoning": reasoning,
        "force_rag": force_rag,
        "complexity": {
            "distinct_rule_types": distinct_rule_types,
            "total_rule_matches": len(all_matched_types),
            "rag_score": rag_score,
            "rule_score": rule_score,
            "is_complex": is_complex,
        },
    }


def extract_parameters(query: str) -> Dict[str, Any]:
    """
    Extract structured loan parameters from natural language.
    This is the NLU (Natural Language Understanding) layer.
    """
    params = {}
    q = query.lower()

    # === Agency ===
    # Use word-boundary matching to avoid false positives like "vacate" → "va"
    for alias, canonical in AGENCY_ALIASES.items():
        # Build regex with word boundaries; escape the alias for safety
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, q):
            params["agency"] = canonical
            break

    # === Transaction Type ===
    if any(w in q for w in ["purchase", "buying", "buy a home", "buy a house"]):
        params["transaction_type"] = "purchase"
    elif any(w in q for w in ["cash out", "cash-out", "cashout"]):
        params["transaction_type"] = "cash_out_refi"
    elif any(w in q for w in ["rate and term", "rate/term", "rate term", "limited cash-out", "lcor"]):
        params["transaction_type"] = "rate_term_refi"
    elif any(w in q for w in ["streamline", "fha streamline"]):
        params["transaction_type"] = "streamline_refi"
    elif any(w in q for w in ["irrrl", "va irrrl", "interest rate reduction"]):
        params["transaction_type"] = "irrrl"
    elif "refi" in q or "refinance" in q:
        params["transaction_type"] = "rate_term_refi"

    # === Occupancy ===
    if any(w in q for w in ["primary", "owner occupied", "owner-occupied", "principal residence"]):
        params["occupancy"] = "primary"
    elif any(w in q for w in ["second home", "vacation home", "secondary"]):
        params["occupancy"] = "second_home"
    elif any(w in q for w in ["investment", "rental", "non-owner", "noo"]):
        params["occupancy"] = "investment"

    # === Units ===
    unit_match = re.search(r"(\d)\s*[-‐]?\s*(?:unit|family|plex)", q)
    if unit_match:
        params["units"] = unit_match.group(1)
    elif "single family" in q or "sfr" in q:
        params["units"] = "1"
    elif "duplex" in q:
        params["units"] = "2"
    elif "triplex" in q:
        params["units"] = "3"
    elif "fourplex" in q or "quadplex" in q:
        params["units"] = "4"
    elif "condo" in q:
        params["units"] = "condo"
    elif "manufactured" in q or "mobile home" in q:
        params["units"] = "manufactured"

    # === Rate Type ===
    if "arm" in q or "adjustable" in q:
        params["rate_type"] = "arm"
    elif "fixed" in q:
        params["rate_type"] = "fixed"

    # === Credit Score ===
    score_match = re.search(r"(?:credit\s*(?:score)?|fico|score)[\s:=]*(\d{3})", q)
    if not score_match:
        score_match = re.search(r"(\d{3})\s*(?:credit|fico|score)", q)
    if not score_match:
        # Standalone 3-digit number that looks like a credit score (500-850)
        for m in re.finditer(r"\b(\d{3})\b", q):
            val = int(m.group(1))
            if 500 <= val <= 850:
                score_match = m
                break
    if score_match:
        score = int(score_match.group(1))
        if 300 <= score <= 900:
            params["credit_score"] = score

    # === LTV ===
    ltv_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%?\s*(?:ltv|loan.to.value|cltv)", q)
    if not ltv_match:
        ltv_match = re.search(r"(?:ltv|loan.to.value)\s*(?:of|is|at|=)?\s*(\d{1,3}(?:\.\d+)?)\s*%?", q)
    if ltv_match:
        params["ltv"] = float(ltv_match.group(1))

    # === Down Payment ===
    dp_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%?\s*(?:down|down\s*payment)", q)
    if not dp_match:
        dp_match = re.search(r"(?:down|down\s*payment)\s*(?:of|is|at|=)?\s*(\d{1,3}(?:\.\d+)?)\s*%?", q)
    if dp_match:
        dp_pct = float(dp_match.group(1))
        params["down_payment_pct"] = dp_pct
        if "ltv" not in params:
            params["ltv"] = round(100 - dp_pct, 2)

    # === DTI ===
    dti_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%?\s*(?:dti|debt.to.income)", q)
    if not dti_match:
        dti_match = re.search(r"(?:dti|debt.to.income)\s*(?:of|is|at|=)?\s*(\d{1,3}(?:\.\d+)?)\s*%?", q)
    if dti_match:
        params["dti"] = float(dti_match.group(1))

    # === Loan Amount ===
    loan_match = re.search(r"\$\s*([\d,]+(?:\.\d+)?)\s*(k|K|thousand)?", q)
    if loan_match:
        amount_str = loan_match.group(1).replace(",", "")
        amount = float(amount_str)
        suffix = loan_match.group(2)
        if suffix and suffix.lower() in ("k", "thousand"):
            amount *= 1000
        # If amount seems too small to be a loan (< 1000), it's probably in thousands
        if amount < 1000 and amount > 0:
            amount *= 1000
        params["loan_amount"] = amount
    else:
        loan_match = re.search(r"(\d[\d,]+(?:\.\d+)?)\s*(k|K)?\s*(?:loan|mortgage|amount)", q)
        if loan_match:
            amount = float(loan_match.group(1).replace(",", ""))
            if loan_match.group(2) and loan_match.group(2).lower() == "k":
                amount *= 1000
            if amount < 1000:
                amount *= 1000
            params["loan_amount"] = amount

    # === Loan Term ===
    term_match = re.search(r"(\d{2})\s*(?:year|yr)", q)
    if term_match:
        params["loan_term_years"] = int(term_match.group(1))

    # === VA Specific ===
    if "first time" in q or "first use" in q:
        params["va_first_use"] = True
    elif "subsequent" in q or "second use" in q:
        params["va_first_use"] = False

    if any(w in q for w in ["disability", "disabled", "exempt", "purple heart"]):
        params["va_disability_exempt"] = True

    # === Underwriting Method ===
    if any(w in q for w in ["manual", "manually underwritten"]):
        params["underwriting_method"] = "manual"
    elif any(w in q for w in ["du", "lpa", "automated", "aus", "total scorecard"]):
        params["underwriting_method"] = "automated"

    # === Compensating Factors ===
    if "compensating" in q:
        params["has_compensating_factors"] = True

    # === State (for VA residual income) ===
    state_match = re.search(r"\b([A-Z]{2})\b", query)  # Use original case
    if state_match:
        st = state_match.group(1)
        valid_states = {"AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA",
                       "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA",
                       "MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY",
                       "NC","ND","OH","OK","OR","PA","PR","RI","SC","SD","TN",
                       "TX","UT","VT","VA","VI","WA","WV","WI","WY"}
        if st in valid_states:
            params["state"] = st

    return params


def _count_agencies_mentioned(query: str) -> int:
    """Count how many distinct agencies are mentioned in the query."""
    found = set()
    for alias, canonical in AGENCY_ALIASES.items():
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, query):
            found.add(canonical)
    return len(found)


# =============================================================================
# ROUTE-AND-ANSWER: THE MAIN ENTRY POINT
# =============================================================================

def route_and_answer(query: str, rag_function=None) -> Dict[str, Any]:
    """
    Main entry point: classify a question, route it, and return the answer.

    Args:
        query: Natural language mortgage question
        rag_function: Optional callback to the RAG pipeline (for hybrid mode)
                      Signature: rag_function(query: str) -> str

    Returns:
        {
            "route": str,
            "classification": dict,
            "rule_engine_answer": str or None,
            "rag_answer": str or None,
            "combined_answer": str,
            "citations": list,
            "parameters_extracted": dict,
        }
    """
    # Step 1: Classify
    classification = classify_query(query)
    route = classification["route"]
    params = classification["parameters"]
    rule_type = classification["rule_type"]

    result = {
        "route": route,
        "classification": classification,
        "rule_engine_answer": None,
        "rag_answer": None,
        "combined_answer": "",
        "citations": [],
        "parameters_extracted": params,
    }

    # Step 2: Execute based on route
    if route == ROUTE_RULE_ENGINE:
        answer, citations = _execute_rule_engine(rule_type, params, query)
        result["rule_engine_answer"] = answer
        result["citations"] = citations
        result["combined_answer"] = answer

    elif route == ROUTE_RAG:
        if rag_function:
            rag_answer = rag_function(query)
            result["rag_answer"] = rag_answer
            result["combined_answer"] = rag_answer
        else:
            result["combined_answer"] = "[RAG pipeline not connected — would search guidelines for this answer]"

    elif route == ROUTE_COMPARISON:
        answer, citations = _execute_comparison(params, query)
        result["rule_engine_answer"] = answer
        result["citations"] = citations
        result["combined_answer"] = answer

    elif route == ROUTE_HYBRID:
        # Rule engine first, then RAG for context
        answer, citations = _execute_rule_engine(rule_type, params, query)
        result["rule_engine_answer"] = answer
        result["citations"] = citations

        if rag_function:
            rag_answer = rag_function(query)
            result["rag_answer"] = rag_answer
            # Merge: deterministic facts first, then RAG explanation
            result["combined_answer"] = (
                f"📊 DETERMINISTIC ANSWER:\n{answer}\n\n"
                f"📖 ADDITIONAL CONTEXT:\n{rag_answer}"
            )
        else:
            result["combined_answer"] = answer

    return result


def _execute_rule_engine(rule_type: str, params: dict, query: str) -> Tuple[str, List[str]]:
    """Execute the appropriate rule engine lookup and return (answer, citations)."""
    citations = []

    # Build a scenario from extracted params
    scenario_kwargs = {}
    param_mapping = {
        "agency": "agency",
        "transaction_type": "transaction_type",
        "occupancy": "occupancy",
        "units": "units",
        "rate_type": "rate_type",
        "credit_score": "credit_score",
        "ltv": "ltv",
        "dti": "dti",
        "loan_amount": "loan_amount",
        "down_payment_pct": "down_payment_pct",
        "loan_term_years": "loan_term_years",
        "va_first_use": "va_first_use",
        "va_disability_exempt": "va_disability_exempt",
        "underwriting_method": "underwriting_method",
        "has_compensating_factors": "has_compensating_factors",
        "state": "state",
    }
    for param_key, scenario_key in param_mapping.items():
        if param_key in params:
            scenario_kwargs[scenario_key] = params[param_key]

    # Route to specific lookup based on rule_type
    if rule_type == "ltv":
        agency = params.get("agency")
        if agency:
            r = lookup_ltv(
                agency,
                params.get("transaction_type", "purchase"),
                params.get("occupancy", "primary"),
                params.get("units", "1"),
                params.get("rate_type", "fixed"),
                params.get("credit_score"),
            )
            citations.append(r.citation)
            return str(r), citations
        else:
            # All agencies
            scenario = LoanScenario(**scenario_kwargs)
            result = evaluate_scenario(scenario)
            return result.to_text(), [r.citation for results in result.results.values() for r in results if r.citation]

    elif rule_type == "dti":
        agency = params.get("agency")
        if agency:
            r = lookup_dti(agency, params.get("underwriting_method", "automated"),
                          params.get("has_compensating_factors", False))
            citations.append(r.citation)
            return str(r), citations
        else:
            lines = []
            for ag in ["Fannie Mae", "Freddie Mac", "FHA", "VA"]:
                r = lookup_dti(ag, params.get("underwriting_method", "automated"))
                lines.append(str(r))
                citations.append(r.citation)
            return "\n".join(lines), citations

    elif rule_type == "credit_score":
        score = params.get("credit_score")
        agency = params.get("agency")
        if agency:
            r = lookup_credit_score(agency, score)
            citations.append(r.citation)
            return str(r), citations
        else:
            lines = []
            for ag in ["Fannie Mae", "Freddie Mac", "FHA", "VA"]:
                r = lookup_credit_score(ag, score)
                lines.append(str(r))
                citations.append(r.citation)
            return "\n".join(lines), citations

    elif rule_type == "mi":
        ltv = params.get("ltv", 95)
        agency = params.get("agency", "Fannie Mae")
        r = lookup_mi(agency, ltv, params.get("loan_term_years", 30),
                     params.get("rate_type", "fixed"))
        citations.append(r.citation)
        return str(r), citations

    elif rule_type == "mip":
        ltv = params.get("ltv", 96.5)
        loan = params.get("loan_amount", 300000)
        term = params.get("loan_term_years", 30)
        r = lookup_mip(ltv, loan, term)
        citations.append(r.citation)
        return str(r), citations

    elif rule_type == "funding_fee":
        dp = params.get("down_payment_pct", 0)
        first = params.get("va_first_use", True)
        exempt = params.get("va_disability_exempt", False)
        loan = params.get("loan_amount")
        tx = params.get("transaction_type", "purchase")
        r = lookup_funding_fee(dp, first, tx, exempt, loan)
        citations.append(r.citation)
        return str(r), citations

    elif rule_type == "loan_limit":
        agency = params.get("agency")
        units = params.get("units", "1")
        if agency:
            r = lookup_loan_limits(agency, units)
            citations.append(r.citation)
            return str(r), citations
        else:
            lines = []
            for ag in ["Fannie Mae", "Freddie Mac", "FHA", "VA"]:
                r = lookup_loan_limits(ag, units)
                lines.append(str(r))
                citations.append(r.citation)
            return "\n".join(lines), citations

    elif rule_type == "reserves":
        agency = params.get("agency")
        occ = params.get("occupancy", "primary")
        units = params.get("units", "1")
        if agency:
            r = lookup_reserves(agency, occ, units)
            return str(r), [r.citation]
        else:
            lines = []
            for ag in ["Fannie Mae", "Freddie Mac"]:
                r = lookup_reserves(ag, occ, units)
                lines.append(str(r))
            return "\n".join(lines), []

    elif rule_type == "residual_income":
        state = params.get("state", "TX")
        family = params.get("family_size", 1)
        loan = params.get("loan_amount", 300000)
        r = lookup_va_residual_income(state, family, loan)
        return str(r), [r.citation]

    elif rule_type in ("eligibility", "scenario"):
        scenario = LoanScenario(**scenario_kwargs)
        result = evaluate_scenario(scenario)
        return result.to_text(), [r.citation for results in result.results.values() for r in results if r.citation]

    # Fallback: full scenario evaluation
    scenario = LoanScenario(**scenario_kwargs)
    result = evaluate_scenario(scenario)
    return result.to_text(), [r.citation for results in result.results.values() for r in results if r.citation]


def _execute_comparison(params: dict, query: str) -> Tuple[str, List[str]]:
    """Execute a cross-agency comparison."""
    scenario_kwargs = {}
    for key in ["transaction_type", "occupancy", "units", "rate_type", "credit_score",
                "ltv", "dti", "loan_amount", "down_payment_pct", "loan_term_years",
                "va_first_use", "state"]:
        if key in params:
            scenario_kwargs[key] = params[key]

    scenario = LoanScenario(**scenario_kwargs)
    text = compare_agencies_text(scenario)
    return text, []


# =============================================================================
# LLM-ENHANCED CLASSIFIER (optional upgrade)
# =============================================================================

def build_classification_prompt(query: str) -> str:
    """
    Build a prompt for an LLM to classify the query.
    Use this when the keyword classifier confidence is low.
    Falls back to LLM only when needed to minimize latency.
    """
    return f"""You are a mortgage query classifier. Classify this question into exactly ONE category:

RULE_ENGINE: Questions with a definite, numerical answer from mortgage guidelines.
  Examples: "What's the max LTV for FHA purchase?", "VA funding fee with 5% down?",
  "Min credit score for Fannie Mae?", "FHA MIP for 96.5% LTV $300K loan?"

RAG: Questions needing explanation, context, process, or policy interpretation.
  Examples: "Explain FHA streamline refi requirements", "What documents do I need?",
  "How does VA residual income work?", "What happens after a foreclosure?"

COMPARISON: Questions comparing two or more agencies/programs.
  Examples: "FHA vs VA for a first-time buyer?", "Which is better, Fannie or Freddie?"

HYBRID: Questions that need both a numerical answer AND explanation.
  Examples: "What's the max DTI for FHA and why is it so high?",
  "Can I qualify with 580 score? What are my options?"

Question: "{query}"

Respond with ONLY a JSON object:
{{"route": "RULE_ENGINE|RAG|COMPARISON|HYBRID", "rule_type": "ltv|dti|credit_score|mi|mip|funding_fee|loan_limit|reserves|eligibility|null", "reasoning": "brief explanation"}}"""


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("SMART ROUTER — TEST SUITE")
    print("=" * 70)

    test_queries = [
        # Rule engine queries
        "What's the maximum LTV for a Fannie Mae purchase on a primary residence?",
        "FHA minimum credit score?",
        "VA funding fee with 5% down, first time use, $400K loan",
        "Max DTI for FHA with automated underwriting?",
        "What is the FHA MIP on a $350,000 loan at 96.5% LTV?",
        "What are the conforming loan limits?",
        "Do I need reserves for an investment property with Freddie Mac?",

        # Comparison queries
        "FHA vs VA for a purchase with 680 credit score",
        "Compare Fannie Mae and Freddie Mac LTV for a 2-unit primary",

        # RAG queries
        "Explain the FHA streamline refinance process",
        "What documents do I need for a VA loan?",
        "How does the VA residual income test work?",
        "What are the compensating factors for manual underwriting?",

        # Hybrid queries
        "What's the max LTV for FHA and what are the requirements?",
        "Can I qualify for a VA loan with a 580 credit score? What are my options?",

        # Complex scenario
        "I have a 720 credit score, looking to purchase a primary 1-unit with 5% down on FHA. What's my MIP?",
    ]

    for q in test_queries:
        classification = classify_query(q)
        print(f"\n{'─' * 60}")
        print(f"Q: {q}")
        print(f"  Route: {classification['route']} (confidence: {classification['confidence']:.0%})")
        print(f"  Type: {classification['rule_type']}")
        print(f"  Params: {json.dumps(classification['parameters'], indent=2) if classification['parameters'] else 'none'}")
        print(f"  Reason: {classification['reasoning']}")

    # Test full route-and-answer
    print("\n\n" + "=" * 70)
    print("FULL ROUTE-AND-ANSWER TESTS")
    print("=" * 70)

    test_full = [
        "What's the maximum LTV for FHA purchase with a 720 credit score?",
        "VA funding fee with 0% down, first use, $400,000 loan",
        "Compare all agencies for a purchase, primary residence, 1-unit, 720 credit, 95% LTV, $350K loan",
        "What's the max DTI for all agencies?",
    ]

    for q in test_full:
        print(f"\n{'━' * 60}")
        print(f"Q: {q}")
        result = route_and_answer(q)
        print(f"Route: {result['route']}")
        print(f"Answer:\n{result['combined_answer'][:500]}")
