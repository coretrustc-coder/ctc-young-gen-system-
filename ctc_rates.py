"""
CoreTrust System (CTC) -- 2026 Rate Assumptions & Tax/Payroll Math
==================================================================

IMPORTANT: These are DEFAULT ASSUMPTIONS for the 2026 tax year, sourced from
public figures (see comments). Rates and thresholds change every year and can be
revised mid-year. VERIFY the current numbers at canada.ca / ontario.ca, and have
a CPA confirm anything you rely on. Every calculation built on these values is an
ESTIMATE, not tax advice.

You can edit the constants below to the official figures for your year.
"""

from __future__ import annotations

FINANCIAL_DISCLAIMER = (
    "Educational estimate only -- not tax, investment, or financial advice. "
    "Figures use default 2026 assumptions that change yearly; verify current "
    "rates with the CRA/Ontario and consult a licensed CPA or advisor before "
    "acting."
)

# --- Federal personal income tax brackets 2026 (upper bound, marginal rate) ---
# 14% / 20.5% / 26% / 29% / 33%
FEDERAL_BRACKETS_2026 = [
    (57375.0, 0.14),
    (114750.0, 0.205),
    (158519.0, 0.26),
    (220000.0, 0.29),
    (float("inf"), 0.33),
]

# --- Ontario provincial brackets 2026 (upper bound, marginal rate) ---
# 5.05% / 9.15% / 11.16% / 12.16% / 13.16%
ONTARIO_BRACKETS_2026 = [
    (53891.0, 0.0505),
    (107785.0, 0.0915),
    (150000.0, 0.1116),
    (220000.0, 0.1216),
    (float("inf"), 0.1316),
]

# Ontario surtax on Ontario basic tax: 20% over t1, plus a further 36% over t2.
ONTARIO_SURTAX_T1 = 5818.0
ONTARIO_SURTAX_T2 = 7446.0

# Basic personal amounts (non-refundable credit at the lowest rate). Approx 2026.
BPA_FEDERAL_2026 = 16384.0
BPA_ONTARIO_2026 = 12990.0

# --- CPP / CPP2 / EI 2026 (employee side) ---
CPP_BASIC_EXEMPTION = 3500.0
CPP_YMPE_2026 = 74600.0        # first earnings ceiling
CPP_YAMPE_2026 = 85000.0       # second ceiling (CPP2)
CPP_RATE = 0.0595              # base employee rate
CPP2_RATE = 0.04               # CPP2 employee rate
CPP1_MAX_2026 = 4230.45        # 5.95% x (74,600 - 3,500)
CPP2_MAX_2026 = 416.00         # 4% x (85,000 - 74,600)

EI_RATE_2026 = 0.0163          # employee, outside Quebec
EI_MIE_2026 = 68900.0          # maximum insurable earnings
EI_MAX_2026 = round(EI_MIE_2026 * EI_RATE_2026, 2)  # ~1,123.07
EI_EMPLOYER_MULTIPLIER = 1.4   # employer pays 1.4x employee premium

# Small business deduction: active business income taxed at the low rate up to
# this federal limit (subject to grind rules). Educational reference only.
SBD_LIMIT = 500000.0


# ---------------------------------------------------------------------------
# Progressive tax helpers
# ---------------------------------------------------------------------------
def _progressive(income: float, brackets) -> float:
    tax, lower = 0.0, 0.0
    for upper, rate in brackets:
        if income <= lower:
            break
        tax += (min(income, upper) - lower) * rate
        lower = upper
    return tax


def federal_tax(taxable_income: float) -> float:
    gross = _progressive(taxable_income, FEDERAL_BRACKETS_2026)
    credit = BPA_FEDERAL_2026 * FEDERAL_BRACKETS_2026[0][1]
    return max(0.0, gross - credit)


def ontario_basic_tax(taxable_income: float) -> float:
    gross = _progressive(taxable_income, ONTARIO_BRACKETS_2026)
    credit = BPA_ONTARIO_2026 * ONTARIO_BRACKETS_2026[0][1]
    return max(0.0, gross - credit)


def ontario_surtax(on_basic: float) -> float:
    s = 0.0
    if on_basic > ONTARIO_SURTAX_T1:
        s += 0.20 * (on_basic - ONTARIO_SURTAX_T1)
    if on_basic > ONTARIO_SURTAX_T2:
        s += 0.36 * (on_basic - ONTARIO_SURTAX_T2)
    return s


def total_income_tax(taxable_income: float) -> float:
    """Estimated combined federal + Ontario income tax (incl. Ontario surtax).
    Excludes the Ontario Health Premium and most other credits/deductions."""
    if taxable_income <= 0:
        return 0.0
    on_basic = ontario_basic_tax(taxable_income)
    return round(federal_tax(taxable_income) + on_basic + ontario_surtax(on_basic), 2)


def marginal_rate(taxable_income: float, step: float = 100.0) -> float:
    """Combined marginal rate at this income (numerical, includes surtax)."""
    hi = total_income_tax(taxable_income + step)
    lo = total_income_tax(taxable_income)
    return round((hi - lo) / step, 4)


def average_rate(taxable_income: float) -> float:
    if taxable_income <= 0:
        return 0.0
    return round(total_income_tax(taxable_income) / taxable_income, 4)


# ---------------------------------------------------------------------------
# CPP / CPP2 / EI
# ---------------------------------------------------------------------------
def cpp_contribution(annual_earnings: float) -> dict:
    pensionable = max(0.0, min(annual_earnings, CPP_YMPE_2026) - CPP_BASIC_EXEMPTION)
    cpp1 = min(pensionable * CPP_RATE, CPP1_MAX_2026)
    cpp2_base = max(0.0, min(annual_earnings, CPP_YAMPE_2026) - CPP_YMPE_2026)
    cpp2 = min(cpp2_base * CPP2_RATE, CPP2_MAX_2026)
    return {"cpp1": round(cpp1, 2), "cpp2": round(cpp2, 2), "total": round(cpp1 + cpp2, 2)}


def ei_premium(annual_earnings: float, exempt: bool = False) -> float:
    if exempt:
        return 0.0
    return round(min(min(annual_earnings, EI_MIE_2026) * EI_RATE_2026, EI_MAX_2026), 2)
