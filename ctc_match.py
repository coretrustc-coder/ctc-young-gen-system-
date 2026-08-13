"""
CoreTrust System (CTC) -- Product-Match Engine (Canada + US, personal + business)
================================================================================
Takes YOUR profile and points you to the specific product categories you're
readiest to be approved for right now -- across Canadian & US major banks,
credit unions, lenders, and digital-asset platforms -- with the exact gaps to
close for the ones you're not ready for yet.

Honest by design: it ranks *product categories* (and names who offers them), it
never claims a specific institution will approve you, it never hides anything
from a lender, and for US products it first checks whether you've built the
cross-border foundation. Digital assets are included as regulated products
(trading/custody, crypto-backed lending) with explicit risk warnings -- not as a
tax-avoidance scheme.
"""

from __future__ import annotations

from typing import List, Optional

from ctc_rates import FINANCIAL_DISCLAIMER


# ---------------------------------------------------------------------------
# Product catalog. Threshold fields are all optional; the evaluator builds
# criteria only from the ones present. Providers are drawn from ctc_reference.
# ---------------------------------------------------------------------------
PRODUCTS: List[dict] = [
    # ---------------- CANADA · PERSONAL ----------------
    {"id": "ca_p_hisa", "country": "CA", "segment": "personal", "category": "High-Interest Savings",
     "name": "High-interest savings (HISA)", "gate": "open", "needs_liquid": True,
     "providers": ["EQ Bank", "Tangerine", "Simplii", "Neo", "Wealthsimple Cash", "Motive"],
     "notes": "No credit needed; deploy idle cash above your emergency buffer."},
    {"id": "ca_p_secured", "country": "CA", "segment": "personal", "category": "Credit Card (secured)",
     "name": "Secured credit card (bootstrap)", "gate": "open",
     "providers": ["Neo Secured", "Capital One Guaranteed", "Home Trust Secured"],
     "notes": "Accessible with thin/low credit; reports to CA bureaus to build history."},
    {"id": "ca_p_card", "country": "CA", "segment": "personal", "category": "Credit Card",
     "name": "Unsecured credit card", "min_score": 640, "max_util": 50, "max_dti": 44,
     "providers": ["RBC", "TD", "Scotiabank", "BMO", "CIBC", "Amex Canada", "Tangerine"]},
    {"id": "ca_p_loan", "country": "CA", "segment": "personal", "category": "Personal Loan",
     "name": "Personal loan", "min_score": 660, "max_dti": 44, "clear_collections": True,
     "providers": ["Big 6 banks", "Meridian/Vancity/Servus", "Fairstone (near-prime)"]},
    {"id": "ca_p_auto", "country": "CA", "segment": "personal", "category": "Auto Loan",
     "name": "Auto loan", "min_score": 620, "max_dti": 45,
     "providers": ["Bank auto finance", "Credit unions", "Dealer/manufacturer finance"]},
    {"id": "ca_p_loc", "country": "CA", "segment": "personal", "category": "Line of Credit",
     "name": "Personal line of credit", "min_score": 660, "max_util": 30, "max_dti": 44,
     "clear_collections": True, "providers": ["Big 6 banks", "Credit unions"]},
    {"id": "ca_p_mortgage", "country": "CA", "segment": "personal", "category": "Mortgage & HELOC",
     "name": "Mortgage / HELOC", "min_score": 680, "max_gds": 39, "max_tds": 44,
     "needs_liquid": True, "clear_collections": True,
     "providers": ["Big 6 banks", "Credit unions", "Monoline (MCAP, First National)"]},
    {"id": "ca_p_crypto", "country": "CA", "segment": "personal", "category": "Digital Assets",
     "name": "Crypto trading / custody account", "gate": "digital",
     "providers": ["Wealthsimple Crypto", "Bitbuy", "Newton", "Shakepay", "Kraken CA", "Coinbase CA"],
     "risk": "Digital assets are volatile and largely uninsured; only use CIRO/CSA-registered platforms.",
     "notes": "Open with KYC; use registered Canadian platforms."},
    {"id": "ca_p_cryptoloan", "country": "CA", "segment": "personal", "category": "Digital Assets",
     "name": "Crypto-backed loan (borrow against holdings)", "gate": "digital", "needs_crypto": True,
     "providers": ["Regulated custodial lenders (limited in CA)"],
     "risk": "HIGH: price drops can trigger margin calls and forced liquidation; borrowing against "
             "an asset puts it at risk. This is not a tax-avoidance strategy. Model it and consult a licensed advisor."},

    # ---------------- CANADA · BUSINESS ----------------
    {"id": "ca_b_bank", "country": "CA", "segment": "business", "category": "Business Banking",
     "name": "Business chequing/savings", "gate": "open", "needs_business": True,
     "providers": ["Big 6 banks", "Credit unions", "EQ Bank Business"]},
    {"id": "ca_b_card", "country": "CA", "segment": "business", "category": "Business Credit Card",
     "name": "Business credit card", "min_score": 660, "needs_business": True,
     "providers": ["Amex Business", "Big 6 business cards", "Float", "Loop"],
     "notes": "Usually personally guaranteed; owner's personal score drives it."},
    {"id": "ca_b_loc", "country": "CA", "segment": "business", "category": "Business Line of Credit",
     "name": "Business line of credit / operating line", "min_score": 680, "needs_business": True,
     "min_time_in_business": 1.0, "min_business_months": 6, "needs_revenue": True, "clear_collections": True,
     "providers": ["Big 6 banks", "Credit unions (Meridian, Vancity)", "BDC"]},
    {"id": "ca_b_term", "country": "CA", "segment": "business", "category": "Business Term Loan",
     "name": "Business term loan", "min_score": 660, "needs_business": True,
     "min_time_in_business": 1.0, "needs_revenue": True,
     "providers": ["BDC", "Big 6 banks", "Credit unions"]},
    {"id": "ca_b_equip", "country": "CA", "segment": "business", "category": "Equipment Financing",
     "name": "Equipment financing (asset-backed)", "needs_business": True, "needs_revenue": True,
     "providers": ["Banks", "CWB/Equipment lenders", "Manufacturer finance"],
     "notes": "Asset secures the loan (PPSA), so easier than unsecured."},
    {"id": "ca_b_commre", "country": "CA", "segment": "business", "category": "Commercial Mortgage",
     "name": "Commercial mortgage", "min_score": 660, "needs_business": True, "needs_revenue": True,
     "needs_liquid": True, "providers": ["Big 6 banks", "Credit unions", "BDC"]},
    {"id": "ca_b_merchant", "country": "CA", "segment": "business", "category": "Merchant / Payments",
     "name": "Merchant / payment services", "gate": "open", "needs_business": True,
     "providers": ["Moneris", "Square", "Stripe", "Helcim"]},
    {"id": "ca_b_digital", "country": "CA", "segment": "business", "category": "Digital Assets",
     "name": "Business crypto treasury / IP holding", "gate": "digital", "needs_business": True,
     "providers": ["Regulated custody platforms", "IP holdco (structure with a CPA/lawyer)"],
     "risk": "Volatility + accounting/tax complexity. IP-holding and treasury structures must be set "
             "up with professional advice; this is reference, not a tax scheme."},

    # ---------------- USA · PERSONAL (cross-border) ----------------
    {"id": "us_p_hisa", "country": "US", "segment": "personal", "category": "High-Yield Savings",
     "name": "US high-yield savings (HYSA)", "gate": "open", "us": True, "needs_liquid": True,
     "providers": ["Ally", "Marcus", "Amex National Bank", "Capital One 360", "Discover"]},
    {"id": "us_p_bootstrap", "country": "US", "segment": "personal", "category": "Credit Card (bootstrap)",
     "name": "First US card (Amex Global Transfer / ITIN secured / builder)", "gate": "open", "us": True,
     "providers": ["Amex Global Transfer", "Capital One Platinum/Quicksilver Secured (ITIN)", "Self builder"],
     "notes": "The on-ramp to a US file; Canadian history does not transfer."},
    {"id": "us_p_card", "country": "US", "segment": "personal", "category": "Credit Card",
     "name": "US unsecured credit card", "us": True, "min_score": 660, "max_util": 50,
     "providers": ["Chase", "BofA", "Citi", "Capital One", "Amex"],
     "notes": "Needs a US FICO score built over ~6-12 months first."},
    {"id": "us_p_auto", "country": "US", "segment": "personal", "category": "Auto Loan",
     "name": "US auto loan", "us": True, "min_score": 620,
     "providers": ["US banks", "Credit unions", "Captive lenders"]},
    {"id": "us_p_mortgage", "country": "US", "segment": "personal", "category": "Mortgage",
     "name": "US mortgage (incl. cross-border)", "us": True, "min_score": 680, "max_tds": 43,
     "needs_liquid": True, "providers": ["RBC Bank (US)", "US banks", "Cross-border lenders"]},
    {"id": "us_p_crypto", "country": "US", "segment": "personal", "category": "Digital Assets",
     "name": "US crypto trading / custody", "gate": "digital", "us": True,
     "providers": ["Coinbase", "Kraken", "Gemini"],
     "risk": "Volatile and largely uninsured; use regulated US platforms. Cross-border tax reporting applies."},

    # ---------------- USA · BUSINESS (cross-border) ----------------
    {"id": "us_b_bank", "country": "US", "segment": "business", "category": "Business Banking",
     "name": "US business bank account", "gate": "open", "us": True, "needs_business": True,
     "providers": ["Mercury", "Relay", "Canadian-affiliate US banks", "Chase Business"],
     "notes": "Needs a US entity (LLC/Corp) + EIN."},
    {"id": "us_b_card", "country": "US", "segment": "business", "category": "Business Credit Card",
     "name": "US business credit card", "us": True, "needs_business": True,
     "providers": ["Amex Business", "Capital One Spark", "Ramp/Brex (funded startups, sometimes no PG)"],
     "notes": "Usually needs a US entity + EIN; often personally guaranteed."},
    {"id": "us_b_loc", "country": "US", "segment": "business", "category": "Business Loan / SBA",
     "name": "US business loan / line (incl. SBA)", "us": True, "needs_business": True,
     "min_time_in_business": 2.0, "needs_revenue": True,
     "providers": ["US banks", "SBA lenders (FICO SBSS)", "Credit unions"],
     "notes": "SBA loans favour US citizens/LPR ownership; build US business credit (D-U-N-S/PAYDEX) first."},
    {"id": "us_b_digital", "country": "US", "segment": "business", "category": "Digital Assets",
     "name": "US business crypto treasury / tokenization", "gate": "digital", "us": True, "needs_business": True,
     "providers": ["Regulated US custodians", "Tokenization platforms"],
     "risk": "Volatility + securities/tax complexity; structure with professional advice. Reference only."},
]


def build_context(db) -> dict:
    m = db.get_aggregate_metrics()
    p = db.get_user_profile()
    nw = db.net_worth()
    entries = db.get_credit_report_entries()
    assets = db.get_assets()

    gross_monthly = m["gross_monthly_income"]
    housing = p.monthly_housing_cost
    monthly_debt = m["monthly_debt_obligations"]
    gds = round(housing / gross_monthly * 100, 1) if gross_monthly > 0 else None
    tds = round((housing + monthly_debt) / gross_monthly * 100, 1) if gross_monthly > 0 else None
    monthly_need = p.monthly_expenses or monthly_debt
    surplus_cash = max(0.0, nw["liquid_assets"] - monthly_need * 3)
    crypto_value = sum(a.market_value for a in assets if a.category.lower() == "crypto")

    return {
        "score": p.best_score(),
        "utilization_pct": m["aggregate_utilization_pct"],
        "dti_pct": m["estimated_dti_pct"],
        "gds_pct": gds,
        "tds_pct": tds,
        "open_collections": sum(1 for e in entries if e.entry_type == "collection"),
        "liquid": nw["liquid_assets"],
        "surplus_cash": surplus_cash,
        "crypto_value": crypto_value,
        "business_exists": bool(db.get_business_accounts()) or p.business_bank_months > 0
                           or p.business_revenue_monthly > 0,
        "us_foundation": p.us_foundation(),
        "time_in_business_years": p.time_in_business_years,
        "business_bank_months": p.business_bank_months,
        "revenue_monthly": p.business_revenue_monthly,
    }


def _crit(label, met, actual, target, fix):
    return {"criterion": label, "met": met, "actual": actual, "target": target, "fix": fix}


def evaluate(product: dict, ctx: dict) -> dict:
    c = []
    if product.get("us"):
        met = ctx["us_foundation"]
        c.append(_crit("US foundation (US bank + ITIN/SSN + US address)", met,
                       "yes" if met else "not set", "established",
                       "Build the cross-border foundation first (reference menu 15 -> 8)."))
    if product.get("needs_business"):
        met = ctx["business_exists"]
        c.append(_crit("Registered business + account", met, "yes" if met else "no", "yes",
                       "Register the business and open a dedicated business account."))
    if product.get("min_score"):
        s = ctx["score"]
        met = (s >= product["min_score"]) if s > 0 else None
        c.append(_crit("Credit score", met, str(s) if s > 0 else "not set",
                       f">= {product['min_score']}",
                       "Raise score: on-time payments, low utilization, aging accounts, dispute genuine errors."))
    if product.get("max_util") is not None:
        u = ctx["utilization_pct"]
        c.append(_crit("Card utilization", u < product["max_util"], f"{u:.1f}%",
                       f"< {product['max_util']:.0f}%", "Pay balances down (ideally <10% before statement)."))
    if product.get("max_dti") is not None:
        d = ctx["dti_pct"]
        c.append(_crit("Debt-to-income", (d is not None and d < product["max_dti"]),
                       "n/a" if d is None else f"{d:.1f}%", f"< {product['max_dti']:.0f}%",
                       "Increase documented income or reduce monthly debt."))
    if product.get("max_gds") is not None:
        g = ctx["gds_pct"]
        c.append(_crit("Gross debt service (GDS)", (g is not None and g <= product["max_gds"]),
                       "n/a" if g is None else f"{g:.1f}%", f"<= {product['max_gds']:.0f}%",
                       "Lower housing cost, raise income, or add down payment."))
    if product.get("max_tds") is not None:
        t = ctx["tds_pct"]
        c.append(_crit("Total debt service (TDS)", (t is not None and t <= product["max_tds"]),
                       "n/a" if t is None else f"{t:.1f}%", f"<= {product['max_tds']:.0f}%",
                       "Pay down debts or raise documented income."))
    if product.get("clear_collections"):
        col = ctx["open_collections"]
        c.append(_crit("No open collections", col == 0, str(col), "0",
                       "Resolve, validate, or dispute genuinely inaccurate/outdated collections."))
    if product.get("min_time_in_business"):
        y = ctx["time_in_business_years"]
        c.append(_crit("Time in business", y >= product["min_time_in_business"], f"{y:.1f} yr",
                       f">= {product['min_time_in_business']} yr", "Build operating history and steady revenue."))
    if product.get("min_business_months"):
        mo = ctx["business_bank_months"]
        c.append(_crit("Business account seasoning", mo >= product["min_business_months"], f"{mo} mo",
                       f">= {product['min_business_months']} mo", "Keep the business account active and funded."))
    if product.get("needs_revenue"):
        rev = ctx["revenue_monthly"]
        c.append(_crit("Documented revenue", rev > 0, f"${rev:,.0f}/mo", "documented (6-12 mo)",
                       "Keep clean statements/financials showing steady revenue."))
    if product.get("needs_liquid"):
        met = ctx["liquid"] > 0
        c.append(_crit("Cash available", met, f"${ctx['liquid']:,.0f} liquid", "some (deploy / down payment)",
                       "Build liquid savings."))
    if product.get("needs_crypto"):
        cv = ctx["crypto_value"]
        c.append(_crit("Digital-asset collateral", cv > 0, f"${cv:,.0f}", "> $0 held on a regulated platform",
                       "Hold digital assets on a regulated platform to use as collateral."))
    if not c:
        c.append(_crit("Eligibility", True, "open", "KYC only", "Complete standard KYC/onboarding."))

    met_count = sum(1 for x in c if x["met"] is True)
    total = len(c)
    readiness = round(met_count / total * 100, 1) if total else 0.0
    gaps = [x for x in c if x["met"] is not True]
    verdict = ("Ready now" if readiness >= 100 else
               "Close -- close the gaps" if readiness >= 60 else
               "Build first")
    return {
        "id": product["id"], "country": product["country"], "segment": product["segment"],
        "category": product["category"], "name": product["name"],
        "providers": product.get("providers", []), "notes": product.get("notes", ""),
        "risk": product.get("risk", ""), "readiness_pct": readiness, "verdict": verdict,
        "criteria": c, "gaps": gaps,
    }


def match(db, country: Optional[str] = None, segment: Optional[str] = None) -> List[dict]:
    """Rank product categories by how ready YOU are, most-ready first. Optional
    filters: country in {'CA','US'}, segment in {'personal','business'}."""
    ctx = build_context(db)
    results = []
    for p in PRODUCTS:
        if country and p["country"] != country:
            continue
        if segment and p["segment"] != segment:
            continue
        results.append(evaluate(p, ctx))
    results.sort(key=lambda r: (-r["readiness_pct"], r["country"], r["segment"], r["category"]))
    return results


def summary_note() -> str:
    return ("Ranks product CATEGORIES by your readiness and names who offers them -- not a "
            "guarantee any institution will approve you. " + FINANCIAL_DISCLAIMER)
