# CoreTrust System (CTC) — Personal Financial Tracker & Young Gen Advisor

[![Live App](https://img.shields.io/badge/Live_App-coretrust--young--gen--advisor.vercel.app-3EC6D0?style=for-the-badge&logo=vercel)](https://coretrust-young-gen-advisor.vercel.app/)
[![Dual AI Engine](https://img.shields.io/badge/AI_Engine-Google_Gemini_%2B_Anthropic_Claude-1D9E75?style=for-the-badge)](https://github.com/coretrustc-coder/ctc-young-gen-system-)
[![License](https://img.shields.io/badge/Compliance-CASL_%7C_PIPEDA_%7C_FCAC-7F77DD?style=for-the-badge)](https://github.com/coretrustc-coder/ctc-young-gen-system-)

## 🌐 Live Web Application & Dashboard Links

- **Production Live App (Vercel)**: [https://coretrust-young-gen-advisor.vercel.app/](https://coretrust-young-gen-advisor.vercel.app/)
- **Local Live Dashboard**: `http://127.0.0.1:8799/` (run `python3 ctc_serve.py`)

A comprehensive financial intelligence engine and advisor for Canadian consumers and youth (18–25). Tracks net worth, credit scores, OSAP grants/loans, funding roadmaps, legal disputes (Ontario Consumer Reporting Act), side hustles, and verified bank/credit union products.

**Personal-finance and consumer-rights education tool. Not legal, tax, or investment advice, not a "credit repair" service, and not a way to game banks or bureaus.** Enter only your own real, verified figures.

## 🚀 Dual-Engine AI Architecture

This repository features a **Hybrid Multi-Model Router**:
1. **Google Antigravity / Gemini 1.5**: Lightning-fast sub-300ms chat streaming, multimodal document/statement OCR, and product discovery.
2. **Anthropic Claude 3.5 Sonnet**: High-precision legal dispute letter synthesis, compliance checking, and deep financial auditing.
3. **Smart Link Engine**: Delivers direct action links & metadata cards for Canadian Banks, Credit Unions, OSAP, and Scholarships.

## Modules


| File | Purpose |
|---|---|
| `ctc_models.py` | Local SQLite store: accounts, cards, debts, income, registered accounts, business cash flow, **assets (incl. crypto/IP)**, credit-report entries, and a profile. Computes utilization, DTI, and **net worth**. |
| `ctc_rates.py` | Editable **2026** tax / CPP / CPP2 / EI assumptions + the tax math engine. |
| `ctc_dashboard.py` | **Composite financial-health score** (0–100) and ordered **opportunity "plays"** built from your data. |
| `ctc_lender.py` | **Approval-readiness engine** — scores you against real underwriting criteria per product and lists the gaps to close. |
| `ctc_tax.py` | Tax **estimates & education** — marginal/average rates, RRSP benefit, registered-account guide, owner concepts. |
| `ctc_payroll.py` | **Owner-operator payroll planner** — gross↔net, deductions, cost to the corp, salary-for-target-net. |
| `ctc_disputes.py` | Ontario reporting-period auditor + dispute/validation/goodwill letters from a genuine issue you describe. |
| `ctc_underwriting.py` | Limit-increase readiness, Bank Act s.455.1 tied-selling refusal, rate-negotiation script, optimization playbook. |
| `ctc_import.py` | **CSV statement importer** — pulls transactions, cards, and accounts from bank/card exports (auto-detects columns). |
| `ctc_reference.py` | **Reference catalog** — Canadian + US banks/credit unions by product, credit bureaus, statutes, and the IDs a Canadian needs. |
| `ctc_match.py` | **Product-match engine** — ranks CA + US, personal + business products (incl. digital assets) by how ready you are, with the gaps to close. |
| `ctc_roadmap.py` | **Funding roadmap** — sequences your matches into an ordered, phased game plan. |
| `ctc_dashboard_web.py` | **Visual dashboard generator** — renders the whole system into a self-contained HTML page (boot sequence, Matrix background, sidebar widgets). |
| `ctc_dashboard_live.py` | **Live editable dashboard** — the compute engine ported to JavaScript so edits recompute in the browser; Export/Save writes back. |
| `ctc_serve.py` | **Local server** — serves the live dashboard and accepts saves back into your database (browser round-trip). |
| `ctc_compliance.py` | **Compliance backbone** — audit log, PIPEDA consent, dispute case management (30-day clock + escalation ladder), statute/rate currency, AES-256 encrypted backups. |
| `ctc_history.py` | **History, goals & deadlines** — snapshots + trend sparklines, goal tracking with projected dates, deadline radar. |
| `ctc_payoff.py` | **Debt payoff planner** — amortization, avalanche/snowball, extra-payment impact. |
| `ctc_entities.py` | **Business & entity layer** — entity registry + business-credit (PAYDEX) vendor tracker. |
| `ctc_pdf.py` | **PDF statement parsing** (best effort, via `pdftotext`). |
| `ctc_report.py` | **Written audit report** — clean print-to-PDF HTML document. |
| `ctc_access.py` | **Access list generator** — filterable catalog of CA/US banks, credit unions, loan systems, cross-border options, and Black-entrepreneur programs; ranks options by your eligibility. |
| `ctc_advisor.py` | **AI advisor** — a live Claude (Opus 4.8) agent with web search + persistent memory when the SDK/key are set up, otherwise an offline advisor that answers from your data. |
| `ctc_rates_watch.py` | **Rate watch** — pulls the Bank of Canada overnight rate + prime from the official Valet API and caches them for the Advisor widget. |
| `ctc_cli.py` | Menu-driven control center (27 tools). |
| `REFERENCE.md` | The reference catalog as a readable document. |

## Run it

```bash
cd coretrust_system
python3 ctc_cli.py
```

Add data through **menu 13**, or copy `sample_profile.json`, replace every value
with your own real numbers, and import via **menu 13 → g**. Data lives in
`coretrust_system.db` on your machine.

**Import from bank CSV exports (menu 13 → j):** transactions (with either
Debit/Credit columns or a single signed Amount column), a cards spreadsheet, or
an accounts spreadsheet. Columns are auto-detected; `$`, commas, parentheses-
negatives, and common date formats are handled.

**Funding roadmap (menu 17):** sequences your matches into an ordered plan —
clear the blockers, activate what you're ready for (Canada), close near-ready
gaps, build the US cross-border foundation, scale into US personal & business
credit, then digital assets last and risk-managed.

**Visual dashboard (menu 18):** writes a single self-contained `dashboard.html`
from your data — a boot/loading sequence, an animated Matrix/machine background,
a sidebar of loadable widgets (Overview, Net Worth, Health, Plays, Product Match,
Roadmap, Credit, Reference), and a clickable logo that returns home. Open it in
any browser; it's responsive for laptop and mobile and needs no internet. Re-run
menu 18 anytime to regenerate it from your latest numbers.

### Auditor & compliance layer (menus 20–25)

- **History, goals & deadlines (20):** snapshot your score/net worth/utilization
  over time, view trend sparklines, set goals with projected completion dates,
  and see a radar of upcoming deadlines (statements, CLI eligibility, RRSP/TFSA
  dates, dispute clocks).
- **Debt payoff planner (21):** avalanche vs. snowball across all your debts,
  months-to-debt-free, total interest, and extra-payment impact.
- **Dispute case tracker (22):** every dispute becomes a case with a 30-day
  response clock and the escalation ladder (bureau → Ontario Ministry → OPC →
  the 2025 statutory civil-damages right).
- **Compliance center (23):** record PIPEDA consent, view the append-only audit
  log, check statute/rate currency (flags anything not recently verified), and
  make/restore **AES-256 encrypted backups** (PIPEDA "encrypt at rest").
- **Business & entities (24):** track personal / operating co / holdco, and build
  a business-credit file with a net-30 vendor / PAYDEX-readiness tracker.
- **Written audit report (25):** one-click professional HTML report you print to
  PDF — the "written audit summary for the consumer" your CLAUDE.md calls for.
- **PDF statement import (13 → j → p):** parse a PDF statement via `pdftotext`
  (best effort — review the rows).

Two compliance touches run automatically: a **consent prompt on first launch**,
and an **audit-log entry** for sessions, generated letters, opened dispute cases,
backups, and reports.

### Access list generator (menu 26, and the dashboard's Access widget)

A filterable catalog of what you can actually access as a Canadian — major banks,
secondary/challenger banks, credit unions, loan & financing systems, US
cross-border options, and **programs built for Black entrepreneurs** (BEP, FACE
loan fund, BDC, Futurpreneur, RBC, Black Opportunity Fund, Foundation for Black
Communities) plus US Black-owned banks / MDIs / CDFIs. Filter by country,
segment, or Black-focused, and **rank by your eligibility** (ready now vs.
prerequisite vs. not eligible). Every entry carries an honest **eligibility**
note (e.g. most US options need the cross-border foundation first, and SBA 8(a)
requires US citizenship).

### AI advisor (menu 27, and the dashboard's Advisor widget)

The **CLI advisor (menu 27)** is a real agentic Claude (Opus 4.8) when the SDK and
a key are present (`pip install anthropic` + `ANTHROPIC_API_KEY` or `ant auth
login`): it reads your financial profile via a tool, researches the live economy
with web search, and remembers what it learns across sessions — direct,
analytical, and compliant (it points you to a licensed CPA/advisor for regulated
advice rather than posing as one). Without the SDK/key it runs an **offline
advisor** that answers from your data with no network. Your data stays local;
only your questions and a computed summary are sent when the live agent runs.

The **dashboard Advisor widget** is a Jarvis-styled, offline assistant — a
published page can't call an LLM, so it reasons over your embedded data instantly
and points you to the CLI agent for live web research.

### The dashboard: 6 consolidated widgets

The live dashboard groups every tool into six correlated widgets:

| Widget | Rolls up |
|---|---|
| **Advisor** | Jarvis-style greeting, your previous-statement report and what's upcoming, at-a-glance score/net worth, and a chat that answers about your money, credit, funding, programs, and next moves — all from your own data, offline |
| **Wealth** | net worth, debt-payoff planner, tax snapshot + editable money data (accounts, debts, registered, income, assets, business) |
| **Credit** | health score, reporting-period audit, dispute cases, optimization playbook + editable credit data (cards, credit-file entries, profile) |
| **Funding** | product match (CA/US, personal/business, digital assets) + funding roadmap |
| **Access** | the access list generator + credit bureaus + Canada→US playbook |
| **Vault** | trends, goals, deadline radar, PIPEDA consent, statute currency, business-credit readiness, audit log |

**Live editable dashboard (menu 19):** the same dashboard, but you type your
balances, limits, and scores directly into a **Live Editor** widget and
everything recomputes instantly in the browser — health score, net worth, plays,
product match, and roadmap — because the whole compute engine is ported to
JavaScript (and verified to match the Python numbers). Two ways to run it:
- **Local server** (menu 19 → 1): edits round-trip — click **SAVE** and it writes
  straight back into `coretrust_system.db` (the database mirrors the editor).
- **File / published page**: **SAVE** falls back to **EXPORT**, downloading a
  `coretrust_profile.json` you re-import via menu 13 → g.

**Product match (menu 16):** takes your profile and ranks the specific product
categories you're readiest to be approved for — across CA + US, personal +
business, banks, credit unions, lenders, and **digital assets** — each with who
offers it and the next gap to close. US products stay gated behind the
cross-border foundation (US bank account + ITIN/SSN + US address) until you've
built it. Digital-asset products (crypto trading/custody, crypto-backed loans,
business treasury/IP) are included as regulated products with explicit risk
warnings — not as a tax-avoidance scheme.

**Reference catalog (menu 15, or `REFERENCE.md`):** Canadian and US major banks
and credit unions by product line (HISA, cards, personal/auto loans, mortgages,
and the business equivalents), the personal and business credit bureaus in both
countries, the consumer/financial statutes, the IDs a Canadian needs (SIN, BN,
D-U-N-S, ITIN, EIN), and a legitimate Canada→US credit-building playbook. It
lists what exists and what's required — not interest rates, which change too
often to hardcode.

## The four systems you asked for

1. **"Get approved" (menu 4)** — lenders *can* say no, so this is honest
   **approval readiness**: it scores your profile against what each product
   actually underwrites (score, utilization, DTI/GDS/TDS, collections, time in
   business) and tells you exactly which gaps to close *before* you apply. It
   never hides applications from lenders.
2. **Dashboard + plays (menu 2 & 3)** — a composite health score and net worth,
   plus ranked opportunities to cut interest cost, shelter tax, improve credit
   metrics, build an emergency fund, and get funding-ready — all from your own
   numbers, with dollar estimates where computable.
3. **Tax strategist (menu 11)** — marginal vs. average rate, RRSP tax reduction,
   TFSA/RRSP/FHSA guidance, and owner concepts (SBD, CCA, salary-vs-dividends,
   holdco/opco) at an educational level. Estimates, not a return.
4. **Payroll (menu 12)** — plan the T4 salary you pay yourself: net take-home,
   CPP/CPP2/EI, income tax, total cost to the corporation, and the gross needed
   to hit a target net. Planning math — actual remittances go through compliant
   payroll and a CPA.

## Where your numbers come from

- **Balances, limits, minimums, APRs** → your statements.
- **Registered-account room** → **CRA MyAccount** (authoritative; the 2026 limits
  in code are just defaults).
- **Income** → pay stubs / T4. **Credit scores** → Equifax CA / TransUnion CA.
- **Credit-report entries** → your bureau reports, entered exactly as shown.

## 2026 rate assumptions (verify yearly)

Baked into `ctc_rates.py` and easy to edit:

- Federal brackets 14% / 20.5% / 26% / 29% / 33%; Ontario 5.05%–13.16% + surtax.
- CPP: YMPE $74,600 @ 5.95%; CPP2 to $85,000 @ 4%; EI MIE $68,900 @ 1.63%.
- CRA room: TFSA $7,000 · RRSP $33,810 ceiling · FHSA $8,000.

These change annually and can be revised mid-year — **confirm current figures at
canada.ca / ontario.ca and with a CPA.**

## What this build deliberately does NOT do

- No fabricated dispute discrepancies or sworn statements about invented errors.
- No "$1 error deletes an accurate tradeline" myth.
- No credit-application "stacking" timed to hide applications from lenders.
- No faked transaction velocity to trick underwriting.
- No tax-avoidance engineering (off-grid crypto, income hiding, phantom
  deductions).

Everything here is something you can say and do honestly, consistent with the
Bank Act, PIPEDA, the Ontario Consumer Reporting Act (RSO 1990 c. C.33), and the
Ontario CPA 2002. Not legal/tax/investment advice — for those, consult a licensed
Ontario lawyer/paralegal, a CPA, or a licensed financial advisor.
