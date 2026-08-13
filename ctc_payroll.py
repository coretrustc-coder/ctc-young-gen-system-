"""
CoreTrust System (CTC) -- Owner-Operator Payroll Planning (EDUCATIONAL)
======================================================================
Ontario / Canada, 2026 assumptions (see ctc_rates.py).

For an incorporated owner deciding how much T4 salary to pay yourself, this
ESTIMATES gross->net, the deductions, and the total cost to the corporation, and
solves for the salary needed to hit a target net or a target personal income.

This is PLANNING math, not a payroll system. Actual source deductions,
remittances to the CRA, T4 filings, and WSIB/EHT obligations must be handled by
compliant payroll software and/or a CPA/bookkeeper. Many owners who control the
company are EI-exempt -- confirm your status.
"""

from __future__ import annotations

import ctc_rates as R


def net_from_gross(annual_gross: float, ei_exempt: bool = True) -> dict:
    """Estimate an employee's take-home from a T4 salary, plus the employer-side
    cost to the corporation."""
    annual_gross = max(0.0, annual_gross)
    cpp = R.cpp_contribution(annual_gross)
    ei = R.ei_premium(annual_gross, exempt=ei_exempt)
    income_tax = R.total_income_tax(annual_gross)   # salary is the taxable income
    net = annual_gross - cpp["total"] - ei - income_tax

    employer_cpp = cpp["total"]                     # employer matches CPP+CPP2
    employer_ei = round(ei * R.EI_EMPLOYER_MULTIPLIER, 2)
    employer_cost = round(annual_gross + employer_cpp + employer_ei, 2)

    return {
        "annual_gross": round(annual_gross, 2),
        "cpp": cpp["total"],
        "cpp_breakdown": {"cpp1": cpp["cpp1"], "cpp2": cpp["cpp2"]},
        "ei": ei,
        "income_tax": income_tax,
        "annual_net": round(net, 2),
        "monthly_net": round(net / 12, 2),
        "employer_cpp": employer_cpp,
        "employer_ei": employer_ei,
        "total_cost_to_corp": employer_cost,
        "note": "Estimate; ignores many credits/deductions, EHT/WSIB, and the CPP "
                "enhancement deduction. " + R.FINANCIAL_DISCLAIMER,
    }


def gross_for_target_net(target_annual_net: float, ei_exempt: bool = True) -> dict:
    """Binary-search the gross salary that yields a target take-home."""
    target = max(0.0, target_annual_net)
    lo, hi = 0.0, max(target * 2.5, 20000.0)
    # ensure hi is high enough
    while net_from_gross(hi, ei_exempt)["annual_net"] < target and hi < 5_000_000:
        hi *= 1.5
    for _ in range(60):
        mid = (lo + hi) / 2
        if net_from_gross(mid, ei_exempt)["annual_net"] < target:
            lo = mid
        else:
            hi = mid
    result = net_from_gross(round((lo + hi) / 2, 2), ei_exempt)
    result["target_annual_net"] = round(target, 2)
    return result


def salary_for_income_target(target_gross_annual: float, ei_exempt: bool = True) -> dict:
    """Simple pass-through when you already know the gross T4 income you want to
    show (e.g. to support a lending application). Returns the net + corp cost."""
    return net_from_gross(target_gross_annual, ei_exempt)
