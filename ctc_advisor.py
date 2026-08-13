"""
CoreTrust System (CTC) -- Agentic AI Financial Advisor (CLI)
============================================================
The real advisor. When the Anthropic SDK and credentials are available it runs an
agentic Claude (Opus 4.8) loop that can:
  * read your local financial profile (a tool that returns your computed numbers),
  * research the live economy with web search (rates, inflation, program terms),
  * remember what it learns about you across sessions (persistent memory),
and give upfront, specific, analytical guidance -- while staying compliant
(educational; it flags when something needs a licensed CPA/lawyer/advisor rather
than pretending to be one).

If the SDK/credentials aren't set up, it falls back to an OFFLINE local advisor
that answers from your data with no network. To enable the live agent:
    pip install anthropic
    export ANTHROPIC_API_KEY=...     (or: ant auth login)

Your financial data stays local; only your questions + a computed summary are
sent to the model when the live agent is used.
"""

from __future__ import annotations

import json
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

MODEL = "claude-opus-4-8"


# ---------------------------------------------------------------------------
# Persistent advisor memory
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
# Computed profile the advisor reasons over
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
        "registered_room": [{"type": p.portfolio_type, "room": p.remaining_room()}
                            for p in db.get_portfolios()],
        "ready_products": [x["name"] for x in matches if x["readiness_pct"] >= 100][:12],
        "near_products": [{"name": x["name"], "readiness": x["readiness_pct"],
                           "gap": (x["gaps"][0]["criterion"] if x["gaps"] else "")}
                          for x in matches if 60 <= x["readiness_pct"] < 100][:6],
        "next_roadmap_phase": (rm["phases"][0]["title"] if rm["phases"] else None),
        "top_plays": [{"title": p["title"], "benefit": p["estimated_benefit"]} for p in generate_plays(db)[:5]],
        "debt_payoff_avalanche": {"months": payoff.get("months_to_debt_free"),
                                  "total_interest": payoff.get("total_interest")},
        "outdated_credit_entries": len([a for a in audit_reporting_periods(db.get_credit_report_entries())
                                        if a.get("disputable_as_outdated")]),
        "upcoming_deadlines": deadline_radar(db)[:6],
        "black_entrepreneur_programs": [{"name": e["name"], "availability": e["availability"]} for e in black],
        "bank_of_canada_rates": ratewatch.get(db),
        "rate_impact": ratewatch.rate_impact(db),
    }


SYSTEM_PROMPT = (
    "You are the CoreTrust Advisor: a sharp, upfront personal-finance and credit "
    "strategist for a Canadian in the Greater Toronto Area (Ontario). Be direct, "
    "specific, and analytical -- give real opinions grounded in the user's actual "
    "numbers, not generic filler or hand-holding. Do the math; name the tradeoffs.\n\n"
    "Call get_financial_profile at the start of a conversation (and again after the "
    "user says their numbers changed) to ground every answer in their real data. "
    "Use web_search for anything time-sensitive about the economy (Bank of Canada "
    "rate, prime, inflation, current program terms, rate comparisons) -- don't guess "
    "at current figures. The profile already carries the latest Bank of Canada "
    "overnight and prime rates (bank_of_canada_rates); use them directly and "
    "web-search for anything else time-sensitive. "
    "Use remember to persist durable facts about the user "
    "(goals, constraints, decisions) so you improve across sessions.\n\n"
    "Compliance is non-negotiable and is what makes your advice trustworthy: you are "
    "an educational tool, not a licensed professional. Give the full analysis, but "
    "for regulated advice (specific investment picks, personalized tax filing, legal "
    "opinions, mortgage brokering) state the analysis and point them to a licensed "
    "CPA / advisor / lawyer / paralegal rather than posing as one. Never invent "
    "numbers, never encourage hiding information from lenders or fabricating disputes."
)

TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"name": "get_financial_profile",
     "description": "Return the user's current computed financial profile (health score, net worth, "
                    "utilization, DTI, credit score, product readiness, registered-account room, "
                    "payoff plan, deadlines, and eligible programs) from their local database.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "remember",
     "description": "Persist a durable fact about the user (a goal, constraint, or decision) so future "
                    "sessions can use it. Keep it to one concise sentence.",
     "input_schema": {"type": "object", "properties": {"note": {"type": "string"}},
                      "required": ["note"], "additionalProperties": False}},
]


def _llm_available():
    try:
        import anthropic  # noqa: F401
        return True
    except Exception:
        return False


def run_agent(db) -> None:
    import anthropic
    try:
        client = anthropic.Anthropic()
    except Exception as ex:  # noqa: BLE001
        print(f"  Could not initialize the Anthropic client: {ex}")
        return run_local(db)

    mem = recall(db)
    system = SYSTEM_PROMPT
    if mem:
        system += "\n\nWhat you've learned about this user so far:\n" + \
                  "\n".join(f"- {m['note']}" for m in mem)

    print("\n  CORETRUST ADVISOR (live agent · Claude Opus 4.8 · web-enabled)")
    print("  Greetings — wealth is on the way. Ask anything; type 'exit' to leave.\n")
    messages = []
    while True:
        user = input("  you > ").strip()
        if user.lower() in ("exit", "quit", ""):
            print("  Advisor signing off. Stay compliant.")
            return
        messages.append({"role": "user", "content": user})
        # agentic loop
        for _ in range(12):
            try:
                resp = client.messages.create(
                    model=MODEL, max_tokens=8000,
                    thinking={"type": "adaptive"},
                    system=system, tools=TOOLS, messages=messages)
            except anthropic.AuthenticationError:
                print("  Auth failed — set ANTHROPIC_API_KEY or run `ant auth login`. Using offline advisor.\n")
                return run_local(db)
            except Exception as ex:  # noqa: BLE001
                print(f"  API error: {ex}")
                return
            if resp.stop_reason == "refusal":
                print("  advisor > (declined this request)")
                messages.append({"role": "assistant", "content": resp.content})
                break
            messages.append({"role": "assistant", "content": resp.content})
            # print any text
            for b in resp.content:
                if b.type == "text" and b.text.strip():
                    print("\n  advisor > " + b.text.strip() + "\n")
            if resp.stop_reason == "pause_turn":
                continue  # server tool paused; resend to resume
            tool_uses = [b for b in resp.content if b.type == "tool_use"]
            if not tool_uses:
                break
            results = []
            for tu in tool_uses:
                if tu.name == "get_financial_profile":
                    out = json.dumps(profile_json(db))
                elif tu.name == "remember":
                    remember(db, tu.input.get("note", ""))
                    out = "saved"
                else:
                    out = "unknown tool"
                results.append({"type": "tool_result", "tool_use_id": tu.id, "content": out})
            messages.append({"role": "user", "content": results})


# ---------------------------------------------------------------------------
# Offline local advisor (no network)
# ---------------------------------------------------------------------------
def briefing(db) -> str:
    p = profile_json(db)
    lines = [
        "  CORETRUST ADVISOR — Greetings, wealth is on the way.",
        f"  Health {p['health_score']} ({p['grade']}) · net worth ${p['net_worth']:,.0f} · "
        f"score {p['best_credit_score'] or '—'} · util {p['utilization_pct']}% · DTI {p['dti_pct']}%",
        f"  Ready now: {len(p['ready_products'])} products" +
        (f" ({', '.join(p['ready_products'][:5])})" if p['ready_products'] else ""),
        f"  Top move: {p['top_plays'][0]['title'] if p['top_plays'] else 'add data'}"
        + (f" — {p['top_plays'][0]['benefit']}" if p['top_plays'] else ""),
        f"  Next phase: {p['next_roadmap_phase'] or '—'}",
    ]
    if p["upcoming_deadlines"]:
        d = p["upcoming_deadlines"][0]
        lines.append(f"  Next deadline: {d['date']} — {d['label']}")
    lines.append("  " + ratewatch.summary_line(p.get("bank_of_canada_rates")))
    lines.append("  " + ratewatch.impact_line(p.get("rate_impact")))
    return "\n".join(lines)


def local_answer(db, q: str) -> str:
    p = profile_json(db)
    t = q.lower()

    def has(*k):
        return any(x in t for x in k)

    if has("black", "bep", "face", "minority", "program", "grant"):
        avail = [b["name"] for b in p["black_entrepreneur_programs"] if b["availability"] == "available"]
        prereq = [b["name"] for b in p["black_entrepreneur_programs"] if b["availability"] == "prerequisite"]
        return ("Black-entrepreneur programs — ready now: " + (", ".join(avail) or "none yet") +
                (". Register a business to unlock: " + ", ".join(prereq) if prereq else "") +
                ". US Black-owned banks need the cross-border foundation first.")
    if has("ready", "approve", "qualify", "mortgage", "loan", "card", "funding"):
        near = "; ".join(f"{n['name']} ({n['readiness']}% — {n['gap']})" for n in p["near_products"])
        return (f"Ready now for {len(p['ready_products'])}: {', '.join(p['ready_products'][:8])}. "
                f"Closest next: {near or 'n/a'}.")
    if has("pay", "payoff", "debt"):
        d = p["debt_payoff_avalanche"]
        return (f"Avalanche (highest-rate first): debt-free in ~{d['months']} months, "
                f"~${(d['total_interest'] or 0):,.0f} interest at your current budget. Tune it in menu 21.")
    if has("us ", "cross-border", "america", "itin"):
        return ("US foundation: " + ("established — pursue US HYSA/ITIN cards, then build FICO 6–12 months."
                if p["us_foundation"] else "not yet — open a US account via a Canadian bank's US affiliate, "
                "get a US address, first US card via Amex Global Transfer / ITIN secured card, apply for an ITIN."))
    if has("tfsa", "rrsp", "fhsa", "registered", "room"):
        return "Registered room — " + (", ".join(f"{r['type']}: ${r['room']:,.0f}" for r in p["registered_room"])
                                        or "none tracked") + ". FHSA is strongest (deductible + tax-free for a first home)."
    if has("score", "health", "improve"):
        c = p["components"]
        weak = min(c, key=c.get)
        return (f"Health {p['health_score']} ({p['grade']}). Weakest lever: {weak} ({c[weak]}). "
                "Fastest wins: utilization <10% before statement, clear/dispute open collections, age accounts.")
    if has("deadline", "due", "when"):
        return "Upcoming: " + ("; ".join(f"{d['date']} {d['label']}" for d in p["upcoming_deadlines"]) or "nothing in range")
    return briefing(db)


def run_local(db) -> None:
    print("\n" + briefing(db))
    print("  (Offline local advisor — answers from your data. Install `anthropic` + a key for the")
    print("   live web-researching agent.) Ask a question, or 'exit'.\n")
    while True:
        q = input("  you > ").strip()
        if q.lower() in ("exit", "quit", ""):
            print("  Advisor signing off. Stay compliant.")
            return
        print("\n  advisor > " + local_answer(db, q) + "\n")


def advise(db) -> None:
    try:
        rw = ratewatch.refresh(db)   # best-effort live pull; caches for the dashboard too
        if rw:
            print("  " + ratewatch.summary_line(rw))
    except Exception:  # noqa: BLE001 -- offline is fine
        pass
    if _llm_available():
        run_agent(db)
    else:
        print("\n  (Live agent needs the Anthropic SDK: pip install anthropic, then set")
        print("   ANTHROPIC_API_KEY or run `ant auth login`. Running the offline advisor now.)")
        run_local(db)
