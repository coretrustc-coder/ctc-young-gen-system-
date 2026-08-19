# CoreTrust System 2.0 — Final Unified Master Repository

[![Live Student App](https://img.shields.io/badge/Live_Student_App-coretrust--young--gen--advisor.vercel.app-3EC6D0?style=for-the-badge&logo=vercel)](https://coretrust-young-gen-advisor.vercel.app/)
[![Founder Admin Portal](https://img.shields.io/badge/Founder_Admin_Portal-admin.html-1D9E75?style=for-the-badge&logo=vercel)](https://coretrust-young-gen-advisor.vercel.app/admin)
[![Dual AI Engine](https://img.shields.io/badge/AI_Engine-Google_Gemini_%2B_Anthropic_Claude-7F77DD?style=for-the-badge)](https://github.com/coretrustc-coder/ctc-young-gen-system-)
[![Compliance](https://img.shields.io/badge/Compliance-CASL_%7C_PIPEDA_%7C_FCAC-EF9F27?style=for-the-badge)](https://github.com/coretrustc-coder/ctc-young-gen-system-)

---

## 🌐 Live System Portals & Applications

| Portal / Module | Direct Live Link | Access Credentials | Description |
|---|---|---|---|
| **Live Student App** | [https://coretrust-young-gen-advisor.vercel.app/](https://coretrust-young-gen-advisor.vercel.app/) | Open Access | Full Young Gen Advisor web app with OSAP float calculator, scholarship stack, side hustles, dispute letters, and CTC GEM Blueprint. |
| **Founder Admin Portal** | [https://coretrust-young-gen-advisor.vercel.app/admin](https://coretrust-young-gen-advisor.vercel.app/admin) | Passcode: `coretrust2026` | Live founder dashboard for real-time client profile tracking, OSAP grant/loan totals, API health checks, and client support assist. |
| **Simplified PDF Guide** | [https://coretrust-young-gen-advisor.vercel.app/guide](https://coretrust-young-gen-advisor.vercel.app/guide) | Open Access | Beginner-friendly CTC GEM guide with real-world case studies and 1-click PDF download button. |
| **Local Live Server** | `http://127.0.0.1:8799/` | Localhost | Local live editable dashboard engine and SQLite store. |

---

## 🏗 Consolidated Master System Architecture

```
ctc-young-gen-system/
├── index.html                   # Live Student Web Application & CTC GEM Blueprint
├── admin.html                   # Founder Admin Command Portal & Client Roster Tracker
├── CoreTrust_CTC_GEM_Simplified_Guide.html # Plain-English Beginner PDF Guide & Case Studies
├── CoreTrust-Core.html          # CoreTrust Core Engine Web Dashboard
├── dashboard.html               # Single-File Standalone Interactive Dashboard
├── vercel.json                  # Modern Vercel Routing & Clean URL Manifest
├── README.md                    # Unified System Documentation
├── REFERENCE.md                 # Complete Reference Catalog (Banks, Credit Bureaus, Statutes)
│
├── api/                         # Serverless Dual-Engine Vercel Functions
│   ├── chat.js                  # Master Router: Google Gemini 1.5 (Fast/OCR) + Anthropic Claude 3.5 (Legal)
│   ├── deliverable.js           # PDF Student Funding Plan Generator
│   ├── audit.js                 # "What am I missing?" Scholarship Audit Engine
│   ├── applications.js          # Student Application Tracker & Deadline Alerts
│   └── intake-doc.js            # Gemini Vision OCR Document & Receipt Reader
│
├── hermes_pipeline/             # Multi-Agent Intelligence Engine (Merged from Hermes System)
│   ├── agents/                  # Planner, Analyst, Compliance, Critic, Executor agents
│   ├── core/                    # Execution rules, disclaimers, and strategist context
│   └── CLAUDE.md                # Hermes Multi-Agent System Rules
│
├── lead_hunting/                # GTA Business Lead Scraping & CASL Outreach Engine
│   ├── scrapers/                # Automated business lead discovery
│   └── outreach/                # Compliant email/SMS outreach workflows
│
├── ctc_advisor.py               # Dual-Engine Hybrid Python CLI Advisor (Gemini + Claude)
├── ctc_cli.py                   # Menu-Driven Control Center (27 Tools)
├── ctc_models.py                # Local SQLite Data Models & Underwriting Engine
├── ctc_dashboard_live.py        # Live Editable Dashboard Engine
├── ctc_access.py                # Bank, Credit Union & Access List Personalizer
├── ctc_disputes.py              # Ontario Consumer Reporting Act Legal Dispute Generator
├── ctc_lender.py                # Approval-Readiness & Underwriting Engine
├── ctc_match.py                 # Financial Product Matching Engine
├── ctc_roadmap.py               # Multi-Year Funding & Credit Roadmap Sequence
├── ctc_serve.py                 # Local Live Web Server (127.0.0.1:8799)
└── ctc_tax.py                   # Tax & Owner-Operator Payroll Calculations
```

---

## 🚀 Dual-Engine AI & Multi-Agent Architecture

1. **Google Antigravity / Gemini 1.5**:
   - Sub-300ms chat response streaming.
   - **Multimodal Document OCR**: Reads OSAP notices, tuition statements, and receipts uploaded by students.
2. **Anthropic Claude 3.5 Sonnet**:
   - High-precision legal dispute letter synthesis (enforcing the 6-year Ontario reporting limit under the Consumer Reporting Act).
   - Strict CASL & PIPEDA compliance checking.
3. **Hermes Multi-Agent Orchestrator ([`hermes_pipeline/`](file:///Users/trevonhalstead/coretrust_system/hermes_pipeline/))**:
   - Sequential multi-agent pipeline: `Planner` $\rightarrow$ `Compliance` $\rightarrow$ `Analyst` $\rightarrow$ `Critic` $\rightarrow$ `Executor`.

---

## 🔒 Security & Compliance

- **Row-Level Security (RLS)**: Client profiles in Supabase are locked so each student can only access their own private row.
- **CASL & PIPEDA Compliant**: Unsubscribe mechanisms, express consent checks, and disclaimers enforced.
- **Git Protection**: All credentials are loaded from `.env` (excluded via `.gitignore`).
