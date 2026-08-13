"""
CoreTrust System (CTC) -- Lender Approval-Readiness Engine
==========================================================

The honest version of "get approved." Lenders CAN say no -- so this scores your
real profile against what they actually underwrite for a given product, tells you
which criteria you already meet, and gives concrete actions to close the gaps
BEFORE you apply. It never fabricates data and never tries to hide applications
from other lenders.

Thresholds below are typical Canadian guidelines (they vary by lender and change
over time). Treat the output as preparation, not a guarantee.
"""

from __future__ import annotations

from typing import Optional

from ctc_rates import FINANCIAL_DISCLAIMER


# Standard Canadian debt-service guidelines (as %). GDS = housing / income;
# TDS = (housing + other debt) / income.
GDS_LIMIT = 39.0
TDS_LIMIT = 44.0


# Product criteria. Each criterion: (label, evaluator, target_text, fix_text).
# Evaluators receive a `ctx` dict and return (met: bool, actual_text: str).
def _pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x:.1f}%"


PRODUCTS = {
    "credit_card": "Unsecured credit card",
    "personal_loc": "Personal line of credit",
    "auto_loan": "Auto loan",
    "mortgage": "Mortgage",
    "business_loc": "Business line of credit / term loan",
}


def _score_ok(ctx, minimum):
    s = ctx["best_score"]
    if s <= 0:
        return None, "score not set"
    return s >= minimum, str(s)


def assess(product: str, ctx: dict) -> dict:
    """ctx keys: best_score, utilization_pct, dti_pct, gds_pct, tds_pct,
    open_collections, has_business_account, business_bank_months,
    time_in_business_years, revenue_documented_monthly."""
    if product not in PRODUCTS:
        raise ValueError(f"product must be one of {list(PRODUCTS)}")

    criteria = []

    def add(label, met, actual, target, fix):
        criteria.append({"criterion": label, "met": met, "actual": actual,
                         "target": target, "fix": fix})

    util = ctx.get("utilization_pct")
    dti = ctx.get("dti_pct")
    gds = ctx.get("gds_pct")
    tds = ctx.get("tds_pct")
    coll = ctx.get("open_collections", 0)

    if product in ("credit_card", "personal_loc", "auto_loan"):
        min_score = {"credit_card": 640, "personal_loc": 660, "auto_loan": 620}[product]
        met, actual = _score_ok(ctx, min_score)
        add("Credit score", met, actual, f">= {min_score}",
            f"Raise your score toward {min_score}: pay on time, lower utilization, "
            "let accounts age, dispute genuine errors.")
        util_target = 30.0 if product != "credit_card" else 50.0
        add("Card utilization", (util is not None and util < util_target), _pct(util),
            f"< {util_target:.0f}%",
            "Pay balances down (ideally below 10% before statement dates).")
        add("Debt-to-income (TDS-style)", (dti is not None and dti < TDS_LIMIT), _pct(dti),
            f"< {TDS_LIMIT:.0f}%",
            "Increase documented income or reduce monthly debt obligations.")
        add("No open collections", coll == 0, str(coll), "0",
            "Resolve, validate, or dispute genuinely inaccurate/outdated collections.")

    elif product == "mortgage":
        met, actual = _score_ok(ctx, 680)
        add("Credit score", met, actual, ">= 680",
            "Build toward 680+ over several months of clean history.")
        add("Gross debt service (GDS)", (gds is not None and gds <= GDS_LIMIT), _pct(gds),
            f"<= {GDS_LIMIT:.0f}%",
            "Lower housing cost or raise income; a larger down payment reduces the payment.")
        add("Total debt service (TDS)", (tds is not None and tds <= TDS_LIMIT), _pct(tds),
            f"<= {TDS_LIMIT:.0f}%",
            "Pay down other debts or increase documented income.")
        add("No open collections", coll == 0, str(coll), "0",
            "Resolve or dispute genuinely inaccurate/outdated collections first.")

    elif product == "business_loc":
        met, actual = _score_ok(ctx, 680)
        add("Personal credit score", met, actual, ">= 680",
            "Lenders lean on the owner's personal score for small-business credit.")
        add("Business bank account", ctx.get("has_business_account", False),
            "yes" if ctx.get("has_business_account") else "no", "yes",
            "Open a dedicated business account, separate from personal.")
        months = ctx.get("business_bank_months", 0)
        add("Account seasoning", months >= 6, f"{months} mo", ">= 6 months",
            "Keep the business account active and funded for 6+ months.")
        yrs = ctx.get("time_in_business_years", 0.0)
        add("Time in business", yrs >= 1.0, f"{yrs:.1f} yr", ">= 1 year (2+ preferred)",
            "Time and consistent revenue history strengthen the file.")
        rev = ctx.get("revenue_documented_monthly", 0.0)
        add("Documented revenue", rev > 0, f"${rev:,.0f}/mo", "documented (6-12 mo statements)",
            "Keep clean statements/financials showing steady revenue.")
        add("No open collections", coll == 0, str(coll), "0",
            "Clear or dispute genuinely inaccurate/outdated collections.")

    met_count = sum(1 for c in criteria if c["met"] is True)
    total = len(criteria)
    readiness = round((met_count / total) * 100, 1) if total else 0.0
    gaps = [c for c in criteria if c["met"] is not True]

    return {
        "product": product,
        "product_name": PRODUCTS[product],
        "readiness_pct": readiness,
        "criteria_met": met_count,
        "criteria_total": total,
        "criteria": criteria,
        "gaps": gaps,
        "verdict": ("Strong -- likely ready to apply" if readiness >= 100 else
                    "Close -- fix the flagged gaps first" if readiness >= 60 else
                    "Not yet -- build the profile before applying"),
        "note": "Preparation estimate, not a guarantee of approval. " + FINANCIAL_DISCLAIMER,
    }


def required_income_for_dti(monthly_debt: float, target_dti_pct: float) -> dict:
    """Reverse the DTI formula: what gross monthly income keeps you at/under a
    target ratio, given your current monthly debt obligations. Useful when
    planning owner salary (see ctc_payroll)."""
    if target_dti_pct <= 0:
        raise ValueError("target_dti_pct must be > 0")
    required_monthly = monthly_debt / (target_dti_pct / 100.0)
    return {
        "monthly_debt_obligations": round(monthly_debt, 2),
        "target_dti_pct": target_dti_pct,
        "required_gross_monthly_income": round(required_monthly, 2),
        "required_gross_annual_income": round(required_monthly * 12, 2),
        "note": "Honest lever: reach the income by paying yourself a real, taxed "
                "salary (see payroll planner) -- not by inflating documents. "
                + FINANCIAL_DISCLAIMER,
    }
