"""
CoreTrust System (CTC) -- Financial Health Dashboard & Opportunity "Plays"
=========================================================================

Turns your tracked data into (1) a composite health score across the dimensions
lenders and planners care about, and (2) concrete, legitimate "plays" -- ordered
opportunities to reduce cost, shelter tax, improve credit metrics, and get
funding-ready.

The plays are financial-literacy EDUCATION, grounded in your own numbers. They
cover account structure, debt cost, credit mechanics, and readiness -- NOT
"buy this investment." Nothing here is investment, tax, or mortgage advice; for
those, use a licensed professional.
"""

from __future__ import annotations

from typing import Optional

from ctc_disputes import audit_reporting_periods
from ctc_rates import FINANCIAL_DISCLAIMER
from ctc_tax import rrsp_contribution_benefit


def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def _grade(score: float) -> str:
    return ("A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55
            else "D" if score >= 40 else "F")


def compute_scorecard(db) -> dict:
    metrics = db.get_aggregate_metrics()
    nw = db.net_worth()
    profile = db.get_user_profile()
    cards = db.get_credit_cards()
    ports = db.get_portfolios()
    entries = db.get_credit_report_entries()

    util = metrics["aggregate_utilization_pct"]
    dti = metrics["estimated_dti_pct"]

    # 1. Utilization (lower is better)
    util_score = 100.0 if util <= 10 else _clamp(100 - (util - 10) * 1.25)
    # 2. Debt-to-income
    dti_score = 50.0 if dti is None else (100.0 if dti <= 20 else _clamp(100 - (dti - 20) * 2.5))
    # 3. Savings rate (from business cash flow, if any)
    sr_values = [db.cash_flow_summary(b.transaction_history)["savings_rate_pct"]
                 for b in db.get_business_accounts()]
    sr_values = [s for s in sr_values if s is not None]
    if sr_values:
        sr = sum(sr_values) / len(sr_values)
        savings_score = _clamp(40 + sr * 3)
    else:
        sr, savings_score = None, 50.0
    # 4. Emergency fund (months of expenses covered by liquid assets)
    monthly_need = profile.monthly_expenses or metrics["monthly_debt_obligations"]
    if monthly_need > 0:
        months = nw["liquid_assets"] / monthly_need
        ef_score = _clamp(months * (100 / 6))   # 6 months -> 100
    else:
        months, ef_score = None, 50.0
    # 5. Registered-account usage
    if ports:
        used = [min(1.0, (p.contributed_ytd / p.contribution_limit)) for p in ports if p.contribution_limit > 0]
        reg_score = _clamp((sum(used) / len(used)) * 100) if used else 50.0
    else:
        reg_score = 50.0
    # 6. Credit health (penalise derogatory / outdated items)
    credit_score_component = 100.0 if entries else 70.0
    penalties = {"collection": 20, "judgment": 25, "bankruptcy_first": 30,
                 "bankruptcy_second": 30, "late_payment": 10, "secured_chargeoff": 15}
    for e in entries:
        credit_score_component -= penalties.get(e.entry_type, 5)
    credit_score_component = _clamp(credit_score_component)

    weights = {"utilization": 0.20, "dti": 0.20, "savings": 0.15,
               "emergency": 0.15, "registered": 0.10, "credit": 0.20}
    parts = {"utilization": util_score, "dti": dti_score, "savings": savings_score,
             "emergency": ef_score, "registered": reg_score, "credit": credit_score_component}
    composite = round(sum(parts[k] * weights[k] for k in weights), 1)

    return {
        "composite_score": composite,
        "grade": _grade(composite),
        "components": {k: round(v, 1) for k, v in parts.items()},
        "weights": weights,
        "net_worth": nw["net_worth"],
        "liquid_assets": nw["liquid_assets"],
        "utilization_pct": util,
        "dti_pct": dti,
        "avg_savings_rate_pct": None if sr is None else round(sr, 1),
        "emergency_fund_months": None if months is None else round(months, 1),
        "note": FINANCIAL_DISCLAIMER,
    }


def generate_plays(db) -> list:
    """Ordered opportunity plays derived from YOUR data. Each play states why,
    an estimated dollar benefit where computable, and a concrete next step."""
    plays = []
    metrics = db.get_aggregate_metrics()
    nw = db.net_worth()
    profile = db.get_user_profile()
    cards = db.get_credit_cards()
    ports = {p.portfolio_type: p for p in db.get_portfolios()}
    assets = db.get_assets()
    entries = db.get_credit_report_entries()

    monthly_need = profile.monthly_expenses or metrics["monthly_debt_obligations"]
    emergency_buffer = monthly_need * 3
    surplus_cash = max(0.0, nw["liquid_assets"] - emergency_buffer)

    # 1. Pay down high-interest revolving debt with genuine surplus cash.
    carrying = [c for c in cards if c.current_balance > 0]
    if carrying and surplus_cash > 0:
        worst = max(carrying, key=lambda c: c.estimated_annual_interest())
        payable = min(surplus_cash, worst.current_balance)
        rate = worst.apr if worst.apr > 0 else 0.1999
        est_saved = round(payable * rate, 2)
        plays.append({
            "priority": 1,
            "title": f"Pay down {worst.institution} card with surplus cash",
            "why": (f"You have ~${surplus_cash:,.0f} above a 3-month buffer, and this "
                    f"card carries a balance at ~{rate*100:.1f}%. Paying it is a "
                    "guaranteed, risk-free return equal to the interest rate."),
            "estimated_benefit": f"~${est_saved:,.0f}/yr interest avoided on ${payable:,.0f}",
            "action": "Move surplus cash to the highest-rate balance first; keep the buffer intact.",
        })

    # 2. Utilization timing before statement date (credit-score mechanic).
    high_util = [c for c in cards if c.utilization() > 0.10]
    if high_util:
        plays.append({
            "priority": 2,
            "title": "Report lower utilization by paying before statement dates",
            "why": ("Bureaus see the balance on your statement date. Paying a card "
                    "down before that date reports lower utilization, which helps "
                    "your score -- without changing what you spend."),
            "estimated_benefit": "Score/utilization improvement (no cash cost)",
            "action": "For " + ", ".join(c.institution for c in high_util)
                      + ": pay down 1-3 days before the statement date.",
        })

    # 3. Shelter idle cash in registered room (tax-advantaged growth).
    fhsa = ports.get("FHSA")
    tfsa = ports.get("TFSA")
    if surplus_cash > 0 and (fhsa and fhsa.remaining_room() > 0 or tfsa and tfsa.remaining_room() > 0):
        target = fhsa if (fhsa and fhsa.remaining_room() > 0) else tfsa
        room = target.remaining_room()
        plays.append({
            "priority": 3,
            "title": f"Move idle cash into {target.portfolio_type} room",
            "why": (f"You have ${room:,.0f} of {target.portfolio_type} room and surplus "
                    "cash sitting in taxable accounts. Registered accounts shelter "
                    "growth from tax"
                    + (" and FHSA contributions are also deductible." if target.portfolio_type == "FHSA"
                       else ".")),
            "estimated_benefit": f"Tax-sheltered growth on up to ${min(room, surplus_cash):,.0f}",
            "action": f"Confirm room in CRA MyAccount, then contribute within the {target.portfolio_type} limit.",
        })

    # 4. RRSP deduction to cut this year's tax (if income + room).
    rrsp = ports.get("RRSP")
    gross_annual = metrics["gross_monthly_income"] * 12
    if rrsp and rrsp.remaining_room() > 0 and gross_annual > 0:
        sample = min(rrsp.remaining_room(), surplus_cash if surplus_cash > 0 else rrsp.remaining_room())
        sample = min(sample, gross_annual)
        if sample > 0:
            benefit = rrsp_contribution_benefit(gross_annual, sample)
            plays.append({
                "priority": 4,
                "title": "Use RRSP room to reduce this year's income tax",
                "why": (f"With ${rrsp.remaining_room():,.0f} of RRSP room, a "
                        f"${sample:,.0f} contribution could cut this year's tax by "
                        f"~${benefit['estimated_tax_reduction']:,.0f} (estimate)."),
                "estimated_benefit": f"~${benefit['estimated_tax_reduction']:,.0f} estimated tax reduction",
                "action": "Discuss timing/amount with a CPA; contributions reduce taxable income now.",
            })

    # 5. Emergency-fund gap.
    if monthly_need > 0:
        months = nw["liquid_assets"] / monthly_need
        if months < 3:
            gap = round(emergency_buffer - nw["liquid_assets"], 2)
            plays.append({
                "priority": 5,
                "title": "Build your emergency fund to 3+ months",
                "why": (f"Liquid savings cover ~{months:.1f} months. A thin buffer forces "
                        "high-interest borrowing when something breaks."),
                "estimated_benefit": f"Resilience; avoids costly borrowing (~${gap:,.0f} gap)",
                "action": "Automate transfers to a HISA until you reach ~3 months of costs.",
            })

    # 6. Asset-backed borrowing to cut interest cost (leverage, with warning).
    total_equity = sum(a.equity() for a in assets)
    if carrying and total_equity > 5000:
        plays.append({
            "priority": 6,
            "title": "Consider secured credit to lower interest on existing debt",
            "why": (f"You hold ~${total_equity:,.0f} of asset equity. Secured credit "
                    "(e.g. a HELOC or GIC-secured LOC) usually carries a much lower "
                    "rate than cards, so consolidating high-interest balances can cut "
                    "interest cost."),
            "estimated_benefit": "Lower interest rate on consolidated balances",
            "action": ("RISK: this moves unsecured debt onto an asset -- missing payments "
                       "can put the asset at risk, and volatile assets (e.g. crypto) can "
                       "trigger margin calls. Model it and consult a licensed advisor first."),
        })

    # 7. Business separation / credit-building.
    biz = db.get_business_accounts()
    if biz and profile.business_bank_months < 6:
        plays.append({
            "priority": 7,
            "title": "Season your business banking and build business credit",
            "why": ("Lenders want a dedicated, seasoned business account and a business "
                    "credit history separate from your personal file."),
            "estimated_benefit": "Improves business funding readiness (see readiness engine)",
            "action": "Keep the business account active 6+ months; pay any net-30 vendors early.",
        })

    # 8. Outdated credit entries you can legitimately dispute.
    audit = audit_reporting_periods(entries)
    outdated = [a for a in audit if a.get("disputable_as_outdated")]
    if outdated:
        plays.append({
            "priority": 8,
            "title": f"Dispute {len(outdated)} outdated credit entr{'y' if len(outdated)==1 else 'ies'}",
            "why": ("These appear to exceed Ontario's maximum reporting period and are "
                    "legitimately disputable as outdated, which can lift your score."),
            "estimated_benefit": "Potential score improvement from removing outdated items",
            "action": "Verify dates on your report, then use the dispute letter tool (aged_item).",
        })

    plays.sort(key=lambda p: p["priority"])
    return plays
