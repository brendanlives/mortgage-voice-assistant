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
        "hcltv_limits": {
            "primary_1_unit": {"max_hcltv": 97, "citation": "B2-1.2-03"},
            "primary_2_unit": {"max_hcltv": 85, "citation": "B2-1.2-03"},
            "second_home": {"max_hcltv": 90, "citation": "B2-1.2-03"},
            "investment": {"max_hcltv": 85, "citation": "B2-1.2-03"},
        },
        "high_balance_adjustments": {
            "description": "Super conforming / high-balance loans have lower max LTVs",
            "purchase_primary_1_unit": {"max_ltv": 95, "citation": "B5-1-01"},
            "purchase_second_home": {"max_ltv": 90, "citation": "B5-1-01"},
            "purchase_investment": {"max_ltv": 85, "citation": "B5-1-01"},
            "cash_out_primary": {"max_ltv": 80, "citation": "B5-1-01"},
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
        "non_traditional_credit": {
            "allowed": True,
            "when": "When borrower has insufficient traditional credit history (fewer than 3 tradelines with 12-month history)",
            "requirements": "Manual UW only with B3-5.4 requirements (rent, utilities, insurance payment history for 12 months)",
            "citation": "B3-5.4",
        },
        "no_score_borrower": {
            "eligible": False,
            "conditions": "Not eligible for DU, may be eligible manual UW with non-traditional credit",
            "citation": "B3-5.1-01",
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
            "forbearance_seasoning": {
                "requirement": "Must be current for 12 months after forbearance plan",
                "citation": "B3-5.3-07",
            },
            "multiple_derogatory_stacking": {
                "rule": "Each event counted separately. If BK includes foreclosure, foreclosure waiting period starts from BK discharge.",
                "citation": "B3-5.3-07",
            },
            "disputed_tradelines": {
                "rule": "Disputed tradelines with aggregate balance >$500 (excluding medical): requires LOE, lender must confirm account is not borrower's or dispute is resolved. Not applicable to non-disputed accounts.",
                "citation": "B3-5.3-09",
            },
        },
        "authorized_user_accounts": {
            "treatment": "May exclude from DTI if documented",
            "condition": "Borrower must document they are NOT the primary obligor AND primary obligor has been making payments",
            "citation": "B3-6-04",
        },
        "heloc_payment": {
            "amortizing": "Use actual monthly payment",
            "interest_only": "Use actual IO payment during draw period",
            "draw_period_zero_balance": "May exclude if zero balance reported during draw period",
            "citation": "B3-6-03",
        },
        "business_debt_in_borrower_name": {
            "may_exclude_if": [
                "Debt is paid by the business (not borrower personally)",
                "Business provides 12 months cancelled checks or proof of payment",
                "Does NOT negatively affect borrower's personal credit",
            ],
            "business_cash_flow": "Business income analysis must account for business debt payments",
            "citation": "B3-6-05",
        },
        "tax_liens_judgments": {
            "judgments": "Must be paid off OR in approved payment plan with evidence of timely payments",
            "tax_liens": "Must be paid off at or before closing OR subordinated",
            "citation": "B3-5.3-09",
        },
        "open_30_day_charge_accounts": {
            "treatment": "NOT included in DTI",
            "condition": "Account is paid in full monthly",
            "citation": "B3-6-04",
        },
        "contingent_liabilities": {
            "general_rule": "Include in DTI",
            "exclusion": "May exclude if borrower provides evidence liability will NOT need to be repaid",
            "cosigner_on_mortgage": "Include unless other party has made last 12 monthly payments",
            "citation": "B3-6-06",
        },
        "solar_panel_lease_loan": {
            "leased_or_ppa": "Include monthly payment in DTI",
            "owned_system": "No DTI impact (UCC fixture filing acceptable)",
            "citation": "B3-6-07",
        },
        "installment_debt_less_than_10_months": {
            "treatment": "May exclude if fewer than 10 months remaining",
            "exception": "MUST include if payment is significant relative to income",
            "citation": "B3-6-04",
        },
        "property_tax_hoa_assessment": {
            "treatment": "Always included in DTI calculation",
            "components": ["Property taxes", "Homeowner's insurance", "HOA dues", "Condo assessments", "Flood insurance"],
            "part_of": "PITIA (Principal, Interest, Taxes, Insurance, Assessments/HOA)",
            "citation": "B3-6-01",
        },
        "deferred_non_student_debt": {
            "actual_payment_known": "Use actual monthly payment",
            "if_no_payment_amount": "Use 1% of outstanding balance OR calculated amortizing payment",
            "citation": "B3-6-03",
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

        # EXPANDED PROPERTY RULES
        "ineligible_property_types": {
            "types": [
                "Timeshares",
                "Houseboats",
                "Housebarges",
                "Properties in excess of 10 acres (unless rural residential)",
                "Commercial properties with >25% commercial space",
                "Working farms and ranches",
                "Properties used for commercial purposes",
                "Properties with income-generating activities as primary use",
                "Vacant land",
                "Condo hotels",
                "Boarding houses",
                "Bed-and-breakfasts"
            ],
            "citation": "B2-3-02, Property Type Eligibility"
        },

        "condo_approval": {
            "requirement": "Must be warrantable condo",
            "established_project_requirements": {
                "owner_occupied_min_pct": 50,
                "hazard_liability_insurance": "Adequate coverage required",
                "hoa_reserves": "Must be adequate per Fannie Mae standards",
                "delinquency_threshold": "No more than 15% of units delinquent on dues",
                "single_entity_max_ownership": "10% of units (20% for new projects)",
                "litigation_restriction": "No litigation affecting habitability or structural integrity"
            },
            "new_project_review": "Required vs. established project review",
            "citation": "B4-2.2, Condo Project Requirements"
        },

        "manufactured_housing": {
            "requirements": [
                "HUD certification label",
                "Permanent foundation meeting HUD standards",
                "Titled as real property (not personal property)",
                "Minimum 600 square feet",
                "Built after June 15, 1976"
            ],
            "ltv_limits": {
                "single_wide_primary": "Max 95% LTV",
                "double_wide_primary": "Max 95% LTV"
            },
            "restrictions": "No manufactured housing on leasehold",
            "citation": "B5-2-01, Manufactured Housing Eligibility"
        },

        "mixed_use_property": {
            "primary_requirement": "Primarily residential",
            "commercial_max_pct": 25,
            "must_have_residential_character": True,
            "cannot_be_zoned_exclusively_commercial": True,
            "citation": "B2-3-04, Mixed-Use Property"
        },

        "property_flipping": {
            "policy": "No specific time-based restriction",
            "appraisal_requirement": "Appraiser should comment on recent sales history",
            "due_diligence": "Large price increases in short period may trigger additional due diligence",
            "citation": "B2-3, Property Appraisal and Eligibility"
        },

        "accessory_dwelling_unit": {
            "allowed": True,
            "max_count": "One ADU in addition to primary dwelling",
            "appraised_value_contribution": "ADU contributes to appraised value",
            "rental_income_usage": "May be used with documentation per B3-3.1-08",
            "zoning_requirement": "Must be legal per local zoning ordinance",
            "citation": "B4-1.3-05, Accessory Dwelling Units"
        },

        "leasehold_estate": {
            "eligible": True,
            "remaining_lease_term": "Must be >=5 years beyond mortgage maturity",
            "lease_renewable": "Lease must be renewable",
            "mortgaging_requirement": "Lease must permit mortgaging of leasehold interest",
            "citation": "B2-3-03, Leasehold Estates"
        },

        "co_op": {
            "eligible": True,
            "requirement": "Must be on Fannie Mae's approved co-op projects list",
            "structure": "Share-loan structure",
            "project_requirements": "Must meet project eligibility requirements",
            "citation": "B4-2.3, Co-operative Housing"
        },

        "pud": {
            "eligible": True,
            "review_type": "Full review for new projects, limited review for established",
            "insurance_requirement": "Adequate insurance required",
            "hoa_requirement": "HOA must be in good standing",
            "citation": "B4-2.1, Planned Unit Development (PUD) Eligibility"
        },

        "rural_property": {
            "acreage_limit": "No specific acreage limit, but property must be residential in character",
            "appraisal_adjustment": "Excessive acreage adjusted in appraisal",
            "amenities_requirement": "Must have typical residential amenities",
            "citation": "B2-3, Property Eligibility and Valuation"
        },

        "second_home_requirements": {
            "unit_limit": "1-unit only",
            "occupancy_requirement": "Must be suitable for year-round occupancy",
            "restrictions": [
                "Cannot be subject to rental pool",
                "Cannot be subject to time-share arrangement"
            ],
            "borrower_control": "Borrower must have personal control over property",
            "location_typical": "Typically 50+ miles from primary OR in resort/vacation area",
            "citation": "B2-2-01, Second Home Mortgages"
        },
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

    # ----- ASSET & RESERVE SOURCES -----
    "asset_rules": {
        "eligible_reserve_sources": {
            "categories": ["checking/savings", "money market", "CDs", "stocks/bonds/mutual funds (current market value)", "retirement (401k/IRA - 60% of vested balance if borrower does not have unrestricted access, 100% if over 59.5 or evidence of distribution)", "trust accounts", "cash value of life insurance"],
            "citation": "B3-4.1-01",
        },
        "ineligible_reserve_sources": {
            "categories": ["gift funds (cannot be used for reserves)", "equity in other properties", "borrowed funds", "unsecured loans", "529 education savings", "stock options (unvested)", "restricted stock units (unvested)"],
            "citation": "B3-4.1-01",
        },
        "gift_of_equity": {
            "allowed": True,
            "eligible_donors": ["family/related parties only"],
            "property_value_calc": "LOWER of sales price or appraised value",
            "uses": ["down payment", "closing costs"],
            "ltv_calculation": "Based on lower of sale price or appraised value",
            "citation": "B3-4.3-05",
        },
        "interested_party_contributions": {
            "ltv_over_90": {"max_pct": 3, "based_on": "purchase price/appraised (whichever less)"},
            "ltv_75_to_90": {"max_pct": 6, "based_on": "purchase price/appraised (whichever less)"},
            "ltv_75_or_under": {"max_pct": 9, "based_on": "purchase price/appraised (whichever less)"},
            "investment_property": {"max_pct": 2},
            "allowed_uses": ["closing costs", "prepaids", "points", "MI premiums"],
            "not_allowed_uses": ["down payment", "financial reserves"],
            "citation": "B3-4.1-02",
        },
        "large_deposit_explanation": {
            "threshold": "Any single deposit >50% of total monthly qualifying income",
            "required_documentation": "Source documentation",
            "also_applies_to": "Recent large deposits that significantly increase account balance",
            "citation": "B3-4.2-02",
        },
        "retirement_account_rules": {
            "for_down_payment": "100% of vested balance if borrower provides evidence of withdrawal/distribution",
            "for_reserves": "60% of vested if <59.5 and no unrestricted access; 100% if ≥59.5 or unrestricted access",
            "citation": "B3-4.3-06",
        },
        "life_insurance_cash_value": {
            "net_cash_surrender_value": "Can be used for reserves or down payment",
            "required_documentation": "Statement from insurance company",
        },
        "sale_of_home_proceeds": {
            "acceptable": True,
            "required_documentation": "Closing disclosure or HUD-1",
        },
        "cryptocurrency": {
            "down_payment": "NOT acceptable UNLESS converted to US dollars and deposited in verified financial institution",
            "reserves": "NOT acceptable UNLESS converted to US dollars",
            "closing_costs": "NOT acceptable UNLESS converted to US dollars",
            "when_converted": "Treated as regular bank deposit (needs sourcing)",
            "citation": "B3-4.1-04",
        },
        "foreign_assets": {
            "acceptable": True,
            "if_verifiable": True,
            "foreign_currency_rule": "Must be converted to USD at current exchange rate",
            "foreign_bank_statements": "Acceptable if translatable and verifiable",
            "citation": "B3-4.2-01",
        },
        "earnest_money_deposit": {
            "must_document_source": True,
            "shown_on": "Sales contract",
            "verified_against": "Bank statements",
            "extra_docs_if_exceeds": ">2% of purchase price",
        },
        "gift_documentation_requirements": {
            "required_items": ["Gift letter (signed by donor) stating: amount, relationship, property address, no repayment expected", "Donor bank statement showing withdrawal", "Borrower bank statement showing deposit (or wire/cashier's check)"],
            "citation": "B3-4.3-04",
        },
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
        "base_pay_salary": {
            "source": "Current W-2 employment or verified contract income",
            "calculation_hourly": "Hourly rate × hours × 52 weeks / 12 months",
            "ytd_variance_check": "If YTD earnings differ significantly from base calculation, may average current year and prior year",
            "documentation": ["current paystub showing YTD earnings", "offer letter or contract", "verification of employment (VOE)"],
            "citation": "B3-3.1-03, Employment Income",
        },
        "overtime_income": {
            "requirement": "2 years history of overtime earnings",
            "calculation_stable_or_increasing": "Use 2-year average",
            "calculation_declining": "Use most recent year (lower amount) or exclude if declining trend unlikely to continue",
            "must_be_likely_to_continue": True,
            "documentation": ["2 years W-2s or VOE showing OT breakdown", "most recent paystub showing YTD OT"],
            "citation": "B3-3.3-02, Variable Income",
        },
        "bonus_income": {
            "requirement": "2 years history of bonus payments",
            "calculation_stable_or_increasing": "Use 2-year average",
            "calculation_declining": "Use most recent year (lower amount) or exclude if declining",
            "must_be_likely_to_continue": True,
            "documentation": ["2 years W-2s or VOE showing bonus breakdown", "most recent paystub", "employment contract if guaranteed"],
            "citation": "B3-3.3-02, Variable Income",
        },
        "tip_income": {
            "requirement": "2 years documented tip income history",
            "calculation": "2-year average, documented on tax returns",
            "must_be_on_tax_returns": True,
            "documentation": ["2 years of tax returns showing tip income", "W-2s or 1099s with tip amounts", "recent paystubs"],
            "citation": "B3-3.1-04, Service Industry Income",
        },
        "part_time_income": {
            "requirement": "2 years uninterrupted history at part-time employer",
            "no_minimum_hours": True,
            "can_be_supplemental": True,
            "documentation": ["2 years VOE", "paystubs", "tax returns"],
            "citation": "B3-3.1-06, Supplemental Income",
        },
        "seasonal_income": {
            "requirement": "2 years history of same seasonal employment",
            "calculation": "2-year average (annualized)",
            "off_season_consideration": "Unemployment compensation during off-season may be counted if available",
            "documentation": ["2 years tax returns", "2 years VOE", "documentation of seasonal employment terms"],
            "citation": "B3-3.1-07, Seasonal Income",
        },
        "employment_gaps": {
            "gaps_require_loe": True,
            "returning_to_same_type_strengthens": True,
            "recent_college_grad_exemption": "If relevant degree earned",
            "documentation": ["Letter of Explanation (LOE) for any gap", "evidence of degree if recent grad"],
            "citation": "B3-3.1-01, Employment History",
        },
        "foreign_income": {
            "requirement": "Borrower must file US tax returns",
            "us_employment_verification": "Verify employment with US employer",
            "documentation": ["US tax returns", "VOE from US employer", "documentation of income"],
            "citation": "B3-3.1-01, Foreign Employment Income",
        },
        "employment_offer_letter": {
            "acceptable_if": "Start date within 90 days of note date AND paystub covering at least 30 days before closing",
            "income_counted": "Guaranteed/base income only",
            "documentation": ["written employment offer letter with terms", "paystub if available (if started before closing)"],
            "citation": "B3-3.3-03, Offer Letter / Prospective Employment",
        },
        "housing_parsonage_allowance": {
            "taxable_treatment": "Non-taxable income (tax-free)",
            "grossup_allowed": True,
            "grossup_factor": 1.25,
            "documentation": ["letter from employer/religious organization documenting allowance"],
            "citation": "B3-3.3-04, Allowances and Add-Backs",
        },
        "automobile_allowance": {
            "calculation": "Only net amount (allowance minus actual documented expenses) = income",
            "if_expense_exceeds_allowance": "Difference treated as monthly liability",
            "documentation": ["documentation of allowance amount", "documentation of actual expenses"],
            "citation": "B3-3.3-04, Allowances and Add-Backs",
        },
        "long_term_disability_income": {
            "can_use": True,
            "requirement": "Must document likely to continue for at least 3 years from closing date",
            "documentation": ["Disability policy or benefits statement", "most recent bank statement or payment stub"],
            "citation": "B3-3.4-08",
        },
        "interest_dividend_income": {
            "can_use": True,
            "requirement": "2-year history on tax returns (Schedule B). Must document sufficient assets to continue generating income.",
            "calculation": "2-year average of interest and dividend income",
            "documentation": ["2 years tax returns (Schedule B)", "current account statements verifying assets"],
            "citation": "B3-3.4-05",
        },
        "capital_gains_income": {
            "can_use": True,
            "requirement": "Must show 2-year history AND sufficient remaining assets to continue generating gains",
            "calculation": "2-year average, net gains (not gross proceeds)",
            "documentation": ["2 years tax returns (Schedule D)", "current investment account statements"],
            "citation": "B3-3.4-06",
        },
        "trust_income": {
            "can_use": True,
            "requirement": "Must document trust terms, sufficient trust assets, and likelihood of continuance",
            "documentation": ["Trust agreement", "trustee letter", "tax returns or K-1 showing distributions"],
            "citation": "B3-3.4-10",
        },
        "royalty_income": {
            "can_use": True,
            "requirement": "2-year history, used average. Oil/gas/mineral rights, book royalties, patent royalties.",
            "documentation": ["2 years tax returns (Schedule E)", "lease/royalty agreement"],
            "citation": "B3-3.4-11",
        },
        "foster_care_income": {
            "can_use": True,
            "requirement": "2-year history of foster care income",
            "documentation": ["Letters from state/placing agency", "tax returns or bank statements showing payments"],
            "citation": "B3-3.1-09",
        },
        "notes_receivable_income": {
            "can_use": True,
            "requirement": "Must show 3-year continuance from closing date",
            "documentation": ["Copy of note", "evidence of receipt for 12+ months", "tax returns"],
            "citation": "B3-3.1-09",
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

    # ----- BORROWER ELIGIBILITY -----
    "borrower_eligibility": {
        "us_citizen": {
            "eligible": True,
            "documentation": "Standard documentation required",
            "citation": "B2-2-02, Borrower Eligibility",
        },
        "permanent_resident": {
            "eligible": True,
            "documentation": "Valid green card (Form I-551) required. Same terms as US citizen.",
            "citation": "B2-2-02, Borrower Eligibility",
        },
        "non_permanent_resident_alien": {
            "eligible": True,
            "requirements": [
                "Valid work visa (H-1B, L-1, E-1, E-2, TN, O-1, etc.)",
                "Valid SSN",
                "Work authorization with 2+ years remaining OR likelihood of renewal based on employer documentation"
            ],
            "citation": "B2-2-02, Borrower Eligibility",
        },
        "daca_recipients": {
            "eligible": True,
            "requirements": [
                "Valid EAD (Employment Authorization Document)",
                "Treated as non-permanent resident alien"
            ],
            "citation": "B2-2-02, Borrower Eligibility",
        },
        "foreign_national_non_resident": {
            "eligible": False,
            "reason": "Must have SSN and legal presence in US",
            "citation": "B2-2-02, Borrower Eligibility",
        },
        "trust_vesting": {
            "eligible": True,
            "requirements": [
                "Revocable/living trust",
                "Borrower is both trustee AND beneficiary",
                "Trust does not prevent lien placement on property"
            ],
            "citation": "B2-2-05, Property in Trust",
        },
        "power_of_attorney": {
            "allowed": True,
            "requirements": [
                "POA must be specific to the transaction",
                "Signed by borrower",
                "Not expired",
                "Attorney-in-fact cannot be lender, broker, or title company"
            ],
            "exceptions": "Active-duty military: broader POA accepted",
            "citation": "B8-5-05, Power of Attorney",
        },
        "first_time_homebuyer": {
            "definition": "No ownership interest in residential property in past 3 years",
            "citation": "B2-1.1-01, Eligibility Matrix",
        },
        "maximum_financed_properties": {
            "limit": 10,
            "includes": "Primary residence plus up to 9 other financed properties",
            "requirements_for_5_to_10": [
                "720+ credit score",
                "25%+ down on investment properties",
                "6 months reserves per property",
                "No 30-day lates in past 12 months"
            ],
            "citation": "B2-2-03, Multiple Properties",
        },
        "age_of_borrower": {
            "requirement": "Must be of legal age to contract in property state (typically 18)",
            "citation": "B2-2-02, Borrower Eligibility",
        },
    },

    # ----- ARM RULES -----
    "arm_rules": {
        "qualifying_rate": {
            "5yr_or_less_arm": {
                "rule": "Use higher of note rate + 2% or fully indexed rate",
                "applies_to": ["1-year ARM", "3-year ARM", "5-year ARM"],
                "citation": "B2-1.4-02, ARM Qualifying Rate",
            },
            "over_5yr_arm": {
                "rule": "Use note rate",
                "applies_to": ["7-year ARM", "10-year ARM"],
                "citation": "B2-1.4-02, ARM Qualifying Rate",
            },
            "manually_underwritten": {
                "rule": "Use note rate + 2% for qualifying DTI",
                "applies_to": "All ARMs on manually underwritten loans",
                "citation": "B2-1.4-02, ARM Qualifying Rate",
            },
        },
        "eligible_indices": {
            "sofr": {
                "acceptable": True,
                "type": "30-day average SOFR (Secured Overnight Financing Rate)",
                "notes": "SOFR replaced LIBOR effective June 2023",
                "citation": "B2-1.4-02",
            },
            "cmt": {
                "acceptable": True,
                "type": "1-year Constant Maturity Treasury",
                "citation": "B2-1.4-02",
            },
        },
        "rate_cap_structures": {
            "standard_structures": [
                {"name": "5/1 ARM", "caps": "5% initial / 2% periodic / 5% lifetime", "citation": "B2-1.4-01"},
                {"name": "1-year ARM", "caps": "2% initial / 2% periodic / 5% lifetime", "citation": "B2-1.4-01"},
                {"name": "5/5 ARM", "caps": "5% initial / 5% periodic / 5% lifetime", "citation": "B2-1.4-01"},
            ],
            "citation": "B2-1.4-01, ARM Interest Rate Caps",
        },
        "interest_only_arm": {
            "eligible": True,
            "ltv_restriction": "80% LTV or less",
            "property_type": "Primary residence or second home only",
            "min_credit_score": 720,
            "minimum_score_citation": "B2-1.4-03",
            "qualification_rule": "Must qualify at fully amortizing payment using higher of note rate + 2% or fully indexed rate",
            "max_io_period": 10,
            "max_io_period_unit": "years",
            "investment_property_eligible": False,
            "citation": "B2-1.4-03, Interest-Only ARM",
        },
        "arm_conversion_option": {
            "available": True,
            "description": "Convertible ARM allowed. Can convert to fixed rate during specific conversion window.",
            "new_rate_basis": "New rate based on Fannie Mae required spread over index",
            "citation": "B2-1.4-05, ARM Conversion Option",
        },
        "arm_ltv_restrictions": {
            "standard_arm": {
                "rule": "Same as fixed rate LTV matrix for most ARMs",
                "citation": "B2-1.4-01, ARM LTV Limits",
            },
            "interest_only_arm": {
                "max_ltv": 80,
                "property_restrictions": "Primary residence and second home only",
                "investment_property_eligible": False,
                "citation": "B2-1.4-03",
            },
        },
    },

    # ----- REFINANCE RULES -----
    "refinance_rules": {
        "cash_out_seasoning": {
            "required_months": 6,
            "calculation": "From note date of existing loan (or deed of acquisition) to note date of new loan",
            "citation": "B2-1.3-03, Seasoning Requirement",
            "exceptions": [
                {
                    "type": "Inherited property",
                    "waiting_period_required": 0,
                    "citation": "B2-1.3-03",
                },
                {
                    "type": "Delayed financing",
                    "description": "Cash-out refi within 6 months of purchase if original purchase was all cash",
                    "conditions": [
                        "Original purchase was all cash (no financing)",
                        "New loan amount ≤ original purchase price + closing costs",
                        "Buyer can document source of funds for original purchase",
                        "Title insurance shows no liens",
                    ],
                    "citation": "B2-1.3-03",
                },
            ],
        },
        "rate_term_refi_seasoning": {
            "required": False,
            "note": "No specific seasoning requirement for rate-term refinance",
            "citation": "B2-1.3-01",
        },
        "continuity_of_obligation": {
            "required": True,
            "rule": "At least one borrower on new loan must have been on the existing loan being refinanced",
            "exception": "Borrower can document they have been making payments for last 12 months (e.g., divorce situation)",
            "citation": "B2-1.3-01, Continuity of Obligation",
        },
        "net_tangible_benefit": {
            "required": False,
            "note": "No specific NTB test. Market-driven decision.",
            "citation": "B2-1.3-01",
        },
        "subordinate_financing_on_refi": {
            "existing_liens_may_remain": True,
            "condition": "Must be resubordinated",
            "new_subordinate_financing": "Treated as cash-out. CLTV limits apply.",
            "citation": "B2-1.3-01, Subordinate Financing",
        },
        "fha_streamline": {"not_applicable": True},
        "va_irrrl": {"not_applicable": True},
    },

    # ----- TEMPORARY BUYDOWNS -----
    "temporary_buydowns": {
        "eligible_structures": {
            "description": "3-2-1, 2-1, 1-0 buydowns permitted for fixed-rate and ARM",
            "transaction_types": ["Purchase", "Rate-term refinance"],
            "exclusions": ["Cash-out refinance", "Investment properties"],
            "citation": "B2-1.4-04, Temporary Rate Buydown",
        },
        "qualifying_rate": {
            "standard_rule": "Qualify at the NOTE rate (not the buydown rate)",
            "exception": {
                "du_approval": "If DU issues 'Approve' at buydown rate for 2-1 buydown on primary purchase",
                "applies_to": "Primary purchase with 2-1 buydown structure only",
            },
            "citation": "B2-1.4-04",
        },
        "who_can_fund": {
            "allowed_sources": ["seller", "builder", "employer (relocation)", "lender", "borrower"],
            "note": "Contributions from interested parties count toward IPC limits",
            "borrower_funded": "Acceptable",
            "citation": "B2-1.4-04",
        },
        "escrow_requirements": {
            "requirement": "Full buydown subsidy must be deposited into escrow account at closing",
            "lender_responsibility": "Lender must maintain escrow account",
            "unused_funds": "Returned to party who funded the buydown",
            "citation": "B2-1.4-04",
        },
        "buydown_not_allowed": {
            "cash_out_refi": True,
            "investment_properties": True,
            "citation": "B2-1.4-04",
        },
    },

    # ----- DOCUMENT AGE REQUIREMENTS -----
    "document_age_requirements": {
        "credit_report": {
            "max_days": 120,
            "measured_from": "Note date",
            "reissue_validity": {
                "max_days": 180,
                "note": "Reissued credit report valid for 180 days",
            },
            "citation": "B1-1-03, Credit Report",
        },
        "appraisal": {
            "standard": {
                "max_days": 120,
                "measured_from": "Effective date",
            },
            "with_update_or_recertification": {
                "max_months": 12,
                "note": "Valid for 12 months if updated/recertified at 4 months",
            },
            "without_update": {
                "max_days": 120,
                "note": "Without update: 4 months (120 days) from effective date",
            },
            "citation": "B4-1.1-03, Appraisal Validity",
        },
        "income_documents": {
            "paystubs": {
                "max_days": 30,
                "measured_from": "Application date",
                "note": "Most recent 30 days of paystubs",
            },
            "w2s": {
                "requirement": "Most recent year",
            },
            "tax_returns": {
                "requirement": "Most recent 1-2 years filed",
            },
            "voe_verbal": {
                "max_days": 10,
                "measured_from": "Note date",
                "note": "Verbal VOE within 10 business days of note date",
            },
            "voe_written": {
                "max_days": 10,
                "measured_from": "Note date",
                "note": "VOE (written) within 10 business days of note date",
            },
            "citation": "B3-3.1-01, Income Documentation",
        },
        "bank_statements": {
            "requirement": "Most recent 2 consecutive months",
            "max_days": 60,
            "measured_from": "Application date",
            "note": "Must cover period up to application date",
            "citation": "B3-4.2-01, Bank Statements",
        },
        "title_search": {
            "requirement": "Must be current",
            "typical_update_window": "30-90 days before closing",
            "title_insurance_commitment": "Required",
            "citation": "B7-3.1-01, Title",
        },
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

    # ----- OCCUPANCY RULES -----
    "occupancy_rules": {
        "kiddie_condo": {
            "description": "Parent buying for child",
            "requirements": "Child must be an occupant or co-borrower",
            "citation": "B4-2.1-01",
        },
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
        "non_traditional_credit": {
            "allowed": True,
            "when": "When borrower has insufficient traditional credit history (fewer than 3 tradelines with 12-month history)",
            "requirements": "Home Possible with LPA Accept",
            "citation": "Section 5203.3",
        },
        "no_score_borrower": {
            "eligible": False,
            "conditions": "Not eligible for LPA",
            "citation": "Section 5201.1",
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
        "coverage_varies": "Coverage determined by LPA based on risk factors. Standard coverage amounts similar to Fannie.",
        "cancellation": {
            "automatic": "At 78% of original value based on amortization",
            "borrower_request": "At 80% current value with good payment history",
        },
        "citation": "Freddie Section 4701",
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

    # ----- ASSET & RESERVE SOURCES -----
    "asset_rules": {
        "eligible_reserve_sources": {
            "categories": ["checking/savings", "money market", "CDs", "stocks/bonds/mutual funds (current market value)", "retirement (401k/IRA - 60% of vested balance if borrower does not have unrestricted access, 100% if over 59.5 or evidence of distribution)", "trust accounts", "cash value of life insurance"],
            "citation": "Section 5501.3",
        },
        "ineligible_reserve_sources": {
            "categories": ["gift funds (cannot be used for reserves)", "equity in other properties", "borrowed funds", "unsecured loans", "529 education savings", "stock options (unvested)", "restricted stock units (unvested)"],
            "citation": "Section 5501.3",
        },
        "gift_of_equity": {
            "allowed": True,
            "eligible_donors": ["family/related parties only"],
            "property_value_calc": "LOWER of sales price or appraised value",
            "uses": ["down payment", "closing costs"],
            "ltv_calculation": "Based on lower of sale price or appraised value",
            "citation": "Section 5501.4",
        },
        "interested_party_contributions": {
            "ltv_over_90": {"max_pct": 3, "based_on": "purchase price/appraised (whichever less)"},
            "ltv_75_to_90": {"max_pct": 6, "based_on": "purchase price/appraised (whichever less)"},
            "ltv_75_or_under": {"max_pct": 9, "based_on": "purchase price/appraised (whichever less)"},
            "investment_property": {"max_pct": 2},
            "allowed_uses": ["closing costs", "prepaids", "points", "MI premiums"],
            "not_allowed_uses": ["down payment", "financial reserves"],
            "citation": "Section 5501.5",
        },
        "large_deposit_explanation": {
            "threshold": "Any single deposit >50% of total monthly qualifying income",
            "required_documentation": "Source documentation",
            "citation": "Section 5501.1",
        },
        "retirement_account_rules": {
            "for_down_payment": "100% of vested balance if borrower provides evidence of withdrawal/distribution",
            "for_reserves": "60% of vested if <59.5 and no unrestricted access; 100% if ≥59.5 or unrestricted access",
            "citation": "Section 5501.3",
        },
        "life_insurance_cash_value": {
            "net_cash_surrender_value": "Can be used for reserves or down payment",
            "required_documentation": "Statement from insurance company",
        },
        "sale_of_home_proceeds": {
            "acceptable": True,
            "required_documentation": "Closing disclosure or HUD-1",
        },
        "cryptocurrency": {
            "down_payment": "NOT acceptable UNLESS converted to US dollars and deposited in verified financial institution",
            "reserves": "NOT acceptable UNLESS converted to US dollars",
            "closing_costs": "NOT acceptable UNLESS converted to US dollars",
            "when_converted": "Treated as regular bank deposit (needs sourcing)",
            "citation": "Section 5501.3",
        },
        "foreign_assets": {
            "acceptable": True,
            "if_verifiable": True,
            "foreign_currency_rule": "Must be converted to USD at current exchange rate",
            "foreign_bank_statements": "Acceptable if translatable and verifiable",
            "citation": "Section 5501.3",
        },
        "earnest_money_deposit": {
            "must_document_source": True,
            "shown_on": "Sales contract",
            "verified_against": "Bank statements",
            "extra_docs_if_exceeds": ">2% of purchase price",
        },
        "gift_documentation_requirements": {
            "required_items": ["Gift letter (signed by donor) stating: amount, relationship, property address, no repayment expected", "Donor bank statement showing withdrawal", "Borrower bank statement showing deposit (or wire/cashier's check)"],
            "citation": "Section 5501.5",
        },
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
            "forbearance_seasoning": {
                "requirement": "12 months current",
                "citation": "Section 5202.3",
            },
            "multiple_derogatory_stacking": {
                "rule": "Same as Fannie. If BK includes foreclosure, foreclosure waiting period starts from BK discharge.",
                "citation": "Section 5202.3",
            },
            "disputed_tradelines": {
                "rule": "Similar treatment to Fannie. Disputed accounts with material balances require documentation.",
                "citation": "Section 5306.2",
            },
        },
        "authorized_user_accounts": {
            "treatment": "May exclude from DTI if documented",
            "condition": "Borrower must not be the primary account holder",
            "citation": "Section 5307.1",
        },
        "heloc_payment": {
            "actual_payment": "Use actual monthly payment",
            "interest_only_draw": "Use actual IO payment during draw period",
            "citation": "Section 5307.1",
        },
        "business_debt_in_borrower_name": {
            "may_exclude_if": "Business has 12-month documented payment history (cancelled checks, bank statements)",
            "citation": "Section 5307.1",
        },
        "tax_liens_judgments": {
            "judgments": "Must be paid prior to or at closing",
            "tax_liens": "Must be paid off (Federal tax liens must be satisfied)",
            "citation": "Section 5306.2",
        },
        "open_30_day_charge_accounts": {
            "treatment": "NOT included in DTI",
            "condition": "Account is paid in full monthly",
            "citation": "Section 5307.1",
        },
        "contingent_liabilities": {
            "general_rule": "Include in DTI",
            "exclusion": "May exclude if borrower provides evidence liability won't need to be repaid",
            "cosigner_on_mortgage": "Include unless other party has made last 12 monthly payments",
            "citation": "Section 5307.1",
        },
        "solar_panel_lease_loan": {
            "leased_or_ppa": "Include monthly payment in DTI",
            "owned_system": "No payment needed",
            "citation": "Section 5307.1",
        },
        "installment_debt_less_than_10_months": {
            "treatment": "May exclude if fewer than 10 months remaining",
            "citation": "Section 5307.1",
        },
        "property_tax_hoa_assessment": {
            "treatment": "Always included in DTI calculation",
            "components": ["Property taxes", "Homeowner's insurance", "HOA dues", "Condo assessments", "Flood insurance"],
            "part_of": "PITIA calculation",
            "citation": "Section 5301.1",
        },
        "deferred_non_student_debt": {
            "actual_payment_known": "Use actual monthly payment",
            "if_no_payment_amount": "Use 1% of outstanding balance or calculated amortizing payment",
            "citation": "Section 5307.1",
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
        "base_pay_salary": {
            "source": "Current W-2 employment or verified contract income",
            "calculation_hourly": "Hourly rate × hours × 52 weeks / 12 months",
            "ytd_variance_check": "If YTD earnings differ significantly from base calculation, may average current year and prior year",
            "documentation": ["current paystub showing YTD earnings", "offer letter or contract", "verification of employment (VOE)", "Form 65 when available"],
            "citation": "Section 5304.1, Employment Income",
        },
        "overtime_income": {
            "requirement": "2 years history of overtime earnings",
            "calculation_stable_or_increasing": "Use 2-year average",
            "calculation_declining": "Use most recent year (lower amount) or exclude if declining trend unlikely to continue",
            "must_be_likely_to_continue": True,
            "documentation": ["2 years W-2s or VOE showing OT breakdown", "most recent paystub showing YTD OT"],
            "citation": "Section 5304.2, Variable Income",
        },
        "bonus_income": {
            "requirement": "2 years history of bonus payments",
            "calculation_stable_or_increasing": "Use 2-year average",
            "calculation_declining": "Use most recent year (lower amount) or exclude if declining",
            "must_be_likely_to_continue": True,
            "documentation": ["2 years W-2s or VOE showing bonus breakdown", "most recent paystub", "employment contract if guaranteed"],
            "citation": "Section 5304.2, Variable Income",
        },
        "tip_income": {
            "requirement": "2 years documented tip income history",
            "calculation": "2-year average, documented on tax returns",
            "must_be_on_tax_returns": True,
            "documentation": ["2 years of tax returns showing tip income", "W-2s or 1099s with tip amounts", "recent paystubs"],
            "citation": "Section 5304.2, Service Industry Income",
        },
        "part_time_income": {
            "requirement": "2 years uninterrupted history at part-time employer",
            "no_minimum_hours": True,
            "can_be_supplemental": True,
            "documentation": ["2 years VOE", "paystubs", "tax returns"],
            "citation": "Section 5304.1, Supplemental Income",
        },
        "seasonal_income": {
            "requirement": "2 years history of same seasonal employment",
            "calculation": "2-year average (annualized)",
            "off_season_consideration": "Unemployment compensation during off-season may be counted if available",
            "documentation": ["2 years tax returns", "2 years VOE", "documentation of seasonal employment terms"],
            "citation": "Section 5304.1, Seasonal Income",
        },
        "employment_gaps": {
            "gaps_require_loe": True,
            "returning_to_same_type_strengthens": True,
            "recent_college_grad_exemption": "If relevant degree earned",
            "documentation": ["Letter of Explanation (LOE) for any gap", "evidence of degree if recent grad"],
            "citation": "Section 5301.1, Employment History",
        },
        "foreign_income": {
            "requirement": "Income must be verifiable",
            "us_employment_verification": "Verify employment with US employer or foreign employer with documented US tax filing",
            "documentation": ["US tax returns", "VOE from employer", "documentation of income"],
            "citation": "Section 5301.1, Foreign Employment Income",
        },
        "employment_offer_letter": {
            "acceptable_if": "Employment to commence prior to or upon delivery of note",
            "income_counted": "Guaranteed/base income only",
            "documentation": ["written employment offer letter with specific terms"],
            "citation": "Section 5304.1, Offer Letter / Prospective Employment",
        },
        "housing_parsonage_allowance": {
            "taxable_treatment": "Non-taxable income (tax-free)",
            "grossup_allowed": True,
            "grossup_factor": 1.25,
            "documentation": ["letter from employer/religious organization documenting allowance"],
            "citation": "Section 5304.2, Allowances and Add-Backs",
        },
        "automobile_allowance": {
            "calculation": "Only net amount (allowance minus actual documented expenses) = income",
            "if_expense_exceeds_allowance": "Difference treated as monthly liability",
            "documentation": ["documentation of allowance amount", "documentation of actual expenses"],
            "citation": "Section 5304.2, Allowances and Add-Backs",
        },
        "long_term_disability_income": {
            "can_use": True,
            "requirement": "Must document likely to continue for at least 3 years from closing date",
            "documentation": ["Disability policy or benefits statement", "most recent bank statement or payment stub"],
            "citation": "Section 5306",
        },
        "interest_dividend_income": {
            "can_use": True,
            "requirement": "2-year history on tax returns (Schedule B). Must document sufficient assets to continue generating income.",
            "calculation": "2-year average of interest and dividend income",
            "documentation": ["2 years tax returns (Schedule B)", "current account statements verifying assets"],
            "citation": "Section 5306",
        },
        "capital_gains_income": {
            "can_use": True,
            "requirement": "Must show 2-year history AND sufficient remaining assets to continue generating gains",
            "calculation": "2-year average, net gains (not gross proceeds)",
            "documentation": ["2 years tax returns (Schedule D)", "current investment account statements"],
            "citation": "Section 5306",
        },
        "trust_income": {
            "can_use": True,
            "requirement": "Must document trust terms, sufficient trust assets, and likelihood of continuance",
            "documentation": ["Trust agreement", "trustee letter", "tax returns or K-1 showing distributions"],
            "citation": "Section 5306",
        },
        "royalty_income": {
            "can_use": True,
            "requirement": "2-year history, used average. Oil/gas/mineral rights, book royalties, patent royalties.",
            "documentation": ["2 years tax returns (Schedule E)", "lease/royalty agreement"],
            "citation": "Section 5306",
        },
        "foster_care_income": {
            "can_use": True,
            "requirement": "2-year history of foster care income",
            "documentation": ["Letters from state/placing agency", "tax returns or bank statements showing payments"],
            "citation": "Section 5306",
        },
        "notes_receivable_income": {
            "can_use": True,
            "requirement": "Must show 3-year continuance from closing date",
            "documentation": ["Copy of note", "evidence of receipt for 12+ months", "tax returns"],
            "citation": "Section 5306",
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

    # ----- BORROWER ELIGIBILITY -----
    "borrower_eligibility": {
        "us_citizen": {
            "eligible": True,
            "documentation": "Standard documentation required",
            "citation": "Section 5104.1, Borrower Eligibility",
        },
        "permanent_resident": {
            "eligible": True,
            "documentation": "Valid green card (Form I-551) required",
            "citation": "Section 5104.1, Borrower Eligibility",
        },
        "non_permanent_resident_alien": {
            "eligible": True,
            "requirements": [
                "Valid work authorization",
                "Valid SSN"
            ],
            "citation": "Section 5104.1, Borrower Eligibility",
        },
        "daca_recipients": {
            "eligible": True,
            "requirements": [
                "Valid EAD (Employment Authorization Document)",
                "Valid SSN"
            ],
            "citation": "Section 5104.1, Borrower Eligibility",
        },
        "foreign_national_non_resident": {
            "eligible": False,
            "citation": "Section 5104.1, Borrower Eligibility",
        },
        "trust_vesting": {
            "eligible": True,
            "requirements": [
                "Inter vivos revocable trust",
                "Borrower must be both trustee and beneficiary"
            ],
            "citation": "Section 5104.2, Property in Trust",
        },
        "power_of_attorney": {
            "allowed": True,
            "requirements": [
                "POA must reference specific transaction",
                "Must be properly executed per state law",
                "Not expired",
                "Attorney-in-fact cannot be lender, broker, or title company"
            ],
            "citation": "Section 5104.3, Power of Attorney",
        },
        "first_time_homebuyer": {
            "definition": "No ownership interest in residential property in past 3 years",
            "citation": "Freddie Mac Guidelines",
        },
        "maximum_financed_properties": {
            "limit": 6,
            "includes": "All financed properties including primary residence",
            "citation": "Section 5104.4, Multiple Properties",
        },
        "age_of_borrower": {
            "requirement": "Must be of legal age to contract in property state (typically 18)",
            "citation": "Section 5104.1, Borrower Eligibility",
        },
    },

    # ----- ARM RULES -----
    "arm_rules": {
        "qualifying_rate": {
            "5yr_or_less_arm": {
                "rule": "5/1 ARM: Use note rate + 2%",
                "applies_to": ["1-year ARM", "3-year ARM", "5-year ARM"],
                "citation": "Section 4305.2, ARM Qualifying Rate",
            },
            "over_5yr_arm": {
                "rule": "7/1 and 10/1 ARM: Use note rate",
                "applies_to": ["7-year ARM", "10-year ARM"],
                "citation": "Section 4305.2, ARM Qualifying Rate",
            },
        },
        "eligible_indices": {
            "sofr": {
                "acceptable": True,
                "type": "30-day average SOFR (Secured Overnight Financing Rate)",
                "notes": "SOFR replaced LIBOR effective June 2023",
                "citation": "Section 4305.2",
            },
            "cmt": {
                "acceptable": True,
                "type": "1-year Constant Maturity Treasury",
                "citation": "Section 4305.2",
            },
        },
        "rate_cap_structures": {
            "standard_structures": [
                {"name": "5/1 ARM", "caps": "5% initial / 2% periodic / 5% lifetime", "citation": "Section 4305.1"},
                {"name": "7/1 ARM", "caps": "5% initial / 2% periodic / 5% lifetime", "citation": "Section 4305.1"},
                {"name": "10/1 ARM", "caps": "5% initial / 2% periodic / 5% lifetime", "citation": "Section 4305.1"},
            ],
            "citation": "Section 4305.1, ARM Interest Rate Caps",
        },
        "interest_only_arm": {
            "eligible": True,
            "ltv_restriction": "80% LTV or less",
            "property_type": "Primary residence or second home only",
            "qualification_rule": "Must qualify at fully amortizing payment",
            "investment_property_eligible": False,
            "citation": "Section 4305.3, Interest-Only ARM",
        },
        "arm_conversion_option": {
            "available": True,
            "description": "Convertible ARM available for eligible borrowers",
            "citation": "Section 4305.5, ARM Conversion Option",
        },
        "arm_ltv_restrictions": {
            "standard_arm": {
                "rule": "Same as fixed rate for standard ARMs",
                "citation": "Section 4305.1, ARM LTV Limits",
            },
        },
    },

    # ----- REFINANCE RULES -----
    "refinance_rules": {
        "cash_out_seasoning": {
            "required_months": 6,
            "calculation": "From note date of existing loan (or deed of acquisition) to note date of new loan",
            "citation": "Section 4301.2, Seasoning Requirement",
        },
        "delayed_financing_exception": {
            "available": True,
            "description": "Can do cash-out refi within 6 months of purchase if original purchase was all cash",
            "conditions": [
                "Original purchase was all cash (no financing)",
                "New loan amount ≤ original purchase price + closing costs",
                "Buyer can document source of funds for original purchase",
                "Title insurance shows no liens",
            ],
            "citation": "Section 4301.2",
        },
        "rate_term_refi_seasoning": {
            "required": False,
            "note": "No specific seasoning requirement for rate-term refinance",
            "citation": "Section 4301.1",
        },
        "continuity_of_obligation": {
            "required": True,
            "rule": "At least one borrower on new loan must have been on the existing loan being refinanced",
            "citation": "Section 4301.1, Continuity of Obligation",
        },
        "net_tangible_benefit": {
            "required": False,
            "note": "No specific NTB test. Market-driven decision.",
            "citation": "Section 4301.1",
        },
        "subordinate_financing_on_refi": {
            "existing_liens_may_remain": True,
            "condition": "Must be resubordinated",
            "new_subordinate_financing": "Treated as cash-out. CLTV limits apply.",
            "citation": "Section 4301.1, Subordinate Financing",
        },
        "fha_streamline": {"not_applicable": True},
        "va_irrrl": {"not_applicable": True},
    },

    # ----- TEMPORARY BUYDOWNS -----
    "temporary_buydowns": {
        "eligible_structures": {
            "description": "3-2-1, 2-1 buydowns permitted",
            "transaction_types": ["Purchase"],
            "exclusions": ["Refinance"],
            "note": "Purchase transactions only",
            "citation": "Section 4304.1, Temporary Rate Buydown",
        },
        "qualifying_rate": {
            "standard_rule": "Qualify at the NOTE rate (not the buydown rate)",
            "citation": "Section 4304.1",
        },
        "who_can_fund": {
            "allowed_sources": ["seller", "builder", "employer (relocation)", "lender", "borrower"],
            "note": "Contributions from interested parties count toward IPC limits",
            "borrower_funded": "Acceptable",
            "citation": "Section 4304.1",
        },
        "escrow_requirements": {
            "requirement": "Full buydown subsidy must be deposited into escrow account at closing",
            "lender_responsibility": "Lender must maintain escrow account",
            "unused_funds": "Returned to party who funded the buydown",
            "citation": "Section 4304.1",
        },
        "buydown_not_allowed": {
            "refinance": True,
            "citation": "Section 4304.1",
        },
    },

    # ----- DOCUMENT AGE REQUIREMENTS -----
    "document_age_requirements": {
        "credit_report": {
            "max_days": 120,
            "measured_from": "Note date",
            "citation": "Section 4101.1, Credit Report",
        },
        "appraisal": {
            "standard": {
                "max_days": 120,
                "measured_from": "Effective date",
            },
            "with_update": {
                "max_days": 180,
                "note": "Can be extended to 180 days with update",
            },
            "citation": "Section 4101.1, Appraisal Validity",
        },
        "income_documents": {
            "paystubs": {
                "max_days": 30,
                "measured_from": "Application date",
            },
            "voe": {
                "max_days": 120,
                "measured_from": "Note date",
                "note": "Verification of Employment within 120 days of note date",
            },
            "citation": "Section 4101.1, Income Documentation",
        },
        "bank_statements": {
            "requirement": "Most recent 2 months",
            "citation": "Section 4101.1, Bank Statements",
        },
        "title_search": {
            "requirement": "Must be current",
            "typical_update_window": "30-90 days before closing",
            "title_insurance_commitment": "Required",
            "citation": "Section 4101.1, Title",
        },
    },

    # ----- PROPERTY ELIGIBILITY -----
    "property": {
        "eligible": [
            "1-4 unit residential",
            "HUD-approved condominiums",
            "Manufactured housing (permanent foundation, real property title)",
            "Mixed-use (51%+ residential square footage)",
        ],
        "ineligible": [
            "Timeshares",
            "Houseboats",
            "Commercial properties (>25% commercial space)",
            "Working farms and ranches",
            "Vacant land",
            "Condo hotels"
        ],
        "citation": "Section 4201.3, Property Type Eligibility",

        "ineligible_property_types": {
            "types": [
                "Timeshares",
                "Houseboats",
                "Commercial properties with >25% commercial space",
                "Working farms and ranches",
                "Vacant land",
                "Condo hotels",
                "Properties used for commercial purposes",
                "Properties with income-generating activities as primary use"
            ],
            "citation": "Section 4201.3, Property Eligibility Requirements"
        },

        "condo_approval": {
            "requirement": "Must meet Freddie Mac project standards or single-unit approval criteria",
            "project_requirements": {
                "owner_occupied_min_pct": 50,
                "hazard_liability_insurance": "Adequate coverage required",
                "hoa_reserves": "Must be adequate",
                "delinquency_threshold": "No more than 15% of units delinquent on dues",
                "single_entity_max_ownership": "10% of units",
                "litigation_restriction": "No litigation affecting habitability or structural integrity"
            },
            "citation": "Section 5701, Condominium Project Requirements"
        },

        "manufactured_housing": {
            "requirements": [
                "Must have HUD certification label",
                "Permanent foundation meeting HUD standards",
                "Titled as real property (not personal property)",
                "Minimum square footage varies by lender"
            ],
            "ltv_limits": {
                "primary_purchase": "Max 95% LTV",
                "refinance": "Varies by program"
            },
            "citation": "Section 5703, Manufactured Housing Eligibility"
        },

        "mixed_use_property": {
            "commercial_max_pct": 25,
            "must_be_primarily_residential": True,
            "citation": "Section 4201.3, Mixed-Use Properties"
        },

        "property_flipping": {
            "policy": "No specific anti-flipping rule",
            "appraisal_requirement": "Value increases must be supported by appraisal",
            "documentation": "Recent sales history should be documented",
            "citation": "Section 4201.3, Property Valuation"
        },

        "accessory_dwelling_unit": {
            "allowed": True,
            "max_count": "One ADU in addition to primary dwelling",
            "appraised_value_contribution": "ADU contributes to appraised value",
            "rental_income_usage": "Income may be used per standard rental rules",
            "citation": "Freddie Mac Seller/Servicer Guide, Property Requirements"
        },

        "leasehold_estate": {
            "eligible": True,
            "remaining_lease_term": "Remaining lease term must be at least 5 years beyond loan maturity",
            "citation": "Section 4201.3, Leasehold Properties"
        },

        "co_op": {
            "eligible": True,
            "requirement": "Must be approved per Freddie Mac guidelines",
            "citation": "Freddie Mac Seller/Servicer Guide"
        },

        "pud": {
            "eligible": True,
            "review_type": "Project review required",
            "insurance_requirement": "Adequate insurance required",
            "hoa_requirement": "HOA must be in good standing",
            "citation": "Section 4201.3, Planned Unit Development (PUD) Eligibility"
        },

        "rural_property": {
            "acreage_limit": "No specific acreage limit if residential",
            "appraisal_requirement": "Commercial/agricultural use value should be excluded",
            "citation": "Section 4201.3, Property Valuation"
        },

        "second_home_requirements": {
            "unit_limit": "1-unit only",
            "occupancy_requirement": "Must be suitable for year-round occupancy",
            "restrictions": [
                "Cannot be subject to rental pool",
                "Cannot be subject to time-share arrangement"
            ],
            "citation": "Section 4201.4, Second Homes"
        },
    },

    # ----- OCCUPANCY RULES -----
    "occupancy_rules": {
        "standard_requirements": {
            "primary_residence": "Borrower must intend to occupy as primary residence",
            "second_home": "1-unit only, must be suitable for year-round occupancy",
            "investment": "No occupancy requirement",
        },
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
        "streamline_refi_detailed": {
            "credit_qualifying": {"max_ltv": 97.75, "citation": "HUD 4000.1 II.A.8"},
            "non_credit_qualifying": {"max_ltv": None, "notes": "No maximum LTV — no appraisal required", "citation": "HUD 4000.1 II.A.8"},
        },
        "identity_of_interest": {
            "standard": {"max_ltv": 85, "citation": "HUD 4000.1 II.A.2"},
            "exceptions_full_ltv": ["family member purchasing principal residence", "tenant purchasing unit they've been renting for 6+ months", "employee relocation"],
            "citation": "HUD 4000.1 II.A.2",
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
        "non_traditional_credit": {
            "allowed": True,
            "when": "When borrower has insufficient traditional credit history (fewer than 3 tradelines with 12-month history)",
            "requirements": "Manual UW with 3+ references, 12-month history, no late payments",
            "citation": "HUD 4000.1 II.A.2",
        },
        "no_score_borrower": {
            "eligible": True,
            "conditions": "Eligible with manual UW + non-traditional credit",
            "citation": "HUD 4000.1 II.A.2",
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
        "mip_duration": {
            "ltv_90_or_less": {"duration": "11 years", "notes": "MIP drops after 11 years if initial LTV ≤ 90%"},
            "ltv_over_90": {"duration": "Life of loan", "notes": "MIP for entire loan term if initial LTV > 90%"},
            "citation": "HUD Mortgagee Letter 2013-04",
        },
        "streamline_refi_mip_discount": {
            "within_36_months": {"upfront_mip_rate": 0.01, "notes": "Reduced UFMIP of 0.01% if refinancing FHA within 3 years"},
            "standard": {"upfront_mip_rate": 1.75},
            "citation": "HUD 4000.1 II.A.8",
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

        "ineligible_property_types": {
            "types": [
                "Commercial properties",
                "Investor properties with >25% commercial use",
                "Manufactured homes not on permanent foundation",
                "Properties in flood zone without proper insurance",
                "Properties with conditions affecting safety/soundness",
                "Properties with defective conditions (lead paint in pre-1978 with deterioration)"
            ],
            "citation": "HUD 4000.1, II.D.2, Property Eligibility"
        },

        "condo_approval": {
            "requirement": "Must be FHA-approved (FHAP) OR meet single-unit approval criteria",
            "project_requirements": {
                "owner_occupied_min_pct": 50,
                "hazard_liability_insurance": "Adequate coverage required",
                "hoa_reserves": "Must be adequate",
                "single_entity_max_ownership": "10% of units owned by single entity (for FHA approval)",
                "delinquency_threshold": "Low delinquency rate required"
            },
            "single_unit_alternative": "Can approve single units that meet HUD 4000.1 criteria even if project not FHA-approved",
            "citation": "HUD 4000.1, Condominium Project Approval"
        },

        "manufactured_housing": {
            "requirements": [
                "HUD certified",
                "Permanent foundation (per HUD handbook 4930.3G)",
                "Classified as real property",
                "Minimum 400 square feet"
            ],
            "ltv_limits": "Same as site-built properties",
            "citation": "HUD 4000.1, Manufactured Housing Eligibility"
        },

        "mixed_use_property": {
            "requirement": "Must be primarily residential",
            "commercial_max_pct": 25,
            "citation": "HUD 4000.1, Mixed-Use Properties"
        },

        "property_flipping": {
            "policy": "STRICT anti-flip rules",
            "rules": {
                "less_than_90_days": "INELIGIBLE if seller acquired property less than 90 days prior",
                "91_to_180_days": "If resale price is >=100% above acquisition price, requires second appraisal at borrower's expense",
                "exceptions": [
                    "HUD REO properties",
                    "Government agencies",
                    "Nonprofits",
                    "Employers",
                    "Relocation companies"
                ]
            },
            "citation": "HUD 4000.1, II.D.1, Property Flipping Restrictions"
        },

        "accessory_dwelling_unit": {
            "allowed": True,
            "treatment": "ADU considered part of the property",
            "requirements": "Must meet Minimum Property Requirements (MPRs)",
            "citation": "HUD 4000.1, Accessory Dwelling Units"
        },

        "leasehold_estate": {
            "eligible": True,
            "remaining_lease_term": "Must have at least 25 years remaining on ground lease beyond FHA mortgage term",
            "lease_renewable": "Lease must be renewable",
            "citation": "HUD 4000.1, Leasehold Properties"
        },

        "co_op": {
            "eligible": True,
            "jurisdiction": "Eligible in some states/markets with FHA approval",
            "citation": "HUD 4000.1, Cooperative Housing"
        },

        "pud": {
            "eligible": True,
            "requirements": "Must meet FHA project requirements",
            "citation": "HUD 4000.1, Planned Unit Development (PUD) Eligibility"
        },

        "rural_property": {
            "acreage_restriction": "No acreage restriction if property is residential",
            "appraisal_requirement": "Value of agricultural-use land should be excluded from appraised value",
            "citation": "HUD 4000.1, Property Valuation for Rural Properties"
        },

        "second_home_requirements": {
            "fha_only_primary": "NOT APPLICABLE - FHA is primary residence only",
            "citation": "HUD 4000.1, II.A.1, Occupancy Requirements"
        },
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

    # ----- RESERVE REQUIREMENTS -----
    "reserves": {
        "primary_1_unit": {"months": 0, "notes": "No minimum reserves required for primary residence purchase"},
        "not_applicable": "FHA does not have separate investment/multi-unit categories due to owner-occupied only requirement",
        "citation": "HUD 4000.1, II.A.4.a",
    },

    # ----- ASSET & RESERVE SOURCES -----
    "asset_rules": {
        "eligible_reserve_sources": {
            "categories": ["checking/savings", "money market", "CDs", "stocks/bonds/mutual funds (current market value)", "retirement funds (if evidence of liquidation ability)", "trust accounts", "cash value of life insurance"],
            "citation": "HUD 4000.1, II.A.4.a",
        },
        "ineligible_reserve_sources": {
            "categories": ["gift funds (not for reserves)", "borrowed funds (not acceptable)", "equity in other properties"],
            "citation": "HUD 4000.1, II.A.4.a",
        },
        "gift_of_equity": {
            "allowed": True,
            "eligible_donors": ["family only"],
            "ltv_calculation": "Based on property value",
            "uses": ["down payment", "closing costs"],
            "citation": "HUD 4000.1, II.A.4.d",
        },
        "interested_party_contributions": {
            "ltv_over_90": {"max_pct": 6, "based_on": "purchase price"},
            "ltv_90_or_under": {"max_pct": 6, "based_on": "purchase price"},
            "allowed_uses": ["closing costs", "prepaids", "discount points", "MIP premium"],
            "not_allowed_uses": ["down payment"],
            "citation": "HUD 4000.1, II.A.4.d.iii",
        },
        "large_deposit_explanation": {
            "threshold": ">1% of the adjusted purchase price OR exceeds borrower's average monthly balance",
            "required_documentation": "Source documentation",
            "citation": "HUD 4000.1, II.A.4.a",
        },
        "retirement_account_rules": {
            "requirement": "Must demonstrate ability to withdraw",
            "for_reserves": "Typically 60% of vested balance",
            "citation": "HUD 4000.1, II.A.4.a",
        },
        "life_insurance_cash_value": {
            "net_cash_surrender_value": "Can be used for reserves or down payment",
            "required_documentation": "Statement from insurance company",
        },
        "sale_of_home_proceeds": {
            "acceptable": True,
            "required_documentation": "Closing disclosure or HUD-1",
        },
        "cryptocurrency": {
            "down_payment": "Not addressed specifically; if converted to cash and in bank, treated as regular deposit",
            "reserves": "Not addressed specifically; if converted to cash and in bank, treated as regular deposit",
            "large_deposit_rule": "Must be sourced if exceeds threshold",
        },
        "foreign_assets": {
            "acceptable": True,
            "if_documented": True,
            "foreign_currency_rule": "Currency conversion required",
            "citation": "HUD 4000.1, II.A.4.a",
        },
        "earnest_money_deposit": {
            "must_document_source": True,
            "shown_on": "Sales contract",
            "verified_against": "Bank statements",
        },
        "gift_documentation_requirements": {
            "required_items": ["Gift letter", "Evidence of transfer", "May verify donor's ability to give"],
            "citation": "HUD 4000.1, II.A.4.d.iii",
        },
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
            "forbearance_seasoning": {
                "requirement": "3 months after plan completion",
                "citation": "HUD 4000.1, II.A.4.a",
            },
            "multiple_derogatory_stacking": {
                "rule": "Same as Fannie and Freddie. Each event counted separately.",
                "citation": "HUD 4000.1, II.A.4.a",
            },
            "disputed_tradelines": {
                "rule": "Must provide documentation of dispute",
                "citation": "HUD 4000.1, II.A.4.b",
            },
        },
        "authorized_user_accounts": {
            "treatment": "MUST INCLUDE in DTI",
            "exception": "May exclude only if borrower can document they are NOT responsible",
            "citation": "HUD 4000.1, II.A.4.b",
        },
        "heloc_payment": {
            "actual_payment": "Use actual monthly payment",
            "if_no_payment_reported": "Use 1% of outstanding balance",
            "citation": "HUD 4000.1",
        },
        "business_debt_in_borrower_name": {
            "may_exclude_if": [
                "Documentation shows business makes payments (12 months history)",
                "Payments are deducted from business income on tax returns",
            ],
            "citation": "HUD 4000.1",
        },
        "tax_liens_judgments": {
            "tax_liens": "Must have payment plan approved by IRS with 3 months of timely payments",
            "judgments": "Must be paid off",
            "citation": "HUD 4000.1",
        },
        "open_30_day_charge_accounts": {
            "treatment": "NOT included in DTI",
            "condition": "Account is paid monthly in full",
            "citation": "HUD 4000.1",
        },
        "contingent_liabilities": {
            "general_rule": "Include in DTI",
            "exclusion": "May exclude if liability is resolved",
            "citation": "HUD 4000.1",
        },
        "solar_panel_lease_loan": {
            "leased_solar_panels": "Include monthly payment in DTI",
            "owned_system": "No DTI impact",
            "citation": "HUD 4000.1",
        },
        "installment_debt_less_than_10_months": {
            "treatment": "MUST INCLUDE in DTI regardless of remaining term",
            "notes": "FHA does NOT allow the 10-month exclusion available to conventional loans",
            "citation": "HUD 4000.1",
        },
        "property_tax_hoa_assessment": {
            "treatment": "Always included in DTI calculation",
            "components": ["Property taxes", "Homeowner's insurance", "HOA dues", "Condo assessments", "Flood insurance"],
            "part_of": "PITIA calculation",
            "citation": "HUD 4000.1, II.A.4.c",
        },
        "deferred_non_student_debt": {
            "actual_payment_known": "Use actual monthly payment",
            "if_no_payment_reported": "Use 5% of balance divided by 12",
            "citation": "HUD 4000.1",
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
        "base_pay_salary": {
            "source": "Current W-2 employment or verified contract income",
            "calculation_hourly": "Hourly rate × hours × 52 weeks / 12 months",
            "ytd_variance_check": "Current base pay, verify YTD earnings are consistent with base calculation",
            "documentation": ["current paystub showing YTD earnings", "offer letter or contract", "verification of employment (VOE)"],
            "citation": "HUD 4000.1, II.A.4.c.2, Employment Income",
        },
        "overtime_income": {
            "requirement": "2 years history of overtime earnings",
            "calculation_stable_or_increasing": "Use 2-year average",
            "calculation_declining": "Use most recent year (lower amount) or exclude with justification if declining",
            "must_be_likely_to_continue": True,
            "documentation": ["2 years W-2s or VOE showing OT breakdown", "most recent paystub showing YTD OT"],
            "citation": "HUD 4000.1, II.A.4.c.4, Variable Income",
        },
        "bonus_income": {
            "requirement": "2 years history of bonus payments",
            "calculation_stable_or_increasing": "Use 2-year average",
            "calculation_declining": "Use most recent year (lower amount) or exclude if declining",
            "must_be_likely_to_continue": True,
            "documentation": ["2 years W-2s or VOE showing bonus breakdown", "most recent paystub", "employment contract if guaranteed"],
            "citation": "HUD 4000.1, II.A.4.c.4, Variable Income",
        },
        "tip_income": {
            "requirement": "2 years documented tip income history",
            "calculation": "2-year average, documented on tax returns",
            "must_be_on_tax_returns": True,
            "documentation": ["2 years of tax returns showing tip income", "W-2s or 1099s with tip amounts", "recent paystubs"],
            "citation": "HUD 4000.1, II.A.4.c.4, Service Industry Income",
        },
        "part_time_income": {
            "requirement": "2 years uninterrupted history at part-time employer",
            "no_minimum_hours": True,
            "can_be_supplemental": True,
            "must_be_likely_to_continue": True,
            "documentation": ["2 years VOE", "paystubs", "tax returns"],
            "citation": "HUD 4000.1, II.A.4.c.2, Supplemental Income",
        },
        "seasonal_income": {
            "requirement": "2 years history of same seasonal employment",
            "calculation": "2-year average (annualized)",
            "off_season_consideration": "Unemployment compensation during off-season may be counted if available",
            "documentation": ["2 years tax returns", "2 years VOE", "documentation of seasonal employment terms"],
            "citation": "HUD 4000.1, II.A.4.c.2, Seasonal Income",
        },
        "employment_gaps": {
            "gaps_must_be_explained": "Yes, gaps > 6 months require explanation",
            "re_establishment_requirement": "Gaps > 6 months require 6+ months re-establishment in employment",
            "documentation": ["Letter of Explanation (LOE) for any gap > 6 months", "evidence of current employment"],
            "citation": "HUD 4000.1, II.A.4.c.i, Employment Requirements",
        },
        "foreign_income": {
            "requirement": "Must file US tax returns",
            "foreign_tax_returns": "Foreign tax returns accepted in conjunction with US returns",
            "us_employment_verification": "Verify employment with documented foreign or US employer",
            "documentation": ["US tax returns", "foreign tax returns if applicable", "VOE from employer"],
            "citation": "HUD 4000.1, II.A.4.c.1, Foreign Employment Income",
        },
        "employment_offer_letter": {
            "note": "Not specifically addressed for future employment start; generally need VOE or other verification",
            "documentation": ["verification of employment (VOE)"],
            "citation": "HUD 4000.1, II.A.4.c, Employment Verification",
        },
        "housing_parsonage_allowance": {
            "taxable_treatment": "Non-taxable income (can be grossed up)",
            "grossup_allowed": True,
            "grossup_calculation": "Can be grossed up to account for non-taxable treatment",
            "documentation": ["letter from employer/religious organization documenting allowance"],
            "citation": "HUD 4000.1, II.A.4.c.ii(B), Non-Taxable Income",
        },
        "automobile_allowance": {
            "calculation": "Use net amount after expenses (allowance minus actual documented expenses) = income",
            "if_expense_exceeds_allowance": "Difference treated as monthly liability",
            "documentation": ["documentation of allowance amount", "documentation of actual expenses"],
            "citation": "HUD 4000.1, II.A.4.c.ii, Allowances",
        },
        "long_term_disability_income": {
            "can_use": True,
            "requirement": "Must document likely to continue for at least 3 years from closing date",
            "documentation": ["Disability policy or benefits statement", "most recent bank statement or payment stub"],
            "citation": "HUD 4000.1 II.A.4.c",
        },
        "interest_dividend_income": {
            "can_use": True,
            "requirement": "2-year history on tax returns (Schedule B). Must document sufficient assets to continue generating income.",
            "calculation": "2-year average of interest and dividend income",
            "documentation": ["2 years tax returns (Schedule B)", "current account statements verifying assets"],
            "citation": "HUD 4000.1 II.A.4.c",
        },
        "capital_gains_income": {
            "can_use": True,
            "requirement": "Must show 2-year history AND sufficient remaining assets to continue generating gains",
            "calculation": "2-year average, net gains (not gross proceeds)",
            "documentation": ["2 years tax returns (Schedule D)", "current investment account statements"],
            "citation": "HUD 4000.1 II.A.4.c",
        },
        "trust_income": {
            "can_use": True,
            "requirement": "Must document trust terms, sufficient trust assets, and likelihood of continuance",
            "documentation": ["Trust agreement", "trustee letter", "tax returns or K-1 showing distributions"],
            "citation": "HUD 4000.1 II.A.4.c",
        },
        "royalty_income": {
            "can_use": True,
            "requirement": "2-year history, used average. Oil/gas/mineral rights, book royalties, patent royalties.",
            "documentation": ["2 years tax returns (Schedule E)", "lease/royalty agreement"],
            "citation": "HUD 4000.1 II.A.4.c",
        },
        "foster_care_income": {
            "can_use": True,
            "requirement": "2-year history of foster care income",
            "documentation": ["Letters from state/placing agency", "tax returns or bank statements showing payments"],
            "citation": "HUD 4000.1 II.A.4.c",
        },
        "notes_receivable_income": {
            "can_use": True,
            "requirement": "Must show 3-year continuance from closing date",
            "documentation": ["Copy of note", "evidence of receipt for 12+ months", "tax returns"],
            "citation": "HUD 4000.1 II.A.4.c",
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

    # ----- BORROWER ELIGIBILITY -----
    "borrower_eligibility": {
        "us_citizen": {
            "eligible": True,
            "documentation": "Standard documentation required",
            "citation": "HUD 4000.1, II.A.2.a, Borrower Eligibility",
        },
        "permanent_resident": {
            "eligible": True,
            "documentation": "Valid green card (Form I-551) required",
            "citation": "HUD 4000.1, II.A.2.a, Borrower Eligibility",
        },
        "non_permanent_resident_alien": {
            "eligible": True,
            "requirements": [
                "Valid EAD (Employment Authorization Document)",
                "Valid SSN"
            ],
            "citation": "HUD 4000.1, II.A.2.a, Borrower Eligibility",
        },
        "daca_recipients": {
            "eligible": True,
            "requirements": [
                "Valid EAD (Employment Authorization Document)",
                "Valid SSN"
            ],
            "policy_note": "Confirmed policy as of 2021",
            "citation": "HUD 4000.1, II.A.2.a, Borrower Eligibility",
        },
        "foreign_national_non_resident": {
            "eligible": False,
            "citation": "HUD 4000.1, II.A.2.a, Borrower Eligibility",
        },
        "trust_vesting": {
            "eligible": True,
            "requirements": [
                "Revocable trust",
                "Borrower retains beneficial interest",
                "Property in trust allowed"
            ],
            "citation": "HUD 4000.1, II.A.2.a, Property in Trust",
        },
        "power_of_attorney": {
            "allowed": True,
            "requirements": [
                "POA must be specific to transaction",
                "Must be properly executed per state law",
                "Not expired"
            ],
            "citation": "HUD 4000.1, II.A.2.a, Power of Attorney",
        },
        "first_time_homebuyer": {
            "definition": "No ownership interest in residential property in past 3 years",
            "exceptions": ["displaced homemaker", "single parent"],
            "citation": "HUD 4000.1, II.A.2.a, First-Time Homebuyer",
        },
        "maximum_financed_properties": {
            "limit": "No specific cap",
            "restriction": "Primary residence only. Only 1 FHA loan at a time (exceptions for relocation >100 miles)",
            "citation": "HUD 4000.1, II.A.2.a, Property Eligibility",
        },
        "age_of_borrower": {
            "requirement": "Must be of legal age to contract in property state (typically 18)",
            "citation": "HUD 4000.1, II.A.2.a, Borrower Eligibility",
        },
    },

    # ----- ARM RULES -----
    "arm_rules": {
        "qualifying_rate": {
            "all_arms": {
                "rule": "Use greater of note rate + 1% or fully indexed rate",
                "applies_to": "All ARM types",
                "citation": "HUD 4000.1, II.A.4.d, ARM Qualifying Rate",
            },
        },
        "eligible_indices": {
            "cmt": {
                "acceptable": True,
                "type": "1-year Constant Maturity Treasury",
                "citation": "HUD 4000.1, II.A.4.d",
            },
        },
        "rate_cap_structures": {
            "1_year_arm": {
                "caps": "1% initial / 1% periodic / 5% lifetime",
                "citation": "HUD 4000.1, II.A.4.d",
            },
            "other_arm": {
                "caps": "2% initial / 2% periodic / 6% lifetime",
                "applies_to": "ARMs with adjustment periods other than 1 year",
                "citation": "HUD 4000.1, II.A.4.d",
            },
        },
        "interest_only_arm": {
            "eligible": False,
            "note": "Interest-only ARMs are NOT allowed under FHA",
            "citation": "HUD 4000.1, II.A.4.d",
        },
        "arm_conversion_option": {
            "available": True,
            "applies_to": "1-year ARM only",
            "citation": "HUD 4000.1, II.A.4.d",
        },
        "arm_ltv_restrictions": {
            "rule": "Same max LTV as fixed rate loans",
            "citation": "HUD 4000.1, II.A.4.d",
        },
    },

    # ----- REFINANCE RULES -----
    "refinance_rules": {
        "cash_out_seasoning": {
            "required_months": 12,
            "requirements": [
                "Must have owned and occupied property for at least 12 months",
                "Must have made 6 on-time mortgage payments",
            ],
            "citation": "HUD 4000.1, II.A.8.d, Cash-Out Refinance Seasoning",
        },
        "delayed_financing_exception": {"not_applicable": True},
        "rate_term_refi_seasoning": {
            "type": "Simple refinance (FHA-to-FHA)",
            "required_days": 210,
            "required_payments": 6,
            "calculation": "210 days since closing and 6 payments made",
            "citation": "HUD 4000.1, II.A.8.b, FHA Streamline Refinance",
        },
        "continuity_of_obligation": {
            "streamline": "Must be FHA-to-FHA refinance for streamline eligibility",
            "standard": "Standard borrower requirements apply for non-streamline",
            "citation": "HUD 4000.1, II.A.8",
        },
        "net_tangible_benefit": {
            "streamline_requirement": True,
            "rule": "Must result in combined rate reduction of at least 0.5% (net tangible benefit)",
            "exception": "No reduction required if refinancing ARM to fixed",
            "citation": "HUD 4000.1, II.A.8.b, Net Tangible Benefit",
        },
        "subordinate_financing_on_refi": {
            "existing_liens_may_remain": True,
            "condition": "Must be resubordinated",
            "citation": "HUD 4000.1, II.A.8",
        },
        "fha_streamline": {
            "available": True,
            "types": [
                {
                    "name": "Credit-qualifying streamline",
                    "requirement": "Full income/DTI review required",
                    "appraisal": "Required",
                },
                {
                    "name": "Non-credit-qualifying streamline",
                    "requirement": "No income verification, no appraisal",
                    "max_ltv": None,
                    "note": "No maximum LTV on non-credit-qualifying streamline",
                },
            ],
            "seasoning": "210 days since closing + 6 payments made",
            "ufmip_reduction": "Reduced if within 3 years of prior FHA loan",
            "citation": "HUD 4000.1, II.A.8, FHA Streamline Refinance",
        },
        "va_irrrl": {"not_applicable": True},
    },

    # ----- TEMPORARY BUYDOWNS -----
    "temporary_buydowns": {
        "eligible_structures": {
            "description": "2-1, 1-0, 3-2-1 buydowns allowed",
            "transaction_types": ["Purchase"],
            "exclusions": ["Refinance", "Cash-out"],
            "note": "Purchase transactions only",
            "citation": "HUD 4000.1, II.A.6, Temporary Rate Buydown",
        },
        "qualifying_rate": {
            "standard_rule": "Qualify at the NOTE rate (not the reduced/buydown rate)",
            "citation": "HUD 4000.1, II.A.6",
        },
        "who_can_fund": {
            "allowed_sources": ["seller", "builder", "employer (relocation)", "lender", "borrower"],
            "note": "Contributions from interested parties count toward IPC limits",
            "borrower_funded": "Acceptable",
            "citation": "HUD 4000.1, II.A.6",
        },
        "escrow_requirements": {
            "requirement": "Full buydown subsidy must be deposited into escrow account at closing",
            "lender_responsibility": "Lender must maintain escrow account",
            "unused_funds": "Returned to party who funded the buydown",
            "citation": "HUD 4000.1, II.A.6",
        },
        "buydown_not_allowed": {
            "cash_out": True,
            "note": "Not on cash-out or non-purchase transactions",
            "citation": "HUD 4000.1, II.A.6",
        },
    },

    # ----- DOCUMENT AGE REQUIREMENTS -----
    "document_age_requirements": {
        "credit_report": {
            "max_days": 120,
            "measured_from": "Case number assignment date",
            "extension_available": {
                "max_days": 150,
                "note": "Can extend 30 days if updated",
            },
            "citation": "HUD 4000.1, II.A.2.a, Credit Report",
        },
        "appraisal": {
            "standard": {
                "max_days": 120,
                "measured_from": "Effective date",
            },
            "with_update_or_recertification": {
                "max_days": 240,
                "note": "Can extend to 240 days (8 months) with update",
            },
            "new_construction": {
                "max_months": 12,
                "note": "For new construction: 12 months",
            },
            "citation": "HUD 4000.1, II.A.5, Appraisal Validity",
        },
        "income_documents": {
            "paystubs": {
                "requirement": "Most recent 30-day period",
                "note": "Current 30 days of paystubs",
            },
            "tax_returns": {
                "requirement": "Most recent 2 years",
                "note": "Must include 2 years of filed returns",
            },
            "voe": {
                "max_days": 180,
                "measured_from": "Disbursement date",
                "note": "VOE within 180 days of disbursement",
            },
            "citation": "HUD 4000.1, II.A.2.a, Income Documentation",
        },
        "bank_statements": {
            "requirement": "Most recent 2 months",
            "max_days": 120,
            "measured_from": "Disbursement date",
            "note": "Must be dated within 120 days of disbursement",
            "citation": "HUD 4000.1, II.A.3.a, Bank Statements",
        },
        "title_search": {
            "requirement": "Must be current",
            "typical_update_window": "30-90 days before closing",
            "title_insurance_commitment": "Required",
            "citation": "HUD 4000.1, II.A.7, Title",
        },
    },

    # ----- OCCUPANCY RULES -----
    "occupancy_rules": {
        "primary_residence": {
            "requirement": "Borrower must intend to occupy as primary residence",
            "affidavit": "Occupancy affidavit required",
            "citation": "HUD 4000.1, II.A.2",
        },
        "investment_properties": {
            "allowed": False,
            "note": "FHA is for owner-occupied only",
        },
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
        "irrrl_simplified": {
            "max_ltv": None,
            "notes": "No maximum LTV on IRRRL — no appraisal required",
            "citation": "VA Pamphlet 26-7, Ch. 6",
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
        "non_traditional_credit": {
            "allowed": True,
            "when": "When borrower has insufficient traditional credit history (fewer than 3 tradelines with 12-month history)",
            "requirements": "VA accepts alternative credit (utility bills, rent, insurance)",
            "citation": "VA Pamphlet 26-7 Ch. 4",
        },
        "no_score_borrower": {
            "eligible": True,
            "conditions": "Eligible (VA has no minimum score requirement)",
            "citation": "VA Pamphlet 26-7 Ch. 4",
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

    # ----- RESERVE REQUIREMENTS -----
    "reserves": {
        "primary_1_4_unit": {"months": 0, "notes": "No minimum reserves required for VA loans"},
        "citation": "VA Pamphlet 26-7, Ch. 4",
    },

    # ----- ASSET & RESERVE SOURCES -----
    "asset_rules": {
        "eligible_reserve_sources": {
            "categories": ["checking/savings", "money market", "CDs", "stocks/bonds/mutual funds (current market value)", "retirement (401k/IRA - 60% of vested balance if borrower does not have unrestricted access, 100% if over 59.5 or evidence of distribution)", "trust accounts", "cash value of life insurance"],
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "ineligible_reserve_sources": {
            "categories": ["gift funds (cannot be used for reserves)", "equity in other properties", "borrowed funds"],
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "gift_of_equity": {
            "allowed": True,
            "eligible_donors": ["family only"],
            "no_down_payment_required": "Full entitlement allows 100% financing",
            "uses": ["purchase price coverage"],
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "interested_party_contributions": {
            "max_pct": 4,
            "based_on": "purchase price",
            "what_it_covers": ["prepaid taxes/insurance (beyond year 1)", "paying off buyer's debts", "VA funding fee credit"],
            "seller_concessions": "Seller can pay ALL closing costs (not counted against 4% cap)",
            "citation": "VA Pamphlet 26-7, Ch. 4, Sec. 4.f, Seller Concessions",
        },
        "large_deposit_explanation": {
            "threshold": "Significant deposits",
            "required_documentation": "Source documentation",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "retirement_account_rules": {
            "treatment": "Same general treatment as other agencies",
            "for_down_payment": "100% of vested balance if borrower provides evidence of withdrawal/distribution",
            "for_reserves": "60% of vested if <59.5 and no unrestricted access; 100% if ≥59.5 or unrestricted access",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "life_insurance_cash_value": {
            "net_cash_surrender_value": "Can be used for down payment or reserves",
            "required_documentation": "Statement from insurance company",
        },
        "sale_of_home_proceeds": {
            "acceptable": True,
            "required_documentation": "Closing disclosure or HUD-1",
        },
        "cryptocurrency": {
            "down_payment": "NOT acceptable UNLESS converted to US dollars and deposited in verified financial institution",
            "reserves": "NOT acceptable UNLESS converted to US dollars",
            "when_converted": "Treated as regular bank deposit (needs sourcing)",
        },
        "foreign_assets": {
            "acceptable": True,
            "if_verifiable": True,
            "foreign_currency_rule": "Must be converted to USD at current exchange rate",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "earnest_money_deposit": {
            "must_document_source": True,
            "shown_on": "Sales contract",
            "verified_against": "Bank statements",
        },
        "gift_documentation_requirements": {
            "required_items": ["Gift letter (signed by donor) stating: amount, relationship, property address, no repayment expected", "Evidence of transfer"],
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
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

        "ineligible_property_types": {
            "types": [
                "Commercial farms",
                "Properties not suitable for year-round occupancy",
                "Income-producing properties as primary purpose"
            ],
            "citation": "VA Pamphlet 26-7, Ch. 12, Property Type Requirements"
        },

        "condo_approval": {
            "requirement": "Must be VA-approved",
            "approval_process": "Condo must be on VA-maintained approved list",
            "approval_submission": "Approval process through VA Regional Loan Center",
            "citation": "VA Pamphlet 26-7, Ch. 12, Condominium Approval"
        },

        "manufactured_housing": {
            "requirements": [
                "Must be classified as real estate",
                "On permanent foundation",
                "Meets VA Minimum Property Requirements (MPRs)",
                "No minimum square footage requirement"
            ],
            "citation": "VA Pamphlet 26-7, Ch. 12, Manufactured Housing"
        },

        "mixed_use_property": {
            "requirement": "Must be primarily residential in character",
            "citation": "VA Pamphlet 26-7, Ch. 12"
        },

        "property_flipping": {
            "policy": "No specific anti-flipping rule",
            "appraisal_requirement": "Appraisal must support the value",
            "citation": "VA Pamphlet 26-7, Ch. 12, Property Appraisal"
        },

        "accessory_dwelling_unit": {
            "allowed": True,
            "requirements": "Must meet VA Minimum Property Requirements (MPRs)",
            "income_consideration": "Income consideration per standard rental rules",
            "citation": "VA Pamphlet 26-7, Ch. 12"
        },

        "leasehold_estate": {
            "eligible": True,
            "remaining_lease_term": "Remaining lease term must extend 14 years beyond mortgage maturity",
            "citation": "VA Pamphlet 26-7, Ch. 12, Leasehold Properties"
        },

        "co_op": {
            "eligible": True,
            "jurisdiction": "Eligible in certain states (mainly New York)",
            "va_approval_requirement": "Must meet VA approval criteria",
            "citation": "VA Pamphlet 26-7, Ch. 12, Cooperative Housing"
        },

        "pud": {
            "eligible": True,
            "citation": "VA Pamphlet 26-7, Ch. 12, Planned Unit Development (PUD)"
        },

        "rural_property": {
            "acreage_restriction": "Eligible if residential",
            "income_restriction": "Agricultural income is NOT used from subject property",
            "citation": "VA Pamphlet 26-7, Ch. 12, Rural Property"
        },

        "second_home_requirements": {
            "va_only_primary": "NOT APPLICABLE - VA is primary residence only",
            "citation": "VA Pamphlet 26-7, Ch. 3, Occupancy Requirements"
        },
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
            "forbearance_seasoning": {
                "requirement": "Current and stable",
                "citation": "VA Pamphlet 26-7, Ch. 4",
            },
            "multiple_derogatory_stacking": {
                "rule": "Same as other agencies. Each event counted separately.",
                "citation": "VA Pamphlet 26-7, Ch. 4",
            },
            "disputed_tradelines": {
                "rule": "Explain but not usually disqualifying",
                "citation": "VA Pamphlet 26-7, Ch. 4",
            },
        },
        "authorized_user_accounts": {
            "treatment": "Include in DTI",
            "exclusion": "May exclude if documentation shows borrower is not responsible",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "heloc_payment": {
            "actual_payment": "Use actual payment or qualifying payment per terms",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "business_debt_in_borrower_name": {
            "may_exclude_with": "Documentation of business paying the debt",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "tax_liens_judgments": {
            "tax_liens": "May be in payment plan (acceptable)",
            "judgments": "Should be paid off",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "open_30_day_charge_accounts": {
            "treatment": "NOT included in DTI",
            "condition": "Account is paid monthly",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "contingent_liabilities": {
            "general_rule": "Include in DTI",
            "exclusion": "May exclude if documented",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "solar_panel_lease_loan": {
            "leased_solar_panels": "Include monthly payment in DTI",
            "owned_system": "No DTI impact",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "installment_debt_less_than_10_months": {
            "treatment": "MUST INCLUDE in DTI regardless of remaining term",
            "notes": "VA does NOT allow the 10-month exclusion available to conventional loans",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "property_tax_hoa_assessment": {
            "treatment": "Always included in DTI calculation",
            "components": ["Property taxes", "Homeowner's insurance", "HOA dues", "Condo assessments", "Flood insurance"],
            "part_of": "PITIA calculation",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "deferred_non_student_debt": {
            "actual_payment_known": "Use actual monthly payment",
            "if_no_payment_reported": "Use 5% of outstanding balance",
            "citation": "VA Pamphlet 26-7, Ch. 4",
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
        "base_pay_salary": {
            "source": "Current W-2 employment or verified contract income",
            "calculation_hourly": "Hourly rate × hours × 52 weeks / 12 months",
            "ytd_variance_check": "If YTD earnings differ from base calculation, may average current and prior year",
            "documentation": ["current paystub showing YTD earnings", "offer letter or contract", "verification of employment (VOE)"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Section 4.04, Employment Income",
        },
        "overtime_income": {
            "requirement": "2 years history of overtime earnings",
            "calculation_stable_or_increasing": "Use 2-year average",
            "calculation_declining": "Use most recent year (lower amount) or exclude if declining",
            "must_be_likely_to_continue": True,
            "documentation": ["2 years W-2s or VOE showing OT breakdown", "most recent paystub showing YTD OT"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Variable Income",
        },
        "bonus_income": {
            "requirement": "2 years history of bonus payments",
            "calculation_stable_or_increasing": "Use 2-year average",
            "calculation_declining": "Use most recent year (lower amount) or exclude if declining",
            "must_be_likely_to_continue": True,
            "documentation": ["2 years W-2s or VOE showing bonus breakdown", "most recent paystub", "employment contract if guaranteed"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Variable Income",
        },
        "tip_income": {
            "requirement": "2 years documented tip income history",
            "calculation": "2-year average, documented on tax returns",
            "must_be_on_tax_returns": True,
            "documentation": ["2 years of tax returns showing tip income", "W-2s or 1099s with tip amounts", "recent paystubs"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Service Industry Income",
        },
        "part_time_income": {
            "requirement": "2 years uninterrupted history at part-time employer",
            "no_minimum_hours": True,
            "can_be_supplemental": True,
            "documentation": ["2 years VOE", "paystubs", "tax returns"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Supplemental Income",
        },
        "seasonal_income": {
            "requirement": "2 years history of same seasonal employment",
            "calculation": "2-year average (annualized)",
            "off_season_consideration": "Unemployment compensation during off-season may be counted if available",
            "documentation": ["2 years tax returns", "2 years VOE", "documentation of seasonal employment terms"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Seasonal Income",
        },
        "employment_gaps": {
            "gaps_require_loe": True,
            "returning_to_same_type_strengthens": True,
            "documentation": ["Letter of Explanation (LOE) for any gap"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Section 2, Employment History",
        },
        "foreign_income": {
            "requirement": "US tax returns required",
            "us_employment_verification": "Verify employment with documented employer",
            "documentation": ["US tax returns", "VOE from employer"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Foreign Employment Income",
        },
        "employment_offer_letter": {
            "acceptable_if": "Employment to start within reasonable period",
            "income_counted": "Guaranteed/base income only",
            "documentation": ["written employment offer letter with specific terms"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Offer Letter / Prospective Employment",
        },
        "housing_parsonage_allowance": {
            "taxable_treatment": "Non-taxable income",
            "grossup_allowed": True,
            "grossup_calculation": "Can be grossed up to account for non-taxable treatment",
            "documentation": ["letter from employer/religious organization documenting allowance"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Non-Taxable Allowances",
        },
        "automobile_allowance": {
            "calculation": "Only net amount (allowance minus actual documented expenses) = income",
            "if_expense_exceeds_allowance": "Difference treated as monthly liability",
            "documentation": ["documentation of allowance amount", "documentation of actual expenses"],
            "citation": "VA Pamphlet 26-7, Ch. 4, Allowances",
        },
        "long_term_disability_income": {
            "can_use": True,
            "requirement": "Must document likely to continue for at least 3 years from closing date",
            "documentation": ["Disability policy or benefits statement", "most recent bank statement or payment stub"],
            "citation": "VA Pamphlet 26-7 Ch.4",
        },
        "interest_dividend_income": {
            "can_use": True,
            "requirement": "2-year history on tax returns (Schedule B). Must document sufficient assets to continue generating income.",
            "calculation": "2-year average of interest and dividend income",
            "documentation": ["2 years tax returns (Schedule B)", "current account statements verifying assets"],
            "citation": "VA Pamphlet 26-7 Ch.4",
        },
        "capital_gains_income": {
            "can_use": True,
            "requirement": "Must show 2-year history AND sufficient remaining assets to continue generating gains",
            "calculation": "2-year average, net gains (not gross proceeds)",
            "documentation": ["2 years tax returns (Schedule D)", "current investment account statements"],
            "citation": "VA Pamphlet 26-7 Ch.4",
        },
        "trust_income": {
            "can_use": True,
            "requirement": "Must document trust terms, sufficient trust assets, and likelihood of continuance",
            "documentation": ["Trust agreement", "trustee letter", "tax returns or K-1 showing distributions"],
            "citation": "VA Pamphlet 26-7 Ch.4",
        },
        "royalty_income": {
            "can_use": True,
            "requirement": "2-year history, used average. Oil/gas/mineral rights, book royalties, patent royalties.",
            "documentation": ["2 years tax returns (Schedule E)", "lease/royalty agreement"],
            "citation": "VA Pamphlet 26-7 Ch.4",
        },
        "foster_care_income": {
            "can_use": True,
            "requirement": "2-year history of foster care income",
            "documentation": ["Letters from state/placing agency", "tax returns or bank statements showing payments"],
            "citation": "VA Pamphlet 26-7 Ch.4",
        },
        "notes_receivable_income": {
            "can_use": True,
            "requirement": "Must show 3-year continuance from closing date",
            "documentation": ["Copy of note", "evidence of receipt for 12+ months", "tax returns"],
            "citation": "VA Pamphlet 26-7 Ch.4",
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

    # ----- BORROWER ELIGIBILITY -----
    "borrower_eligibility": {
        "us_citizen": {
            "eligible": True,
            "note": "Must meet VA service requirements",
            "citation": "VA Pamphlet 26-7, Ch. 2",
        },
        "permanent_resident": {
            "eligible": True,
            "note": "Eligible if veteran meets service requirements",
            "citation": "VA Pamphlet 26-7, Ch. 2",
        },
        "non_permanent_resident_alien": {
            "eligible": "if_veteran",
            "requirements": [
                "Must have valid legal presence in US",
                "Generally must be eligible veteran first"
            ],
            "citation": "VA Pamphlet 26-7, Ch. 2",
        },
        "daca_recipients": {
            "eligible": False,
            "reason": "Must meet military service requirements. DACA recipients cannot enlist in most branches",
            "citation": "VA Pamphlet 26-7, Ch. 2",
        },
        "foreign_national_non_resident": {
            "eligible": False,
            "citation": "VA Pamphlet 26-7, Ch. 2",
        },
        "trust_vesting": {
            "eligible": True,
            "requirements": [
                "Living trust acceptable",
                "Same conditions as other agencies"
            ],
            "citation": "VA Pamphlet 26-7, Ch. 3",
        },
        "power_of_attorney": {
            "allowed": True,
            "military_exception": "Broader POA accepted for deployed service members",
            "citation": "VA Pamphlet 26-7, Ch. 3",
        },
        "first_time_homebuyer": {
            "requirement": "No requirement for VA (not relevant to eligibility)",
            "citation": "VA Pamphlet 26-7",
        },
        "maximum_financed_properties": {
            "limit": "No limit on financed properties",
            "restriction": "Only 1 VA loan at a time unless entitlement allows second",
            "citation": "VA Pamphlet 26-7, Ch. 2",
        },
        "age_of_borrower": {
            "requirement": "Must be of legal age to contract in property state (typically 18)",
            "citation": "VA Pamphlet 26-7, Ch. 2",
        },
        "va_service_requirements": {
            "active_duty": [
                "90 days continuous during wartime OR",
                "181 days continuous during peacetime OR",
                "24 months / full period ordered (post-1980 enlisted / post-1981 officer)"
            ],
            "reserves_national_guard": [
                "6 years in Selected Reserve OR",
                "90 days active duty wartime OR",
                "Called to active duty under federal authority"
            ],
            "surviving_spouse": [
                "Unremarried OR remarried after age 57 (Dec 16, 2003+)",
                "Service-connected death, MIA, or POW"
            ],
            "current_service_member": "After 90 days continuous active duty",
            "character_of_discharge": "Must be under conditions other than dishonorable",
            "citation": "VA Pamphlet 26-7, Ch. 2; 38 USC 3702",
        },
        "va_surviving_spouse": {
            "eligible_if": [
                "Veteran died from service-connected disability, OR",
                "Veteran was MIA/POW, OR",
                "Veteran had total disability rating for 10+ years before death"
            ],
            "remarriage_rule": "If remarried after age 57 (on or after Dec 16, 2003), still eligible",
            "benefits": "Same loan benefits as veteran, exempt from funding fee",
            "citation": "VA Pamphlet 26-7, Ch. 2, Sec 2.05",
        },
    },

    # ----- ARM RULES -----
    "arm_rules": {
        "qualifying_rate": {
            "all_arms": {
                "rule": "Use note rate + 2% for qualifying DTI",
                "applies_to": "All ARM types",
                "citation": "VA Pamphlet 26-7, Ch. 4, ARM Qualifying Rate",
            },
        },
        "eligible_indices": {
            "cmt": {
                "acceptable": True,
                "type": "1-year Constant Maturity Treasury",
                "citation": "VA Pamphlet 26-7, Ch. 4",
            },
            "sofr": {
                "acceptable": True,
                "type": "SOFR (Secured Overnight Financing Rate)",
                "notes": "SOFR replaced LIBOR effective June 2023",
                "citation": "VA Pamphlet 26-7, Ch. 4",
            },
        },
        "rate_cap_structures": {
            "annual_adjustment": {
                "caps": "1% initial / 1% periodic / 5% lifetime",
                "citation": "VA Pamphlet 26-7, Ch. 4",
            },
        },
        "interest_only_arm": {
            "eligible": False,
            "note": "Interest-only ARMs are NOT allowed under VA",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "arm_conversion_option": {
            "available": False,
            "note": "ARM conversion not commonly offered for VA loans",
            "citation": "VA Pamphlet 26-7, Ch. 4",
        },
        "arm_ltv_restrictions": {
            "rule": "100% LTV same as fixed rate (no down payment)",
            "citation": "VA Pamphlet 26-7, Ch. 3",
        },
    },

    # ----- REFINANCE RULES -----
    "refinance_rules": {
        "cash_out_seasoning": {
            "required_months": 0,
            "note": "No specific seasoning requirement for cash-out refi",
            "requirements": [
                "Must meet credit and income requirements",
            ],
            "citation": "VA Pamphlet 26-7, Ch. 6, Cash-Out Refinance",
        },
        "delayed_financing_exception": {"not_applicable": True},
        "rate_term_refi_seasoning": {
            "type": "IRRRL (Interest Rate Reduction Refinance Loan)",
            "required_days": 210,
            "required_payments": 6,
            "calculation": "210 days since first payment and 6 payments made",
            "citation": "VA Pamphlet 26-7, Ch. 6, Section 6.01, IRRRL Requirements",
        },
        "continuity_of_obligation": {
            "requirement": "Veteran must have been on the original VA loan",
            "citation": "VA Pamphlet 26-7, Ch. 6",
        },
        "net_tangible_benefit": {
            "irrrl_requirement": True,
            "rule": "Must result in lower interest rate",
            "exception": "Can be higher rate if converting ARM to fixed",
            "must_demonstrate": "Net tangible benefit",
            "citation": "VA Pamphlet 26-7, Ch. 6, Section 6.01, Net Tangible Benefit",
        },
        "subordinate_financing_on_refi": {
            "requirement": "Second liens must be subordinated or paid off",
            "citation": "VA Pamphlet 26-7, Ch. 6",
        },
        "fha_streamline": {"not_applicable": True},
        "va_irrrl": {
            "available": True,
            "full_name": "Interest Rate Reduction Refinance Loan",
            "requirement": "Must be VA-to-VA refi",
            "appraisal_required": False,
            "income_verification_required": False,
            "seasoning": "210 days since first payment + 6 payments made",
            "rate_reduction": "Must result in lower rate (except ARM to fixed)",
            "funding_fee": 0.5,
            "funding_fee_notes": "0.5% funding fee regardless of usage",
            "cash_back_limit": 500,
            "cash_back_limit_notes": "Cash back limited to $500",
            "citation": "VA Pamphlet 26-7, Ch. 6, Section 6.01, IRRRL",
        },
    },

    # ----- TEMPORARY BUYDOWNS -----
    "temporary_buydowns": {
        "eligible_structures": {
            "description": "2-1, 1-0 buydowns allowed",
            "transaction_types": ["Purchase"],
            "exclusions": ["Refinance", "Cash-out"],
            "note": "Purchase transactions only",
            "citation": "VA Pamphlet 26-7, Ch. 7, Temporary Rate Buydown",
        },
        "qualifying_rate": {
            "standard_rule": "Qualify at the NOTE rate (not the reduced/buydown rate)",
            "citation": "VA Pamphlet 26-7, Ch. 7",
        },
        "who_can_fund": {
            "allowed_sources": ["seller", "builder", "employer (relocation)", "lender", "borrower"],
            "note": "Contributions from interested parties count toward IPC limits",
            "borrower_funded": "Acceptable",
            "citation": "VA Pamphlet 26-7, Ch. 7",
        },
        "escrow_requirements": {
            "requirement": "Full buydown subsidy must be deposited into escrow account at closing",
            "lender_responsibility": "Lender must maintain escrow account",
            "unused_funds": "Returned to party who funded the buydown",
            "citation": "VA Pamphlet 26-7, Ch. 7",
        },
        "buydown_not_allowed": {
            "cash_out": True,
            "note": "Not on cash-out or non-purchase transactions",
            "citation": "VA Pamphlet 26-7, Ch. 7",
        },
    },

    # ----- DOCUMENT AGE REQUIREMENTS -----
    "document_age_requirements": {
        "credit_report": {
            "max_days": 120,
            "measured_from": "Note date",
            "citation": "VA Pamphlet 26-7, Ch. 4, Credit Report",
        },
        "appraisal": {
            "nov_notice_of_value": {
                "max_months": 6,
                "note": "NOV (Notice of Value) valid for 6 months",
            },
            "extension": {
                "max_months": 12,
                "note": "Can request 6-month extension for 12 months total",
            },
            "irrrl": {
                "requirement": "No appraisal required for IRRRL",
            },
            "citation": "VA Pamphlet 26-7, Ch. 5, Appraisal Validity",
        },
        "income_documents": {
            "paystubs": {
                "requirement": "Most recent 30-day period",
                "note": "Current 30 days of paystubs",
            },
            "voe": {
                "requirement": "Within a reasonable period of closing",
                "note": "Verification of Employment - reasonable period requirement",
            },
            "citation": "VA Pamphlet 26-7, Ch. 4, Income Documentation",
        },
        "bank_statements": {
            "requirement": "Most recent 2 months",
            "citation": "VA Pamphlet 26-7, Ch. 4, Bank Statements",
        },
        "title_search": {
            "requirement": "Must be current",
            "typical_update_window": "30-90 days before closing",
            "title_insurance_commitment": "Required",
            "citation": "VA Pamphlet 26-7, Ch. 5, Title",
        },
    },

    # ----- OCCUPANCY RULES -----
    "occupancy_rules": {
        "primary_residence": {
            "requirement": "Veteran must intend to occupy as primary residence",
            "occupancy_timeline": "Must occupy within 60 days of closing",
            "affidavit": "VA occupancy affidavit required",
            "citation": "VA Pamphlet 26-7, Ch. 3",
        },
        "investment_properties": {
            "allowed": False,
            "note": "VA loans are for owner-occupied properties only",
        },
    },
}


# =============================================================================
# CROSS-AGENCY DETERMINISTIC RULES
# =============================================================================

# ARM Qualifying Rate comparison across agencies
ARM_QUALIFYING_RATE = {
    "Fannie Mae": {
        "5yr_or_less": "Higher of note rate + 2% or fully indexed rate",
        "over_5yr": "Note rate",
        "manual_underwriting": "Note rate + 2%",
        "citation": "B2-1.4-02",
    },
    "Freddie Mac": {
        "5yr_or_less": "Note rate + 2%",
        "over_5yr": "Note rate",
        "citation": "Section 4305.2",
    },
    "FHA": {
        "all": "Greater of note rate + 1% or fully indexed rate",
        "citation": "HUD 4000.1, II.A.4.d",
    },
    "VA": {
        "all": "Note rate + 2%",
        "citation": "VA Pamphlet 26-7, Ch. 4",
    },
}

# Refinance Seasoning comparison across agencies
REFINANCE_SEASONING = {
    "cash_out": {
        "Fannie Mae": {
            "months": 6,
            "exception": "Delayed financing within 6 months if all-cash purchase; Inheritance (no waiting period)",
            "citation": "B2-1.3-03",
        },
        "Freddie Mac": {
            "months": 6,
            "exception": "Delayed financing exception available",
            "citation": "Section 4301.2",
        },
        "FHA": {
            "months": 12,
            "payments_required": 6,
            "citation": "HUD 4000.1, II.A.8.d",
        },
        "VA": {
            "months": 0,
            "notes": "No specific seasoning requirement for cash-out refi",
            "citation": "VA Pamphlet 26-7, Ch. 6",
        },
    },
    "rate_term_refi": {
        "Fannie Mae": {
            "months": 0,
            "notes": "No seasoning requirement for rate-term refi",
            "citation": "B2-1.3-01",
        },
        "Freddie Mac": {
            "months": 0,
            "notes": "No seasoning requirement for rate-term refi",
            "citation": "Section 4301.1",
        },
        "FHA": {
            "days": 210,
            "payments": 6,
            "type": "FHA-to-FHA streamline",
            "citation": "HUD 4000.1, II.A.8.b",
        },
        "VA": {
            "days": 210,
            "payments": 6,
            "type": "IRRRL (Interest Rate Reduction Refinance Loan)",
            "citation": "VA Pamphlet 26-7, Ch. 6, Section 6.01",
        },
    },
    "net_tangible_benefit_requirement": {
        "Fannie Mae": False,
        "Freddie Mac": False,
        "FHA": "Streamline only: 0.5% combined rate reduction (except ARM to fixed)",
        "VA": "IRRRL: Lower rate required (except ARM to fixed)",
    },
    "citation": "Fannie B2-1.3-03; Freddie 4301.2; HUD 4000.1 II.A.8; VA Pamphlet 26-7 Ch.6",
}

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

# Interested party contributions (seller concessions) by agency
INTERESTED_PARTY_CONTRIBUTIONS = {
    "Fannie Mae": {
        "ltv_over_90": {
            "max_pct": 3,
            "based_on": "purchase price or appraised value (whichever is less)",
            "allowed_uses": ["closing costs", "prepaids", "points", "mortgage insurance premiums"],
            "not_allowed_uses": ["down payment", "financial reserves"],
            "citation": "B3-4.1-02",
        },
        "ltv_75_to_90": {
            "max_pct": 6,
            "based_on": "purchase price or appraised value (whichever is less)",
            "allowed_uses": ["closing costs", "prepaids", "points", "mortgage insurance premiums"],
            "not_allowed_uses": ["down payment", "financial reserves"],
            "citation": "B3-4.1-02",
        },
        "ltv_75_or_under": {
            "max_pct": 9,
            "based_on": "purchase price or appraised value (whichever is less)",
            "allowed_uses": ["closing costs", "prepaids", "points", "mortgage insurance premiums"],
            "not_allowed_uses": ["down payment", "financial reserves"],
            "citation": "B3-4.1-02",
        },
        "investment_property": {
            "max_pct": 2,
            "based_on": "purchase price or appraised value (whichever is less)",
            "citation": "B3-4.1-02",
        },
    },
    "Freddie Mac": {
        "ltv_over_90": {
            "max_pct": 3,
            "based_on": "purchase price or appraised value (whichever is less)",
            "allowed_uses": ["closing costs", "prepaids", "points", "mortgage insurance premiums"],
            "not_allowed_uses": ["down payment", "financial reserves"],
            "citation": "Section 5501.5",
        },
        "ltv_75_to_90": {
            "max_pct": 6,
            "based_on": "purchase price or appraised value (whichever is less)",
            "allowed_uses": ["closing costs", "prepaids", "points", "mortgage insurance premiums"],
            "not_allowed_uses": ["down payment", "financial reserves"],
            "citation": "Section 5501.5",
        },
        "ltv_75_or_under": {
            "max_pct": 9,
            "based_on": "purchase price or appraised value (whichever is less)",
            "allowed_uses": ["closing costs", "prepaids", "points", "mortgage insurance premiums"],
            "not_allowed_uses": ["down payment", "financial reserves"],
            "citation": "Section 5501.5",
        },
        "investment_property": {
            "max_pct": 2,
            "based_on": "purchase price or appraised value (whichever is less)",
            "citation": "Section 5501.5",
        },
    },
    "FHA": {
        "all_ltv_levels": {
            "max_pct": 6,
            "based_on": "purchase price",
            "allowed_uses": ["closing costs", "prepaids", "discount points", "mortgage insurance premium (MIP)"],
            "not_allowed_uses": ["down payment"],
            "citation": "HUD 4000.1, II.A.4.d.iii",
        },
    },
    "VA": {
        "all_loans": {
            "max_pct": 4,
            "based_on": "purchase price",
            "what_it_covers": ["prepaid taxes/insurance (beyond year 1)", "paying off buyer's debts", "VA funding fee credit"],
            "seller_concessions_exception": "Seller can pay ALL closing costs without being counted against 4% cap",
            "citation": "VA Pamphlet 26-7, Ch. 4, Sec. 4.f, Seller Concessions",
        },
    },
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

# Borrower eligibility by immigration/citizenship status — cross-agency lookup
BORROWER_ELIGIBILITY_BY_STATUS = {
    "us_citizen": {"Fannie Mae": True, "Freddie Mac": True, "FHA": True, "VA": True},
    "permanent_resident": {"Fannie Mae": True, "Freddie Mac": True, "FHA": True, "VA": True},
    "non_permanent_resident": {"Fannie Mae": True, "Freddie Mac": True, "FHA": True, "VA": "if_veteran"},
    "daca": {"Fannie Mae": True, "Freddie Mac": True, "FHA": True, "VA": False},
    "foreign_national": {"Fannie Mae": False, "Freddie Mac": False, "FHA": False, "VA": False},
    "citation": "Fannie B2-2-02; Freddie 5104.1; HUD 4000.1; VA Pamphlet 26-7 Ch. 2",
}

# Document age requirements — cross-agency lookup table
DOCUMENT_AGE_REQUIREMENTS = {
    "credit_report": {
        "Fannie Mae": {"max_days": 120, "reissue_max": 180},
        "Freddie Mac": {"max_days": 120},
        "FHA": {"max_days": 120, "extension": 30},
        "VA": {"max_days": 120},
        "measured_from": "note date (Fannie/Freddie/VA) or case number assignment (FHA)",
    },
    "appraisal": {
        "Fannie Mae": {"max_days": 120, "with_update_max_months": 12},
        "Freddie Mac": {"max_days": 120, "with_update_max_days": 180},
        "FHA": {"max_days": 120, "with_update_max_days": 240, "new_construction_months": 12},
        "VA": {"max_months": 6, "extension_months": 6, "note": "NOV (Notice of Value) validity"},
    },
    "bank_statements": {"all_agencies": "Most recent 2 consecutive months"},
    "paystubs": {"all_agencies": "Most recent 30-day period"},
    "citation": "Fannie B1-1-03; Freddie 4101.1; HUD 4000.1 II.A; VA Ch.5",
}

# Temporary buydown rules — cross-agency lookup table
TEMPORARY_BUYDOWN_RULES = {
    "qualifying_rate": "Note rate for all agencies (not buydown rate)",
    "eligible_structures": {
        "Fannie Mae": ["3-2-1", "2-1", "1-0"],
        "Freddie Mac": ["3-2-1", "2-1"],
        "FHA": ["3-2-1", "2-1", "1-0"],
        "VA": ["2-1", "1-0"],
    },
    "allowed_transactions": {
        "Fannie Mae": ["Purchase", "Rate-term refinance"],
        "Freddie Mac": ["Purchase"],
        "FHA": ["Purchase"],
        "VA": ["Purchase"],
    },
    "escrow": "Full subsidy deposited at closing, maintained by lender",
    "funding_sources": ["seller", "builder", "employer (relocation)", "lender", "borrower"],
    "ipc_treatment": "Third-party contributions count toward IPC limits",
    "who_can_fund": {
        "allowed": ["seller", "builder", "employer", "lender", "borrower"],
        "note": "All agencies permit all five funding sources",
    },
    "cash_out_refi_not_allowed": {
        "Fannie Mae": True,
        "Freddie Mac": True,
        "FHA": True,
        "VA": True,
    },
    "citation": "Fannie B2-1.4-04; Freddie 4304.1; HUD 4000.1; VA Ch.7",
}


# =============================================================================
# SPECIAL PROGRAM DTI LIMITS
# =============================================================================

SPECIAL_PROGRAM_DTI = {
    "HomeReady": {"max_dti": 50, "method": "DU", "notes": "Same as standard Fannie DU", "citation": "B5-6-02"},
    "Home_Possible": {"max_dti": 50, "method": "LPA", "notes": "Same as standard Freddie LPA", "citation": "Freddie 4501.9"},
    "FHA_EEM": {"dti_stretch": "Energy savings can be added to income, effectively stretching DTI", "citation": "HUD 4000.1"},
}

# =============================================================================
# APPRAISAL REQUIREMENTS
# =============================================================================

APPRAISAL_REQUIREMENTS = {
    "waiver_eligible": {
        "Fannie Mae": "DU PIW (Property Inspection Waiver)",
        "Freddie Mac": "ACE (Automated Collateral Evaluation)",
        "FHA": "No waiver",
        "VA": "No waiver"
    },
    "form_types": {
        "1_unit_sfr": "Form 1004 (Fannie/Freddie), FHA uses same",
        "2_4_unit": "Form 1025 (Small Residential Income Property)",
        "condo": "Form 1073",
        "manufactured": "Form 1004C",
    },
    "minimum_comparables": 3,
    "fha_appraisal_portability": "FHA appraisal stays with property for 120 days, can transfer between lenders",
    "va_appraisal_assignment": "VA assigns appraiser through portal — lender cannot select",
    "desktop_appraisal": "Fannie/Freddie allow desktop appraisals when DU/LPA issues waiver with inspection alternative",
    "citation": "Fannie B4-1; Freddie 4600; HUD 4000.1 II.D; VA Pamphlet 26-7 Ch.10-11",
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
