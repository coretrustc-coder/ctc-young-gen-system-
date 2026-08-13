"""
CoreTrust System (CTC) -- Written Audit Report
==============================================
Generates the "written audit summary for the consumer" the CoreTrust CLAUDE.md
calls for: a clean, professional, self-contained HTML document you open and
print to PDF (Cmd/Ctrl+P -> Save as PDF). Document treatment -- light, legible,
tabular -- distinct from the Matrix operations dashboard.
"""

from __future__ import annotations

from datetime import date

from ctc_dashboard import compute_scorecard, generate_plays
from ctc_match import match
from ctc_roadmap import build_roadmap
from ctc_disputes import audit_reporting_periods, DISCLAIMER
from ctc_compliance import list_dispute_cases, get_consent, statute_currency
from ctc_history import list_goals, trend, get_snapshots


def _money(n):
    return "$" + format(round(n or 0), ",")


_STYLE = """
:root{--ink:#14201b;--muted:#5c6b64;--line:#d7e0da;--accent:#0d7a52;--warn:#b4472b;--paper:#fdfdfb}
*{box-sizing:border-box}
body{margin:0;background:#e9ede9;color:var(--ink);
  font-family:'Iowan Old Style',Palatino,Georgia,serif;line-height:1.5}
.page{max-width:820px;margin:24px auto;background:var(--paper);padding:52px 60px;
  box-shadow:0 2px 20px rgba(0,0,0,.08)}
h1{font-size:26px;margin:0;letter-spacing:.5px}
.sub{color:var(--muted);font-size:13px;margin-top:4px}
h2{font-size:15px;text-transform:uppercase;letter-spacing:2px;color:var(--accent);
  border-bottom:1px solid var(--line);padding-bottom:6px;margin:30px 0 12px}
.kpi{display:flex;gap:26px;flex-wrap:wrap;margin:14px 0}
.kpi .b{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:1px}
.kpi .v{font-size:24px;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:13px;font-family:ui-monospace,Menlo,Consolas,monospace}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:1px}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.pill{display:inline-block;font-size:11px;padding:1px 8px;border-radius:20px;border:1px solid var(--line)}
.ok{color:var(--accent);border-color:var(--accent)}
.warn{color:var(--warn);border-color:var(--warn)}
.note,.disc{color:var(--muted);font-size:12px;line-height:1.55}
.disc{border-top:1px solid var(--line);margin-top:34px;padding-top:14px}
ol.steps{padding-left:20px;font-size:13px}ol.steps li{margin:6px 0}
.phase{font-weight:700;margin:14px 0 4px}
@media print{body{background:#fff}.page{box-shadow:none;margin:0;max-width:none;padding:0 8px}h2{page-break-after:avoid}tr{page-break-inside:avoid}}
"""


def _row(cells, numcols=()):
    return "<tr>" + "".join(
        f'<td class="num">{c}</td>' if i in numcols else f"<td>{c}</td>"
        for i, c in enumerate(cells)) + "</tr>"


def build_report_html(db) -> str:
    sc = compute_scorecard(db)
    m = db.get_aggregate_metrics()
    nw = db.net_worth()
    prof = db.get_user_profile()
    consent = get_consent(db)
    plays = generate_plays(db)
    matches = match(db)
    ready = [x for x in matches if x["readiness_pct"] >= 100]
    rm = build_roadmap(db)
    audit = audit_reporting_periods(db.get_credit_report_entries())
    cases = list_dispute_cases(db)
    goals = list_goals(db)
    tr = trend(db, "composite_score")

    consent_pill = ('<span class="pill ok">consent on file</span>' if consent["consent_obtained"]
                    else '<span class="pill warn">no consent recorded</span>')

    h = [f"""<div class="page">
    <h1>CoreTrust &mdash; Personal Financial Audit</h1>
    <div class="sub">Prepared {date.today().strftime('%B %d, %Y')} &middot; Ontario (GTA) &middot; {consent_pill}</div>
    <p class="note">This report summarizes your tracked financial position, credit standing, funding
    readiness, and open compliance items. It is educational and is not legal, tax, or investment advice.</p>

    <h2>Position at a glance</h2>
    <div class="kpi">
      <div><div class="b">Health score</div><div class="v">{sc['composite_score']} ({sc['grade']})</div></div>
      <div><div class="b">Net worth</div><div class="v">{_money(nw['net_worth'])}</div></div>
      <div><div class="b">Best credit score</div><div class="v">{prof.best_score() or '—'}</div></div>
      <div><div class="b">Utilization</div><div class="v">{m['aggregate_utilization_pct']}%</div></div>
      <div><div class="b">DTI</div><div class="v">{m['estimated_dti_pct'] if m['estimated_dti_pct'] is not None else '—'}%</div></div>
    </div>"""]

    # Net worth
    a, l = nw["assets"], nw["liabilities"]
    h.append("<h2>Net worth</h2><table><tr><th>Assets</th><th class='num'>Amount</th>"
             "<th>Liabilities</th><th class='num'>Amount</th></tr>")
    arows = [("Cash accounts", a["cash_accounts"]), ("Business cash", a["business_cash"]),
             ("Registered", a["registered_value"]), ("Other assets", a["other_assets"]),
             ("Total assets", a["total"])]
    lrows = [("Credit cards", l["credit_cards"]), ("Installment", l["installment_debts"]),
             ("Secured on assets", l["secured_on_assets"]), ("", ""), ("Total liabilities", l["total"])]
    for (an, av), (ln, lv) in zip(arows, lrows):
        h.append(f"<tr><td>{an}</td><td class='num'>{_money(av) if an else ''}</td>"
                 f"<td>{ln}</td><td class='num'>{_money(lv) if ln else ''}</td></tr>")
    h.append("</table>")

    # Health components
    h.append("<h2>Health score components</h2><table><tr><th>Component</th><th class='num'>Score</th>"
             "<th class='num'>Weight</th></tr>")
    for k, v in sc["components"].items():
        h.append(_row([k, v, f"{int(sc['weights'][k]*100)}%"], numcols=(1, 2)))
    h.append("</table>")
    if tr["points"] >= 2:
        h.append(f"<p class='note'>Score trend over {tr['points']} snapshots: "
                 f"{tr['spark']} (change {tr['change']:+}).</p>")

    # Plays
    if plays:
        h.append("<h2>Priority opportunities</h2><table><tr><th>#</th><th>Move</th>"
                 "<th>Estimated benefit</th></tr>")
        for p in plays[:8]:
            h.append(_row([p["priority"], p["title"], p["estimated_benefit"]]))
        h.append("</table>")

    # Readiness
    h.append("<h2>Funding readiness (ready now)</h2>")
    if ready:
        h.append("<table><tr><th>Product</th><th>Where</th><th class='num'>Readiness</th></tr>")
        for r in ready[:12]:
            h.append(_row([f"{r['name']} ({r['country']}/{r['segment']})",
                           ", ".join(r["providers"][:3]), f"{r['readiness_pct']}%"], numcols=(2,)))
        h.append("</table>")
    else:
        h.append("<p class='note'>No products at 100% yet &mdash; see the roadmap below.</p>")

    # Roadmap
    h.append("<h2>Funding roadmap</h2>")
    for ph in rm["phases"]:
        h.append(f"<div class='phase'>Phase {ph['n']}: {ph['title']}</div><ol class='steps'>")
        for s in ph["steps"]:
            h.append(f"<li>{s['action']}</li>")
        h.append("</ol>")

    # Reporting-period audit
    h.append("<h2>Ontario reporting-period audit</h2>")
    if audit:
        h.append("<table><tr><th>Creditor</th><th>Type</th><th>Status</th></tr>")
        for a2 in audit:
            pill = ('<span class="pill warn">disputable</span>' if a2.get("disputable_as_outdated")
                    else '<span class="pill ok">within window</span>')
            h.append(_row([a2["creditor"], a2["entry_type"], pill]))
        h.append("</table>")
    else:
        h.append("<p class='note'>No credit-report entries tracked.</p>")

    # Dispute cases
    if cases:
        h.append("<h2>Open dispute cases</h2><table><tr><th>#</th><th>Creditor</th><th>Bureau</th>"
                 "<th>Response due</th><th class='num'>Days</th><th>Stage</th></tr>")
        for c in cases:
            days = f'<span class="pill warn">{c["days_remaining"]}</span>' if c["overdue"] else c["days_remaining"]
            h.append(f"<tr><td>#{c['id']}</td><td>{c['creditor']}</td><td>{c['bureau']}</td>"
                     f"<td>{c['response_due']}</td><td class='num'>{days}</td><td>{c['current_step']}</td></tr>")
        h.append("</table>")

    # Goals
    if goals:
        h.append("<h2>Goals</h2><table><tr><th>Goal</th><th class='num'>Target</th>"
                 "<th class='num'>Current</th><th class='num'>Progress</th><th>Projected</th></tr>")
        for g in goals:
            h.append(f"<tr><td>{g['name']} ({g['metric']})</td><td class='num'>{g['target']}</td>"
                     f"<td class='num'>{round(g['current'],1)}</td><td class='num'>{g['progress_pct']}%</td>"
                     f"<td>{g['projected_date']}</td></tr>")
        h.append("</table>")

    # Statute currency
    h.append("<h2>Statute &amp; rate currency</h2><table><tr><th>Item</th><th>Source</th>"
             "<th>Verified</th></tr>")
    for s in statute_currency():
        pill = ('<span class="pill warn">stale</span>' if s["stale"]
                else '<span class="pill ok">current</span>')
        h.append(_row([s["item"], s["source"], f"{s['last_verified']} {pill}"]))
    h.append("</table>")

    h.append(f"<div class='disc'>{DISCLAIMER}<br><br>"
             "CoreTrust provides credit education, financial-literacy guidance, and dispute-letter "
             "drafting assistance. It is not a law firm and does not provide legal advice. Data is "
             "stored locally; consent status is shown above.</div></div>")
    return "".join(h)


def write_audit_report(db, path: str = "audit_report.html") -> str:
    html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>CoreTrust — Financial Audit Report</title><style>" + _STYLE +
            "</style></head><body>" + build_report_html(db) + "</body></html>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path
