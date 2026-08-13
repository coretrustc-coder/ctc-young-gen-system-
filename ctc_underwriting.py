"""
CoreTrust System (CTC) -- Credit Optimization & Consumer-Rights Scripts
=======================================================================

What this module does (all legitimate, consumer-side):
  * tracks when YOU appear eligible to *request* a credit-limit increase, based
    on your own utilization and how long it's been since your last increase;
  * gives you a Bank Act s.455.1 script to refuse illegal tied selling;
  * builds an interest-rate negotiation script around a REAL competing offer you
    actually hold;
  * summarizes the standard, legitimate credit-optimization playbook.

What it deliberately does NOT do:
  * pretend to reproduce a bank's secret internal risk model,
  * tell you to fake transaction "velocity" to trigger auto-approvals,
  * time applications to hide them from other lenders.
Those are misrepresentation. This module sticks to things you can say and do
honestly.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Optional

from ctc_disputes import DISCLAIMER


# Many Canadian issuers ask you to wait roughly 6 months between voluntary
# credit-limit-increase requests. This is a common convention, not a universal
# rule -- confirm your specific issuer's policy.
TYPICAL_CLI_COOLDOWN_DAYS = 180


def credit_limit_increase_readiness(
    card_id: str,
    institution: str,
    limit_amt: float,
    current_balance: float,
    utilization_history: List[float],
    last_increase_date: str,
    has_stable_income: bool,
) -> dict:
    """A personal reminder of whether YOU appear ready to *request* a limit
    increase. It reflects sound consumer habits (low utilization, spacing
    requests out, stable income) -- not a guarantee of approval, and not a way
    to game anyone. The decision is always the lender's."""
    today = date.today()

    cooldown_passed = True
    days_since_increase = None
    next_request_date = "eligible now"
    if last_increase_date:
        last_inc = datetime.strptime(last_increase_date, "%Y-%m-%d").date()
        days_since_increase = (today - last_inc).days
        cooldown_passed = days_since_increase >= TYPICAL_CLI_COOLDOWN_DAYS
        if not cooldown_passed:
            next_request_date = str(last_inc + timedelta(days=TYPICAL_CLI_COOLDOWN_DAYS))

    current_util = round(current_balance / limit_amt, 4) if limit_amt > 0 else 0.0
    # Healthy utilization for a request: recent statements consistently low.
    recent = utilization_history[-3:] if utilization_history else []
    utilization_healthy = bool(recent) and all(u < 0.30 for u in recent)

    appears_ready = cooldown_passed and utilization_healthy and has_stable_income

    if appears_ready:
        suggestion = (
            "You appear ready to request an increase. Ask through your issuer's "
            "app/portal or by phone. You may ask whether it's a soft or hard pull "
            "before you proceed."
        )
    else:
        reasons = []
        if not cooldown_passed:
            reasons.append(f"space requests out (eligible ~{next_request_date})")
        if not utilization_healthy:
            reasons.append("bring recent statement utilization under 30% (ideally <10%)")
        if not has_stable_income:
            reasons.append("have documented, stable income ready")
        suggestion = "Before requesting: " + "; ".join(reasons) + "."

    return {
        "card_id": card_id,
        "institution": institution,
        "current_utilization": current_util,
        "utilization_healthy": utilization_healthy,
        "days_since_last_increase": days_since_increase,
        "cooldown_passed": cooldown_passed,
        "next_request_date": next_request_date,
        "appears_ready_to_request": appears_ready,
        "suggestion": suggestion,
    }


def tied_selling_refusal_script(
    rep_name: str, product_pressured: str, credit_product: str
) -> str:
    """Bank Act s.455.1 prohibits coercive tied selling -- a bank cannot require
    you to buy another product to get a loan. This is a calm script to assert
    that right."""
    rep = rep_name or "there"
    return f"""[Bank Act s.455.1 -- Tied Selling Refusal]

"Hi {rep}. Under section 455.1 of the Bank Act, a bank can't require me to buy
another product or service -- like {product_pressured} -- as a condition of
getting the {credit_product}. Can you confirm my approval and rate for the
{credit_product} are not conditional on purchasing {product_pressured}? If that
purchase is an absolute condition, please put that in writing so I can review it,
and otherwise please process the {credit_product} on its own. Thank you."

Note: coercive tied selling is prohibited; optional bundles you freely choose are
not. You can raise concerns with the bank's complaints office, then an external
complaints body (OBSI/ADRBO), and the FCAC.

---
""" + DISCLAIMER + "\n"


def rate_negotiation_script(
    lender: str,
    current_rate: float,
    competing_offer_rate: Optional[float] = None,
    competing_offer_source: str = "",
    on_time_history: bool = True,
) -> str:
    """Build a rate-negotiation script. If you have a REAL competing offer, cite
    it; otherwise the script leans on your payment history and loyalty. It never
    invents a competitor's rate for you."""
    leverage_lines = []
    if on_time_history:
        leverage_lines.append("I've kept this account in good standing with on-time payments.")
    if competing_offer_rate is not None and competing_offer_source:
        leverage_lines.append(
            f"I have a competing offer from {competing_offer_source} at "
            f"{competing_offer_rate:.2f}%, and I'd rather stay with you if you can match or beat it."
        )
    elif competing_offer_rate is not None:
        leverage_lines.append(
            f"I'm looking at alternatives around {competing_offer_rate:.2f}% and would prefer to stay."
        )
    else:
        leverage_lines.append(
            "I'm reviewing my options and would prefer to keep my business with you."
        )
    leverage = " ".join(leverage_lines)

    return f"""[Interest-Rate Negotiation -- {lender}]

"Hello, I'd like to review the rate on my account. It's currently {current_rate:.2f}%.
{leverage} Is there room to lower my rate? If you're not able to authorize a
reduction, could you please escalate this to a retention or product specialist?"

Tips: be polite and specific, only cite a competing offer you actually have, and
ask them to note the request on your file. If they decline, you can revisit at
renewal or when your credit profile improves.

---
""" + DISCLAIMER + "\n"


CREDIT_OPTIMIZATION_PLAYBOOK = [
    "Pay every account on time -- payment history is the biggest factor (~35%).",
    "Keep revolving utilization under 30%, and under 10% before statement dates, "
    "to report low balances (~30%).",
    "Keep old accounts open -- length of history helps; closing an old card can hurt.",
    "Batch rate-shopping for one loan type into a short window so inquiries are "
    "treated as a single shop.",
    "Keep a healthy mix (revolving + installment) over time -- naturally, not forced.",
    "Ask for limit increases on clean accounts periodically (see readiness check).",
    "Check both Equifax CA and TransUnion CA regularly; Ontario now gives free "
    "monthly score access -- use it to catch errors early.",
]


def credit_optimization_playbook() -> str:
    lines = "\n".join(f"  {i+1}. {tip}" for i, tip in enumerate(CREDIT_OPTIMIZATION_PLAYBOOK))
    return "[Legitimate Credit Optimization Playbook]\n\n" + lines + "\n\n---\n" + DISCLAIMER + "\n"
