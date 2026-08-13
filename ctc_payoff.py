"""
CoreTrust System (CTC) -- Debt Payoff & Amortization Planner
============================================================
Pure math (no stored state): amortization schedules, payoff dates, total
interest, the effect of extra payments, and avalanche vs. snowball ordering
across all your debts.

Educational estimates -- your lender's exact interest method (daily accrual,
compounding, fees) may differ. Verify against your statements.
"""

from __future__ import annotations

from typing import List, Optional


def amortize(balance: float, annual_rate_pct: float, monthly_payment: float,
             extra: float = 0.0, max_months: int = 1200) -> dict:
    """Months to pay off `balance` at `annual_rate_pct` with `monthly_payment`
    (+ optional `extra`). Returns months, total interest, total paid."""
    bal = float(balance)
    pay = monthly_payment + extra
    r = (annual_rate_pct / 100.0) / 12.0
    if bal <= 0:
        return {"months": 0, "total_interest": 0.0, "total_paid": 0.0, "payoff": True}
    # If the payment can't cover the first month's interest, it never amortizes.
    if pay <= bal * r:
        return {"months": None, "total_interest": None, "total_paid": None, "payoff": False,
                "note": "Payment is too small to cover interest -- balance would never fall. "
                        "Increase the monthly payment."}
    months = 0
    interest = 0.0
    while bal > 0 and months < max_months:
        i = bal * r
        interest += i
        bal = bal + i - pay
        months += 1
        if bal < 0:
            bal = 0.0
    total_paid = balance + interest
    return {"months": months, "years": round(months / 12, 1),
            "total_interest": round(interest, 2), "total_paid": round(total_paid, 2),
            "payoff": bal <= 0}


def extra_payment_impact(balance: float, annual_rate_pct: float, monthly_payment: float,
                         extra: float) -> dict:
    base = amortize(balance, annual_rate_pct, monthly_payment)
    boosted = amortize(balance, annual_rate_pct, monthly_payment, extra=extra)
    if not base.get("payoff") or not boosted.get("payoff"):
        return {"base": base, "with_extra": boosted}
    return {
        "base": base, "with_extra": boosted,
        "months_saved": base["months"] - boosted["months"],
        "interest_saved": round(base["total_interest"] - boosted["total_interest"], 2),
    }


def _debt_records(db) -> List[dict]:
    """Collect debts to plan: installment loans + card balances (cards use their
    APR or a labelled 19.99% estimate, and a rough minimum payment)."""
    debts = []
    for d in db.get_installment_debts():
        debts.append({"name": f"{d.lender} ({d.debt_type})", "balance": d.balance,
                      "rate": d.interest_rate, "min_payment": d.monthly_payment,
                      "estimated_rate": d.interest_rate <= 0})
    for c in db.get_credit_cards():
        if c.current_balance > 0:
            rate = (c.apr * 100) if c.apr > 0 else 19.99
            debts.append({"name": f"{c.institution} card", "balance": c.current_balance,
                          "rate": rate, "min_payment": c.estimated_min_payment(),
                          "estimated_rate": c.apr <= 0})
    return debts


def payoff_plan(db, monthly_budget: float, method: str = "avalanche") -> dict:
    """Order your debts by `method` and estimate the total payoff.

    avalanche = highest interest rate first (cheapest overall).
    snowball  = smallest balance first (fastest wins for momentum).
    `monthly_budget` is the TOTAL you'll put toward all debts each month; it must
    at least cover every minimum payment.
    """
    debts = _debt_records(db)
    if not debts:
        return {"method": method, "debts": [], "note": "No debts tracked."}
    total_min = sum(d["min_payment"] for d in debts)
    if monthly_budget < total_min:
        return {"method": method, "debts": debts, "total_min_payment": round(total_min, 2),
                "note": f"Budget ${monthly_budget:,.0f} is below the ${total_min:,.0f} total "
                        "minimum. Raise the budget to at least the sum of minimums."}

    order = sorted(debts, key=(lambda d: -d["rate"]) if method == "avalanche" else (lambda d: d["balance"]))
    # Simulate month by month with rollover of freed-up payments to the target debt.
    bals = {i: d["balance"] for i, d in enumerate(order)}
    rates = {i: (d["rate"] / 100.0) / 12.0 for i, d in enumerate(order)}
    mins = {i: d["min_payment"] for i, d in enumerate(order)}
    months = 0
    total_interest = 0.0
    payoff_month = {}
    while any(b > 0 for b in bals.values()) and months < 1200:
        months += 1
        # accrue interest
        for i in bals:
            if bals[i] > 0:
                itr = bals[i] * rates[i]
                bals[i] += itr
                total_interest += itr
        # pay minimums on all, throw the remainder at the first unpaid in order
        budget = monthly_budget
        for i in bals:
            if bals[i] > 0:
                p = min(mins[i], bals[i])
                bals[i] -= p
                budget -= p
        for i in bals:  # order is by index already (target first)
            if bals[i] > 0 and budget > 0:
                p = min(budget, bals[i])
                bals[i] -= p
                budget -= p
        for i in bals:
            if bals[i] <= 0 and i not in payoff_month:
                payoff_month[i] = months
                bals[i] = 0.0

    return {
        "method": method,
        "order": [{"name": order[i]["name"], "balance": round(order[i]["balance"], 2),
                   "rate": order[i]["rate"], "estimated_rate": order[i]["estimated_rate"],
                   "payoff_month": payoff_month.get(i)} for i in range(len(order))],
        "total_min_payment": round(total_min, 2),
        "monthly_budget": round(monthly_budget, 2),
        "months_to_debt_free": months,
        "years_to_debt_free": round(months / 12, 1),
        "total_interest": round(total_interest, 2),
        "note": "Estimate; real accrual/fees differ. Avalanche minimizes interest; "
                "snowball clears small balances first for momentum.",
    }
