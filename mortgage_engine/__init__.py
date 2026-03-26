"""
Mortgage Hybrid Engine
======================
Deterministic rule engine + RAG hybrid system for mortgage underwriting.

Usage:
    from mortgage_engine import hybrid_pipeline, classify_query, LoanScenario

    # Full hybrid pipeline (drop-in replacement for full_rag_pipeline)
    answer, chunks, query, metadata = hybrid_pipeline(question, rag_fn)

    # Direct rule engine query
    from mortgage_engine.rule_engine import lookup_ltv, compare_agencies
    result = lookup_ltv("fannie", "purchase", "primary", "1")

    # Smart routing
    from mortgage_engine.router import classify_query, route_and_answer
    classification = classify_query("What's the max LTV for FHA?")
"""

from .hybrid_integration import (
    hybrid_pipeline,
    hybrid_stream_preprocess,
    inject_rule_context_into_rag,
    build_rule_engine_context_block,
    format_rule_answer_for_voice,
    format_rule_answer_for_web,
    get_hybrid_system_prompt_addition,
    build_hybrid_metadata_event,
)
from .router import classify_query, route_and_answer, extract_parameters
from .rule_engine import (
    LoanScenario,
    evaluate_scenario,
    compare_agencies,
    lookup_ltv,
    lookup_dti,
    lookup_credit_score,
    lookup_mi,
    lookup_mip,
    lookup_funding_fee,
    lookup_reserves,
    lookup_loan_limits,
    lookup_va_residual_income,
)
from .rules_database import ALL_AGENCIES, AGENCY_ALIASES, resolve_agency

__version__ = "1.0.0"
__all__ = [
    "hybrid_pipeline",
    "hybrid_stream_preprocess",
    "classify_query",
    "route_and_answer",
    "LoanScenario",
    "evaluate_scenario",
    "compare_agencies",
    "lookup_ltv",
    "lookup_dti",
    "lookup_credit_score",
    "lookup_mi",
    "lookup_mip",
    "lookup_funding_fee",
    "ALL_AGENCIES",
]
