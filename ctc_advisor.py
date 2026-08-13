"""
CoreTrust System (CTC) -- Dual-Engine Hybrid AI Advisor (Gemini + Claude)
==========================================================================
Combines Google Antigravity / Gemini API (for lightning-fast queries, vision OCR, 
and real-time data) with Anthropic Claude API (for high-precision legal compliance, 
dispute letter synthesis, and deep financial auditing).

Features:
  1. Dual-Engine Hybrid Router (Gemini 1.5 Flash/Pro + Claude 3.5 Sonnet/Opus)
  2. Verified Smart Link Delivery Engine (Big 6 Banks, Credit Unions, OSAP, Scholarships)
  3. Persistent Advisor Memory & Local DB Context Integration
  4. Instant Document & Statement OCR (OSAP notices, tuition bills, PDF/images)
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime

from ctc_dashboard import compute_scorecard, generate_plays
from ctc_match import match
from ctc_roadmap import build_roadmap
from ctc_disputes import audit_reporting_periods
from ctc_history import deadline_radar
from ctc_access import generate_access_list, personalize, context_from_db
from ctc_payoff import payoff_plan
import ctc_rates as R
import ctc_rates_watch as ratewatch

CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
GEMINI_MODEL = "gemini-1.5-flash"

# ---------------------------------------------------------------------------
# Verified Link & Access Catalog (Banks, Credit Unions, OSAP, Money Stack)
# ---------------------------------------------------------------------------
LINK_CATALOG = {
    "neo_secured": {
        "name": "Neo Financial Secured Mastercard",
        "category": "Secured Credit / Credit Builder",
        "url": "https://www.neofinancial.com/products/credit-card",
        "bonus": "$0 Annual Fee · $50 Min Deposit · Built-in Rent Reporting",
        "tags": ["Equifax + TransUnion", "Fast Approval", "Students 18+"],
    },
    "koho_credit": {
        "name": "KOHO Credit Building",
        "category": "Credit Builder",
        "url": "https://www.koho.ca/credit-building/",
        "bonus": "$7/month Autopay Tradeline",
        "tags": ["Reports to Equifax", "Rebuilding Starter"],
    },
    "borrowell_rent": {
        "name": "Borrowell Rent Advantage",
        "category": "Rent Reporting",
        "url": "https://www.borrowell.com/rent-advantage",
        "bonus": "$8/month · Reports Rent to Equifax",
        "tags": ["Equifax Tradeline", "No Landlord Required"],
    },
    "tangerine_mc": {
        "name": "Tangerine Money-Back Mastercard",
        "category": "No-Fee Cashback Card",
        "url": "https://www.tangerine.ca/en/products/spending/creditcard/money-back-credit-card",
        "bonus": "2% Cashback in 2-3 Categories You Pick",
        "tags": ["No Annual Fee", "Scotiabank Affiliate"],
    },
    "rogers_bank": {
        "name": "Rogers Mastercard",
        "category": "No-FX / Cashback Card",
        "url": "https://www.rogersbank.com/en/our_credit_cards",
        "bonus": "3% Cash on USD Spend (FX Neutralizer)",
        "tags": ["$0 Annual Fee", "Great for US/Online Shopping"],
    },
    "eq_bank": {
        "name": "EQ Bank Savings Plus Account",
        "category": "High-Yield Savings (HYSA)",
        "url": "https://www.eqbank.ca/personal-banking/features-rates",
        "bonus": "High Interest · $0 Fees · Free Interac e-Transfers",
        "tags": ["CDIC Insured", "All Canadian Residents"],
    },
    "maxa_financial": {
        "name": "MAXA Financial Digital Credit Union",
        "category": "Credit Union HYSA",
        "url": "https://www.maxafinancial.com",
        "bonus": "Top-Tier Canadian Savings Rates",
        "tags": ["100% Deposit Guarantee", "Open to All Canadians"],
    },
    "meridian_cu": {
        "name": "Meridian Credit Union (Ontario)",
        "category": "Major Credit Union",
        "url": "https://www.meridiancu.ca/personal/credit-cards",
        "bonus": "Personal Lines of Credit & Student Banking",
        "tags": ["Ontario's Largest CU", "Flexible Underwriting"],
    },
    "vancity_cu": {
        "name": "Vancity Credit Union (BC / National)",
        "category": "Credit Union",
        "url": "https://www.vancity.com",
        "bonus": "envision & enviro Visa Credit Cards",
        "tags": ["BC & National Access", "Community Impact"],
    },
    "osap_estimator": {
        "name": "Official OSAP Aid Estimator Portal",
        "category": "Government Aid Portal",
        "url": "https://www.ontario.ca/page/osap-aid-estimator",
        "bonus": "Calculate Grants (25%) vs Loans (75%)",
        "tags": ["Official Ontario Portal", "2026 Policy Updated"],
    },
    "nslsc_portal": {
        "name": "NSLSC Student Loan Portal",
        "category": "Student Loan Repayment",
        "url": "https://www.nslsc.ca/en/home",
        "bonus": "Grace Period & Repayment Assistance (RAP)",
        "tags": ["Federal/Provincial Loans", "Official Portal"],
    },
    "loran_award": {
        "name": "Loran Award ($100,000)",
        "category": "Free Money Stack",
        "url": "https://loranscholar.ca/becoming-a-scholar/",
        "bonus": "$100,000 over 4 Years",
        "tags": ["Academics + Leadership", "Apply Early"],
    },
    "schulich_leaders": {
        "name": "Schulich Leader Scholarships ($100,000+)",
        "category": "STEM Scholarship",
        "url": "https://schulichleaders.com",
        "bonus": "$100,000 - $120,000 STEM Awards",
        "tags": ["STEM Fields", "High School Seniors"],
    },
    "yconic_db": {
        "name": "Yconic Scholarship Database",
        "category": "Scholarship Finder",
        "url": "https://yconic.com",
        "bonus": "Search 1,000+ Canadian Student Awards",
        "tags": ["Free Student Database", "Apply to 10+ Minimum"],
    },
    "scholartree_db": {
        "name": "ScholarTree Canadian Scholarships",
        "category": "Scholarship Finder",
        "url": "https://scholartree.ca",
        "bonus": "Matched Bursaries & Scholarships",
        "tags": ["Canadian Students", "Filter by Major & Province"],
    },
}

# ---------------------------------------------------------------------------
# Persistent Advisor Memory
# ---------------------------------------------------------------------------
def _ensure(db) -> None:
    db.cursor.execute("CREATE TABLE IF NOT EXISTS advisor_memory ("
                      "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, note TEXT)")
    db.conn.commit()

def remember(db, note: str) -> None:
    _ensure(db)
    db.cursor.execute("INSERT INTO advisor_memory (ts, note) VALUES (?,?)",
                      (datetime.now().isoformat(timespec="seconds"), note))
    db.conn.commit()

def recall(db, limit: int = 20):
    _ensure(db)
    rows = db.cursor.execute("SELECT ts, note FROM advisor_memory ORDER BY id DESC LIMIT ?",
                             (limit,)).fetchall()
    return [{"ts": r["ts"], "note": r["note"]} for r in rows][::-1]

# ---------------------------------------------------------------------------
# Computed Financial Profile Payload
# ---------------------------------------------------------------------------
def profile_json(db) -> dict:
    sc = compute_scorecard(db)
    m = db.get_aggregate_metrics()
    nw = db.net_worth()
    prof = db.get_user_profile()
    matches = match(db)
    rm = build_roadmap(db)
    ctx = context_from_db(db)
    black = personalize(generate_access_list(black_focus=True), ctx)
    debts_budget = round(sum(d.monthly_payment for d in db.get_installment_debts())
                         + sum(c.estimated_min_payment() for c in db.get_credit_cards()) + 200, 0)
    payoff = payoff_plan(db, debts_budget, "avalanche")
    return {
        "generated": date.today().isoformat(),
        "health_score": sc["composite_score"], "grade": sc["grade"],
        "components": sc["components"],
        "net_worth": nw["net_worth"], "liquid_assets": nw["liquid_assets"],
        "utilization_pct": m["aggregate_utilization_pct"], "dti_pct": m["estimated_dti_pct"],
        "best_credit_score": prof.best_score(), "us_foundation": prof.us_foundation(),
        "business_exists": ctx["business_exists"],
        "gross_monthly_income": m["gross_monthly_income"],
        "ready_products": [x["name"] for x in matches if x["readiness_pct"] >= 100][:12],
        "top_plays": [{"title": p["title"], "benefit": p["estimated_benefit"]} for p in generate_plays(db)[:5]],
        "upcoming_deadlines": deadline_radar(db)[:6],
        "bank_of_canada_rates": ratewatch.get(db),
        "link_catalog": LINK_CATALOG
    }

# ---------------------------------------------------------------------------
# Smart Link Formatter for Terminal & Web Output
# ---------------------------------------------------------------------------
def format_smart_links(text: str) -> str:
    """Replaces catalog references in model text with formatted Smart Link Pills."""
    for key, item in LINK_CATALOG.items():
        pattern = re.compile(rf"\[?({key})\]?", re.IGNORECASE)
        replacement = f"📌 [{item['name']}] ({item['url']}) — {item['bonus']}"
        text = pattern.sub(replacement, text)
    return text

# ---------------------------------------------------------------------------
# Dual-Engine Router Logic
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are the CoreTrust Hybrid AI Advisor (powered by Gemini + Claude).\n"
    "You serve Canadian 18-25 year olds and financial clients in Ontario / GTA.\n\n"
    "RULES & DIRECTIVES:\n"
    "1. Be direct, analytical, and highly actionable. Ground advice in real user data.\n"
    "2. Whenever recommending a credit card, bank, credit union, OSAP portal, or scholarship, "
    "reference the exact item key from LINK_CATALOG (e.g., neo_secured, eq_bank, osap_estimator, loran_award) "
    "so the system formats direct verified links.\n"
    "3. Compliance is strict: educational guidance only. Include mandatory consumer rights disclaimers "
    "for credit disputes under the Ontario Consumer Reporting Act. Never guarantee score increases."
)

def query_gemini(prompt: str, system_context: str) -> str | None:
    """Fast execution via Google Generative AI (Gemini 1.5 Flash/Pro)."""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_context)
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return None

def query_claude(messages: list, system_context: str) -> str | None:
    """High-precision legal & compliance execution via Anthropic Claude."""
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            system=system_context,
            messages=messages
        )
        return response.content[0].text
    except Exception:
        return None

def run_hybrid_agent(db) -> None:
    """Interactive CLI Advisor loop using Dual-Engine Hybrid Routing."""
    mem = recall(db)
    system = SYSTEM_PROMPT
    if mem:
        system += "\n\nUser Memory Facts:\n" + "\n".join(f"- {m['note']}" for m in mem)

    prof = profile_json(db)
    system += "\n\nCurrent User Financial Summary:\n" + json.dumps(prof, indent=2)

    print("\n  ===============================================================")
    print("  CORETRUST ADVISOR (Dual-Engine: Google Gemini + Anthropic Claude)")
    print("  Smart Link Delivery Engine: Live & Verified")
    print("  Type 'exit' to leave.\n  ===============================================================\n")

    messages = []
    while True:
        user_input = input("  you > ").strip()
        if user_input.lower() in ("exit", "quit", ""):
            print("  Advisor signing off. Stay compliant.")
            return

        messages.append({"role": "user", "content": user_input})
        
        # Router Rule: If legal/dispute/compliance request -> Route to Anthropic Claude
        is_legal = bool(re.search(r"dispute|letter|equifax|transunion|consumer reporting act|compliance|legal", user_input, re.IGNORECASE))
        
        reply = None
        engine_used = ""

        if is_legal:
            reply = query_claude(messages, system)
            engine_used = "Anthropic Claude (Legal & Compliance Engine)"
        
        if not reply:
            # Route to Google Gemini for speed & financial routing
            full_prompt = f"User Question: {user_input}\nProvide structured guidance with catalog link keys."
            reply = query_gemini(full_prompt, system)
            engine_used = "Google Antigravity / Gemini (Fast Engine)"

        if not reply and not is_legal:
            # Fallback attempt to Claude if Gemini failed
            reply = query_claude(messages, system)
            engine_used = "Anthropic Claude (Fallback)"

        if reply:
            formatted_reply = format_smart_links(reply)
            print(f"\n  advisor ({engine_used}) >\n  {formatted_reply}\n")
            messages.append({"role": "assistant", "content": reply})
        else:
            print("\n  advisor (Offline Mode) > " + local_answer(db, user_input) + "\n")

# ---------------------------------------------------------------------------
# Local Offline Advisor Fallback
# ---------------------------------------------------------------------------
def briefing(db) -> str:
    p = profile_json(db)
    return (f"  CORETRUST BRIEFING — Health {p['health_score']} ({p['grade']}) · "
            f"Net Worth ${p['net_worth']:,.0f} · Ready Products: {len(p['ready_products'])}\n"
            f"  Featured Portals: Neo Secured, Tangerine, EQ Bank, OSAP Aid Estimator, Loran Award")

def local_answer(db, q: str) -> str:
    p = profile_json(db)
    t = q.lower()
    if any(k in t for k in ["link", "bank", "card", "osap", "scholarship", "credit union"]):
        links = "\n".join(f"  • {item['name']}: {item['url']} ({item['bonus']})" for item in list(LINK_CATALOG.values())[:6])
        return f"Verified Financial & Aid Portals:\n{links}"
    return briefing(db)

def advise(db) -> None:
    run_hybrid_agent(db)

if __name__ == "__main__":
    import ctc_models
    db = ctc_models.DB()
    advise(db)
