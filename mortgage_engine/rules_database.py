"""
MORTGAGE UNDERWRITING RULE DATABASE
====================================
The world's most comprehensive deterministic mortgage guideline engine.
Encodes every hard rule across Fannie Mae, Freddie Mac, FHA, and VA
as structured, queryable data. Zero hallucination. Instant answers.

Architecture:
- Each agency has LTV matrices, DTI limits, credit floors, MI/MIP/FF tables,
  property eligibility, occupancy rules, and special program rules.
- Rules are structured as condition→result lookups with full citations.
- The engine evaluates a loan scenario against ALL applicable rules
  and returns precise answers.
"""

# =============================================================================
# FANNIE MAE (FNMA) RULES
# =============================================================================

FANNIE_MAE = {
    "agency": "Fannie Mae",
    "agency_code": "FNMA",
    "source": "Fannie Mae Selling Guide",

    # ----- LTV / CLTV MATRICES -----
    "ltv_matrix": {
        "purchase": {
            "primary": {
                "1_unit": {
                    "fixed": {"max_ltv": 97, "max_cltv": 97, "citation": "B2-1.1-01, Eligibility Matrix", "notes": "97% requires DU; manual max 95%"},
                    "arm":   {"max_ltv": 95, "max_cltv": 95, "citation": "B2-1.1-01, Eligibility Matrix"},
                },
                "2_unit": {
                    "fixed": {"max_ltv": 85, "max_cltv": 85, "citation": "B2-1.1-01, Eligibility Matrix"},
                    "arm":   {"max_ltv": 85, "max_cltv": 85, "citation": "B2-1.1-01, Eligibility Matrix"},
                },
                "3_4_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01, Eligibility Matrix"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01, Eligibility Matrix"},
                },
                "condo": {
                    "fixed": {"max_ltv": 97, "max_cltv": 97, "citation": "B4-2.1-01, Condo Eligibility"},
                    "arm":   {"max_ltv": 95, "max_cltv": 95, "citation": "B4-2.1-01"},
                },
                "manufactured": {
                    "fixed": {"max_ltv": 95, "max_cltv": 95, "citation": "B5-2-01, Manufactured Housing"},
                    "arm":   {"max_ltv": 95, "max_cltv": 95, "citation": "B5-2-01"},
                },
            },
            "second_home": {
                "1_unit": {
                    "fixed": {"max_ltv": 90, "max_cltv": 90, "citation": "B2-1.1-01, Eligibility Matrix"},
                    "arm":   {"max_ltv": 90, "max_cltv": 90, "citation": "B2-1.1-01"},
                },
            },
            "investment": {
                "1_unit": {
                    "fixed": {"max_ltv": 85, "max_cltv": 85, "citation": "B2-1.1-01, Eligibility Matrix"},
                    "arm":   {"max_ltv": 85, "max_cltv": 85, "citation": "B2-1.1-01"},
                },
                "2_4_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01, Eligibility Matrix"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                },
            },
        },
        "rate_term_refi": {
            "primary": {
                "1_unit": {
                    "fixed": {"max_ltv": 97, "max_cltv": 97, "citation": "B2-1.1-01, High LTV Refi / LCOR"},
                    "arm":   {"max_ltv": 95, "max_cltv": 95, "citation": "B2-1.1-01"},
                },
                "2_unit": {
                    "fixed": {"max_ltv": 85, "max_cltv": 85, "citation": "B2-1.1-01"},
                    "arm":   {"max_ltv": 85, "max_cltv": 85, "citation": "B2-1.1-01"},
                },
                "3_4_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                },
            },
            "second_home": {
                "1_unit": {
                    "fixed": {"max_ltv": 90, "max_cltv": 90, "citation": "B2-1.1-01"},
                    "arm":   {"max_ltv": 90, "max_cltv": 90, "citation": "B2-1.1-01"},
                },
            },
            "investment": {
                "1_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                },
                "2_4_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                },
            },
        },
        "cash_out_refi": {
            "primary": {
                "1_unit": {
                    "fixed": {"max_ltv": 80, "max_cltv": 80, "citation": "B2-1.1-01, Eligibility Matrix"},
                    "arm":   {"max_ltv": 80, "max_cltv": 80, "citation": "B2-1.1-01"},
                },
                "2_4_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                },
            },
            "second_home": {
                "1_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                },
            },
            "investment": {
                "1_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "B2-1.1-01"},
                },
                "2_4_unit": {
                    "fixed": {"max_ltv": 70, "max_cltv": 70, "citation": "B2-1.1-01"},
                    "arm":   {"max_ltv": 70, "max_cltv": 70, "citation": "B2-1.1-01"},
                },
            },
        },
    },

    # ----- DTI LIMITS -----
    "dti": {
        "du_approve": {
            "max_dti": 50,
            "citation": "B3-6-02, DU Requirements",
            "notes": "DU may approve up to 50%; actual limit depends on risk factors"
        },
        "manual_standard": {
            "max_dti": 36,
            "citation": "B3-6-02, Manual Underwriting DTI",
            "notes": "Standard manual underwriting limit"
        },
        "manual_with_compensating": {
            "max_dti": 45,
            "citation": "B3-6-02, Manual Underwriting with Compensating Factors",
            "notes": "Up to 45% with strong compensating factors (reserves, credit score, low payment shock)"
        },
        "high_ltv_refi": {
            "max_dti": None,  # No max
            "citation": "B5-7-01, High LTV Refinance",
            "notes": "No maximum DTI for High LTV Refinance (except Alternative Qualification Path = 45%)"
        },
    },

    # ----- CREDIT SCORE -----
    "credit_score": {
        "du_minimum": {
            "min_score": 620,
            "citation": "B3-5.1-01, Credit Score Requirements",
            "notes": "DU requires minimum 620 representative score"
        },
        "manual_minimum": {
            "min_score": 620,
            "citation": "B3-5.1-01",
            "notes": "Manual underwriting also requires 620 minimum"
        },
        "homeready": {
            "min_score": 620,
            "citation": "B5-6-02, HomeReady Requirements",
        },
        "score_methodology": {
            "two_scores": "Use lower of two",
            "three_scores": "Use middle score",
            "multiple_borrowers": "Use lowest representative score among all borrowers",
            "citation": "B3-5.1-01"
        },
    },

    # ----- MORTGAGE INSURANCE -----
    "mi": {
        "required_when": "LTV > 80%",
        "citation": "B7-1-02, MI Coverage Requirements",
        "coverage_fixed_30yr": [
            {"ltv_min": 80.01, "ltv_max": 85.00, "standard": 6,  "minimum": 6,  "citation": "B7-1-02"},
            {"ltv_min": 85.01, "ltv_max": 90.00, "standard": 25, "minimum": 12, "citation": "B7-1-02"},
            {"ltv_min": 90.01, "ltv_max": 95.00, "standard": 30, "minimum": 25, "citation": "B7-1-02"},
            {"ltv_min": 95.01, "ltv_max": 97.00, "standard": 35, "minimum": 35, "citation": "B7-1-02"},
        ],
        "coverage_fixed_15_20yr": [
            {"ltv_min": 80.01, "ltv_max": 85.00, "standard": 6,  "minimum": 6,  "citation": "B7-1-02"},
            {"ltv_min": 85.01, "ltv_max": 90.00, "standard": 12, "minimum": 6,  "citation": "B7-1-02"},
            {"ltv_min": 90.01, "ltv_max": 95.00, "standard": 25, "minimum": 12, "citation": "B7-1-02"},
            {"ltv_min": 95.01, "ltv_max": 97.00, "standard": 35, "minimum": 35, "citation": "B7-1-02"},
        ],
        "coverage_arm": [
            {"ltv_min": 80.01, "ltv_max": 85.00, "standard": 6,  "minimum": 6,  "citation": "B7-1-02"},
            {"ltv_min": 85.01, "ltv_max": 90.00, "standard": 25, "minimum": 25, "citation": "B7-1-02"},
            {"ltv_min": 90.01, "ltv_max": 95.00, "standard": 30, "minimum": 25, "citation": "B7-1-02"},
        ],
        "cancellation": {
            "automatic": "At 78% of original value based on amortization schedule",
            "borrower_request": "At 80% current value with good payment history",
            "citation": "Homeowners Protection Act / B7-1"
        },
    },

    # ----- STUDENT LOAN DTI TREATMENT -----
    "student_loans": {
        "deferred_or_ibr": {
            "monthly_payment_calc": "Greater of: 0.5% of outstanding balance OR actual monthly payment",
            "if_no_payment_reported": "Use 0.5% of outstanding balance",
            "if_ibr_payment_reported": "Use greater of IBR payment or 0.5% of balance",
            "fully_deferred": "Use 0.5% of outstanding balance",
            "forbearance": "Use 0.5% of outstanding balance",
            "citation": "B3-6-05, Monthly Debt Obligations",
            "notes": "Fannie Mae changed from 1% to 0.5% effective 2023. If actual documented payment is $0 or not reported, must use 0.5% of balance."
        },
        "standard_repayment": {
            "monthly_payment_calc": "Use actual monthly payment from credit report or documentation",
            "citation": "B3-6-05",
        },
        "forgiveness_programs": {
            "notes": "Projected forgiveness does NOT reduce the balance for DTI purposes",
            "citation": "B3-6-05",
        },
    },

    # ----- LIABILITY TREATMENT -----
    "liabilities": {
        "installment_debt": {
            "include_if": "More than 10 months remaining",
            "may_exclude_if": "10 or fewer payments remaining",
            "citation": "B3-6-05",
        },
        "cosigned_debt": {
            "include_in_dti": True,
            "exception": "May exclude if primary obligor has made last 12 months payments (documented)",
            "citation": "B3-6-05",
        },
        "derogatory_events": {
            "bankruptcy_ch7": {"waiting_period_years": 4, "from": "discharge date", "citation": "B3-5.3-07"},
            "bankruptcy_ch13": {"waiting_period_years": 2, "from": "discharge date", "with_extenuating": 2, "citation": "B3-5.3-07"},
            "foreclosure": {"waiting_period_years": 7, "with_extenuating": 3, "citation": "B3-5.3-07"},
            "short_sale": {"waiting_period_years": 4, "with_extenuating": 2, "citation": "B3-5.3-07"},
            "deed_in_lieu": {"waiting_period_years": 4, "with_extenuating": 2, "citation": "B3-5.3-07"},
            "repossession": {"waiting_period_years": 4, "with_extenuating": 2, "citation": "B3-5.3-07", "notes": "Treated same as foreclosure for conventional"},
        },
    },

    # ----- PROPERTY ELIGIBILITY -----
    "property": {
        "eligible": [
            "1-4 unit residential (detached, attached, row, townhouse)",
            "Condominiums (with project eligibility per B4-2)",
            "PUDs (Planned Unit Developments)",
            "Co-op share loans",
            "Manufactured housing (per B5-2 requirements)",
            "Leasehold estates (per B2-3-03)",
            "Mixed-use (residential primary, limited commercial)",
        ],
        "ineligible": [
            "Houseboats / floating homes",
            "Timeshares / fractional ownership",
            "Properties primarily for business or agriculture",
            "Properties with deferred maintenance affecting safety/integrity",
            "Boarding houses",
            "Bed and breakfast operations",
        ],
        "citation": "B2-3-01, B2-3-02, Property Eligibility",
    },

    # ----- SPECIAL PROGRAMS -----
    "special_programs": {
        "homeready": {
            "max_ltv": 97,
            "units": "1-unit only",
            "occupancy": "Primary residence only",
            "min_borrower_contribution": "3% own funds",
            "income_limit": "80% of AMI (area median income)",
            "du_required_above_95": True,
            "ineligible": ["2-4 unit", "co-op", "manufactured", "new construction", "HomeStyle combo", ">=$1M"],
            "citation": "B5-6-02, HomeReady Mortgage",
        },
        "homestyle_renovation": {
            "max_ltv": 97,
            "description": "Purchase or LCOR + renovation costs",
            "completion_timeline": "15 months",
            "manufactured_cap": "50% of as-completed value",
            "citation": "B5-3.2-01, HomeStyle Renovation",
        },
        "high_ltv_refi": {
            "max_ltv": 97,
            "no_max_dti": True,
            "must_own_existing_fannie_loan": True,
            "citation": "B5-7-01, High LTV Refinance",
        },
    },

    # ----- RESERVE REQUIREMENTS -----
    "reserves": {
        "primary_1_unit": {"months": 0, "notes": "No reserves required for primary 1-unit (DU may require)"},
        "second_home": {"months": 2, "citation": "B3-4.1-01"},
        "investment_1_unit": {"months": 6, "citation": "B3-4.1-01"},
        "investment_2_4_unit": {"months": 6, "citation": "B3-4.1-01"},
        "multiple_financed": {"months": 2, "per": "each additional financed property", "citation": "B3-4.1-01"},
    },

    # ----- BORROWER CONTRIBUTION / GIFT FUNDS -----
    "borrower_contribution": {
        "ltv_lte_80_primary": {"min_own_funds": "0%", "gift_ok": True, "citation": "B3-4.3-04"},
        "ltv_gt_80_1_unit": {"min_own_funds": "3%", "gift_for_remainder": True, "citation": "B3-4.3-04"},
        "ltv_gt_80_2_4_unit": {"min_own_funds": "5%", "gift_for_remainder": True, "citation": "B3-4.3-04"},
    },
    "gift_funds": {
        "eligible_donors": ["relative", "domestic partner", "fiance", "employer", "labor union", "government entity", "nonprofit"],
        "ineligible_donors": ["interested party (seller, builder, real estate agent)", "any person with financial interest in the transaction"],
        "documentation_required": ["gift letter (amount, donor, relationship, no repayment)", "donor bank statement showing withdrawal", "borrower bank statement showing deposit"],
        "foreign_gifts": {
            "allowed": True,
            "additional_docs": ["wire transfer confirmation", "donor bank statement from foreign bank", "currency conversion documentation"],
            "citation": "B3-4.3-04",
        },
        "citation": "B3-4.3-04, Gift Fund Requirements",
    },

    # ----- NON-TAXABLE INCOME GROSS-UP -----
    "nontaxable_income_grossup": {
        "allowed": True,
        "default_factor": 1.25,
        "default_pct": "25%",
        "documentation_based_factor": "May use actual tax rate if documented with tax returns",
        "eligible_income_types": ["Social Security", "SSDI", "VA disability compensation", "child support", "municipal bond interest", "certain retirement income", "military allowances (BAH, BAS)"],
        "not_eligible": ["Alimony (taxable for pre-2019 divorces)"],
        "how_to_apply": "Multiply non-taxable monthly income by 1.25 (or 1 + actual tax rate)",
        "citation": "B3-3.1-01, General Income Information",
        "notes": "DU automatically grosses up when non-taxable income is identified. For manual UW, lender calculates.",
    },

    # ----- ALIMONY / CHILD SUPPORT AS INCOME -----
    "alimony_child_support_income": {
        "alimony_as_income": {
            "can_use": True,
            "continuity_required": "Must continue for at least 3 years from closing",
            "documentation": ["divorce decree or separation agreement", "court order", "12 months receipt history (bank statements or cancelled checks)"],
            "taxable": "Taxable for divorces finalized before 1/1/2019; non-taxable after",
            "grossup_eligible": "Only if non-taxable (post-2018 divorces)",
            "citation": "B3-3.1-09, Alimony and Child Support",
        },
        "child_support_as_income": {
            "can_use": True,
            "continuity_required": "Must continue for at least 3 years from closing",
            "documentation": ["divorce decree, court order, or separation agreement", "12 months receipt history"],
            "non_taxable": True,
            "grossup_eligible": True,
            "citation": "B3-3.1-09",
        },
        "alimony_as_liability": {
            "always_included_in_dti": True,
            "documentation": "Court order or divorce decree amount",
            "citation": "B3-6-05, Monthly Debt Obligations",
        },
    },

    # ----- EMPLOYMENT / INCOME TYPE RULES -----
    "income_rules": {
        "employment_history": {
            "standard_requirement": "2 years continuous employment history",
            "gaps_allowed": "Yes, if explained with LOE (Letter of Explanation)",
            "exceptions": ["recent college graduates (transcript + offer letter)", "military personnel transitioning to civilian", "seasonal workers with 2-year history"],
            "citation": "B3-3.1-01, General Income Requirements",
        },
        "commission_income": {
            "requirement": "2 years history of commission earnings",
            "calculation_stable_or_increasing": "Use 2-year average",
            "calculation_declining": "Use most recent year (lower amount)",
            "if_less_than_25pct_of_total": "Not considered variable; no 2-year history needed",
            "documentation": ["2 years W-2s", "2 years tax returns (if >25% commission)", "most recent paystub"],
            "citation": "B3-3.1-05, Commission Income",
        },
        "self_employment_income": {
            "requirement": "2 years history required (1 year acceptable if prior related employment)",
            "calculation": "Use Form 1084/1088 (Fannie) to compute net income from tax returns",
            "declining_income": "If year-over-year decline, use most recent year's lower income",
            "schedule_c_add_backs": ["depreciation", "depletion", "amortization", "business use of home", "meals/entertainment (non-deductible portion)"],
            "schedule_e_add_backs": ["depreciation", "amortization", "insurance", "taxes (if already in PITIA)"],
            "form_used": "Form 1084 (Cash Flow Analysis) or Form 1088 (Comparative Income Analysis)",
            "citation": "B3-3.2-01, Self-Employment Income; B3-3.2-02, Tax Return Analysis",
        },
        "rental_income_from_subject": {
            "can_use": True,
            "factor": 0.75,
            "formula": "75% of gross monthly rent minus full PITIA = net rental income",
            "documentation": ["current lease agreements OR", "Fannie Mae Form 1025 (Small Residential Income Property Appraisal)"],
            "owner_occupied_multi_unit": "Can use rental income from non-owner-occupied units",
            "investment_property": "Can use rental income from all units",
            "citation": "B3-3.1-08, Rental Income",
        },
        "rental_income_existing_properties": {
            "factor": 0.75,
            "formula": "75% of gross rent per Schedule E or lease - PITIA = net rental income",
            "negative_cash_flow": "Net loss is added to monthly obligations (increases DTI)",
            "documentation": ["Schedule E from tax returns (2-year history)", "current lease agreements"],
            "citation": "B3-3.1-08, Rental Income",
        },
        "departure_residence": {
            "definition": "Current primary residence being vacated/converted to rental",
            "rental_income_allowed": True,
            "requirements": ["executed lease agreement for the departure property", "evidence of security deposit"],
            "factor": 0.75,
            "formula": "75% of gross rent minus full PITIA on departure residence",
            "if_no_lease": "Full PITIA of departure residence counted as liability with zero rental offset",
            "citation": "B3-3.1-08, Rental Income; B3-6-06, Qualifying Impact of Other Real Estate Owned",
        },
        "asset_depletion_income": {
            "allowed": True,
            "eligible_assets": ["checking/savings", "stocks/bonds/mutual funds (use 70% of value)", "retirement accounts (use 70% if under 59.5, 100% if over)", "trust accounts"],
            "ineligible_assets": ["business assets", "stock options/restricted stock", "non-vested RSUs", "529 education accounts"],
            "formula": "(Eligible assets - down payment - closing costs) / remaining loan term in months",
            "loan_term_divisor": "Use actual loan term (e.g., 360 for 30-year, 240 for 20-year)",
            "age_restriction": "Borrower must be at least 62 for DU to accept (no age restriction for manual UW if asset ownership documented)",
            "citation": "B3-3.1-09, Other Income; B3-4.3-19, Asset Depletion",
        },
        "social_security_income": {
            "can_use": True,
            "non_taxable": True,
            "grossup_eligible": True,
            "documentation": ["SSA award letter or benefit verification letter", "most recent bank statement showing deposit"],
            "continuity": "Assumed to continue (no expiration for retirement/SSDI)",
            "citation": "B3-3.1-09, Other Income",
        },
        "pension_retirement_income": {
            "can_use": True,
            "documentation": ["pension/retirement award letter", "1099-R", "bank statements showing deposits"],
            "continuity": "Assumed to continue if no expiration date",
            "grossup_eligible": "If non-taxable portion documented",
            "citation": "B3-3.1-01, General Income; B3-3.1-09, Other Income",
        },
        "va_disability_income": {
            "can_use": True,
            "non_taxable": True,
            "grossup_eligible": True,
            "grossup_factor": 1.25,
            "documentation": ["VA benefit letter or award letter", "bank statements"],
            "continuity": "Assumed to continue (permanent disability)",
            "citation": "B3-3.1-09, Other Income",
        },
        "boarder_income": {
            "homeready_only": True,
            "max_percentage_of_income": "30% of total qualifying income",
            "documentation": ["12 months history of shared residency (e.g., utility bills, drivers license)", "documentation of boarder payments"],
            "not_available_for": "Standard conventional, FHA, VA",
            "citation": "B5-6-02, HomeReady; B3-3.1-09",
        },
    },

    # ----- COLLECTIONS / CHARGE-OFFS -----
    "collections_chargeoffs": {
        "medical_collections": {
            "excluded_from_dti": True,
            "no_payoff_required": True,
            "citation": "B3-5.3-08, Collections and Charge-Offs",
        },
        "non_medical_collections": {
            "excluded_from_dti": True,
            "notes": "DU does not require payoff of collections. Manual UW may require explanation.",
            "citation": "B3-5.3-08",
        },
        "charge_offs": {
            "excluded_from_dti": True,
            "notes": "Charge-offs do not need to be paid off for DU. For manual UW, lender discretion.",
            "citation": "B3-5.3-08",
        },
    },

    # ----- LOAN MODIFICATION SEASONING -----
    "loan_modification_seasoning": {
        "standard": {
            "waiting_period_months": 12,
            "payments_required": 12,
            "from": "effective date of modification",
            "applies_to": "Rate-term and cash-out refinance of a modified loan",
            "citation": "B2-1.3-05, Refinance of Modified Mortgage",
        },
    },

    # ----- NON-OCCUPANT CO-BORROWER -----
    "non_occupant_coborrower": {
        "allowed": True,
        "max_ltv_1_unit": 97,
        "max_ltv_2_unit": 85,
        "max_ltv_investment": "Not applicable (non-occ co-borrower only for primary)",
        "income_can_be_used": True,
        "must_be_on_title": True,
        "relationship_requirement": "None (any individual)",
        "citation": "B2-2-04, Non-Occupant Borrowers",
    },

    # ----- LOAN LIMITS (2024 baseline, update annually) -----
    "loan_limits": {
        "conforming_1_unit": 766550,
        "conforming_2_unit": 981500,
        "conforming_3_unit": 1186350,
        "conforming_4_unit": 1474400,
        "high_balance_1_unit": 1149825,
        "citation": "FHFA Conforming Loan Limits",
        "notes": "Limits adjusted annually. High-cost areas up to 150% of baseline.",
    },
}


# =============================================================================
# FREDDIE MAC (FHLMC) RULES
# =============================================================================

FREDDIE_MAC = {
    "agency": "Freddie Mac",
    "agency_code": "FHLMC",
    "source": "Freddie Mac Seller/Servicer Guide",

    "ltv_matrix": {
        "purchase": {
            "primary": {
                "1_unit": {
                    "fixed": {"max_ltv": 97, "max_cltv": 97, "citation": "Section 4201.4, Eligibility Matrix", "notes": "97% via Home Possible or HomeOne"},
                    "arm":   {"max_ltv": 95, "max_cltv": 95, "citation": "Section 4201.4"},
                },
                "2_unit": {
                    "fixed": {"max_ltv": 95, "max_cltv": 95, "citation": "Section 4201.4", "notes": "More generous than Fannie (85%)"},
                    "arm":   {"max_ltv": 85, "max_cltv": 85, "citation": "Section 4201.4"},
                },
                "3_4_unit": {
                    "fixed": {"max_ltv": 80, "max_cltv": 80, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                },
                "condo": {
                    "fixed": {"max_ltv": 97, "max_cltv": 97, "citation": "Section 5601, Condo Eligibility"},
                    "arm":   {"max_ltv": 95, "max_cltv": 95, "citation": "Section 5601"},
                },
                "manufactured": {
                    "fixed": {"max_ltv": 95, "max_cltv": 95, "citation": "Section 5701, Manufactured Housing"},
                    "arm":   {"max_ltv": 95, "max_cltv": 95, "citation": "Section 5701"},
                },
            },
            "second_home": {
                "1_unit": {
                    "fixed": {"max_ltv": 90, "max_cltv": 90, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 90, "max_cltv": 90, "citation": "Section 4201.4"},
                },
            },
            "investment": {
                "1_unit": {
                    "fixed": {"max_ltv": 85, "max_cltv": 85, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 85, "max_cltv": 85, "citation": "Section 4201.4"},
                },
                "2_4_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                },
            },
        },
        "rate_term_refi": {
            "primary": {
                "1_unit": {
                    "fixed": {"max_ltv": 97, "max_cltv": 97, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 95, "max_cltv": 95, "citation": "Section 4201.4"},
                },
                "2_unit": {
                    "fixed": {"max_ltv": 85, "max_cltv": 85, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 85, "max_cltv": 85, "citation": "Section 4201.4"},
                },
                "3_4_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                },
            },
            "second_home": {
                "1_unit": {
                    "fixed": {"max_ltv": 90, "max_cltv": 90, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 90, "max_cltv": 90, "citation": "Section 4201.4"},
                },
            },
            "investment": {
                "1_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                },
                "2_4_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                },
            },
        },
        "cash_out_refi": {
            "primary": {
                "1_unit": {
                    "fixed": {"max_ltv": 80, "max_cltv": 80, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 80, "max_cltv": 80, "citation": "Section 4201.4"},
                },
                "2_4_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                },
            },
            "second_home": {
                "1_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                },
            },
            "investment": {
                "1_unit": {
                    "fixed": {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 75, "max_cltv": 75, "citation": "Section 4201.4"},
                },
                "2_4_unit": {
                    "fixed": {"max_ltv": 70, "max_cltv": 70, "citation": "Section 4201.4"},
                    "arm":   {"max_ltv": 70, "max_cltv": 70, "citation": "Section 4201.4"},
                },
            },
        },
    },

    "dti": {
        "lpa_accept": {
            "max_dti": 50,
            "citation": "Section 5401.1, LPA DTI Requirements",
            "notes": "LPA (Loan Product Advisor) may approve up to 50%"
        },
        "manual_standard": {
            "max_dti": 43,
            "citation": "Section 5401.1, Manual Underwriting",
            "notes": "Standard manual limit; QM safe harbor at 43%"
        },
        "manual_with_compensating": {
            "max_dti": 45,
            "citation": "Section 5401.1",
            "notes": "Up to 45% with compensating factors"
        },
    },

    "credit_score": {
        "lpa_minimum": {"min_score": 620, "citation": "Section 5201.1, Credit Score Requirements"},
        "manual_minimum": {"min_score": 620, "citation": "Section 5201.1"},
        "home_possible": {"min_score": 620, "citation": "Section 4501.8, Home Possible"},
        "score_methodology": {
            "two_scores": "Use lower of two",
            "three_scores": "Use middle score",
            "multiple_borrowers": "Use lowest representative score",
            "citation": "Section 5201.1"
        },
    },

    "mi": {
        "required_when": "LTV > 80%",
        "citation": "Section 4701, Mortgage Insurance",
        "coverage_fixed_30yr": [
            {"ltv_min": 80.01, "ltv_max": 85.00, "standard": 6,  "minimum": 6,  "citation": "Section 4701.3"},
            {"ltv_min": 85.01, "ltv_max": 90.00, "standard": 25, "minimum": 12, "citation": "Section 4701.3"},
            {"ltv_min": 90.01, "ltv_max": 95.00, "standard": 30, "minimum": 25, "citation": "Section 4701.3"},
            {"ltv_min": 95.01, "ltv_max": 97.00, "standard": 35, "minimum": 35, "citation": "Section 4701.3"},
        ],
    },

    "special_programs": {
        "home_possible": {
            "max_ltv": 97,
            "units": "1-unit (2-4 unit at lower LTV)",
            "occupancy": "Primary residence only",
            "income_limit": "80% of AMI",
            "min_borrower_contribution": "3% own funds",
            "citation": "Section 4501.8, Home Possible",
            "notes": "Freddie's affordable program, comparable to Fannie HomeReady"
        },
        "homeone": {
            "max_ltv": 97,
            "units": "1-unit only",
            "occupancy": "Primary residence only",
            "income_limit": None,  # No income limit
            "first_time_buyer_required": True,
            "citation": "Section 4501.9, HomeOne",
            "notes": "No income limit but requires first-time homebuyer"
        },
        "super_conforming": {
            "description": "Loans above conforming limit up to high-cost area ceiling",
            "citation": "Section 4201.16",
        },
    },

    "reserves": {
        "primary_1_unit": {"months": 0, "notes": "No reserves for primary 1-unit"},
        "second_home": {"months": 2, "citation": "Section 5501.1"},
        "investment_1_unit": {"months": 6, "citation": "Section 5501.1"},
        "investment_2_4_unit": {"months": 6, "citation": "Section 5501.1"},
    },

    "loan_limits": {
        "conforming_1_unit": 766550,
        "conforming_2_unit": 981500,
        "conforming_3_unit": 1186350,
        "conforming_4_unit": 1474400,
        "high_balance_1_unit": 1149825,
        "citation": "FHFA Conforming Loan Limits (same as Fannie Mae)",
    },

    # ----- STUDENT LOAN DTI TREATMENT -----
    "student_loans": {
        "deferred_or_ibr": {
            "monthly_payment_calc": "Greater of: 0.5% of outstanding balance OR actual monthly payment",
            "if_no_payment_reported": "Use 0.5% of outstanding balance",
            "if_ibr_payment_reported": "Use greater of IBR payment or 0.5% of balance",
            "fully_deferred": "Use 0.5% of outstanding balance",
            "forbearance": "Use 0.5% of outstanding balance",
            "citation": "Section 5501.1, Freddie Mac Seller/Servicer Guide",
            "notes": "Same as Fannie Mae: 0.5% of outstanding balance if payment is $0, deferred, or in forbearance."
        },
        "standard_repayment": {
            "monthly_payment_calc": "Use actual monthly payment",
            "citation": "Section 5501.1",
        },
    },

    # ----- LIABILITY TREATMENT -----
    "liabilities": {
        "cosigned_debt": {
            "include_in_dti": True,
            "exception": "May exclude if primary obligor has made last 12 months payments (documented)",
            "citation": "Section 5501.1",
        },
        "derogatory_events": {
            "bankruptcy_ch7": {"waiting_period_years": 4, "from": "discharge date", "citation": "Section 5202.3"},
            "bankruptcy_ch13": {"waiting_period_years": 2, "from": "discharge date", "citation": "Section 5202.3"},
            "foreclosure": {"waiting_period_years": 7, "with_extenuating": 3, "citation": "Section 5202.3"},
            "short_sale": {"waiting_period_years": 4, "with_extenuating": 2, "citation": "Section 5202.3"},
            "deed_in_lieu": {"waiting_period_years": 4, "with_extenuating": 2, "citation": "Section 5202.3"},
            "repossession": {"waiting_period_years": 4, "citation": "Section 5202.3"},
        },
    },

    # ----- GIFT FUNDS -----
    "gift_funds": {
        "eligible_donors": ["relative", "domestic partner", "employer", "government entity", "nonprofit"],
        "documentation_required": ["gift letter", "donor bank statement", "borrower bank statement showing deposit"],
        "foreign_gifts": {"allowed": True, "additional_docs": ["wire transfer", "foreign bank statement", "currency conversion docs"]},
        "citation": "Section 5501.2, Gift Funds",
    },

    # ----- NON-TAXABLE INCOME GROSS-UP -----
    "nontaxable_income_grossup": {
        "allowed": True,
        "default_factor": 1.25,
        "default_pct": "25%",
        "eligible_income_types": ["Social Security", "SSDI", "VA disability", "child support", "military allowances"],
        "citation": "Section 5301.1, Income Requirements",
    },

    # ----- ALIMONY / CHILD SUPPORT -----
    "alimony_child_support_income": {
        "alimony_as_income": {
            "can_use": True,
            "continuity_required": "Must continue for at least 3 years from closing",
            "documentation": ["divorce decree/court order", "12 months receipt history"],
            "citation": "Section 5301.1, Income Assessment",
        },
        "child_support_as_income": {
            "can_use": True,
            "continuity_required": "3 years from closing",
            "non_taxable": True,
            "grossup_eligible": True,
            "citation": "Section 5301.1",
        },
        "alimony_as_liability": {"always_included_in_dti": True, "citation": "Section 5501.1"},
    },

    # ----- INCOME TYPE RULES -----
    "income_rules": {
        "employment_history": {
            "standard_requirement": "2 years continuous employment",
            "gaps_allowed": "Yes, with LOE",
            "citation": "Section 5301.1",
        },
        "commission_income": {
            "requirement": "2 years history",
            "calculation_stable_or_increasing": "2-year average",
            "calculation_declining": "Use most recent year (lower)",
            "citation": "Section 5302.2, Variable Income",
        },
        "self_employment_income": {
            "requirement": "2 years (1 year with prior related employment)",
            "calculation": "Use Form 91 (Income Analysis) from tax returns",
            "declining_income": "Use most recent year if declining",
            "schedule_c_add_backs": ["depreciation", "depletion", "amortization", "business use of home"],
            "schedule_e_add_backs": ["depreciation", "amortization"],
            "form_used": "Freddie Mac Form 91 (Income Analysis)",
            "citation": "Section 5302.1, Self-Employment Income",
        },
        "rental_income_from_subject": {
            "can_use": True,
            "factor": 0.75,
            "formula": "75% of gross rent minus full PITIA = net rental income",
            "documentation": ["current lease agreements", "Form 72 (Appraisal)"],
            "citation": "Section 5306.1, Rental Income",
        },
        "rental_income_existing_properties": {
            "factor": 0.75,
            "formula": "75% of gross rent per Schedule E - PITIA = net rental income",
            "negative_cash_flow": "Net loss added to monthly obligations",
            "citation": "Section 5306.1",
        },
        "departure_residence": {
            "rental_income_allowed": True,
            "requirements": ["executed lease agreement", "evidence of security deposit"],
            "factor": 0.75,
            "formula": "75% of gross rent minus full PITIA",
            "if_no_lease": "Full PITIA counted as liability with zero offset",
            "citation": "Section 5306.1; Section 5501.1",
        },
        "asset_depletion_income": {
            "allowed": True,
            "eligible_assets": ["checking/savings", "stocks/bonds (use 70%)", "retirement (70% if under 59.5, 100% if over)"],
            "formula": "(Eligible assets - down payment - closing costs) / remaining loan term months",
            "citation": "Section 5305.1, Asset Income",
        },
        "social_security_income": {
            "can_use": True, "non_taxable": True, "grossup_eligible": True,
            "documentation": ["SSA award letter", "bank statement"],
            "citation": "Section 5301.1",
        },
        "pension_retirement_income": {
            "can_use": True,
            "documentation": ["award letter", "1099-R", "bank statements"],
            "citation": "Section 5301.1",
        },
        "va_disability_income": {
            "can_use": True, "non_taxable": True, "grossup_eligible": True, "grossup_factor": 1.25,
            "citation": "Section 5301.1",
        },
    },

    # ----- COLLECTIONS / CHARGE-OFFS -----
    "collections_chargeoffs": {
        "medical_collections": {"excluded_from_dti": True, "no_payoff_required": True, "citation": "Section 5202.1"},
        "non_medical_collections": {"excluded_from_dti": True, "notes": "LPA does not require payoff", "citation": "Section 5202.1"},
        "charge_offs": {"excluded_from_dti": True, "citation": "Section 5202.1"},
    },

    # ----- LOAN MODIFICATION SEASONING -----
    "loan_modification_seasoning": {
        "standard": {
            "waiting_period_months": 12,
            "payments_required": 6,
            "from": "effective date of modification",
            "citation": "Section 4301.2, Refinance Transactions",
        },
    },

    # ----- NON-OCCUPANT CO-BORROWER -----
    "non_occupant_coborrower": {
        "allowed": True,
        "max_ltv_1_unit": 95,
        "max_ltv_2_unit": 85,
        "income_can_be_used": True,
        "citation": "Section 4201.17, Non-Occupant Borrowers",
    },
}


# =============================================================================
# FHA RULES
# =============================================================================

FHA = {
    "agency": "FHA",
    "agency_code": "FHA",
    "source": "HUD Handbook 4000.1 (FHA Single Family Housing Policy Handbook)",

    "ltv_matrix": {
        "purchase": {
            "primary": {
                "1_unit": {
                    "credit_gte_580": {"max_ltv": 96.5, "max_cltv": 96.5, "citation": "HUD 4000.1, II.A.2.a", "notes": "3.5% minimum down payment"},
                    "credit_500_579": {"max_ltv": 90.0, "max_cltv": 90.0, "citation": "HUD 4000.1, II.A.2.a", "notes": "10% minimum down payment"},
                    "credit_below_500": {"max_ltv": 0, "max_cltv": 0, "citation": "HUD 4000.1, II.A.2.a", "notes": "NOT ELIGIBLE for FHA"},
                },
                "2_unit": {
                    "credit_gte_580": {"max_ltv": 96.5, "max_cltv": 96.5, "citation": "HUD 4000.1, II.A.2.a"},
                    "credit_500_579": {"max_ltv": 90.0, "max_cltv": 90.0, "citation": "HUD 4000.1, II.A.2.a"},
                },
                "3_4_unit": {
                    "credit_gte_580": {"max_ltv": 96.5, "max_cltv": 96.5, "citation": "HUD 4000.1, II.A.2.a"},
                    "credit_500_579": {"max_ltv": 90.0, "max_cltv": 90.0, "citation": "HUD 4000.1, II.A.2.a"},
                },
                "condo": {
                    "credit_gte_580": {"max_ltv": 96.5, "max_cltv": 96.5, "citation": "HUD 4000.1, II.A.2.a"},
                },
                "manufactured": {
                    "credit_gte_580": {"max_ltv": 96.5, "max_cltv": 96.5, "citation": "HUD 4000.1, II.A.8.e", "notes": "Must be on permanent foundation, titled as real property"},
                },
            },
            "primary_non_occupant_coborrower": {
                "1_unit": {
                    "family_member": {"max_ltv": 96.5, "max_cltv": 96.5, "citation": "HUD 4000.1, II.A.2.a", "notes": "Family member non-occ co-borrower: same LTV as owner-occupied for 1-unit"},
                },
                "2_unit": {
                    "any": {"max_ltv": 75, "max_cltv": 75, "citation": "HUD 4000.1, II.A.2.a", "notes": "Non-occupant co-borrower on 2+ units: 75% max LTV"},
                },
                "3_4_unit": {
                    "any": {"max_ltv": 75, "max_cltv": 75, "citation": "HUD 4000.1, II.A.2.a"},
                },
            },
        },
        "rate_term_refi": {
            "primary": {
                "1_4_unit": {
                    "standard": {"max_ltv": 97.75, "max_cltv": 97.75, "citation": "HUD 4000.1, II.A.2.c", "notes": "Includes UFMIP in loan amount"},
                },
            },
        },
        "cash_out_refi": {
            "primary": {
                "1_4_unit": {
                    "standard": {"max_ltv": 80, "max_cltv": 80, "citation": "HUD 4000.1, II.A.2.d", "notes": "Must have owned and occupied 12+ months"},
                },
            },
        },
        "streamline_refi": {
            "primary": {
                "all": {
                    "standard": {"max_ltv": None, "citation": "HUD 4000.1, II.A.2.b", "notes": "No LTV cap for FHA Streamline Refinance. No appraisal required for non-credit qualifying."},
                },
            },
        },
    },

    "dti": {
        "total_scorecard_approve": {
            "max_dti": 56.99,
            "citation": "HUD 4000.1, II.A.5.a, TOTAL Mortgage Scorecard",
            "notes": "TOTAL Scorecard may approve up to 56.99% (just under 57%)"
        },
        "manual_standard": {
            "front_end": 31,
            "back_end": 43,
            "citation": "HUD 4000.1, II.A.5.d, Manual Underwriting",
            "notes": "Standard manual ratios: 31% housing / 43% total"
        },
        "manual_with_compensating": {
            "front_end": 40,
            "back_end": 50,
            "citation": "HUD 4000.1, II.A.5.d",
            "notes": "With compensating factors: up to 40% / 50%"
        },
        "manual_energy_efficient": {
            "front_end": 33,
            "back_end": 45,
            "citation": "HUD 4000.1, II.A.5.d",
            "notes": "Energy Efficient Homes stretch ratios +2%"
        },
    },

    "credit_score": {
        "minimum_580": {
            "min_score": 580,
            "max_ltv": 96.5,
            "citation": "HUD 4000.1, II.A.2.a",
            "notes": "580+ score = 3.5% down payment"
        },
        "minimum_500": {
            "min_score": 500,
            "max_ltv": 90,
            "citation": "HUD 4000.1, II.A.2.a",
            "notes": "500-579 score = 10% down payment"
        },
        "below_500": {
            "eligible": False,
            "citation": "HUD 4000.1, II.A.2.a",
            "notes": "Below 500 = NOT eligible for FHA"
        },
        "manual_underwriting_minimums": {
            "min_score_with_no_discretionary_debt": 500,
            "min_score_standard": 580,
            "citation": "HUD 4000.1, II.A.5.d"
        },
    },

    # ----- MIP (Mortgage Insurance Premium) -----
    "mip": {
        "upfront_mip": {
            "rate": 1.75,
            "unit": "percent of base loan amount",
            "can_be_financed": True,
            "citation": "HUD 4000.1, I.A.5.b, UFMIP",
            "notes": "1.75% UFMIP applies to all FHA purchase and most refi loans"
        },
        "annual_mip": {
            "term_gt_15yr": [
                {"base_loan_max": 726200, "ltv_min": 0,     "ltv_max": 90,    "annual_rate": 0.50, "duration": "11 years", "citation": "HUD 4000.1, I.A.5.c"},
                {"base_loan_max": 726200, "ltv_min": 90.01, "ltv_max": 95,    "annual_rate": 0.50, "duration": "Life of loan", "citation": "HUD 4000.1, I.A.5.c"},
                {"base_loan_max": 726200, "ltv_min": 95.01, "ltv_max": 100,   "annual_rate": 0.55, "duration": "Life of loan", "citation": "HUD 4000.1, I.A.5.c"},
                {"base_loan_max": None,   "ltv_min": 0,     "ltv_max": 90,    "annual_rate": 0.70, "duration": "11 years", "citation": "HUD 4000.1, I.A.5.c"},
                {"base_loan_max": None,   "ltv_min": 90.01, "ltv_max": 95,    "annual_rate": 0.70, "duration": "Life of loan", "citation": "HUD 4000.1, I.A.5.c"},
                {"base_loan_max": None,   "ltv_min": 95.01, "ltv_max": 100,   "annual_rate": 0.75, "duration": "Life of loan", "citation": "HUD 4000.1, I.A.5.c"},
            ],
            "term_lte_15yr": [
                {"base_loan_max": 726200, "ltv_min": 0,     "ltv_max": 90,    "annual_rate": 0.15, "duration": "11 years", "citation": "HUD 4000.1, I.A.5.c"},
                {"base_loan_max": 726200, "ltv_min": 90.01, "ltv_max": 100,   "annual_rate": 0.40, "duration": "Life of loan", "citation": "HUD 4000.1, I.A.5.c"},
                {"base_loan_max": None,   "ltv_min": 0,     "ltv_max": 78,    "annual_rate": 0.15, "duration": "11 years", "citation": "HUD 4000.1, I.A.5.c"},
                {"base_loan_max": None,   "ltv_min": 78.01, "ltv_max": 90,    "annual_rate": 0.40, "duration": "11 years", "citation": "HUD 4000.1, I.A.5.c"},
                {"base_loan_max": None,   "ltv_min": 90.01, "ltv_max": 100,   "annual_rate": 0.65, "duration": "Life of loan", "citation": "HUD 4000.1, I.A.5.c"},
            ],
        },
        "streamline_refi_mip": {
            "upfront": 0.01,
            "annual": "Reduced (case-by-case based on original endorsement date)",
            "citation": "HUD 4000.1, II.A.2.b",
        },
    },

    "property": {
        "eligible": [
            "1-4 unit residential",
            "HUD-approved condominiums",
            "Manufactured housing (permanent foundation, real property title)",
            "Mixed-use (51%+ residential square footage)",
        ],
        "ineligible": [
            "Investment properties (FHA is owner-occupied only)",
            "Vacation/second homes",
            "Properties with health/safety deficiencies not corrected before closing",
        ],
        "citation": "HUD 4000.1, II.A.1",
    },

    "special_programs": {
        "fha_203k_standard": {
            "max_ltv": 96.5,
            "min_repair_cost": 5000,
            "max_repair_cost": "FHA loan limit for area",
            "requires_consultant": True,
            "citation": "HUD 4000.1, II.A.8.h, Section 203(k)",
        },
        "fha_203k_limited": {
            "max_ltv": 96.5,
            "max_repair_cost": 35000,
            "requires_consultant": False,
            "citation": "HUD 4000.1, II.A.8.h",
        },
        "streamline_refi": {
            "appraisal_required": False,
            "income_verification": "Not required for non-credit qualifying",
            "net_tangible_benefit": "Required (reduction in monthly payment)",
            "seasoning": "210 days from closing / 6 payments made",
            "citation": "HUD 4000.1, II.A.2.b",
        },
    },

    "loan_limits": {
        "floor_1_unit": 498257,
        "ceiling_1_unit": 1149825,
        "notes": "FHA limits are 65% of conforming limit (floor) to 150% (ceiling/high-cost)",
        "citation": "HUD 4000.1, II.A.2, Annual FHA Loan Limits",
    },

    "occupancy": {
        "primary_only": True,
        "notes": "FHA does NOT allow second homes or investment properties",
        "citation": "HUD 4000.1, II.A.1.a",
    },

    # ----- STUDENT LOAN DTI TREATMENT -----
    "student_loans": {
        "deferred_or_ibr": {
            "monthly_payment_calc": "1% of outstanding balance OR actual documented payment, whichever is greater",
            "if_no_payment_reported": "Use 1% of outstanding balance",
            "if_ibr_payment_greater_than_zero": "Use actual IBR/IDR/PAYE payment if documented and > $0",
            "if_ibr_payment_is_zero": "Use 1% of outstanding balance (cannot use $0)",
            "fully_deferred": "Use 1% of outstanding balance",
            "forbearance": "Use 1% of outstanding balance",
            "citation": "HUD 4000.1, II.A.4.c.ii(E), Student Loans",
            "notes": "FHA uses 1% (NOT 0.5% like conventional). If the payment is income-driven and > $0, the actual payment may be used. If the IDR payment is $0, must use 1% of balance."
        },
        "standard_repayment": {
            "monthly_payment_calc": "Use actual monthly payment from credit report or documentation",
            "citation": "HUD 4000.1, II.A.4.c.ii(E)",
        },
    },

    # ----- LIABILITY TREATMENT -----
    "liabilities": {
        "cosigned_debt": {
            "include_in_dti": True,
            "exception": "May exclude if documentation shows another party has made payments for last 12 months",
            "citation": "HUD 4000.1, II.A.4.c.ii",
        },
        "derogatory_events": {
            "bankruptcy_ch7": {"waiting_period_years": 2, "from": "discharge date", "citation": "HUD 4000.1, II.A.4.a.iv(A)"},
            "bankruptcy_ch13": {"waiting_period_years": 1, "from": "payout period start", "notes": "Must have 12 months of satisfactory payments and court approval", "citation": "HUD 4000.1, II.A.4.a.iv(A)"},
            "foreclosure": {"waiting_period_years": 3, "from": "deed transfer or sheriff sale", "citation": "HUD 4000.1, II.A.4.a.iv(B)"},
            "short_sale": {"waiting_period_years": 3, "citation": "HUD 4000.1, II.A.4.a.iv(B)", "notes": "Treated as pre-foreclosure sale"},
            "deed_in_lieu": {"waiting_period_years": 3, "citation": "HUD 4000.1, II.A.4.a.iv(B)"},
            "repossession": {"waiting_period_years": 0, "citation": "HUD 4000.1, II.A.4.a", "notes": "FHA does not have a specific waiting period for repossession, but it must be addressed in LOE and credit analysis"},
        },
    },

    # ----- GIFT FUNDS -----
    "gift_funds": {
        "eligible_donors": ["family member", "employer", "labor union", "close friend (with LOE)", "government agency", "nonprofit"],
        "min_borrower_own_funds": "None for FHA — 100% of down payment can be gift",
        "interested_party_contributions": {
            "ltv_gt_90": {"max_pct": 6, "citation": "HUD 4000.1, II.A.4.d.iii"},
            "ltv_lte_90": {"max_pct": 6, "citation": "HUD 4000.1, II.A.4.d.iii"},
        },
        "documentation_required": ["gift letter", "donor bank statement", "transfer evidence"],
        "foreign_gifts": {"allowed": True, "additional_docs": ["wire transfer", "foreign bank statement", "currency conversion"]},
        "citation": "HUD 4000.1, II.A.4.d.iii, Gift Funds",
    },

    # ----- NON-TAXABLE INCOME GROSS-UP -----
    "nontaxable_income_grossup": {
        "allowed": True,
        "default_factor": 1.25,
        "default_pct": "25%",
        "eligible_income_types": ["Social Security", "SSDI", "VA disability", "child support", "military allowances", "certain pension income"],
        "citation": "HUD 4000.1, II.A.4.c.i(B), Income Adjustments",
    },

    # ----- ALIMONY / CHILD SUPPORT -----
    "alimony_child_support_income": {
        "alimony_as_income": {
            "can_use": True,
            "continuity_required": "Must continue for at least 3 years from closing",
            "documentation": ["divorce decree", "court order", "12 months receipt history"],
            "citation": "HUD 4000.1, II.A.4.c.ii(D), Alimony",
        },
        "child_support_as_income": {
            "can_use": True,
            "continuity_required": "3 years from closing",
            "non_taxable": True,
            "grossup_eligible": True,
            "citation": "HUD 4000.1, II.A.4.c.ii(D)",
        },
        "alimony_as_liability": {"always_included_in_dti": True, "citation": "HUD 4000.1, II.A.4.c.ii"},
    },

    # ----- INCOME TYPE RULES -----
    "income_rules": {
        "employment_history": {
            "standard_requirement": "2 years continuous employment",
            "gaps_allowed": "Yes, with LOE; gaps > 6 months require re-establishment of employment for 6+ months",
            "citation": "HUD 4000.1, II.A.4.c.i, Employment Requirements",
        },
        "commission_income": {
            "requirement": "2 years history",
            "calculation_stable_or_increasing": "2-year average",
            "calculation_declining": "Use most recent year",
            "citation": "HUD 4000.1, II.A.4.c.i(F), Commission Income",
        },
        "self_employment_income": {
            "requirement": "2 years (1 year with strong compensating factors)",
            "calculation": "Net income from tax returns after add-backs",
            "declining_income": "Use most recent year if declining",
            "schedule_c_add_backs": ["depreciation", "depletion", "amortization", "business use of home"],
            "schedule_e_add_backs": ["depreciation", "amortization"],
            "citation": "HUD 4000.1, II.A.4.c.i(G), Self-Employment Income",
        },
        "rental_income_from_subject": {
            "can_use": True,
            "factor": 0.75,
            "formula": "75% of gross monthly rent minus PITIA = net rental income for qualifying",
            "self_sufficiency_test": {
                "applies_to": "3-4 unit properties",
                "formula": "Monthly PITIA must not exceed 75% of total gross rental income from ALL units (including borrower's unit at market rent)",
                "citation": "HUD 4000.1, II.A.8.d, Self-Sufficiency Rental Income",
            },
            "documentation": ["current lease agreements", "appraisal with rental survey"],
            "citation": "HUD 4000.1, II.A.4.c.ii(H), Rental Income",
        },
        "departure_residence": {
            "rental_income_allowed": True,
            "requirements": ["executed lease agreement", "security deposit evidence"],
            "factor": 0.75,
            "formula": "75% of gross rent minus full PITIA",
            "if_no_lease": "Full PITIA counted as liability",
            "citation": "HUD 4000.1, II.A.4.c.ii(H)",
        },
        "asset_depletion_income": {
            "allowed": False,
            "notes": "FHA does NOT allow asset depletion as qualifying income",
            "citation": "HUD 4000.1, II.A.4.c",
        },
        "social_security_income": {
            "can_use": True, "non_taxable": True, "grossup_eligible": True,
            "documentation": ["SSA award letter", "bank statements"],
            "citation": "HUD 4000.1, II.A.4.c.ii(C)",
        },
        "pension_retirement_income": {
            "can_use": True,
            "documentation": ["award letter", "1099-R", "bank statements"],
            "citation": "HUD 4000.1, II.A.4.c.ii(C)",
        },
    },

    # ----- COLLECTIONS / CHARGE-OFFS -----
    "collections_chargeoffs": {
        "medical_collections": {
            "excluded_from_dti": True,
            "no_payoff_required": True,
            "no_amount_limit": True,
            "citation": "HUD 4000.1, II.A.4.a.iv(F), Medical Collections",
        },
        "non_medical_collections": {
            "cumulative_threshold": 2000,
            "if_over_threshold": "Must pay off OR establish payment plan (5% of balance/month added to DTI)",
            "if_under_threshold": "No payoff or payment plan required",
            "citation": "HUD 4000.1, II.A.4.a.iv(F), Collections/Charge-Offs",
        },
        "charge_offs": {
            "cumulative_threshold": 2000,
            "same_as_collections": True,
            "citation": "HUD 4000.1, II.A.4.a.iv(F)",
        },
        "disputed_accounts": {
            "if_over_1000": "Must provide LOE; may affect TOTAL Scorecard",
            "citation": "HUD 4000.1, II.A.4.a.iv(F)",
        },
    },

    # ----- NON-OCCUPANT CO-BORROWER -----
    "non_occupant_coborrower": {
        "allowed": True,
        "max_ltv_1_unit_family": 96.5,
        "max_ltv_1_unit_non_family": 75,
        "max_ltv_2_4_unit": 75,
        "relationship_for_high_ltv": "Family member only for 96.5% LTV",
        "identity_of_interest": {
            "max_ltv": 85,
            "exceptions": ["family member purchasing primary residence", "tenant purchasing unit they rent"],
            "citation": "HUD 4000.1, II.A.2.a",
        },
        "citation": "HUD 4000.1, II.A.2.a, Non-Occupying Borrower",
    },
}


# =============================================================================
# VA RULES
# =============================================================================

VA = {
    "agency": "VA",
    "agency_code": "VA",
    "source": "VA Pamphlet 26-7, VA Lender's Handbook",

    "ltv_matrix": {
        "purchase": {
            "primary": {
                "1_4_unit": {
                    "standard": {"max_ltv": 100, "max_cltv": 100, "citation": "VA Pamphlet 26-7, Ch. 3", "notes": "No down payment required (100% financing)"},
                },
            },
        },
        "rate_term_refi": {
            "primary": {
                "1_4_unit": {
                    "standard": {"max_ltv": 100, "max_cltv": 100, "citation": "VA Pamphlet 26-7, Ch. 6", "notes": "Can include funding fee and closing costs"},
                },
            },
        },
        "cash_out_refi": {
            "primary": {
                "1_4_unit": {
                    "standard": {"max_ltv": 100, "max_cltv": 100, "citation": "VA Pamphlet 26-7, Ch. 6", "notes": "100% cash-out refinance available"},
                },
            },
        },
        "irrrl": {
            "primary": {
                "all": {
                    "standard": {"max_ltv": None, "citation": "VA Pamphlet 26-7, Ch. 6", "notes": "No LTV cap for IRRRL. No appraisal required. Must result in lower rate or convert ARM to fixed."},
                },
            },
        },
    },

    "dti": {
        "standard": {
            "max_dti": 41,
            "citation": "VA Pamphlet 26-7, Ch. 4, Section 4.d",
            "notes": "41% is guideline, not hard cap. Can exceed with residual income."
        },
        "residual_income_override": {
            "max_dti": None,
            "citation": "VA Pamphlet 26-7, Ch. 4",
            "notes": "VA primarily uses residual income test. DTI above 41% acceptable if residual income exceeds minimum by 20%+."
        },
    },

    "credit_score": {
        "va_minimum": {
            "min_score": None,
            "citation": "VA Pamphlet 26-7, Ch. 4",
            "notes": "VA does NOT set a minimum credit score. Most lenders overlay 580-620 minimum."
        },
        "lender_overlays_typical": {
            "min_score": 620,
            "notes": "Common lender overlay, not a VA requirement"
        },
    },

    # ----- VA FUNDING FEE -----
    "funding_fee": {
        "purchase_first_use": [
            {"down_pct_min": 0,    "down_pct_max": 4.99,  "fee_pct": 2.15, "citation": "VA Pamphlet 26-7, Ch. 8"},
            {"down_pct_min": 5,    "down_pct_max": 9.99,  "fee_pct": 1.50, "citation": "VA Pamphlet 26-7, Ch. 8"},
            {"down_pct_min": 10,   "down_pct_max": 100,   "fee_pct": 1.25, "citation": "VA Pamphlet 26-7, Ch. 8"},
        ],
        "purchase_subsequent_use": [
            {"down_pct_min": 0,    "down_pct_max": 4.99,  "fee_pct": 3.30, "citation": "VA Pamphlet 26-7, Ch. 8"},
            {"down_pct_min": 5,    "down_pct_max": 9.99,  "fee_pct": 1.50, "citation": "VA Pamphlet 26-7, Ch. 8"},
            {"down_pct_min": 10,   "down_pct_max": 100,   "fee_pct": 1.25, "citation": "VA Pamphlet 26-7, Ch. 8"},
        ],
        "cash_out_refi_first_use": {"fee_pct": 2.15, "citation": "VA Pamphlet 26-7, Ch. 8"},
        "cash_out_refi_subsequent": {"fee_pct": 3.30, "citation": "VA Pamphlet 26-7, Ch. 8"},
        "irrrl": {"fee_pct": 0.50, "citation": "VA Pamphlet 26-7, Ch. 8"},
        "reserves_national_guard": {
            "notes": "Reservists/National Guard: add 0.15% to first-use rates (removed as of 2020 for most)",
        },
        "exempt_from_funding_fee": [
            "Veterans receiving VA disability compensation",
            "Veterans rated eligible for compensation but receiving retirement pay",
            "Surviving spouses of veterans who died in service or from service-connected disability",
            "Active duty Purple Heart recipients",
        ],
        "can_be_financed": True,
        "citation": "VA Pamphlet 26-7, Ch. 8",
    },

    # ----- VA RESIDUAL INCOME REQUIREMENTS -----
    "residual_income": {
        "description": "VA requires minimum residual income after all obligations. Amount varies by region, family size, and loan amount.",
        "regions": {
            "northeast": {"states": ["CT", "MA", "ME", "NH", "NJ", "NY", "PA", "RI", "VT"]},
            "midwest": {"states": ["IA", "IL", "IN", "KS", "MI", "MN", "MO", "ND", "NE", "OH", "SD", "WI"]},
            "south": {"states": ["AL", "AR", "DC", "DE", "FL", "GA", "KY", "LA", "MD", "MS", "NC", "OK", "PR", "SC", "TN", "TX", "VA", "VI", "WV"]},
            "west": {"states": ["AK", "AZ", "CA", "CO", "HI", "ID", "MT", "NM", "NV", "OR", "UT", "WA", "WY"]},
        },
        "minimums_loan_under_80k": {
            "family_1": {"northeast": 390, "midwest": 382, "south": 382, "west": 425},
            "family_2": {"northeast": 654, "midwest": 641, "south": 641, "west": 713},
            "family_3": {"northeast": 788, "midwest": 772, "south": 772, "west": 859},
            "family_4": {"northeast": 888, "midwest": 868, "south": 868, "west": 967},
            "family_5_plus_add": {"northeast": 75, "midwest": 75, "south": 75, "west": 80},
        },
        "minimums_loan_80k_plus": {
            "family_1": {"northeast": 450, "midwest": 441, "south": 441, "west": 491},
            "family_2": {"northeast": 755, "midwest": 738, "south": 738, "west": 823},
            "family_3": {"northeast": 909, "midwest": 889, "south": 889, "west": 990},
            "family_4": {"northeast": 1025, "midwest": 1003, "south": 1003, "west": 1117},
            "family_5_plus_add": {"northeast": 80, "midwest": 80, "south": 80, "west": 90},
        },
        "citation": "VA Pamphlet 26-7, Ch. 4, Table 4.c",
    },

    "property": {
        "eligible": [
            "1-4 unit residential (veteran must occupy one unit)",
            "VA-approved condominiums",
            "Manufactured housing (permanent foundation, meets VA MPRs)",
            "Farms (with residential dwelling)",
            "Lots with construction loans (one-time close)",
        ],
        "ineligible": [
            "Investment properties (must be owner-occupied)",
            "Vacation/second homes",
            "Properties not meeting VA Minimum Property Requirements (MPRs)",
        ],
        "citation": "VA Pamphlet 26-7, Ch. 12",
    },

    "special_programs": {
        "irrrl": {
            "full_name": "Interest Rate Reduction Refinancing Loan",
            "appraisal_required": False,
            "income_verification": "Not required",
            "credit_qualifying": "Not required (non-credit qualifying option)",
            "net_tangible_benefit": "Required (lower rate or ARM-to-fixed)",
            "max_loan_amount": "Existing VA loan balance + funding fee + up to 2 discount points",
            "seasoning": "210 days from first payment",
            "citation": "VA Pamphlet 26-7, Ch. 6",
        },
        "native_american_direct_loan": {
            "description": "VA direct loan for Native American veterans on trust land",
            "citation": "VA Pamphlet 26-7, Ch. 16",
        },
        "adapted_housing": {
            "description": "Specially Adapted Housing (SAH) and Special Housing Adaptation (SHA) grants",
            "citation": "VA Pamphlet 26-7, Ch. 15",
        },
    },

    "entitlement": {
        "basic_entitlement": 36000,
        "bonus_entitlement": "Available for loans above $144,000",
        "full_entitlement": {
            "description": "No loan limit for veterans with full entitlement (post Blue Water Navy Act 2020)",
            "citation": "VA Pamphlet 26-7, Ch. 3",
        },
        "partial_entitlement": {
            "description": "County loan limits apply when partial entitlement used",
            "citation": "VA Pamphlet 26-7, Ch. 3",
        },
    },

    "occupancy": {
        "primary_only": True,
        "notes": "Veteran must certify intent to occupy as primary residence. May rent out other units in 2-4 unit.",
        "citation": "VA Pamphlet 26-7, Ch. 3",
    },

    # ----- STUDENT LOAN DTI TREATMENT -----
    "student_loans": {
        "deferred_or_ibr": {
            "monthly_payment_calc": "Use actual monthly payment. If $0 or deferred, use 5% of balance divided by 12",
            "if_no_payment_reported": "5% of outstanding balance / 12",
            "if_ibr_payment_is_zero": "5% of outstanding balance / 12",
            "fully_deferred": "5% of outstanding balance / 12",
            "forbearance": "5% of outstanding balance / 12",
            "citation": "VA Pamphlet 26-7, Ch. 4, Section 9.e",
            "notes": "VA uses 5% of balance divided by 12 months as the estimated payment when deferred. This is different from conventional (0.5%) and FHA (1%)."
        },
        "standard_repayment": {
            "monthly_payment_calc": "Use actual monthly payment",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
    },

    # ----- LIABILITY TREATMENT -----
    "liabilities": {
        "cosigned_debt": {
            "include_in_dti": True,
            "exception": "May exclude if evidence shows other party has been making payments for 12 months",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "derogatory_events": {
            "bankruptcy_ch7": {"waiting_period_years": 2, "from": "discharge date", "citation": "VA Pamphlet 26-7, Ch. 4", "notes": "Veteran must have re-established satisfactory credit"},
            "bankruptcy_ch13": {"waiting_period_years": 1, "from": "payout period start", "notes": "12 months of satisfactory payments required", "citation": "VA Pamphlet 26-7, Ch. 4"},
            "foreclosure": {"waiting_period_years": 2, "from": "completion date", "citation": "VA Pamphlet 26-7, Ch. 4"},
            "short_sale": {"waiting_period_years": 2, "citation": "VA Pamphlet 26-7, Ch. 4"},
            "deed_in_lieu": {"waiting_period_years": 2, "citation": "VA Pamphlet 26-7, Ch. 4"},
            "repossession": {"waiting_period_years": 0, "citation": "VA Pamphlet 26-7, Ch. 4", "notes": "No specific waiting period but must show satisfactory credit re-established"},
        },
    },

    # ----- NON-TAXABLE INCOME GROSS-UP -----
    "nontaxable_income_grossup": {
        "allowed": True,
        "default_factor": 1.25,
        "default_pct": "25%",
        "eligible_income_types": ["VA disability compensation", "Social Security", "SSDI", "child support", "military allowances (BAH, BAS)", "combat pay"],
        "citation": "VA Pamphlet 26-7, Ch. 4, Section 3",
    },

    # ----- ALIMONY / CHILD SUPPORT -----
    "alimony_child_support_income": {
        "alimony_as_income": {
            "can_use": True,
            "continuity_required": "Must be received for 12 months and likely to continue",
            "documentation": ["divorce decree/court order", "12 months receipt history"],
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "child_support_as_income": {
            "can_use": True,
            "continuity_required": "Likely to continue for at least 3 years",
            "non_taxable": True,
            "grossup_eligible": True,
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "alimony_as_liability": {"always_included_in_dti": True, "citation": "VA Pamphlet 26-7, Ch. 4"},
    },

    # ----- INCOME TYPE RULES -----
    "income_rules": {
        "employment_history": {
            "standard_requirement": "2 years (flexible for military-to-civilian transitions)",
            "military_transition": "Service members transitioning to civilian jobs: military service counts toward employment history",
            "citation": "VA Pamphlet 26-7, Ch. 4, Section 2",
        },
        "commission_income": {
            "requirement": "2 years history",
            "calculation_stable_or_increasing": "2-year average",
            "calculation_declining": "Use most recent year (lower)",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "self_employment_income": {
            "requirement": "2 years",
            "calculation": "Net income from tax returns with add-backs",
            "declining_income": "Use most recent year if declining",
            "schedule_c_add_backs": ["depreciation", "depletion", "amortization"],
            "schedule_e_add_backs": ["depreciation", "amortization"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Section 7",
        },
        "rental_income_from_subject": {
            "can_use": True,
            "factor": 0.75,
            "formula": "75% of gross rent minus PITIA = net rental income",
            "documentation": ["current lease agreements", "appraisal"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Section 8",
        },
        "departure_residence": {
            "rental_income_allowed": True,
            "requirements": ["executed lease", "security deposit evidence"],
            "factor": 0.75,
            "formula": "75% of gross rent minus full PITIA",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "military_income": {
            "base_pay": {"can_use": True, "documentation": "LES (Leave and Earnings Statement)"},
            "bah": {"can_use": True, "non_taxable": True, "grossup_eligible": True},
            "bas": {"can_use": True, "non_taxable": True, "grossup_eligible": True},
            "combat_pay": {"can_use": True, "non_taxable": True, "grossup_eligible": True, "must_be_likely_to_continue": True},
            "flight_pay": {"can_use": True},
            "hazard_pay": {"can_use": True},
            "citation": "VA Pamphlet 26-7, Ch. 4, Section 2",
        },
        "va_disability_income": {
            "can_use": True,
            "non_taxable": True,
            "grossup_eligible": True,
            "grossup_factor": 1.25,
            "documentation": ["VA benefit/award letter", "bank statements"],
            "also_exempts_funding_fee": True,
            "citation": "VA Pamphlet 26-7, Ch. 4; Ch. 8 (Funding Fee Exemption)",
        },
        "social_security_income": {
            "can_use": True, "non_taxable": True, "grossup_eligible": True,
            "documentation": ["SSA award letter", "bank statements"],
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "pension_retirement_income": {
            "can_use": True,
            "documentation": ["award letter", "1099-R", "bank statements"],
            "military_retirement": {
                "can_use": True,
                "documentation": "Retiree Account Statement (RAS) or DD-214 + retirement order",
                "concurrent_receipt": "Veterans may receive both military retirement and VA disability simultaneously",
            },
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "asset_depletion_income": {
            "allowed": False,
            "notes": "VA does NOT recognize asset depletion as qualifying income",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
    },

    # ----- COLLECTIONS / CHARGE-OFFS -----
    "collections_chargeoffs": {
        "medical_collections": {"excluded_from_dti": True, "citation": "VA Pamphlet 26-7, Ch. 4"},
        "non_medical_collections": {
            "not_required_to_payoff": True,
            "notes": "VA does not require payoff of collections, but lender must comment on overall credit pattern",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "charge_offs": {"not_required_to_payoff": True, "citation": "VA Pamphlet 26-7, Ch. 4"},
    },

    # ----- COMMUNITY PROPERTY / NON-BORROWING SPOUSE -----
    "non_borrowing_spouse": {
        "community_property_states": {
            "applies_when": "Veteran is married and spouse is NOT on the loan, in a community property state",
            "spouse_debts_in_dti": True,
            "spouse_credit_score_used": False,
            "spouse_income_cannot_be_used": "Unless spouse is on the loan",
            "citation": "VA Pamphlet 26-7, Ch. 4, Section 5",
            "notes": "In community property states, all of the non-borrowing spouse's debts must be included in the veteran's DTI, but the spouse's credit score is NOT used for qualifying.",
        },
        "non_community_property_states": {
            "spouse_debts_in_dti": False,
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
    },

    # ----- NON-OCCUPANT CO-BORROWER -----
    "non_occupant_coborrower": {
        "allowed": "Only spouse or another eligible veteran",
        "civilian_non_occupant": "Not allowed on VA loans",
        "citation": "VA Pamphlet 26-7, Ch. 3",
    },
}


# =============================================================================
# CROSS-AGENCY DETERMINISTIC RULES
# =============================================================================

# Community property states — affects DTI for married borrowers
COMMUNITY_PROPERTY_STATES = {
    "states": ["AZ", "CA", "ID", "LA", "NV", "NM", "TX", "WA", "WI"],
    "state_names": ["Arizona", "California", "Idaho", "Louisiana", "Nevada", "New Mexico", "Texas", "Washington", "Wisconsin"],
    "rule": "In community property states, debts of non-borrowing spouse MUST be included in DTI calculation even if spouse is not on the loan",
    "credit_score_impact": "Non-borrowing spouse's credit score is NOT used for qualifying (VA, FHA). Conventional may pull spouse credit for community property debt verification.",
    "applies_to": {
        "VA": "All community property state debts included in DTI; spouse credit not used",
        "FHA": "Non-borrowing spouse debts included; credit report pulled but score not used for qualifying",
        "Fannie Mae": "Non-borrowing spouse debts may need to be included; depends on state law and title",
        "Freddie Mac": "Same as Fannie Mae",
    },
    "citation": "VA Pamphlet 26-7, Ch. 4; HUD 4000.1, II.A.4; Fannie Mae B2-2-04",
}

# Non-taxable income gross-up — universal across all agencies
NONTAXABLE_GROSSUP = {
    "universal_factor": 1.25,
    "universal_pct": "25%",
    "rule": "Non-taxable income may be grossed up by 25% (or actual tax rate if documented) to account for the borrower not paying taxes on that income",
    "eligible_types": [
        "Social Security (retirement, survivor)",
        "SSDI (Social Security Disability)",
        "VA disability compensation",
        "Child support (always non-taxable)",
        "Alimony (non-taxable for divorces finalized after 12/31/2018)",
        "Military allowances (BAH, BAS, combat pay)",
        "Municipal bond interest",
        "Certain pension/retirement income (non-taxable portion)",
    ],
    "not_eligible": [
        "W-2 employment income",
        "Self-employment income",
        "Rental income",
        "Commission income",
        "Alimony from pre-2019 divorces (taxable)",
    ],
    "citation": "Fannie B3-3.1-01; Freddie Section 5301.1; HUD 4000.1 II.A.4.c.i(B); VA Pamphlet 26-7 Ch.4",
}

# Asset depletion eligibility by agency
ASSET_DEPLETION_RULES = {
    "Fannie Mae": {
        "allowed": True,
        "formula": "(Eligible assets - down payment - closing costs) / remaining loan term months",
        "eligible_assets": ["checking/savings (100%)", "stocks/bonds/mutual funds (70% of value)", "retirement accounts (70% if under 59.5, 100% if over 59.5)", "vested stock options"],
        "ineligible_assets": ["business assets", "non-vested RSUs", "529 plans", "life insurance cash value (unless documented)"],
        "age_note": "DU may require borrower be at least 62; manual UW has no age requirement",
        "citation": "B3-3.1-09; B3-4.3-19",
    },
    "Freddie Mac": {
        "allowed": True,
        "formula": "(Eligible assets - down payment - closing costs) / remaining loan term months",
        "eligible_assets": ["checking/savings (100%)", "stocks/bonds (70%)", "retirement (70% if under 59.5, 100% if over)"],
        "citation": "Section 5305.1",
    },
    "FHA": {
        "allowed": False,
        "notes": "FHA does NOT allow asset depletion as qualifying income",
        "citation": "HUD 4000.1, II.A.4.c",
    },
    "VA": {
        "allowed": False,
        "notes": "VA does NOT recognize asset depletion as qualifying income",
        "citation": "VA Pamphlet 26-7, Ch. 4",
    },
}

# Rental income factors — universal
RENTAL_INCOME_RULES = {
    "vacancy_factor": 0.75,
    "vacancy_pct": "25%",
    "rule": "All agencies use 75% of gross rent (25% vacancy/maintenance factor) for qualifying",
    "formula": "75% of gross monthly rent - PITIA = net rental income (or loss)",
    "negative_result": "If net is negative, the loss is added to borrower's monthly obligations (increases DTI)",
    "subject_property": {
        "owner_occupied_multi_unit": "Can use rental income from units borrower does NOT occupy",
        "investment_property": "Can use projected rent from all units",
        "documentation": ["current lease agreements", "appraisal with rental survey (Form 1025 Fannie, Form 72 Freddie)"],
    },
    "existing_rental_properties": {
        "documentation": ["Schedule E (2-year tax return history)", "current lease agreements"],
        "depreciation_add_back": True,
        "notes": "Depreciation from Schedule E is added back to rental income (non-cash expense)",
    },
    "departure_residence": {
        "rule": "Primary residence being vacated can be counted as rental IF executed lease is provided",
        "with_lease": "75% of gross rent minus PITIA = net rental offset",
        "without_lease": "Full PITIA counted as liability with ZERO rental income offset",
    },
    "fha_self_sufficiency": {
        "applies_to": "FHA 3-4 unit properties",
        "test": "Total PITIA must not exceed 75% of total gross rental income from ALL units (including borrower's at market rent)",
        "citation": "HUD 4000.1, II.A.8.d",
    },
    "citation": "Fannie B3-3.1-08; Freddie Section 5306.1; HUD 4000.1 II.A.4.c.ii(H); VA Pamphlet 26-7 Ch.4",
}

# Collections & charge-offs treatment by agency
COLLECTIONS_RULES = {
    "Fannie Mae": {
        "medical_collections": "Excluded from DTI, no payoff required",
        "non_medical_collections": "Excluded from DTI for DU; manual UW at lender discretion",
        "charge_offs": "Excluded from DTI for DU",
        "citation": "B3-5.3-08",
    },
    "Freddie Mac": {
        "medical_collections": "Excluded from DTI, no payoff required",
        "non_medical_collections": "Excluded from DTI for LPA",
        "charge_offs": "Excluded from DTI for LPA",
        "citation": "Section 5202.1",
    },
    "FHA": {
        "medical_collections": "Excluded from DTI regardless of amount",
        "non_medical_collections": "If cumulative balance >$2,000: must pay off or set up payment plan (5% of balance/month counted in DTI)",
        "non_medical_under_2000": "No payoff or payment plan required",
        "charge_offs": "Same $2,000 cumulative rule as collections",
        "disputed_accounts_over_1000": "Must provide LOE; may affect TOTAL Scorecard",
        "citation": "HUD 4000.1, II.A.4.a.iv(F)",
    },
    "VA": {
        "medical_collections": "Excluded from DTI",
        "non_medical_collections": "No payoff required; lender analyzes overall credit pattern",
        "charge_offs": "No payoff required",
        "citation": "VA Pamphlet 26-7, Ch. 4",
    },
}

# Self-employment depreciation add-backs
DEPRECIATION_ADDBACK_RULES = {
    "rule": "Depreciation, depletion, and amortization are non-cash expenses and are ADDED BACK to qualifying income for self-employed borrowers",
    "applies_to": ["Schedule C (sole proprietor)", "Schedule E (rental properties)", "K-1 (S-Corp, Partnership)"],
    "common_add_backs": {
        "depreciation": "Always added back (non-cash)",
        "depletion": "Always added back (non-cash)",
        "amortization": "Always added back (non-cash/casualty loss)",
        "business_use_of_home": "Added back (already accounted for in housing expense)",
        "meals_entertainment": "Non-deductible portion may be added back",
    },
    "forms": {
        "Fannie Mae": "Form 1084 (Cash Flow Analysis) or Form 1088",
        "Freddie Mac": "Form 91 (Income Analysis)",
        "FHA": "Direct calculation from tax returns",
        "VA": "Direct calculation from tax returns",
    },
    "citation": "Fannie B3-3.2-01/B3-3.2-02; Freddie Section 5302.1; HUD 4000.1 II.A.4.c.i(G); VA Pamphlet 26-7 Ch.4 Sec.7",
}

# Loan modification seasoning by agency
LOAN_MODIFICATION_SEASONING = {
    "Fannie Mae": {
        "waiting_period_months": 12,
        "payments_required": 12,
        "from": "effective date of modification",
        "citation": "B2-1.3-05",
    },
    "Freddie Mac": {
        "waiting_period_months": 12,
        "payments_required": 6,
        "from": "effective date of modification",
        "citation": "Section 4301.2",
    },
    "FHA": {
        "waiting_period_months": 12,
        "payments_required": 12,
        "from": "effective date of modification",
        "notes": "For FHA streamline, 210 days + 6 payments from modification",
        "citation": "HUD 4000.1, II.A.2",
    },
    "VA": {
        "waiting_period_months": 6,
        "payments_required": 6,
        "from": "effective date of modification",
        "citation": "VA Pamphlet 26-7, Ch. 6",
    },
}

# Multiple borrower qualifying credit score methodology
QUALIFYING_CREDIT_SCORE = {
    "rule": "When multiple borrowers, the LOWEST representative score among all borrowers is the qualifying score",
    "single_borrower_two_scores": "Use the lower of the two scores",
    "single_borrower_three_scores": "Use the middle score",
    "multiple_borrowers": "Calculate each borrower's representative score first, then use the LOWEST among all borrowers",
    "exceptions": {
        "VA": "VA has no minimum credit score requirement (lender overlay only). Non-borrowing spouse score is NOT used.",
        "FHA_non_borrowing_spouse": "Non-borrowing spouse credit is pulled in community property states but their score is NOT the qualifying score",
    },
    "citation": "Fannie B3-5.1-01; Freddie Section 5201.1; HUD 4000.1 II.A.2.a; VA Pamphlet 26-7 Ch.4",
}


# =============================================================================
# CROSS-AGENCY COMPARISON INDEX
# =============================================================================

ALL_AGENCIES = {
    "Fannie Mae": FANNIE_MAE,
    "Freddie Mac": FREDDIE_MAC,
    "FHA": FHA,
    "VA": VA,
}

AGENCY_ALIASES = {
    "fnma": "Fannie Mae", "fannie": "Fannie Mae", "fannie mae": "Fannie Mae", "conventional": "Fannie Mae",
    "fhlmc": "Freddie Mac", "freddie": "Freddie Mac", "freddie mac": "Freddie Mac",
    "fha": "FHA", "hud": "FHA", "government": "FHA",
    "va": "VA", "veterans": "VA", "veteran": "VA", "veterans affairs": "VA",
}

def resolve_agency(name):
    """Resolve agency name from alias."""
    if name is None:
        return None
    return AGENCY_ALIASES.get(name.lower().strip(), name)
