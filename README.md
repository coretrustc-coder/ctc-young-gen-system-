# CoreTrust System (CTC) — Complete Financial Intelligence & Young Gen Platform

[![Live App](https://img.shields.io/badge/Live_Student_App-coretrust--young--gen--advisor.vercel.app-3EC6D0?style=for-the-badge&logo=vercel)](https://coretrust-young-gen-advisor.vercel.app/)
[![Founder Admin Portal](https://img.shields.io/badge/Founder_Admin_Portal-admin.html-1D9E75?style=for-the-badge&logo=vercel)](https://coretrust-young-gen-advisor.vercel.app/admin.html)
[![Dual AI Engine](https://img.shields.io/badge/AI_Engine-Google_Gemini_%2B_Anthropic_Claude-7F77DD?style=for-the-badge)](https://github.com/coretrustc-coder/ctc-young-gen-system-)
[![License](https://img.shields.io/badge/Compliance-CASL_%7C_PIPEDA_%7C_FCAC-EF9F27?style=for-the-badge)](https://github.com/coretrustc-coder/ctc-young-gen-system-)

---

## 🌐 Live System Portals & Applications

| Portal / Application | Direct Live Link | Access Credentials | Description |
|---|---|---|---|
| **Live Student App** | [https://coretrust-young-gen-advisor.vercel.app/](https://coretrust-young-gen-advisor.vercel.app/) | Open Access / Magic Link | Full Young Gen Advisor web app with OSAP float calculator, scholarship stack, side hustles, dispute letters, and verified bank/CU links. |
| **Founder Admin Portal** | [https://coretrust-young-gen-advisor.vercel.app/admin.html](https://coretrust-young-gen-advisor.vercel.app/admin.html) | Passcode: `coretrust2026` | Live founder dashboard for tracking client roster files, OSAP funding totals, system security status, and AI API health. |
| **Local Live Server** | `http://127.0.0.1:8799/` | Localhost | Run `python3 ctc_serve.py` for local offline/online DB editing and Matrix dashboard. |

---

## 🏗 Repository Structure & Architecture

```
ctc-young-gen-system/
├── index.html                   # Live Student Web Application & Young Gen AI Advisor
├── admin.html                   # Founder Admin Command Portal & Client Tracker
├── CoreTrust-Core.html          # CoreTrust Core Engine Web Dashboard
├── dashboard.html               # Single-File Standalone Interactive Dashboard
├── vercel.json                  # Vercel Routing Configuration (/admin, /api, static)
├── README.md                    # Master System Documentation & Architecture Guide
├── REFERENCE.md                 # Complete Reference Catalog (Banks, Credit Bureaus, Statutes)
│
├── api/                         # Serverless Dual-Engine Vercel Functions
│   ├── chat.js                  # Master Router: Google Gemini (Fast/Vision) + Anthropic Claude (Legal)
│   ├── deliverable.js           # PDF Student Funding Plan Generator
│   ├── audit.js                 # "What am I missing?" Scholarship Audit Engine
│   ├── applications.js          # Student Application Tracker & Deadline Alerts
│   └── intake-doc.js            # Gemini Vision OCR Document & Receipt Reader
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

## 🚀 Dual-Engine AI Architecture

The system features a **Hybrid Multi-Model Router**:

1. **Google Antigravity / Gemini 1.5**:
   - Sub-300ms chat response streaming.
   - **Multimodal Document OCR**: Reads OSAP notices, tuition statements, and receipts uploaded by students.
2. **Anthropic Claude 3.5 Sonnet**:
   - High-precision legal dispute letter synthesis (enforcing the 6-year Ontario reporting limit under the Consumer Reporting Act).
   - Strict CASL & PIPEDA compliance checking.
3. **Smart Link Engine**:
   - Automatically injects direct application links (`target="_blank"`) for Big 6 Banks, Credit Unions, OSAP, and Canadian Universities.

---

## 🔒 Security & Privacy Framework

- **Row-Level Security (RLS)**: Client profiles in Supabase are locked so each student can only access their own private row.
- **Local SQLite Storage**: Core engine runs locally via `coretrust_system.db` with AES-256 backup support.
- **Git Protection**: All private credentials are read from `.env` (which is excluded from Git via `.gitignore`).

---

## 🛠 Local Setup & Running CLI

To run the Python CLI control center locally:

```bash
cd coretrust_system

# 1. Install dependencies
pip3 install google-generativeai anthropic

# 2. Add API Keys to .env (Git-ignored)
echo "GEMINI_API_KEY=your_key" >> .env
echo "ANTHROPIC_API_KEY=your_key" >> .env

# 3. Launch CLI Control Center
python3 ctc_cli.py

# 4. Launch Local Live Dashboard Server
python3 ctc_serve.py
```
