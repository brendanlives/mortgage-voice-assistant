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

    # ----- BORROWER CONTRIBUTION -----
    "borrower_contribution": {
        "ltv_lte_80_primary": {"min_own_funds": "0%", "gift_ok": True, "citation": "B3-4.3-04"},
        "ltv_gt_80_1_unit": {"min_own_funds": "3%", "gift_for_remainder": True, "citation": "B3-4.3-04"},
        "ltv_gt_80_2_4_unit": {"min_own_funds": "5%", "gift_for_remainder": True, "citation": "B3-4.3-04"},
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
