"""
CoreTrust System (CTC) -- Funding Roadmap
=========================================
Turns your ranked product matches into an ORDERED game plan: clear the blockers,
activate what you're ready for, close near-ready gaps, build the US cross-border
foundation, then scale into US personal & business credit -- with digital assets
handled last and risk-managed.

Deterministic and grounded in your own data. Not advice; sequence, not a promise.
"""

from __future__ import annotations

from ctc_rates import FINANCIAL_DISCLAIMER
from ctc_match import match, build_context
from ctc_disputes import audit_reporting_periods


def build_roadmap(db) -> dict:
    ctx = build_context(db)
    results = match(db)
    by_id = {r["id"]: r for r in results}
    ready = [r for r in results if r["readiness_pct"] >= 100]
    near = [r for r in results if 60 <= r["readiness_pct"] < 100]

    phases = []

    # --- Phase: clear blockers ------------------------------------------
    steps = []
    outdated = [a for a in audit_reporting_periods(db.get_credit_report_entries())
                if a.get("disputable_as_outdated")]
    if ctx["open_collections"] > 0:
        steps.append({"action": "Resolve or dispute the open collection(s) on your file",
                      "why": "An open collection is the main gap holding back your personal loan, "
                             "line of credit, and mortgage.",
                      "unlocks": ["Personal loan", "Personal LOC", "Mortgage"]})
    if outdated:
        steps.append({"action": f"Dispute {len(outdated)} outdated entry(ies) past the Ontario limit",
                      "why": "Removing outdated items can lift your score.",
                      "unlocks": ["Higher score across products"]})
    if ctx["utilization_pct"] > 30:
        steps.append({"action": "Bring card utilization under 30% (ideally <10% before statement dates)",
                      "why": "Lower reported utilization improves your score and approvals.",
                      "unlocks": ["Better cards", "Lines of credit"]})
    if steps:
        phases.append({"n": len(phases) + 1, "title": "Clear the blockers", "steps": steps})

    # --- Phase: activate ready-now Canadian foundation ------------------
    order = ["ca_p_hisa", "ca_b_bank", "ca_p_card", "ca_b_card", "ca_p_secured", "ca_b_merchant"]
    picks = [by_id[i] for i in order if i in by_id and by_id[i]["readiness_pct"] >= 100]
    if picks:
        steps = [{"action": f"Open: {p['name']}",
                  "why": f"Ready now via {', '.join(p['providers'][:3])}.",
                  "unlocks": [p["category"]]} for p in picks]
        phases.append({"n": len(phases) + 1,
                       "title": "Activate what you're ready for (Canada)", "steps": steps})

    # --- Phase: close near-ready gaps -----------------------------------
    if near:
        steps = []
        for r in near[:6]:
            gap = r["gaps"][0] if r["gaps"] else None
            steps.append({"action": f"Get ready for {r['name']} ({r['readiness_pct']:.0f}%)",
                          "why": gap["fix"] if gap else "Close the remaining criteria.",
                          "unlocks": [r["category"]]})
        phases.append({"n": len(phases) + 1,
                       "title": "Close the gaps on near-ready facilities", "steps": steps})

    # --- Phase: build the US cross-border foundation --------------------
    if not ctx["us_foundation"]:
        phases.append({"n": len(phases) + 1, "title": "Build the US cross-border foundation", "steps": [
            {"action": "Open a US account via your Canadian bank's US affiliate "
                       "(RBC Bank, TD, BMO, CIBC Bank USA, Natbank, Desjardins)",
             "why": "Typically no SSN required; it anchors your US foundation.",
             "unlocks": ["US banking"]},
            {"action": "Establish a US mailing address", "why": "Required for US applications.",
             "unlocks": ["US applications"]},
            {"action": "Get your first US card — Amex Global Transfer (uses your Canadian Amex) "
                       "or an ITIN-friendly secured card",
             "why": "Starts a US credit file; Canadian history does not transfer.",
             "unlocks": ["US credit history"]},
            {"action": "Apply for an ITIN (IRS Form W-7) if you'll file/earn in the US",
             "why": "Several issuers accept an ITIN in place of an SSN.",
             "unlocks": ["US cards & loans"]},
        ]})

    # --- Phase: scale into US personal & business credit ---------------
    phases.append({"n": len(phases) + 1, "title": "Scale into US personal & business credit", "steps": [
        {"action": "Pay the US card in full, on time, for 6-12 months",
         "why": "US FICO reaches usable (~640) in 4-6 months and good (670+) in 9-12.",
         "unlocks": ["US HYSA", "US cards", "US auto loan"]},
        {"action": "For US business: form a US LLC/Corp, get an EIN (SS-4), open a US business "
                   "account, and get a US D-U-N-S number",
         "why": "Builds a US business credit file (PAYDEX) separate from your personal file.",
         "unlocks": ["US business banking, cards, loans/SBA"]},
    ]})

    # --- Phase: digital assets (optional, risk-managed) ----------------
    steps = [{"action": "Keep any crypto on a regulated platform "
                        "(Wealthsimple, Bitbuy, Kraken, Coinbase) with clean records for the CRA",
              "why": "KYC-compliant custody and accurate tax reporting.",
              "unlocks": ["Digital-asset tracking"]}]
    if ctx["crypto_value"] > 0:
        steps.append({"action": "Only consider a crypto-backed loan with a large safety margin",
                      "why": "RISK: volatility can trigger margin calls and forced liquidation; "
                             "this is not a tax-avoidance strategy.",
                      "unlocks": ["Liquidity without selling (high risk)"]})
    phases.append({"n": len(phases) + 1, "title": "Digital assets (optional, risk-managed)", "steps": steps})

    return {"phases": phases, "note": FINANCIAL_DISCLAIMER}


def render_text(roadmap: dict) -> str:
    out = ["FUNDING ROADMAP -- your ordered game plan", "=" * 50]
    for ph in roadmap["phases"]:
        out.append(f"\nPHASE {ph['n']}: {ph['title']}")
        for s in ph["steps"]:
            out.append(f"  -> {s['action']}")
            out.append(f"     why: {s['why']}")
            if s.get("unlocks"):
                out.append(f"     unlocks: {', '.join(s['unlocks'])}")
    out.append("\n" + roadmap["note"])
    return "\n".join(out)
