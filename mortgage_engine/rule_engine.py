"""
MORTGAGE RULE ENGINE — CORE EVALUATION LAYER
=============================================
The world-class deterministic query engine for mortgage underwriting.
Takes a loan scenario and returns precise, cited answers in milliseconds.

Capabilities:
- evaluate_scenario(): Full scenario evaluation across all applicable rules
- lookup_ltv(): LTV/CLTV limits for any agency/transaction/occupancy/unit combo
- lookup_dti(): DTI limits by agency and underwriting method
- lookup_credit_score(): Credit score requirements and eligibility
- lookup_mi(): Conventional MI coverage requirements
- lookup_mip(): FHA MIP (upfront + annual) calculator
- lookup_funding_fee(): VA funding fee calculator
- compare_agencies(): Side-by-side comparison of all agencies for a scenario
- check_eligibility(): Binary yes/no eligibility check with explanation
- calculate_costs(): Total insurance/fee cost calculation for a loan amount
"""

from rules_database import (
    ALL_AGENCIES, AGENCY_ALIASES, resolve_agency,
    FANNIE_MAE, FREDDIE_MAC, FHA, VA
)
from typing import Optional, Dict, List, Any, Tuple
import json


# =============================================================================
# INPUT NORMALIZATION
# =============================================================================

def normalize_transaction_type(raw: str) -> str:
    """Normalize transaction type to canonical form."""
    raw = raw.lower().strip().replace("-", "_").replace(" ", "_")
    aliases = {
        "purchase": "purchase",
        "buy": "purchase",
        "buying": "purchase",
        "rate_term": "rate_term_refi",
        "rate_term_refi": "rate_term_refi",
        "rate_term_refinance": "rate_term_refi",
        "rate_and_term": "rate_term_refi",
        "rt_refi": "rate_term_refi",
        "limited_cash_out": "rate_term_refi",
        "lcor": "rate_term_refi",
        "cash_out": "cash_out_refi",
        "cash_out_refi": "cash_out_refi",
        "cash_out_refinance": "cash_out_refi",
        "cashout": "cash_out_refi",
        "streamline": "streamline_refi",
        "streamline_refi": "streamline_refi",
        "fha_streamline": "streamline_refi",
        "irrrl": "irrrl",
        "va_irrrl": "irrrl",
        "interest_rate_reduction": "irrrl",
    }
    return aliases.get(raw, raw)


def normalize_occupancy(raw: str) -> str:
    """Normalize occupancy type."""
    raw = raw.lower().strip().replace("-", "_").replace(" ", "_")
    aliases = {
        "primary": "primary",
        "primary_residence": "primary",
        "owner_occupied": "primary",
        "principal": "primary",
        "second_home": "second_home",
        "secondary": "second_home",
        "vacation": "second_home",
        "investment": "investment",
        "rental": "investment",
        "non_owner": "investment",
        "noo": "investment",
    }
    return aliases.get(raw, raw)


def normalize_units(raw) -> str:
    """Normalize unit count to canonical key."""
    raw = str(raw).lower().strip().replace("-", "_").replace(" ", "_")
    aliases = {
        "1": "1_unit", "1_unit": "1_unit", "single_family": "1_unit", "sfr": "1_unit",
        "2": "2_unit", "2_unit": "2_unit", "duplex": "2_unit",
        "3": "3_4_unit", "3_unit": "3_4_unit", "triplex": "3_4_unit",
        "4": "3_4_unit", "4_unit": "3_4_unit", "fourplex": "3_4_unit", "quadplex": "3_4_unit",
        "3_4_unit": "3_4_unit", "3_4": "3_4_unit",
        "condo": "condo", "condominium": "condo",
        "manufactured": "manufactured", "mobile_home": "manufactured",
        "1_4_unit": "1_4_unit", "all": "all",
    }
    return aliases.get(raw, raw)


def normalize_rate_type(raw: str) -> str:
    """Normalize rate type."""
    raw = raw.lower().strip().replace("-", "_").replace(" ", "_")
    if raw in ("fixed", "fixed_rate", "30yr_fixed", "15yr_fixed", "20yr_fixed"):
        return "fixed"
    if raw in ("arm", "adjustable", "adjustable_rate", "variable"):
        return "arm"
    return raw


# =============================================================================
# SCENARIO DATA CLASS
# =============================================================================

class LoanScenario:
    """
    A complete loan scenario for evaluation.
    All fields are optional — the engine evaluates whatever is provided.
    """
    def __init__(
        self,
        agency: Optional[str] = None,
        transaction_type: str = "purchase",
        occupancy: str = "primary",
        units: str = "1",
        rate_type: str = "fixed",
        credit_score: Optional[int] = None,
        ltv: Optional[float] = None,
        cltv: Optional[float] = None,
        dti: Optional[float] = None,
        loan_amount: Optional[float] = None,
        property_value: Optional[float] = None,
        down_payment_pct: Optional[float] = None,
        loan_term_years: int = 30,
        # VA-specific
        va_first_use: bool = True,
        va_disability_exempt: bool = False,
        family_size: int = 1,
        state: Optional[str] = None,
        # FHA-specific
        non_occupant_coborrower: bool = False,
        coborrower_is_family: bool = True,
        # Underwriting method
        underwriting_method: str = "automated",  # "automated" | "manual"
        has_compensating_factors: bool = False,
    ):
        self.agency = resolve_agency(agency) if agency else None
        self.transaction_type = normalize_transaction_type(transaction_type)
        self.occupancy = normalize_occupancy(occupancy)
        self.units = normalize_units(units)
        self.rate_type = normalize_rate_type(rate_type)
        self.credit_score = credit_score
        self.ltv = ltv
        self.cltv = cltv or ltv
        self.dti = dti
        self.loan_amount = loan_amount
        self.property_value = property_value
        self.down_payment_pct = down_payment_pct
        self.loan_term_years = loan_term_years
        self.va_first_use = va_first_use
        self.va_disability_exempt = va_disability_exempt
        self.family_size = family_size
        self.state = state.upper() if state else None
        self.non_occupant_coborrower = non_occupant_coborrower
        self.coborrower_is_family = coborrower_is_family
        self.underwriting_method = underwriting_method.lower()
        self.has_compensating_factors = has_compensating_factors

        # Input validation
        if self.credit_score is not None and (self.credit_score < 0 or self.credit_score > 900):
            self.credit_score = None  # Ignore invalid scores
        if self.ltv is not None and self.ltv < 0:
            self.ltv = None
        if self.dti is not None and self.dti < 0:
            self.dti = None
        if self.loan_amount is not None and self.loan_amount < 0:
            self.loan_amount = None
        if self.property_value is not None and self.property_value < 0:
            self.property_value = None

        # Auto-calculate missing fields
        if self.property_value and self.loan_amount and not self.ltv:
            self.ltv = round((self.loan_amount / self.property_value) * 100, 2)
        if self.ltv and not self.down_payment_pct:
            self.down_payment_pct = round(100 - self.ltv, 2)
        if self.down_payment_pct and not self.ltv:
            self.ltv = round(100 - self.down_payment_pct, 2)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


# =============================================================================
# RESULT DATA CLASS
# =============================================================================

class RuleResult:
    """A single rule evaluation result with citation."""
    def __init__(self, rule_name: str, value: Any, citation: str = "",
                 notes: str = "", eligible: bool = True, agency: str = ""):
        self.rule_name = rule_name
        self.value = value
        self.citation = citation
        self.notes = notes
        self.eligible = eligible
        self.agency = agency

    def to_dict(self) -> dict:
        return {
            "rule": self.rule_name,
            "value": self.value,
            "citation": self.citation,
            "notes": self.notes,
            "eligible": self.eligible,
            "agency": self.agency,
        }

    def __repr__(self):
        status = "✓" if self.eligible else "✗"
        return f"[{status}] {self.agency} | {self.rule_name}: {self.value} ({self.citation})"


class ScenarioResult:
    """Complete evaluation result for a scenario against one or more agencies."""
    def __init__(self, scenario: LoanScenario):
        self.scenario = scenario
        self.results: Dict[str, List[RuleResult]] = {}  # agency -> [results]
        self.eligible_agencies: List[str] = []
        self.ineligible_agencies: Dict[str, str] = {}  # agency -> reason
        self.warnings: List[str] = []

    def add_result(self, agency: str, result: RuleResult):
        if agency not in self.results:
            self.results[agency] = []
        self.results[agency].append(result)

    def mark_eligible(self, agency: str):
        if agency not in self.eligible_agencies:
            self.eligible_agencies.append(agency)

    def mark_ineligible(self, agency: str, reason: str):
        self.ineligible_agencies[agency] = reason

    def to_dict(self) -> dict:
        return {
            "scenario": self.scenario.to_dict(),
            "eligible_agencies": self.eligible_agencies,
            "ineligible_agencies": self.ineligible_agencies,
            "results": {
                agency: [r.to_dict() for r in results]
                for agency, results in self.results.items()
            },
            "warnings": self.warnings,
        }

    def to_text(self) -> str:
        """Human-readable summary."""
        lines = []
        lines.append("=" * 70)
        lines.append("MORTGAGE SCENARIO EVALUATION")
        lines.append("=" * 70)
        s = self.scenario
        lines.append(f"Transaction: {s.transaction_type.replace('_', ' ').title()}")
        lines.append(f"Occupancy: {s.occupancy.replace('_', ' ').title()}")
        lines.append(f"Units: {s.units}")
        lines.append(f"Rate Type: {s.rate_type.title()}")
        if s.credit_score: lines.append(f"Credit Score: {s.credit_score}")
        if s.ltv: lines.append(f"LTV: {s.ltv}%")
        if s.dti: lines.append(f"DTI: {s.dti}%")
        if s.loan_amount: lines.append(f"Loan Amount: ${s.loan_amount:,.0f}")

        if self.eligible_agencies:
            lines.append(f"\n✓ ELIGIBLE: {', '.join(self.eligible_agencies)}")
        if self.ineligible_agencies:
            for ag, reason in self.ineligible_agencies.items():
                lines.append(f"✗ INELIGIBLE for {ag}: {reason}")

        for agency, results in self.results.items():
            lines.append(f"\n--- {agency} ---")
            for r in results:
                lines.append(f"  {r}")

        if self.warnings:
            lines.append("\n⚠ WARNINGS:")
            for w in self.warnings:
                lines.append(f"  - {w}")

        return "\n".join(lines)


# =============================================================================
# CORE LOOKUP FUNCTIONS
# =============================================================================

def lookup_ltv(agency_name: str, transaction_type: str, occupancy: str,
               units: str, rate_type: str = "fixed",
               credit_score: Optional[int] = None,
               non_occupant_coborrower: bool = False,
               coborrower_is_family: bool = True) -> RuleResult:
    """
    Look up the maximum LTV/CLTV for a specific agency and scenario.
    Returns a RuleResult with the max LTV, citation, and eligibility.
    """
    agency_key = resolve_agency(agency_name)
    if not agency_key or agency_key not in ALL_AGENCIES:
        return RuleResult("max_ltv", None, notes=f"Unknown agency: {agency_name}", eligible=False, agency=str(agency_name))

    agency = ALL_AGENCIES[agency_key]
    tx = normalize_transaction_type(transaction_type)
    occ = normalize_occupancy(occupancy)
    unit = normalize_units(units)
    rt = normalize_rate_type(rate_type)

    matrix = agency.get("ltv_matrix", {})

    # Navigate: transaction -> occupancy -> units
    tx_data = matrix.get(tx)
    if not tx_data:
        return RuleResult("max_ltv", None, agency=agency_key,
                          notes=f"{agency_key} does not offer {tx.replace('_', ' ')} transactions",
                          eligible=False)

    # Handle FHA non-occupant co-borrower
    if agency_key == "FHA" and non_occupant_coborrower and tx == "purchase":
        occ_key = "primary_non_occupant_coborrower"
        occ_data = tx_data.get(occ_key, {})
        if occ_data:
            unit_data = _find_unit_data(occ_data, unit)
            if unit_data:
                if coborrower_is_family and "family_member" in unit_data:
                    entry = unit_data["family_member"]
                else:
                    entry = unit_data.get("any", next(iter(unit_data.values())))
                return RuleResult("max_ltv", entry.get("max_ltv"), agency=agency_key,
                                  citation=entry.get("citation", ""),
                                  notes=entry.get("notes", ""),
                                  eligible=True)

    occ_data = tx_data.get(occ)
    if not occ_data:
        # FHA and VA don't allow non-primary
        if occ in ("second_home", "investment"):
            if agency_key == "FHA":
                return RuleResult("max_ltv", 0, agency="FHA",
                                  citation="HUD 4000.1, II.A.1.a",
                                  notes="FHA does not allow second homes or investment properties",
                                  eligible=False)
            if agency_key == "VA":
                return RuleResult("max_ltv", 0, agency="VA",
                                  citation="VA Pamphlet 26-7, Ch. 3",
                                  notes="VA requires owner-occupied primary residence",
                                  eligible=False)
        return RuleResult("max_ltv", None, agency=agency_key,
                          notes=f"{agency_key} {tx} not available for {occ} occupancy",
                          eligible=False)

    # Find unit data
    unit_data = _find_unit_data(occ_data, unit)
    if not unit_data:
        return RuleResult("max_ltv", None, agency=agency_key,
                          notes=f"No LTV data for {unit} in {agency_key} {tx}/{occ}",
                          eligible=False)

    # For FHA, LTV depends on credit score
    if agency_key == "FHA" and tx == "purchase":
        return _lookup_fha_ltv(unit_data, credit_score, agency_key)

    # For conventional/VA, look up by rate type
    if rt in unit_data:
        entry = unit_data[rt]
    elif "standard" in unit_data:
        entry = unit_data["standard"]
    else:
        # Take first available
        entry = next(iter(unit_data.values()))

    max_ltv = entry.get("max_ltv")
    # None means "no cap" (e.g., FHA Streamline, VA IRRRL) — that's eligible
    is_eligible = True if max_ltv is None else (max_ltv > 0)
    return RuleResult("max_ltv", max_ltv, agency=agency_key,
                      citation=entry.get("citation", ""),
                      notes=entry.get("notes", ""),
                      eligible=is_eligible)


def _find_unit_data(occ_data: dict, unit: str) -> Optional[dict]:
    """Find unit data, with fallback for combined keys like 1_4_unit, 2_4_unit, all."""
    if unit in occ_data:
        return occ_data[unit]
    # Try combined keys
    unit_num = unit.split("_")[0] if "_" in unit else unit
    for key in occ_data:
        if key == "all":
            return occ_data[key]
        if "_" in key:
            parts = key.replace("_unit", "").split("_")
            if len(parts) == 2:
                try:
                    lo, hi = int(parts[0]), int(parts[1])
                    if lo <= int(unit_num) <= hi:
                        return occ_data[key]
                except (ValueError, TypeError):
                    pass
            elif len(parts) == 1:
                try:
                    if int(parts[0]) == int(unit_num):
                        return occ_data[key]
                except (ValueError, TypeError):
                    pass
    return None


def _lookup_fha_ltv(unit_data: dict, credit_score: Optional[int], agency_key: str) -> RuleResult:
    """FHA LTV depends on credit score tier."""
    if credit_score is None:
        # Return the best case (580+)
        if "credit_gte_580" in unit_data:
            entry = unit_data["credit_gte_580"]
            return RuleResult("max_ltv", entry["max_ltv"], agency=agency_key,
                              citation=entry.get("citation", ""),
                              notes="Assumes 580+ credit score. " + entry.get("notes", ""),
                              eligible=True)
        entry = next(iter(unit_data.values()))
        return RuleResult("max_ltv", entry.get("max_ltv"), agency=agency_key,
                          citation=entry.get("citation", ""))

    if credit_score >= 580:
        key = "credit_gte_580"
    elif credit_score >= 500:
        key = "credit_500_579"
    else:
        key = "credit_below_500"

    if key in unit_data:
        entry = unit_data[key]
        max_ltv = entry.get("max_ltv", 0)
        return RuleResult("max_ltv", max_ltv, agency=agency_key,
                          citation=entry.get("citation", ""),
                          notes=entry.get("notes", ""),
                          eligible=max_ltv > 0)
    elif key == "credit_below_500":
        return RuleResult("max_ltv", 0, agency=agency_key,
                          citation="HUD 4000.1, II.A.2.a",
                          notes="Credit score below 500 is NOT eligible for FHA",
                          eligible=False)
    else:
        # Fallback
        entry = next(iter(unit_data.values()))
        return RuleResult("max_ltv", entry.get("max_ltv"), agency=agency_key,
                          citation=entry.get("citation", ""))


def lookup_dti(agency_name: str, underwriting_method: str = "automated",
               has_compensating: bool = False) -> RuleResult:
    """Look up DTI limits for a given agency and underwriting method."""
    agency_key = resolve_agency(agency_name)
    if not agency_key or agency_key not in ALL_AGENCIES:
        return RuleResult("max_dti", None, notes=f"Unknown agency: {agency_name}", eligible=False)

    agency = ALL_AGENCIES[agency_key]
    dti_rules = agency.get("dti", {})
    method = underwriting_method.lower()

    if agency_key == "Fannie Mae":
        if method in ("automated", "du", "du_approve"):
            entry = dti_rules.get("du_approve", {})
        elif has_compensating:
            entry = dti_rules.get("manual_with_compensating", {})
        else:
            entry = dti_rules.get("manual_standard", {})
        return RuleResult("max_dti", entry.get("max_dti"), agency=agency_key,
                          citation=entry.get("citation", ""),
                          notes=entry.get("notes", ""))

    elif agency_key == "Freddie Mac":
        if method in ("automated", "lpa", "lpa_accept"):
            entry = dti_rules.get("lpa_accept", {})
        elif has_compensating:
            entry = dti_rules.get("manual_with_compensating", {})
        else:
            entry = dti_rules.get("manual_standard", {})
        return RuleResult("max_dti", entry.get("max_dti"), agency=agency_key,
                          citation=entry.get("citation", ""),
                          notes=entry.get("notes", ""))

    elif agency_key == "FHA":
        if method in ("automated", "total", "total_scorecard"):
            entry = dti_rules.get("total_scorecard_approve", {})
            return RuleResult("max_dti", entry.get("max_dti"), agency="FHA",
                              citation=entry.get("citation", ""),
                              notes=entry.get("notes", ""))
        else:
            if has_compensating:
                entry = dti_rules.get("manual_with_compensating", {})
            else:
                entry = dti_rules.get("manual_standard", {})
            front = entry.get("front_end")
            back = entry.get("back_end")
            return RuleResult("max_dti", {"front_end": front, "back_end": back},
                              agency="FHA",
                              citation=entry.get("citation", ""),
                              notes=entry.get("notes", ""))

    elif agency_key == "VA":
        entry = dti_rules.get("standard", {})
        residual = dti_rules.get("residual_income_override", {})
        return RuleResult("max_dti", entry.get("max_dti"), agency="VA",
                          citation=entry.get("citation", ""),
                          notes=f"{entry.get('notes', '')} | {residual.get('notes', '')}")

    return RuleResult("max_dti", None, agency=agency_key or "", notes="No DTI rules found")


def lookup_credit_score(agency_name: str, credit_score: Optional[int] = None) -> RuleResult:
    """Look up credit score requirements and check eligibility."""
    agency_key = resolve_agency(agency_name)
    if not agency_key or agency_key not in ALL_AGENCIES:
        return RuleResult("credit_score", None, notes=f"Unknown agency", eligible=False)

    agency = ALL_AGENCIES[agency_key]
    cs_rules = agency.get("credit_score", {})

    if agency_key in ("Fannie Mae", "Freddie Mac"):
        # Both require 620 minimum
        min_key = "du_minimum" if agency_key == "Fannie Mae" else "lpa_minimum"
        entry = cs_rules.get(min_key, {})
        min_score = entry.get("min_score", 620)
        eligible = credit_score >= min_score if credit_score else True
        return RuleResult("min_credit_score", min_score, agency=agency_key,
                          citation=entry.get("citation", ""),
                          notes=entry.get("notes", ""),
                          eligible=eligible)

    elif agency_key == "FHA":
        if credit_score is None:
            return RuleResult("min_credit_score", "500 (10% down) / 580 (3.5% down)",
                              agency="FHA",
                              citation="HUD 4000.1, II.A.2.a",
                              notes="FHA has tiered credit requirements")
        if credit_score >= 580:
            entry = cs_rules.get("minimum_580", {})
            return RuleResult("min_credit_score", 580, agency="FHA",
                              citation=entry.get("citation", ""),
                              notes=f"Score {credit_score} qualifies for 3.5% down (96.5% LTV)",
                              eligible=True)
        elif credit_score >= 500:
            entry = cs_rules.get("minimum_500", {})
            return RuleResult("min_credit_score", 500, agency="FHA",
                              citation=entry.get("citation", ""),
                              notes=f"Score {credit_score} qualifies for 10% down (90% LTV)",
                              eligible=True)
        else:
            return RuleResult("min_credit_score", 500, agency="FHA",
                              citation="HUD 4000.1, II.A.2.a",
                              notes=f"Score {credit_score} is below 500: NOT eligible for FHA",
                              eligible=False)

    elif agency_key == "VA":
        entry = cs_rules.get("va_minimum", {})
        overlay = cs_rules.get("lender_overlays_typical", {})
        return RuleResult("min_credit_score", "None (VA has no minimum)",
                          agency="VA",
                          citation=entry.get("citation", ""),
                          notes=f"VA sets no minimum credit score. Typical lender overlay: {overlay.get('min_score', 620)}",
                          eligible=True)

    return RuleResult("min_credit_score", None, agency=agency_key)


def lookup_mi(agency_name: str, ltv: float, loan_term_years: int = 30,
              rate_type: str = "fixed") -> RuleResult:
    """Look up conventional MI (Fannie/Freddie) coverage requirements."""
    agency_key = resolve_agency(agency_name)
    if agency_key not in ("Fannie Mae", "Freddie Mac"):
        return RuleResult("mi_coverage", "N/A", agency=agency_key or "",
                          notes="MI lookup only applies to conventional (Fannie/Freddie). Use lookup_mip() for FHA, lookup_funding_fee() for VA.")

    if ltv <= 80:
        return RuleResult("mi_coverage", "Not required", agency=agency_key,
                          citation="LTV ≤ 80%",
                          notes="No mortgage insurance required at 80% LTV or below",
                          eligible=True)

    agency = ALL_AGENCIES[agency_key]
    mi_rules = agency.get("mi", {})

    # Select coverage table
    rt = normalize_rate_type(rate_type)
    if rt == "arm":
        table = mi_rules.get("coverage_arm", mi_rules.get("coverage_fixed_30yr", []))
    elif loan_term_years <= 20:
        table = mi_rules.get("coverage_fixed_15_20yr", mi_rules.get("coverage_fixed_30yr", []))
    else:
        table = mi_rules.get("coverage_fixed_30yr", [])

    for band in table:
        if band["ltv_min"] <= ltv <= band["ltv_max"]:
            return RuleResult("mi_coverage", {
                "standard_coverage": f"{band['standard']}%",
                "minimum_coverage": f"{band.get('minimum', band['standard'])}%",
                "ltv_band": f"{band['ltv_min']:.1f}% - {band['ltv_max']:.1f}%",
            }, agency=agency_key,
                citation=band.get("citation", ""),
                notes=f"MI required at {ltv}% LTV",
                eligible=True)

    return RuleResult("mi_coverage", "LTV outside defined bands", agency=agency_key,
                      eligible=False)


def lookup_mip(ltv: float, loan_amount: float, loan_term_years: int = 30) -> RuleResult:
    """Calculate FHA MIP (upfront + annual)."""
    mip_rules = FHA.get("mip", {})
    upfront = mip_rules.get("upfront_mip", {})
    annual_tables = mip_rules.get("annual_mip", {})

    upfront_rate = upfront.get("rate", 1.75)
    upfront_amount = round(loan_amount * upfront_rate / 100, 2)

    # Select annual MIP table
    if loan_term_years <= 15:
        table = annual_tables.get("term_lte_15yr", [])
    else:
        table = annual_tables.get("term_gt_15yr", [])

    annual_rate = None
    duration = None
    for row in table:
        max_loan = row.get("base_loan_max")
        if max_loan and loan_amount > max_loan:
            continue
        if max_loan is None:
            # This is the "above threshold" tier — only match if we didn't match a capped tier
            pass
        if row["ltv_min"] <= ltv <= row["ltv_max"]:
            annual_rate = row["annual_rate"]
            duration = row["duration"]
            break

    # If no match on capped tiers, try uncapped
    if annual_rate is None:
        for row in table:
            if row.get("base_loan_max") is None and row["ltv_min"] <= ltv <= row["ltv_max"]:
                annual_rate = row["annual_rate"]
                duration = row["duration"]
                break

    annual_amount = round(loan_amount * (annual_rate or 0) / 100, 2)
    monthly_mip = round(annual_amount / 12, 2)

    return RuleResult("fha_mip", {
        "upfront_mip_rate": f"{upfront_rate}%",
        "upfront_mip_amount": f"${upfront_amount:,.2f}",
        "annual_mip_rate": f"{annual_rate}%" if annual_rate else "Unknown",
        "annual_mip_amount": f"${annual_amount:,.2f}/year",
        "monthly_mip": f"${monthly_mip:,.2f}/month",
        "duration": duration or "Unknown",
        "can_finance_upfront": True,
    }, agency="FHA",
        citation=upfront.get("citation", ""),
        notes=f"UFMIP {upfront_rate}% + annual {annual_rate}% for {duration}",
        eligible=True)


def lookup_funding_fee(down_payment_pct: float = 0, first_use: bool = True,
                       transaction_type: str = "purchase",
                       disability_exempt: bool = False,
                       loan_amount: Optional[float] = None) -> RuleResult:
    """Calculate VA funding fee."""
    if disability_exempt:
        return RuleResult("va_funding_fee", {
            "fee_pct": "0% (EXEMPT)",
            "fee_amount": "$0.00",
            "reason": "Exempt from funding fee",
        }, agency="VA",
            citation="VA Pamphlet 26-7, Ch. 8",
            notes="Veteran is exempt from VA funding fee due to disability compensation or other qualifying status",
            eligible=True)

    ff_rules = VA.get("funding_fee", {})
    tx = normalize_transaction_type(transaction_type)

    fee_pct = None
    citation = ff_rules.get("citation", "VA Pamphlet 26-7, Ch. 8")

    if tx in ("purchase", "rate_term_refi"):
        table_key = "purchase_first_use" if first_use else "purchase_subsequent_use"
        table = ff_rules.get(table_key, [])
        for row in table:
            if row["down_pct_min"] <= down_payment_pct <= row["down_pct_max"]:
                fee_pct = row["fee_pct"]
                citation = row.get("citation", citation)
                break
    elif tx == "cash_out_refi":
        key = "cash_out_refi_first_use" if first_use else "cash_out_refi_subsequent"
        entry = ff_rules.get(key, {})
        fee_pct = entry.get("fee_pct")
        citation = entry.get("citation", citation)
    elif tx == "irrrl":
        entry = ff_rules.get("irrrl", {})
        fee_pct = entry.get("fee_pct")
        citation = entry.get("citation", citation)

    fee_amount = round((loan_amount or 0) * (fee_pct or 0) / 100, 2) if fee_pct else None

    use_label = "first" if first_use else "subsequent"
    return RuleResult("va_funding_fee", {
        "fee_pct": f"{fee_pct}%" if fee_pct else "Unknown",
        "fee_amount": f"${fee_amount:,.2f}" if fee_amount else "N/A",
        "usage": use_label,
        "can_be_financed": True,
    }, agency="VA",
        citation=citation,
        notes=f"{'First' if first_use else 'Subsequent'} use, {down_payment_pct:.1f}% down",
        eligible=True)


def lookup_reserves(agency_name: str, occupancy: str, units: str = "1") -> RuleResult:
    """Look up reserve requirements."""
    agency_key = resolve_agency(agency_name)
    if not agency_key or agency_key not in ALL_AGENCIES:
        return RuleResult("reserves", None, notes="Unknown agency", eligible=False)

    agency = ALL_AGENCIES[agency_key]
    reserves = agency.get("reserves", {})
    occ = normalize_occupancy(occupancy)

    if occ == "primary":
        entry = reserves.get("primary_1_unit", {"months": 0})
    elif occ == "second_home":
        entry = reserves.get("second_home", {"months": 2})
    elif occ == "investment":
        unit = normalize_units(units)
        if unit in ("1_unit", "1"):
            entry = reserves.get("investment_1_unit", {"months": 6})
        else:
            entry = reserves.get("investment_2_4_unit", {"months": 6})
    else:
        entry = {"months": 0}

    return RuleResult("reserve_months", entry.get("months", 0), agency=agency_key,
                      citation=entry.get("citation", ""),
                      notes=entry.get("notes", ""))


def lookup_loan_limits(agency_name: str, units: str = "1") -> RuleResult:
    """Look up loan limits."""
    agency_key = resolve_agency(agency_name)
    if not agency_key or agency_key not in ALL_AGENCIES:
        return RuleResult("loan_limit", None, notes="Unknown agency", eligible=False)

    agency = ALL_AGENCIES[agency_key]
    limits = agency.get("loan_limits", {})
    unit = normalize_units(units)

    if agency_key in ("Fannie Mae", "Freddie Mac"):
        unit_key_map = {
            "1_unit": "conforming_1_unit",
            "2_unit": "conforming_2_unit",
            "3_4_unit": "conforming_3_unit",
            "condo": "conforming_1_unit",
        }
        key = unit_key_map.get(unit, "conforming_1_unit")
        limit = limits.get(key)
        high = limits.get("high_balance_1_unit")
        return RuleResult("loan_limit", {
            "conforming": f"${limit:,}" if limit else "N/A",
            "high_balance": f"${high:,}" if high else "N/A",
        }, agency=agency_key,
            citation=limits.get("citation", ""),
            notes=limits.get("notes", ""))

    elif agency_key == "FHA":
        floor = limits.get("floor_1_unit")
        ceiling = limits.get("ceiling_1_unit")
        return RuleResult("loan_limit", {
            "floor": f"${floor:,}" if floor else "N/A",
            "ceiling": f"${ceiling:,}" if ceiling else "N/A",
        }, agency="FHA",
            citation=limits.get("citation", ""),
            notes=limits.get("notes", ""))

    elif agency_key == "VA":
        ent = agency.get("entitlement", {})
        full = ent.get("full_entitlement", {})
        return RuleResult("loan_limit", {
            "full_entitlement": "No loan limit",
            "partial_entitlement": "County limits apply",
        }, agency="VA",
            citation=full.get("citation", ""),
            notes=full.get("description", ""))

    return RuleResult("loan_limit", None, agency=agency_key or "")


def lookup_va_residual_income(state: str, family_size: int,
                              loan_amount: float = 80001) -> RuleResult:
    """Look up VA residual income minimums by state and family size."""
    residual = VA.get("residual_income", {})
    regions = residual.get("regions", {})

    # Find region for state
    state_upper = state.upper() if state else ""
    region = None
    for reg_name, reg_data in regions.items():
        if state_upper in reg_data.get("states", []):
            region = reg_name
            break

    if not region:
        return RuleResult("va_residual_income", None, agency="VA",
                          notes=f"Could not determine VA region for state: {state}",
                          eligible=False)

    # Select loan amount tier
    if loan_amount < 80000:
        table = residual.get("minimums_loan_under_80k", {})
    else:
        table = residual.get("minimums_loan_80k_plus", {})

    family_key = f"family_{family_size}" if family_size <= 4 else "family_5_plus_add"

    if family_size <= 4:
        entry = table.get(family_key, {})
        minimum = entry.get(region)
    else:
        base = table.get("family_4", {}).get(region, 0)
        add_per = table.get("family_5_plus_add", {}).get(region, 0)
        minimum = base + (family_size - 4) * add_per

    return RuleResult("va_residual_income_minimum", {
        "monthly_minimum": f"${minimum:,}" if minimum else "Unknown",
        "region": region,
        "state": state_upper,
        "family_size": family_size,
        "loan_tier": "under $80K" if loan_amount < 80000 else "$80K+",
    }, agency="VA",
        citation=residual.get("citation", ""),
        notes=f"Region: {region}, Family size: {family_size}",
        eligible=True)


# =============================================================================
# FULL SCENARIO EVALUATION
# =============================================================================

def evaluate_scenario(scenario: LoanScenario) -> ScenarioResult:
    """
    Evaluate a complete loan scenario against one or all agencies.
    Returns comprehensive results with eligibility, limits, costs, and citations.
    """
    result = ScenarioResult(scenario)

    # Determine which agencies to evaluate
    if scenario.agency:
        agencies_to_check = [scenario.agency]
    else:
        agencies_to_check = list(ALL_AGENCIES.keys())

    for agency_name in agencies_to_check:
        _evaluate_agency(scenario, agency_name, result)

    return result


def _evaluate_agency(scenario: LoanScenario, agency_name: str, result: ScenarioResult):
    """Evaluate a scenario against a single agency."""
    eligible = True
    ineligible_reason = None

    # 1. LTV CHECK
    ltv_result = lookup_ltv(
        agency_name, scenario.transaction_type, scenario.occupancy,
        scenario.units, scenario.rate_type, scenario.credit_score,
        scenario.non_occupant_coborrower, scenario.coborrower_is_family
    )
    result.add_result(agency_name, ltv_result)

    if not ltv_result.eligible:
        eligible = False
        ineligible_reason = ltv_result.notes

    # Check if scenario LTV exceeds max
    if scenario.ltv and ltv_result.value is not None and isinstance(ltv_result.value, (int, float)):
        if scenario.ltv > ltv_result.value:
            eligible = False
            ineligible_reason = ineligible_reason or f"LTV {scenario.ltv}% exceeds max {ltv_result.value}%"
            result.add_result(agency_name, RuleResult(
                "ltv_check", f"FAIL: {scenario.ltv}% > {ltv_result.value}% max",
                agency=agency_name, eligible=False,
                notes=f"Scenario LTV ({scenario.ltv}%) exceeds maximum allowed ({ltv_result.value}%)"
            ))
        else:
            result.add_result(agency_name, RuleResult(
                "ltv_check", f"PASS: {scenario.ltv}% ≤ {ltv_result.value}% max",
                agency=agency_name, eligible=True
            ))
    elif scenario.ltv and ltv_result.value is None and ltv_result.eligible:
        # No LTV cap (streamline/IRRRL) — always passes
        result.add_result(agency_name, RuleResult(
            "ltv_check", f"PASS: No LTV cap for this program",
            agency=agency_name, eligible=True
        ))

    # 2. DTI CHECK
    dti_result = lookup_dti(agency_name, scenario.underwriting_method,
                            scenario.has_compensating_factors)
    result.add_result(agency_name, dti_result)

    if scenario.dti and dti_result.value:
        max_dti = dti_result.value
        if isinstance(max_dti, dict):
            # FHA manual has front_end/back_end
            back_end = max_dti.get("back_end")
            if back_end and scenario.dti > back_end:
                eligible = False
                ineligible_reason = ineligible_reason or f"DTI {scenario.dti}% exceeds max {back_end}%"
                result.add_result(agency_name, RuleResult(
                    "dti_check", f"FAIL: {scenario.dti}% > {back_end}% max",
                    agency=agency_name, eligible=False
                ))
            else:
                result.add_result(agency_name, RuleResult(
                    "dti_check", f"PASS: {scenario.dti}% ≤ {back_end}% max",
                    agency=agency_name, eligible=True
                ))
        elif isinstance(max_dti, (int, float)):
            if scenario.dti > max_dti:
                eligible = False
                ineligible_reason = ineligible_reason or f"DTI {scenario.dti}% exceeds max {max_dti}%"
                result.add_result(agency_name, RuleResult(
                    "dti_check", f"FAIL: {scenario.dti}% > {max_dti}% max",
                    agency=agency_name, eligible=False
                ))
            else:
                result.add_result(agency_name, RuleResult(
                    "dti_check", f"PASS: {scenario.dti}% ≤ {max_dti}% max",
                    agency=agency_name, eligible=True
                ))

    # 3. CREDIT SCORE CHECK
    cs_result = lookup_credit_score(agency_name, scenario.credit_score)
    result.add_result(agency_name, cs_result)

    if not cs_result.eligible:
        eligible = False
        ineligible_reason = ineligible_reason or cs_result.notes

    # 4. INSURANCE / FEE CALCULATION
    if agency_name in ("Fannie Mae", "Freddie Mac") and scenario.ltv:
        mi_result = lookup_mi(agency_name, scenario.ltv, scenario.loan_term_years,
                              scenario.rate_type)
        result.add_result(agency_name, mi_result)

    elif agency_name == "FHA" and scenario.ltv and scenario.loan_amount:
        mip_result = lookup_mip(scenario.ltv, scenario.loan_amount, scenario.loan_term_years)
        result.add_result(agency_name, mip_result)

    elif agency_name == "VA":
        ff_result = lookup_funding_fee(
            scenario.down_payment_pct or 0, scenario.va_first_use,
            scenario.transaction_type, scenario.va_disability_exempt,
            scenario.loan_amount
        )
        result.add_result(agency_name, ff_result)

        # Residual income if state provided
        if scenario.state:
            ri_result = lookup_va_residual_income(
                scenario.state, scenario.family_size,
                scenario.loan_amount or 80001
            )
            result.add_result(agency_name, ri_result)

    # 5. RESERVES
    reserve_result = lookup_reserves(agency_name, scenario.occupancy, scenario.units)
    result.add_result(agency_name, reserve_result)

    # 6. LOAN LIMITS
    limit_result = lookup_loan_limits(agency_name, scenario.units)
    result.add_result(agency_name, limit_result)

    # Mark eligibility
    if eligible:
        result.mark_eligible(agency_name)
    else:
        result.mark_ineligible(agency_name, ineligible_reason or "Does not meet requirements")


# =============================================================================
# CROSS-AGENCY COMPARISON
# =============================================================================

def compare_agencies(scenario: LoanScenario) -> Dict[str, Any]:
    """
    Compare all 4 agencies side-by-side for the same loan scenario.
    Returns a structured comparison with clear winners/losers.
    """
    # Force all-agency evaluation
    scenario.agency = None
    eval_result = evaluate_scenario(scenario)

    comparison = {
        "scenario_summary": {
            "transaction": scenario.transaction_type,
            "occupancy": scenario.occupancy,
            "units": scenario.units,
            "credit_score": scenario.credit_score,
            "ltv": scenario.ltv,
            "dti": scenario.dti,
            "loan_amount": scenario.loan_amount,
        },
        "eligible": eval_result.eligible_agencies,
        "ineligible": eval_result.ineligible_agencies,
        "agency_details": {},
        "best_options": [],
    }

    for agency_name, results in eval_result.results.items():
        details = {}
        for r in results:
            details[r.rule_name] = {
                "value": r.value,
                "citation": r.citation,
                "notes": r.notes,
                "eligible": r.eligible,
            }
        comparison["agency_details"][agency_name] = details

    # Determine best options
    if eval_result.eligible_agencies:
        # Score agencies (simple heuristic: higher LTV = more flexible, lower fees = cheaper)
        scored = []
        for agency in eval_result.eligible_agencies:
            details = comparison["agency_details"].get(agency, {})
            ltv_data = details.get("max_ltv", {})
            max_ltv = ltv_data.get("value", 0)
            if isinstance(max_ltv, (int, float)):
                scored.append((agency, max_ltv))
            else:
                scored.append((agency, 0))

        scored.sort(key=lambda x: x[1], reverse=True)
        comparison["best_options"] = [
            {"agency": a, "max_ltv": ltv, "rank": i + 1}
            for i, (a, ltv) in enumerate(scored)
        ]

    return comparison


def compare_agencies_text(scenario: LoanScenario) -> str:
    """Human-readable cross-agency comparison."""
    comp = compare_agencies(scenario)
    lines = []
    lines.append("=" * 70)
    lines.append("CROSS-AGENCY COMPARISON")
    lines.append("=" * 70)

    s = comp["scenario_summary"]
    lines.append(f"Scenario: {s['transaction']} | {s['occupancy']} | {s['units']} units")
    if s.get("credit_score"): lines.append(f"Credit: {s['credit_score']}")
    if s.get("ltv"): lines.append(f"LTV: {s['ltv']}%")
    if s.get("loan_amount"): lines.append(f"Loan: ${s['loan_amount']:,.0f}")

    lines.append(f"\n✓ Eligible: {', '.join(comp['eligible']) if comp['eligible'] else 'None'}")
    if comp["ineligible"]:
        for ag, reason in comp["ineligible"].items():
            lines.append(f"✗ {ag}: {reason}")

    if comp["best_options"]:
        lines.append("\nRANKING (by maximum LTV flexibility):")
        for opt in comp["best_options"]:
            lines.append(f"  #{opt['rank']} {opt['agency']} — Max LTV: {opt['max_ltv']}%")

    for agency, details in comp["agency_details"].items():
        lines.append(f"\n--- {agency} ---")
        for rule_name, data in details.items():
            status = "✓" if data["eligible"] else "✗"
            val = data["value"]
            if isinstance(val, dict):
                val_str = " | ".join(f"{k}: {v}" for k, v in val.items())
            else:
                val_str = str(val)
            lines.append(f"  [{status}] {rule_name}: {val_str}")
            if data["citation"]:
                lines.append(f"       Citation: {data['citation']}")

    return "\n".join(lines)


# =============================================================================
# QUICK-ANSWER FUNCTIONS (for the router to call)
# =============================================================================

def quick_ltv(agency: str, transaction: str = "purchase", occupancy: str = "primary",
              units: str = "1", rate_type: str = "fixed", credit_score: int = None) -> str:
    """One-liner answer: What's the max LTV?"""
    r = lookup_ltv(agency, transaction, occupancy, units, rate_type, credit_score)
    if r.value is None:
        return f"{r.agency}: Not eligible. {r.notes}"
    return f"{r.agency} max LTV: {r.value}% for {transaction.replace('_',' ')} / {occupancy} / {units} / {rate_type}. ({r.citation})"


def quick_dti(agency: str, method: str = "automated") -> str:
    """One-liner answer: What's the max DTI?"""
    r = lookup_dti(agency, method)
    val = r.value
    if isinstance(val, dict):
        return f"{r.agency} max DTI ({method}): {val.get('front_end','?')}% front / {val.get('back_end','?')}% back. ({r.citation})"
    return f"{r.agency} max DTI ({method}): {val}%. ({r.citation})"


def quick_credit(agency: str, score: int = None) -> str:
    """One-liner: What's the minimum credit score?"""
    r = lookup_credit_score(agency, score)
    if score:
        status = "ELIGIBLE" if r.eligible else "NOT ELIGIBLE"
        return f"{r.agency}: Score {score} → {status}. Min: {r.value}. ({r.citation}) {r.notes}"
    return f"{r.agency} minimum credit score: {r.value}. ({r.citation})"


def quick_funding_fee(down_pct: float = 0, first_use: bool = True,
                      loan_amount: float = None, exempt: bool = False) -> str:
    """One-liner: What's the VA funding fee?"""
    r = lookup_funding_fee(down_pct, first_use, "purchase", exempt, loan_amount)
    val = r.value
    return f"VA funding fee: {val.get('fee_pct','?')} (down: {down_pct}%, {'first' if first_use else 'subsequent'} use). {val.get('fee_amount','')} ({r.citation})"


def quick_mip(ltv: float = 96.5, loan_amount: float = 300000, term: int = 30) -> str:
    """One-liner: What's the FHA MIP?"""
    r = lookup_mip(ltv, loan_amount, term)
    val = r.value
    return f"FHA MIP: UFMIP {val.get('upfront_mip_rate','?')} (${val.get('upfront_mip_amount','?')}), Annual {val.get('annual_mip_rate','?')} ({val.get('monthly_mip','?')}/mo), Duration: {val.get('duration','?')}. ({r.citation})"


# =============================================================================
# ENTRY POINT FOR TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MORTGAGE RULE ENGINE — TEST SUITE")
    print("=" * 70)

    # Test 1: Basic LTV lookup
    print("\n📋 TEST 1: Fannie Mae Purchase, Primary, 1-unit, Fixed")
    r = lookup_ltv("fannie", "purchase", "primary", "1", "fixed")
    print(f"  {r}")

    # Test 2: FHA with credit score
    print("\n📋 TEST 2: FHA Purchase, 550 credit score")
    r = lookup_ltv("fha", "purchase", "primary", "1", credit_score=550)
    print(f"  {r}")

    # Test 3: VA funding fee
    print("\n📋 TEST 3: VA Funding Fee, 0% down, first use, $400K loan")
    r = lookup_funding_fee(0, True, "purchase", False, 400000)
    print(f"  {r}")

    # Test 4: FHA MIP
    print("\n📋 TEST 4: FHA MIP, 96.5% LTV, $300K loan, 30yr")
    r = lookup_mip(96.5, 300000, 30)
    print(f"  {r}")

    # Test 5: Full scenario evaluation
    print("\n📋 TEST 5: Full Scenario — Purchase, Primary, 1-unit, 720 FICO, 95% LTV, $350K")
    scenario = LoanScenario(
        transaction_type="purchase",
        occupancy="primary",
        units="1",
        rate_type="fixed",
        credit_score=720,
        ltv=95,
        loan_amount=350000,
        loan_term_years=30,
        va_first_use=True,
        state="TX",
        family_size=3,
    )
    result = evaluate_scenario(scenario)
    print(result.to_text())

    # Test 6: Cross-agency comparison
    print("\n\n📋 TEST 6: Cross-Agency Comparison — Same scenario")
    print(compare_agencies_text(scenario))

    # Test 7: Quick answers
    print("\n📋 TEST 7: Quick Answers")
    print(f"  {quick_ltv('va', 'purchase', 'primary', '1')}")
    print(f"  {quick_dti('fha', 'automated')}")
    print(f"  {quick_credit('fannie', 580)}")
    print(f"  {quick_funding_fee(5, True, 400000)}")
    print(f"  {quick_mip(96.5, 300000, 30)}")
