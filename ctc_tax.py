"""
CoreTrust System (CTC) -- Tax Planning & Estimation (EDUCATIONAL)
================================================================
Ontario / Canada, 2026 assumptions (see ctc_rates.py).

This module ESTIMATES and EXPLAINS -- it is not tax advice and does not model
your full return. It helps you understand marginal vs average rates, the value
of registered-account contributions, and common owner-operator concepts, so you
can have a better conversation with a CPA.

It does NOT do aggressive avoidance schemes. Legitimate planning (using TFSA/
RRSP/FHSA room, the small business deduction, capital cost allowance) is
education here; structuring to hide income or fabricate deductions is not, and
is out of scope.
"""

from __future__ import annotations

from typing import Optional

import ctc_rates as R


def income_tax_snapshot(taxable_income: float) -> dict:
    return {
        "taxable_income": round(taxable_income, 2),
        "estimated_income_tax": R.total_income_tax(taxable_income),
        "average_rate_pct": round(R.average_rate(taxable_income) * 100, 2),
        "marginal_rate_pct": round(R.marginal_rate(taxable_income) * 100, 2),
        "after_tax_income": round(taxable_income - R.total_income_tax(taxable_income), 2),
        "note": "Excludes Ontario Health Premium and most credits/deductions. " + R.FINANCIAL_DISCLAIMER,
    }


def rrsp_contribution_benefit(taxable_income: float, contribution: float) -> dict:
    """Estimated tax reduction from an RRSP contribution: the difference in tax
    with vs without the deduction (captures bracket crossings, not a flat rate)."""
    contribution = max(0.0, contribution)
    tax_before = R.total_income_tax(taxable_income)
    tax_after = R.total_income_tax(max(0.0, taxable_income - contribution))
    refund = round(tax_before - tax_after, 2)
    effective = round((refund / contribution) * 100, 2) if contribution > 0 else 0.0
    return {
        "contribution": round(contribution, 2),
        "estimated_tax_reduction": refund,
        "effective_refund_rate_pct": effective,
        "note": "An RRSP deduction lowers this year's taxable income; withdrawals "
                "are taxed later. " + R.FINANCIAL_DISCLAIMER,
    }


def registered_account_guide(remaining_tfsa: float, remaining_rrsp: float,
                             remaining_fhsa: float, taxable_income: float) -> dict:
    """Explains, in plain terms, how each registered account treats your money.
    Not a recommendation to buy any particular investment."""
    tips = []
    if remaining_fhsa > 0:
        tips.append(f"FHSA: ${remaining_fhsa:,.0f} room. Contributions are "
                    "tax-deductible AND qualified first-home withdrawals are "
                    "tax-free -- the only account with both.")
    if remaining_rrsp > 0:
        est = rrsp_contribution_benefit(taxable_income, min(remaining_rrsp, taxable_income))
        tips.append(f"RRSP: ${remaining_rrsp:,.0f} room. A deduction now defers tax "
                    f"to retirement; a full contribution could reduce tax by roughly "
                    f"${est['estimated_tax_reduction']:,.0f} this year (estimate).")
    if remaining_tfsa > 0:
        tips.append(f"TFSA: ${remaining_tfsa:,.0f} room. No deduction, but growth and "
                    "withdrawals are tax-free and withdrawn room comes back next year.")
    if not tips:
        tips.append("No remaining room detected. Confirm your actual room in CRA MyAccount.")
    return {"tips": tips, "note": R.FINANCIAL_DISCLAIMER}


CONCEPTS = {
    "small_business_deduction":
        f"Active business income up to ${R.SBD_LIMIT:,.0f} (federal) is taxed at the "
        "low small-business rate, subject to grind rules (e.g. passive income, "
        "taxable capital). Keeping active income under the limit preserves the low "
        "rate. Structure and eligibility are CPA territory.",
    "capital_cost_allowance":
        "Capital assets (equipment, computers, some software) are deducted over "
        "time via CCA classes, not all at once. Some incentives allow accelerated "
        "or immediate expensing in year one. A CPA maps assets to the right class.",
    "salary_vs_dividends":
        "Owner-managers can be paid salary (creates RRSP room, CPP, T4 income banks "
        "like) or dividends (no CPP, different tax). The right mix depends on your "
        "whole picture -- decide it with a CPA.",
    "holdco_opco":
        "A holding company can hold retained earnings/assets separately from the "
        "operating company for creditor protection and deferral, using inter-"
        "corporate dividends. Set up and used properly, with professional advice.",
}


def explain_concept(key: str) -> str:
    body = CONCEPTS.get(key)
    if not body:
        return f"Unknown concept '{key}'. Options: {', '.join(CONCEPTS)}"
    return body + "\n\n" + R.FINANCIAL_DISCLAIMER
