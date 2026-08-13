"""
CoreTrust System (CTC) -- Command-Line Control Center
=====================================================
A local, single-user personal financial tracker & optimizer for a Canadian
consumer (GTA).

Run:  python3 ctc_cli.py

All data lives in a local SQLite file (coretrust_system.db) on this machine.
Enter YOUR real, verified numbers, or bulk-load them from a JSON file
(see sample_profile.json). Nothing is sent anywhere. Educational tool only --
not legal, tax, or investment advice.
"""

from __future__ import annotations

import os

from ctc_models import (
    CTCDatabase, CreditCard, InstallmentDebt, RegisteredPortfolio, IncomeSource,
    PersonalAccount, BusinessAccount, Asset, CreditReportEntry, UserProfile,
    CRA_2026_LIMITS,
)
from ctc_disputes import (
    audit_reporting_periods, generate_dispute_letter, ONTARIO_MAX_PERIODS, LETTER_TYPES,
)
from ctc_underwriting import (
    credit_limit_increase_readiness, tied_selling_refusal_script,
    rate_negotiation_script, credit_optimization_playbook,
)
from ctc_lender import PRODUCTS, assess, required_income_for_dti
from ctc_dashboard import compute_scorecard, generate_plays
from ctc_tax import (
    income_tax_snapshot, rrsp_contribution_benefit, registered_account_guide,
    explain_concept, CONCEPTS,
)
from ctc_payroll import net_from_gross, gross_for_target_net
from ctc_import import import_transactions_csv, import_cards_csv, import_accounts_csv
from ctc_reference import SECTIONS, full_reference
from ctc_match import match as match_products, summary_note
from ctc_roadmap import build_roadmap, render_text as roadmap_text
from ctc_dashboard_web import write_dashboard
from ctc_dashboard_live import write_live_dashboard
from ctc_serve import serve as serve_live
from ctc_compliance import (log_event, get_audit_log, set_consent, get_consent,
                            create_dispute_case, list_dispute_cases, update_dispute_case,
                            statute_currency, encrypt_backup, decrypt_backup, ESCALATION_LADDER)
from ctc_history import (take_snapshot, trend, add_goal, list_goals, deadline_radar,
                         GOAL_METRICS, get_snapshots)
from ctc_payoff import payoff_plan, extra_payment_impact
from ctc_entities import (add_entity, list_entities, add_vendor, record_payment, list_vendors,
                          business_credit_readiness, ENTITY_TYPES, BUREAUS)
from ctc_pdf import import_pdf_statement, pdftotext_available
from ctc_report import write_audit_report
from ctc_access import (generate_access_list, render_text as access_text, CATEGORIES,
                        DISCLAIMER as ACCESS_DISC, personalize, context_from_db, render_personalized)
from ctc_advisor import advise

DB_FILE = "coretrust_system.db"
LINE = "=" * 72


def banner() -> None:
    print(LINE)
    print("        CORETRUST SYSTEM (CTC) -- Personal Financial Tracker")
    print("        Canada / Ontario (GTA)  |  Local & private  |  2026")
    print(LINE)
    print("Educational personal-finance tool. Not legal, tax, or investment advice.")
    print("Enter only YOUR own real, verified figures.\n")


def _f(prompt: str, default: float = 0.0) -> float:
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        return float(raw.replace("$", "").replace(",", "").replace("%", ""))
    except ValueError:
        print("  (not a number, using default)")
        return default


def _i(prompt: str, default: int = 0) -> int:
    return int(_f(prompt, default))


def _yn(prompt: str, default: bool = False) -> bool:
    raw = input(prompt).strip().lower()
    if not raw:
        return default
    return raw.startswith("y") or raw in ("1", "true")


def _s(prompt: str, default: str = "") -> str:
    return input(prompt).strip() or default


# ---------------------------------------------------------------------------
# Context for the lender engine
# ---------------------------------------------------------------------------
def _lender_context(db: CTCDatabase) -> dict:
    m = db.get_aggregate_metrics()
    p = db.get_user_profile()
    entries = db.get_credit_report_entries()
    gross_monthly = m["gross_monthly_income"]
    housing = p.monthly_housing_cost
    monthly_debt = m["monthly_debt_obligations"]
    gds = round(housing / gross_monthly * 100, 1) if gross_monthly > 0 else None
    tds = round((housing + monthly_debt) / gross_monthly * 100, 1) if gross_monthly > 0 else None
    open_collections = sum(1 for e in entries if e.entry_type == "collection")
    return {
        "best_score": p.best_score(),
        "utilization_pct": m["aggregate_utilization_pct"],
        "dti_pct": m["estimated_dti_pct"],
        "gds_pct": gds,
        "tds_pct": tds,
        "open_collections": open_collections,
        "has_business_account": bool(db.get_business_accounts()) or p.business_bank_months > 0,
        "business_bank_months": p.business_bank_months,
        "time_in_business_years": p.time_in_business_years,
        "revenue_documented_monthly": p.business_revenue_monthly,
    }


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def show_profile(db: CTCDatabase) -> None:
    m = db.get_aggregate_metrics()
    ports = {p.portfolio_type: p for p in db.get_portfolios()}
    print("\n" + "-" * 60 + "\n  FINANCIAL PROFILE\n" + "-" * 60)
    print(f"  Total card balance     : ${m['total_card_balance']:,.2f}")
    print(f"  Total card limit       : ${m['total_card_limit']:,.2f}")
    print(f"  Aggregate utilization  : {m['aggregate_utilization_pct']}%")
    if m["estimated_dti_pct"] is None:
        print("  Debt-to-income (DTI)   : n/a (add an income source)")
    else:
        tag = " (uses estimated card minimums)" if m["dti_uses_estimated_minimums"] else ""
        print(f"  Gross monthly income   : ${m['gross_monthly_income']:,.2f}")
        print(f"  Monthly debt payments  : ${m['monthly_debt_obligations']:,.2f}{tag}")
        print(f"  Estimated DTI          : {m['estimated_dti_pct']}%")
    print("\n  Registered accounts (confirm YOUR room in CRA MyAccount):")
    for kind, cap in CRA_2026_LIMITS.items():
        p = ports.get(kind)
        if p:
            print(f"    {kind:5s}: room ${p.contribution_limit:,.0f} | contributed "
                  f"${p.contributed_ytd:,.0f} | remaining ${p.remaining_room():,.0f} | "
                  f"value ${p.market_value:,.0f}")
        else:
            print(f"    {kind:5s}: 2026 reference limit ${cap:,.0f} (not tracked yet)")
    print("-" * 60)


def show_dashboard(db: CTCDatabase) -> None:
    nw = db.net_worth()
    sc = compute_scorecard(db)
    print("\n" + "-" * 60 + "\n  FINANCIAL HEALTH DASHBOARD\n" + "-" * 60)
    print(f"  COMPOSITE SCORE : {sc['composite_score']}/100  (grade {sc['grade']})")
    print(f"  Net worth       : ${nw['net_worth']:,.2f}")
    print(f"    Assets        : ${nw['assets']['total']:,.2f} "
          f"(liquid ${nw['liquid_assets']:,.2f})")
    print(f"    Liabilities   : ${nw['liabilities']['total']:,.2f}")
    print("\n  Component scores (0-100):")
    for k, v in sc["components"].items():
        print(f"    {k:12s}: {v:5.1f}   (weight {int(sc['weights'][k]*100)}%)")
    print("\n  Signals:")
    print(f"    Utilization       : {sc['utilization_pct']}%")
    print(f"    DTI               : {sc['dti_pct']}%")
    print(f"    Avg savings rate  : {sc['avg_savings_rate_pct']}%")
    print(f"    Emergency months  : {sc['emergency_fund_months']}")
    print("\n  " + sc["note"])
    print("-" * 60)


def show_plays(db: CTCDatabase) -> None:
    plays = generate_plays(db)
    print("\n" + "-" * 60 + "\n  OPPORTUNITY PLAYS (from your data)\n" + "-" * 60)
    if not plays:
        print("  No plays surfaced yet -- add more of your data (cards, savings,")
        print("  registered room, assets, profile) to unlock recommendations.")
        print("-" * 60)
        return
    for p in plays:
        print(f"\n  [{p['priority']}] {p['title']}")
        print(f"      Why    : {p['why']}")
        print(f"      Benefit: {p['estimated_benefit']}")
        print(f"      Do     : {p['action']}")
    print("\n  Educational only -- not investment/tax advice. Verify with a licensed pro.")
    print("-" * 60)


def run_lender_readiness(db: CTCDatabase) -> None:
    ctx = _lender_context(db)
    print("\n  PRODUCTS:")
    for k, v in PRODUCTS.items():
        print(f"    {k:14s} - {v}")
    product = _s("  Which product? ").lower()
    if product not in PRODUCTS:
        print("  Unknown product.")
        return
    if ctx["best_score"] <= 0:
        print("  Note: no credit score set. Add it via menu 13 -> i for accurate results.")
    r = assess(product, ctx)
    print("\n" + "-" * 60)
    print(f"  APPROVAL READINESS -- {r['product_name']}")
    print("-" * 60)
    print(f"  Readiness: {r['readiness_pct']}%  ({r['criteria_met']}/{r['criteria_total']} criteria)  "
          f"-> {r['verdict']}")
    for c in r["criteria"]:
        mark = "PASS" if c["met"] is True else ("n/a " if c["met"] is None else "GAP ")
        print(f"\n  [{mark}] {c['criterion']}: {c['actual']}  (target {c['target']})")
        if c["met"] is not True:
            print(f"        Fix: {c['fix']}")
    print("\n  " + r["note"])
    # Offer the income lever.
    if _s("\n  Estimate income needed to hit a target DTI? (y/n): ").lower().startswith("y"):
        target = _f("    Target DTI % (e.g. 40): ", 40.0)
        m = db.get_aggregate_metrics()
        req = required_income_for_dti(m["monthly_debt_obligations"], target)
        print(f"    Required gross income: ${req['required_gross_monthly_income']:,.2f}/mo "
              f"(${req['required_gross_annual_income']:,.2f}/yr)")
        print(f"    {req['note']}")
    print("-" * 60)


def show_cash_flow(db: CTCDatabase) -> None:
    accts = db.get_business_accounts()
    if not accts:
        print("\n  No business accounts with transactions tracked yet.")
        return
    print("\n" + "-" * 60 + "\n  CASH-FLOW SUMMARY (your real activity)\n" + "-" * 60)
    for a in accts:
        cf = db.cash_flow_summary(a.transaction_history)
        print(f"\n  {a.institution} {a.account_type} -- balance ${a.balance:,.2f}")
        print(f"    Transactions {cf['transaction_count']} | in ${cf['total_inflow']:,.2f} | "
              f"out ${cf['total_outflow']:,.2f} | net ${cf['net_flow']:,.2f}")
        sr = cf["savings_rate_pct"]
        print(f"    Savings rate : {sr}%" if sr is not None else "    Savings rate : n/a")
    print("\n  Personal cash-flow view -- not a bank risk score.")
    print("-" * 60)


def check_cli_readiness(db: CTCDatabase) -> None:
    cards = db.get_credit_cards()
    if not cards:
        print("\n  No credit cards tracked yet.")
        return
    has_income = bool(db.get_income_sources())
    print("\n" + "-" * 60 + "\n  CREDIT-LIMIT-INCREASE READINESS\n" + "-" * 60)
    for c in cards:
        r = credit_limit_increase_readiness(
            c.id, c.institution, c.limit_amt, c.current_balance,
            c.utilization_history, c.last_limit_increase, has_income)
        print(f"\n  {r['card_id']} ({r['institution']})")
        print(f"    Utilization {r['current_utilization']*100:.1f}% "
              f"({'healthy' if r['utilization_healthy'] else 'high'}) | "
              f"ready: {'YES' if r['appears_ready_to_request'] else 'not yet'} | "
              f"earliest: {r['next_request_date']}")
        print(f"    {r['suggestion']}")
    print("-" * 60)


def run_period_audit(db: CTCDatabase) -> None:
    entries = db.get_credit_report_entries()
    if not entries:
        print("\n  No credit-report entries tracked. Add them via menu 13 -> f.")
        print("  Valid entry types:", ", ".join(ONTARIO_MAX_PERIODS.keys()))
        return
    print("\n" + "-" * 60 + "\n  ONTARIO REPORTING-PERIOD AUDIT\n" + "-" * 60)
    flagged = 0
    for r in audit_reporting_periods(entries):
        mark = "!! DISPUTABLE (outdated)" if r.get("disputable_as_outdated") else "ok"
        flagged += 1 if r.get("disputable_as_outdated") else 0
        print(f"\n  [{mark}] {r['creditor']} ({r['entry_type']})\n        {r['note']}")
    print(f"\n  {flagged} flagged as potentially outdated. Verify dates on your report first.")
    print("-" * 60)


def draft_letter(db: CTCDatabase) -> None:
    print("\n  LETTER TYPES:", ", ".join(LETTER_TYPES))
    lt = _s("  Letter type: ").lower()
    if lt not in LETTER_TYPES:
        print("  Unknown letter type.")
        return
    name = _s("  Your full name: ")
    address = _s("  Your mailing address: ")
    if lt == "goodwill":
        recipient = _s("  Creditor name (recipient): "); creditor = recipient
    elif lt == "debt_validation":
        recipient = _s("  Collector name (recipient): ")
        creditor = _s("  Original creditor name: ")
    else:
        recipient = _s("  Bureau (Equifax Canada / TransUnion Canada): ")
        creditor = _s("  Creditor on the disputed entry: ")
    account = _s("  Account number (as shown): ")
    file_no = _s("  Credit file / reference no. (optional): ")
    print("\n  Describe the REAL issue in your own words (required).")
    basis = _s("  Factual basis: ")
    docs_raw = _s("  Enclosed documents, comma-separated (optional): ")
    docs = [d.strip() for d in docs_raw.split(",") if d.strip()] if docs_raw else None
    try:
        letter = generate_dispute_letter(lt, name, address, recipient, creditor,
                                         account, basis, file_no, docs)
    except ValueError as ex:
        print(f"\n  Cannot draft letter: {ex}")
        return
    log_event(db, "dispute_letter_generated", f"{lt} — {creditor}")
    if _s("  Track this as a dispute case with a 30-day clock? (y/n): ").lower().startswith("y"):
        bureau = recipient if lt not in ("goodwill", "debt_validation") else _s("  Bureau: ")
        cid = create_dispute_case(db, creditor, bureau, lt)
        print(f"  opened dispute case #{cid} (response due in 30 days).")
    print("\n" + "=" * 60 + "\n" + letter)
    save = _s("  Save to a .txt file? (path or blank): ")
    if save:
        with open(save, "w", encoding="utf-8") as fh:
            fh.write(letter)
        print(f"  Saved to {save}")


def show_tied_selling(db: CTCDatabase) -> None:
    rep = _s("  Bank rep's name (optional): ")
    product = _s("  Product being pushed (e.g. creditor insurance, mutual fund): ")
    loan = _s("  Credit product you actually want (e.g. line of credit): ")
    print("\n" + tied_selling_refusal_script(rep, product, loan))


def show_rate_script(db: CTCDatabase) -> None:
    lender = _s("  Lender: ")
    rate = _f("  Your current rate/APR (e.g. 19.99): ")
    have = _s("  Real competing offer? (y/n): ").lower().startswith("y")
    comp_rate, comp_src = (None, "")
    if have:
        comp_rate = _f("  Competing rate: ")
        comp_src = _s("  Competing lender: ")
    print("\n" + rate_negotiation_script(lender, rate, comp_rate, comp_src))


def run_tax(db: CTCDatabase) -> None:
    m = db.get_aggregate_metrics()
    ports = {p.portfolio_type: p for p in db.get_portfolios()}
    default_income = round(m["gross_monthly_income"] * 12, 2)
    print("\n  TAX PLANNING (educational estimates)")
    print("   a. Income-tax snapshot")
    print("   b. RRSP contribution benefit")
    print("   c. Registered-account guide")
    print("   d. Explain a concept")
    pick = _s("  Choose: ").lower()
    if pick == "a":
        inc = _f(f"  Taxable income (blank = ${default_income:,.0f}): ", default_income)
        s = income_tax_snapshot(inc)
        print(f"\n  Income        : ${s['taxable_income']:,.2f}")
        print(f"  Est. tax      : ${s['estimated_income_tax']:,.2f}")
        print(f"  Avg rate      : {s['average_rate_pct']}%   Marginal: {s['marginal_rate_pct']}%")
        print(f"  After-tax     : ${s['after_tax_income']:,.2f}")
        print(f"  {s['note']}")
    elif pick == "b":
        inc = _f(f"  Taxable income (blank = ${default_income:,.0f}): ", default_income)
        contrib = _f("  RRSP contribution: ")
        b = rrsp_contribution_benefit(inc, contrib)
        print(f"\n  Contribution  : ${b['contribution']:,.2f}")
        print(f"  Est. tax cut  : ${b['estimated_tax_reduction']:,.2f} "
              f"(~{b['effective_refund_rate_pct']}%)")
        print(f"  {b['note']}")
    elif pick == "c":
        g = registered_account_guide(
            ports["TFSA"].remaining_room() if "TFSA" in ports else CRA_2026_LIMITS["TFSA"],
            ports["RRSP"].remaining_room() if "RRSP" in ports else 0.0,
            ports["FHSA"].remaining_room() if "FHSA" in ports else CRA_2026_LIMITS["FHSA"],
            default_income)
        print()
        for t in g["tips"]:
            print("  - " + t)
        print(f"\n  {g['note']}")
    elif pick == "d":
        print("  Concepts:", ", ".join(CONCEPTS))
        key = _s("  Concept: ")
        print("\n  " + explain_concept(key))
    else:
        print("  Unknown option.")


def run_payroll(db: CTCDatabase) -> None:
    print("\n  OWNER PAYROLL PLANNER (educational estimates)")
    print("   a. Net take-home from a gross salary")
    print("   b. Gross salary needed for a target net")
    pick = _s("  Choose: ").lower()
    exempt = _s("  EI-exempt owner (usually yes if you control the corp)? (y/n): ").lower()
    exempt = not exempt.startswith("n")
    if pick == "a":
        gross = _f("  Annual gross salary: ")
        r = net_from_gross(gross, exempt)
    elif pick == "b":
        target = _f("  Target annual net (take-home): ")
        r = gross_for_target_net(target, exempt)
        print(f"\n  To net ${r.get('target_annual_net', target):,.2f}, pay yourself about "
              f"${r['annual_gross']:,.2f} gross.")
    else:
        print("  Unknown option.")
        return
    print(f"\n  Gross salary       : ${r['annual_gross']:,.2f}")
    print(f"  CPP (cpp1+cpp2)    : ${r['cpp']:,.2f}  ({r['cpp_breakdown']})")
    print(f"  EI                 : ${r['ei']:,.2f}")
    print(f"  Income tax         : ${r['income_tax']:,.2f}")
    print(f"  ANNUAL NET         : ${r['annual_net']:,.2f}  (${r['monthly_net']:,.2f}/mo)")
    print(f"  Total cost to corp : ${r['total_cost_to_corp']:,.2f} "
          f"(+employer CPP ${r['employer_cpp']:,.2f}, EI ${r['employer_ei']:,.2f})")
    print(f"  {r['note']}")


def import_csv_menu(db: CTCDatabase) -> None:
    print("\n  IMPORT FROM CSV / PDF (bank/card exports)")
    print("   t. Transactions CSV (into a business account)")
    print("   c. Credit cards spreadsheet")
    print("   a. Personal accounts spreadsheet")
    print(f"   p. PDF statement (best effort{' — pdftotext ready' if pdftotext_available() else ' — pdftotext MISSING'})")
    pick = _s("  Choose: ").lower()
    path = _s("  File path: ")
    if not os.path.exists(path):
        print("  file not found."); return
    try:
        if pick == "p":
            inst = _s("  Institution: ")
            atype = _s("  Account type: ", "Business Operating")
            r = import_pdf_statement(db, path, inst, atype)
            print(f"  imported {r['imported']} transactions (review these samples):")
            for s in r["sample"]:
                print(f"    {s['date']}  {s['type']:6s} ${s['amount']:>10,.2f}  {s['description']}")
            print(f"  {r['note']}")
        elif pick == "t":
            inst = _s("  Institution (e.g. EQ Bank): ")
            atype = _s("  Account type (e.g. Business Operating): ", "Business Operating")
            dp = _s("  Are debits POSITIVE numbers in this file? (y/n): ").lower().startswith("y")
            n = import_transactions_csv(db, path, inst, atype, debit_positive=dp)
            print(f"  imported {n} transactions into {inst} {atype}.")
        elif pick == "c":
            print(f"  imported {import_cards_csv(db, path)} cards.")
        elif pick == "a":
            print(f"  imported {import_accounts_csv(db, path)} personal accounts.")
        else:
            print("  unknown option.")
    except Exception as ex:  # noqa: BLE001 -- surface parse errors plainly
        print(f"  import failed: {ex}")


def show_product_match(db: CTCDatabase) -> None:
    print("\n  PRODUCT MATCH -- what you're readiest for")
    print("   Filters: country CA/US (blank=both), segment personal/business (blank=both)")
    country = _s("  Country (CA/US/blank): ").upper() or None
    segment = _s("  Segment (personal/business/blank): ").lower() or None
    if country not in (None, "CA", "US"):
        country = None
    if segment not in (None, "personal", "business"):
        segment = None
    results = match_products(db, country, segment)
    if not results:
        print("  No products for that filter."); return
    show_all = _s(f"  Show all {len(results)}? (y = all, blank = top 10): ").lower().startswith("y")
    shown = results if show_all else results[:10]
    print("\n" + "-" * 64)
    print("  READIEST -> LEAST READY")
    print("-" * 64)
    for r in shown:
        flag = f"{r['country']}/{r['segment'][:4]}"
        print(f"\n  [{r['readiness_pct']:5.1f}%] {r['name']}  ({flag}, {r['category']})")
        print(f"      Verdict : {r['verdict']}")
        if r["providers"]:
            print(f"      Who     : {', '.join(r['providers'])}")
        if r["gaps"]:
            g = r["gaps"][0]
            print(f"      Next    : {g['criterion']} -> {g['fix']}")
            if len(r["gaps"]) > 1:
                print(f"                (+{len(r['gaps'])-1} more gap(s))")
        if r["risk"]:
            print(f"      RISK    : {r['risk']}")
    print("\n  " + summary_note())
    print("-" * 64)


def show_roadmap(db: CTCDatabase) -> None:
    print("\n" + roadmap_text(build_roadmap(db)))


def gen_dashboard(db: CTCDatabase) -> None:
    path = _s("  Output file (blank=dashboard.html): ", "dashboard.html")
    p = write_dashboard(db, path)
    ap = os.path.abspath(p)
    print(f"\n  Visual dashboard written to: {ap}")
    print(f"  Open it in a browser (double-click, or:  open '{ap}' ).")
    print("  It's a single self-contained file — works on laptop and mobile, online or offline.")


def launch_live_dashboard(db: CTCDatabase) -> None:
    print("\n  LIVE EDITABLE DASHBOARD")
    print("   1. Launch local server (edit in browser, SAVE writes back here)")
    print("   2. Just write the editable HTML file (SAVE downloads a JSON to import)")
    pick = _s("  Choose: ")
    if pick == "2":
        p = write_live_dashboard(db, _s("  Output file (blank=dashboard_live.html): ", "dashboard_live.html"))
        print(f"\n  Editable dashboard written to: {os.path.abspath(p)}")
        print("  Open it, edit, then EXPORT JSON and import via menu 13 -> g.")
        return
    port = _i("  Port (blank=8799): ", 8799)
    serve_live(db, port)   # blocks until Ctrl+C


def history_menu(db: CTCDatabase) -> None:
    print("\n  HISTORY, GOALS & DEADLINES")
    print("   a. Take a snapshot now       d. List goals & progress")
    print("   b. View trends               e. Deadline radar")
    print("   c. Add a goal")
    pick = _s("  Choose: ").lower()
    if pick == "a":
        r = take_snapshot(db)
        print(f"   snapshot saved: score {r['composite_score']}, net worth ${r['net_worth']:,.0f}, "
              f"util {r['utilization']}%")
    elif pick == "b":
        n = len(get_snapshots(db))
        if n < 2:
            print(f"   Only {n} snapshot(s). Take a few over time to see a trend.")
            return
        for metric in ("composite_score", "net_worth", "utilization", "dti"):
            t = trend(db, metric)
            print(f"   {metric:16s} {t['spark']}  {t['first']} -> {t['last']} (Δ {t['change']:+})")
    elif pick == "c":
        print("   metrics:", ", ".join(GOAL_METRICS))
        metric = _s("   Metric: ")
        if metric not in GOAL_METRICS:
            print("   unknown metric."); return
        name = _s("   Goal name: ")
        target = _f("   Target value: ")
        deadline = _s("   Deadline (YYYY-MM-DD, optional): ")
        add_goal(db, name, metric, target, deadline)
        log_event(db, "goal_added", f"{name} {metric}={target}")
        print("   goal added.")
    elif pick == "d":
        goals = list_goals(db)
        if not goals:
            print("   No goals yet."); return
        for g in goals:
            mark = "✓" if g["reached"] else f"{g['progress_pct']}%"
            print(f"   [{mark}] {g['name']}: {round(g['current'],1)} / {g['target']} "
                  f"({g['metric']}, {g['direction']}) | projected {g['projected_date']}")
    elif pick == "e":
        rad = deadline_radar(db)
        if not rad:
            print("   Nothing due in the window.")
            return
        for d in rad:
            tag = "OVERDUE" if d["overdue"] else f"in {d['days']}d"
            print(f"   {d['date']}  [{tag}]  {d['label']}")


def payoff_menu(db: CTCDatabase) -> None:
    print("\n  DEBT PAYOFF PLANNER")
    print("   a. Full payoff plan (avalanche / snowball)")
    print("   b. Extra-payment impact on one debt")
    pick = _s("  Choose: ").lower()
    if pick == "a":
        method = _s("   Method (avalanche/snowball): ", "avalanche").lower()
        budget = _f("   Total monthly budget for all debts: $")
        r = payoff_plan(db, budget, method)
        if r.get("note") and not r.get("order"):
            print("   " + r["note"]); return
        print(f"\n   Method: {r['method']} | budget ${r['monthly_budget']:,.0f} "
              f"(min ${r['total_min_payment']:,.0f})")
        for d in r["order"]:
            est = " (est. rate)" if d["estimated_rate"] else ""
            pm = f"paid off ~month {d['payoff_month']}" if d["payoff_month"] else "not paid in window"
            print(f"     {d['name']}: ${d['balance']:,.0f} @ {d['rate']:.2f}%{est} -> {pm}")
        print(f"   DEBT-FREE in ~{r['months_to_debt_free']} months ({r['years_to_debt_free']} yrs), "
              f"total interest ~${r['total_interest']:,.0f}")
        print(f"   {r['note']}")
    elif pick == "b":
        bal = _f("   Balance: $")
        rate = _f("   Annual rate %: ")
        pay = _f("   Current monthly payment: $")
        extra = _f("   Extra per month: $")
        r = extra_payment_impact(bal, rate, pay, extra)
        b, w = r["base"], r["with_extra"]
        if not b.get("payoff"):
            print("   " + b.get("note", "payment too small.")); return
        print(f"\n   Base: {b['months']} months, interest ${b['total_interest']:,.0f}")
        print(f"   +${extra:,.0f}/mo: {w['months']} months, interest ${w['total_interest']:,.0f}")
        if "months_saved" in r:
            print(f"   -> saves {r['months_saved']} months and ~${r['interest_saved']:,.0f} interest.")


def dispute_case_menu(db: CTCDatabase) -> None:
    print("\n  DISPUTE CASE TRACKER (30-day clock + escalation ladder)")
    print("   a. Open a new case          c. Update / escalate a case")
    print("   b. List cases")
    pick = _s("  Choose: ").lower()
    if pick == "a":
        cid = create_dispute_case(db, _s("   Creditor: "), _s("   Bureau (Equifax/TransUnion): "),
                                  _s("   Dispute type: "), notes=_s("   Notes (optional): "))
        print(f"   case #{cid} opened; response due in 30 days.")
    elif pick == "b":
        cases = list_dispute_cases(db)
        if not cases:
            print("   No cases."); return
        for c in cases:
            tag = "OVERDUE" if c["overdue"] else (f"{c['days_remaining']}d left" if c["status"] == "open" else c["status"])
            print(f"   #{c['id']} {c['creditor']} via {c['bureau']} [{tag}] | stage: {c['current_step']}")
            if c["status"] == "open" and c["next_step"] != "—":
                print(f"        next if unresolved: {c['next_step']}")
    elif pick == "c":
        cid = _i("   Case #: ")
        st = _s("   New status (open/resolved/escalated, blank=keep): ")
        esc = _s("   Escalate one stage? (y/n): ").lower().startswith("y")
        try:
            update_dispute_case(db, cid, status=st or None, escalate=esc, notes=None)
            print("   updated.")
        except ValueError as ex:
            print(f"   {ex}")


def compliance_menu(db: CTCDatabase) -> None:
    print("\n  COMPLIANCE CENTER")
    print("   a. Record consent           d. Encrypted backup (AES-256)")
    print("   b. View audit log           e. Restore an encrypted backup")
    print("   c. Statute & rate currency")
    pick = _s("  Choose: ").lower()
    if pick == "a":
        obtained = _s("   Consent obtained? (y/n): ").lower().startswith("y")
        method = _s("   Method (e.g. signed form, verbal, in-app): ")
        set_consent(db, obtained, method)
        print("   consent recorded.")
    elif pick == "b":
        for e in get_audit_log(db, 40):
            print(f"   {e['ts']}  {e['action']:22s} {e['detail']}")
    elif pick == "c":
        for s in statute_currency():
            flag = "STALE" if s["stale"] else "ok"
            print(f"   [{flag}] {s['item']} — verified {s['last_verified']} ({s['source']})")
    elif pick == "d":
        pw = _s("   Passphrase (KEEP IT SAFE — not recoverable): ")
        if not pw:
            print("   passphrase required."); return
        try:
            out = encrypt_backup(db, pw)
            print(f"   encrypted backup written: {os.path.abspath(out)}")
        except Exception as ex:  # noqa: BLE001
            print(f"   backup failed: {ex}")
    elif pick == "e":
        enc = _s("   Path to .enc file: ")
        pw = _s("   Passphrase: ")
        try:
            out = decrypt_backup(enc, pw)
            print(f"   decrypted to: {os.path.abspath(out)}")
        except Exception as ex:  # noqa: BLE001
            print(f"   restore failed (wrong passphrase?): {ex}")


def entities_menu(db: CTCDatabase) -> None:
    print("\n  BUSINESS & ENTITIES")
    print("   a. Add entity               d. Record a vendor payment")
    print("   b. List entities            e. Business-credit readiness")
    print("   c. Add business-credit vendor")
    pick = _s("  Choose: ").lower()
    if pick == "a":
        print("   types:", ", ".join(ENTITY_TYPES))
        add_entity(db, _s("   Name: "), _s("   Type: "), _s("   Jurisdiction: "), _s("   Notes: "))
        print("   entity added.")
    elif pick == "b":
        for e in list_entities(db):
            print(f"   #{e['id']} {e['name']} [{e['entity_type']}] {e['jurisdiction'] or ''}")
        if not list_entities(db):
            print("   No entities yet.")
    elif pick == "c":
        print("   bureaus:", ", ".join(BUREAUS))
        add_vendor(db, _s("   Vendor: "), _i("   Net terms (30/60): ", 30),
                   _s("   Reports to (bureau): "), entity=_s("   Entity (optional): "),
                   balance=_f("   Current balance: $"))
        print("   vendor added.")
    elif pick == "d":
        vid = _i("   Vendor #: ")
        on_time = _s("   Paid on time / early? (y/n): ").lower().startswith("y")
        record_payment(db, vid, on_time)
        print("   payment recorded.")
    elif pick == "e":
        r = business_credit_readiness(db)
        print(f"   Vendors: {r['total_vendors']} | reporting: {r['reporting_vendors']} | "
              f"on-time reporting: {r['on_time_reporting']}")
        print(f"   PAYDEX-ready: {'YES' if r['paydex_ready'] else 'not yet'}")
        for g in r["gaps"]:
            print(f"     - {g}")


def access_menu(db: CTCDatabase) -> None:
    print("\n  ACCESS LIST GENERATOR — banks, credit unions, loans, cross-border, programs")
    country = _s("  Country (CA/US/blank=both): ").upper() or None
    segment = _s("  Segment (personal/business/blank=both): ").lower() or None
    bf = _s("  Only Black-focused programs/institutions? (y/n/blank=all): ").lower()
    black = True if bf.startswith("y") else (False if bf.startswith("n") else None)
    if country not in (None, "CA", "US"):
        country = None
    if segment not in (None, "personal", "business"):
        segment = None
    items = generate_access_list(country=country, segment=segment, black_focus=black)
    if _s("  Rank by MY eligibility (readiest first)? (y/n): ").lower().startswith("y"):
        ranked = personalize(items, context_from_db(db))
        print(f"\n  {len(ranked)} option(s), ranked by your fit:")
        print(render_personalized(ranked))
    else:
        print(f"\n  {len(items)} option(s):")
        print(access_text(items))
    print("\n  " + ACCESS_DISC)


def export_audit_report(db: CTCDatabase) -> None:
    path = _s("  Output file (blank=audit_report.html): ", "audit_report.html")
    p = write_audit_report(db, path)
    log_event(db, "audit_report_generated", os.path.basename(p))
    print(f"\n  Audit report written to: {os.path.abspath(p)}")
    print("  Open it and print to PDF (Cmd/Ctrl+P -> Save as PDF).")


def show_reference(db: CTCDatabase) -> None:
    print("\n  REFERENCE: Canada + US banks/CUs, bureaus, codes")
    print("   1. Product categories        5. Credit bureaus (personal & business)")
    print("   2. Canadian banks            6. Statutes / consumer & financial codes")
    print("   3. Canadian credit unions    7. IDs a Canadian needs (SIN/BN/DUNS/ITIN/EIN)")
    print("   4. US banks & credit unions  8. Canada -> US credit playbook")
    print("   9. Everything (full dump)")
    keys = {"1": "categories", "2": "canada_banks", "3": "canada_credit_unions",
            "4": "us", "5": "bureaus", "6": "statutes", "7": "ids", "8": "crossborder"}
    pick = _s("  Choose: ")
    if pick == "9":
        print("\n" + full_reference())
    elif pick in keys:
        print("\n" + SECTIONS[keys[pick]]())
    else:
        print("  unknown option.")


def add_data_menu(db: CTCDatabase) -> None:
    while True:
        print("\n  ADD / UPDATE DATA")
        print("   a. Credit card              e. Personal bank account")
        print("   b. Installment debt         f. Credit-report entry")
        print("   c. Income source            g. Import from JSON")
        print("   d. Registered account       h. Asset (incl. crypto/IP)")
        print("   i. My profile (scores, housing, business)")
        print("   j. Import from CSV (bank/card exports)")
        print("   x. Back")
        pick = _s("  Choose: ").lower()
        if pick == "a":
            db.sync_credit_card(CreditCard(
                id=_s("   Card id/label: "), institution=_s("   Institution: "),
                secured=_s("   Secured? (y/n): ").lower().startswith("y"),
                limit_amt=_f("   Credit limit: $"), current_balance=_f("   Current balance: $"),
                statement_date=_s("   Statement date (YYYY-MM-DD): "), utilization_history=[],
                last_limit_increase=_s("   Last limit increase (YYYY-MM-DD, blank if none): "),
                min_payment=_f("   Min payment (blank=estimate): $"),
                apr=_f("   APR as decimal e.g. 0.1999 (blank=estimate): ")))
            print("   saved.")
        elif pick == "b":
            db.sync_installment_debt(InstallmentDebt(
                id=_s("   Debt id/label: "), lender=_s("   Lender: "),
                debt_type=_s("   Type (Auto/Student/Personal/LOC): "), balance=_f("   Balance: $"),
                monthly_payment=_f("   Monthly payment: $"), interest_rate=_f("   Rate % (optional): ")))
            print("   saved.")
        elif pick == "c":
            db.sync_income(IncomeSource(
                source=_s("   Source (e.g. TD Payroll T4): "), gross_monthly=_f("   Gross monthly: $"),
                net_monthly=_f("   Net monthly: $"), next_pay_date=_s("   Next pay date (optional): ")))
            print("   saved.")
        elif pick == "d":
            kind = _s("   Type (TFSA/RRSP/FHSA): ").upper()
            db.sync_portfolio(RegisteredPortfolio(
                portfolio_type=kind, contribution_limit=_f(f"   Your {kind} room (CRA MyAccount): $"),
                contributed_ytd=_f("   Contributed this year: $"),
                last_contribution=_s("   Last contribution date (optional): "),
                market_value=_f("   Current market value (optional): $")))
            print("   saved.")
        elif pick == "e":
            db.sync_personal_account(PersonalAccount(
                id=_s("   Account id/label: "), institution=_s("   Institution: "),
                account_type=_s("   Type (Chequing/Savings): "), balance=_f("   Balance: $"),
                liquid=not _s("   Locked/illiquid (e.g. GIC)? (y/n): ").lower().startswith("y")))
            print("   saved.")
        elif pick == "f":
            print("   Valid entry types:", ", ".join(ONTARIO_MAX_PERIODS.keys()))
            db.sync_credit_report_entry(CreditReportEntry(
                id=_s("   Entry id/label: "), bureau=_s("   Bureau (Equifax/TransUnion): "),
                creditor=_s("   Creditor: "), entry_type=_s("   Entry type: "),
                status=_s("   Status: "), reported_balance=_f("   Reported balance: $"),
                date_of_last_activity=_s("   Date of last activity (YYYY-MM-DD): ")))
            print("   saved.")
        elif pick == "g":
            path = _s("   JSON file path: ")
            if not os.path.exists(path):
                print("   file not found."); continue
            try:
                counts = db.import_from_json(path)
                print("   imported:", ", ".join(f"{k}={v}" for k, v in counts.items()))
            except Exception as ex:  # noqa: BLE001
                print(f"   import failed: {ex}")
        elif pick == "h":
            db.sync_asset(Asset(
                id=_s("   Asset id/label: "), name=_s("   Name: "),
                category=_s("   Category (Real Estate/Vehicle/Equipment/Crypto/IP/Other): "),
                market_value=_f("   Market value: $"),
                associated_debt=_f("   Debt secured by this asset (e.g. mortgage): $"),
                liquid=_s("   Easily sellable / liquid? (y/n): ").lower().startswith("y")))
            print("   saved.")
        elif pick == "i":
            p = db.get_user_profile()
            db.sync_user_profile(UserProfile(
                equifax_score=_i(f"   Equifax score (blank={p.equifax_score}): ", p.equifax_score),
                transunion_score=_i(f"   TransUnion score (blank={p.transunion_score}): ", p.transunion_score),
                monthly_housing_cost=_f(f"   Monthly housing cost (blank=${p.monthly_housing_cost:,.0f}): $",
                                        p.monthly_housing_cost),
                time_in_business_years=_f(f"   Years in business (blank={p.time_in_business_years}): ",
                                          p.time_in_business_years),
                business_revenue_monthly=_f(f"   Business monthly revenue (blank=${p.business_revenue_monthly:,.0f}): $",
                                            p.business_revenue_monthly),
                business_bank_months=_i(f"   Business account age months (blank={p.business_bank_months}): ",
                                        p.business_bank_months),
                monthly_expenses=_f(f"   Monthly living expenses (blank=${p.monthly_expenses:,.0f}): $",
                                    p.monthly_expenses),
                us_bank_account=_yn(f"   Have a US bank account? (y/n, now={'y' if p.us_bank_account else 'n'}): ",
                                    p.us_bank_account),
                us_tax_id=_yn(f"   Have a US ITIN or SSN? (y/n, now={'y' if p.us_tax_id else 'n'}): ",
                              p.us_tax_id),
                us_address=_yn(f"   Have a US mailing address? (y/n, now={'y' if p.us_address else 'n'}): ",
                               p.us_address)))
            print("   saved.")
        elif pick == "j":
            import_csv_menu(db)
        elif pick == "x":
            return
        else:
            print("   unknown option.")


def main() -> None:
    db = CTCDatabase(DB_FILE)
    banner()
    log_event(db, "session_start", "")
    if not get_consent(db)["consent_obtained"]:
        print("PIPEDA: no consent recorded yet. This tool stores and processes YOUR own")
        print("financial data locally on this machine only.")
        if _s("Record consent to store & process your data? (y/n): ").lower().startswith("y"):
            set_consent(db, True, "in-app CLI")
            print("Consent recorded.\n")
    if not db.get_credit_cards() and not db.get_income_sources():
        print("No data yet. Use option 13 to add figures, or import a JSON file")
        print("(see sample_profile.json).\n")

    actions = {
        "1": show_profile, "2": show_dashboard, "3": show_plays,
        "4": run_lender_readiness, "5": show_cash_flow, "6": check_cli_readiness,
        "7": run_period_audit, "8": draft_letter, "9": show_tied_selling,
        "10": show_rate_script, "11": run_tax, "12": run_payroll, "13": add_data_menu,
        "15": show_reference, "16": show_product_match, "17": show_roadmap,
        "18": gen_dashboard, "19": launch_live_dashboard,
        "20": history_menu, "21": payoff_menu, "22": dispute_case_menu,
        "23": compliance_menu, "24": entities_menu, "25": export_audit_report,
        "26": access_menu, "27": advise,
    }
    while True:
        print("\n--- MENU ---------------------------------------------------")
        print("  1. Financial profile              8. Draft dispute/validation/goodwill letter")
        print("  2. Health dashboard & net worth   9. Tied-selling refusal (Bank Act s.455.1)")
        print("  3. Opportunity plays             10. Interest-rate negotiation script")
        print("  4. Lender approval-readiness     11. Tax planning & estimates")
        print("  5. Cash-flow summary             12. Owner payroll planner")
        print("  6. Credit-limit-increase check   13. Add / update / import my data")
        print("  7. Ontario reporting-period audit 14. Credit optimization playbook")
        print("                                   15. Reference: CA+US banks/bureaus/codes")
        print("                                   16. Product match: what you're readiest for")
        print("                                   17. Funding roadmap (ordered game plan)")
        print("                                   18. Generate visual dashboard (HTML)")
        print("                                   19. Live editable dashboard (edit in browser)")
        print("  --- auditor & compliance ---------------------------------")
        print("  20. History, goals & deadlines   23. Compliance center (consent/audit/backup)")
        print("  21. Debt payoff planner          24. Business & entities")
        print("  22. Dispute case tracker         25. Export written audit report (PDF)")
        print("                                   26. Access list generator (banks/CUs/loans/programs)")
        print("                                   27. AI advisor chat (live agent / offline)")
        print("  0. Exit")
        choice = _s("Select: ")
        if choice == "0":
            print("\nClosing CoreTrust. Your data stays local. Stay compliant.")
            db.close(); return
        if choice == "14":
            print("\n" + credit_optimization_playbook()); continue
        action = actions.get(choice)
        if action:
            action(db)
        else:
            print("Unknown option.")


if __name__ == "__main__":
    main()
