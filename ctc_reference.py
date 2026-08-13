"""
CoreTrust System (CTC) -- Institutions, Bureaus & Codes Reference (Canada + US)
==============================================================================
A structured, queryable reference layer for the tracker:

  * Canadian major banks + credit unions, personal & business product lines
  * US major banks + credit unions (the cross-border play), same product lines
  * Credit bureaus -- personal & business, both countries
  * Consumer/financial statutes ("codes") -- personal & business, both countries
  * The identifiers a Canadian actually needs (SIN, BN, D-U-N-S, ITIN, EIN...)
  * A legitimate Canadian -> US credit-building playbook

REFERENCE ONLY. This lists what EXISTS and what's typically required; it is not
advice, and it does not list interest rates/yields (those change constantly --
confirm current numbers with each institution). Eligibility varies; many US
credit unions require US residency/SSN. Verify everything before acting.
"""

from __future__ import annotations

from typing import List, Optional

PERSONAL_CATEGORIES = [
    "High-Interest Savings (HISA)", "Credit Cards", "Personal Loans",
    "Auto Loans", "Mortgages & HELOC", "Lines of Credit",
]
BUSINESS_CATEGORIES = [
    "Business Chequing/Savings", "Business Credit Cards", "Business Lines of Credit",
    "Business Term Loans", "Equipment Financing", "Commercial Mortgages",
    "Merchant/Payment Services",
]

FULL = "all of the above"

# --- Canadian institutions ------------------------------------------------
CANADIAN_BANKS = [
    {"name": "RBC Royal Bank", "kind": "Big 6 bank", "personal": FULL, "business": FULL,
     "us_affiliate": "RBC Bank (US) — full cross-border banking, cards, mortgages", "hisa": False},
    {"name": "TD Canada Trust", "kind": "Big 6 bank", "personal": FULL, "business": FULL,
     "us_affiliate": "TD Bank, N.A. (US) — cross-border accounts/cards, links CA+US", "hisa": False},
    {"name": "Scotiabank", "kind": "Big 6 bank", "personal": FULL, "business": FULL,
     "us_affiliate": "Limited US retail; international footprint", "hisa": False},
    {"name": "BMO Bank of Montreal", "kind": "Big 6 bank", "personal": FULL, "business": FULL,
     "us_affiliate": "BMO Bank N.A. (formerly BMO Harris) — US accounts/cards", "hisa": False},
    {"name": "CIBC", "kind": "Big 6 bank", "personal": FULL, "business": FULL,
     "us_affiliate": "CIBC Bank USA — cross-border banking", "hisa": False},
    {"name": "National Bank of Canada", "kind": "Big 6 bank", "personal": FULL, "business": FULL,
     "us_affiliate": "Natbank (Florida) — accounts for Canadians", "hisa": False},
    {"name": "Desjardins", "kind": "Co-operative / caisse", "personal": FULL, "business": FULL,
     "us_affiliate": "Desjardins Bank (Florida)", "hisa": False},
    {"name": "EQ Bank", "kind": "Digital bank", "personal": "HISA, some cards, mortgages (via Equitable)",
     "business": "Business/notice savings (growing)", "us_affiliate": "US-dollar account", "hisa": True},
    {"name": "Tangerine (Scotia)", "kind": "Digital bank", "personal": "HISA, cards, loans, mortgages, LOC",
     "business": "Limited", "us_affiliate": "—", "hisa": True},
    {"name": "Simplii Financial (CIBC)", "kind": "Digital bank", "personal": "HISA, cards, loans, mortgages, LOC",
     "business": "Limited", "us_affiliate": "US-dollar account", "hisa": True},
    {"name": "Neo Financial", "kind": "Fintech", "personal": "HISA, credit cards, secured cards",
     "business": "Limited", "us_affiliate": "—", "hisa": True},
    {"name": "Wealthsimple", "kind": "Fintech", "personal": "Cash (HISA-like), some credit, investing",
     "business": "—", "us_affiliate": "—", "hisa": True},
    {"name": "Manulife Bank", "kind": "Bank", "personal": "HISA, Manulife One, mortgages, LOC",
     "business": "Limited", "us_affiliate": "—", "hisa": True},
    {"name": "Motive Financial / motusbank", "kind": "Digital bank", "personal": "HISA, mortgages, loans",
     "business": "Limited", "us_affiliate": "—", "hisa": True},
]

CANADIAN_CREDIT_UNIONS = [
    {"name": "Meridian (ON)", "personal": FULL, "business": FULL},
    {"name": "Vancity (BC)", "personal": FULL, "business": FULL},
    {"name": "Coast Capital (BC)", "personal": FULL, "business": FULL},
    {"name": "Servus / Connect First (AB)", "personal": FULL, "business": FULL},
    {"name": "First West — Envision/Valley First (BC)", "personal": FULL, "business": FULL},
    {"name": "Alterna Savings (ON)", "personal": FULL, "business": FULL},
    {"name": "DUCA (ON)", "personal": FULL, "business": FULL},
    {"name": "FirstOntario (ON)", "personal": FULL, "business": FULL},
    {"name": "Libro (ON)", "personal": FULL, "business": FULL},
    {"name": "Prospera (BC)", "personal": FULL, "business": FULL},
    {"name": "Conexus (SK) / Assiniboine (MB)", "personal": FULL, "business": FULL},
    {"name": "Desjardins caisses (QC/ON)", "personal": FULL, "business": FULL},
]

# --- US institutions (cross-border) --------------------------------------
US_BANKS = [
    {"name": "JPMorgan Chase", "kind": "Big bank", "personal": FULL, "business": FULL},
    {"name": "Bank of America", "kind": "Big bank", "personal": FULL, "business": FULL,
     "note": "Accepts ITIN for some card applications"},
    {"name": "Wells Fargo", "kind": "Big bank", "personal": FULL, "business": FULL,
     "note": "Accepts ITIN for some applications"},
    {"name": "Citibank", "kind": "Big bank", "personal": FULL, "business": FULL,
     "note": "Accepts ITIN for some applications"},
    {"name": "U.S. Bank", "kind": "Big bank", "personal": FULL, "business": FULL},
    {"name": "Capital One", "kind": "Big bank", "personal": FULL, "business": FULL,
     "note": "ITIN-friendly: Platinum Secured, Quicksilver Secured — good bootstrap cards"},
    {"name": "PNC / Truist", "kind": "Big banks", "personal": FULL, "business": FULL},
    {"name": "RBC Bank (US)", "kind": "Canadian-affiliate", "personal": FULL, "business": "Limited",
     "note": "Built for Canadians; US accounts/cards/mortgages, no SSN required"},
    {"name": "TD Bank, N.A. (US)", "kind": "Canadian-affiliate", "personal": FULL, "business": FULL,
     "note": "Cross-border; links CA + US TD accounts"},
    {"name": "BMO Bank N.A. (US)", "kind": "Canadian-affiliate", "personal": FULL, "business": FULL},
    {"name": "CIBC Bank USA / Natbank / Desjardins Bank", "kind": "Canadian-affiliate",
     "personal": "Accounts + some cards", "business": "Some", "note": "Canadian-owned US banks"},
    {"name": "American Express (US)", "kind": "Card issuer", "personal": "Credit cards",
     "business": "Business cards", "note": "Amex Global (Card) Transfer: use your Canadian Amex to get a first US Amex"},
    {"name": "Ally / Marcus / Amex National Bank / Capital One 360 / Discover / SoFi",
     "kind": "Digital / HYSA", "personal": "High-yield savings, cards, loans", "business": "Some (Amex/SoFi)",
     "note": "The US high-yield-savings leaders"},
]

US_CREDIT_UNIONS = [
    {"name": "Navy Federal", "note": "Military/family eligibility"},
    {"name": "PenFed", "note": "Open membership in many cases"},
    {"name": "Alliant / First Tech / BECU / SECU", "note": "Various eligibility"},
]

# --- Credit bureaus -------------------------------------------------------
BUREAUS = {
    "Canada — personal": [
        "Equifax Canada", "TransUnion Canada",
    ],
    "Canada — business": [
        "Equifax Business Canada", "Dun & Bradstreet Canada (D-U-N-S #, PAYDEX)",
        "TransUnion (limited business data)",
    ],
    "US — personal": [
        "Equifax", "Experian", "TransUnion (the 'big three'); scoring: FICO, VantageScore",
    ],
    "US — business": [
        "Dun & Bradstreet (D-U-N-S #, PAYDEX score)", "Experian Business (Intelliscore Plus)",
        "Equifax Business", "SBFE — Small Business Financial Exchange",
        "FICO SBSS (Small Business Scoring Service) — used for SBA loans",
    ],
}

# --- Statutes / "codes" ---------------------------------------------------
STATUTES = {
    "Canada — personal / consumer": [
        "Bank Act, S.C. 1991, c.46 — incl. s.455.1 (prohibits coercive tied selling)",
        "PIPEDA — federal privacy (consent, access, correction of your data)",
        "Provincial Consumer Reporting Acts — e.g. Ontario CRA, RSO 1990, c.C.33 (s.9 accuracy, s.12 dispute/delete)",
        "Consumer Protection Act, 2002 (ON) — bans upfront credit-repair fees, deceptive practices",
        "Collection & Debt Settlement Services Act (ON) — collector conduct rules",
        "Criminal Code s.347 — criminal interest-rate ceiling (contracts above it are void)",
        "FCAC Act — Financial Consumer Agency of Canada oversight & complaints",
    ],
    "Canada — business": [
        "Canada Business Corporations Act (CBCA) s.15 — a corporation is a distinct legal person",
        "Personal Property Security Act (PPSA, provincial) — secured lending / GSA registration",
        "Income Tax Act — Small Business Deduction (up to $500k), Capital Cost Allowance",
        "Bank Act — governs business lending disclosure",
    ],
    "US — personal / consumer": [
        "FCRA — Fair Credit Reporting Act (15 U.S.C. §1681): accuracy, disputes, permissible purpose",
        "FDCPA — Fair Debt Collection Practices Act (15 U.S.C. §1692): collector conduct",
        "FCBA — Fair Credit Billing Act: billing-error disputes",
        "ECOA — Equal Credit Opportunity Act (15 U.S.C. §1691): anti-discrimination in credit",
        "TILA — Truth in Lending Act (Reg Z): cost-of-credit disclosure",
        "GLBA — Gramm-Leach-Bliley: financial privacy",
        "CROA — Credit Repair Organizations Act: rules on credit-repair firms",
        "Regulators: CFPB and FTC",
    ],
    "US — business": [
        "Business credit reports are NOT covered by the FCRA (FCRA = consumer reports only)",
        "ECOA still applies to business credit APPLICATIONS (anti-discrimination)",
        "Uniform Commercial Code (UCC) filings — secured-lending liens (US analogue to PPSA)",
        "IRS rules — EIN issuance (Form SS-4)",
    ],
}

# --- IDs / codes a Canadian needs ----------------------------------------
IDS_NEEDED = {
    "Canada — personal": [
        "SIN (Social Insurance Number) — identity for credit files and payroll",
        "Government photo ID + Canadian address",
    ],
    "Canada — business": [
        "Federal/provincial incorporation number (CBCA or provincial registry)",
        "CRA Business Number (BN, 9-digit) + program accounts: RT (HST/GST), RP (payroll), RC (corp income tax)",
        "D-U-N-S number (Dun & Bradstreet) — to open a business credit file",
        "Business address (commercial, not a P.O. box) + registered phone",
    ],
    "US — personal (cross-border credit)": [
        "US mailing address",
        "US bank account (open via a Canadian bank's US affiliate — no SSN needed)",
        "ITIN (Individual Taxpayer Identification Number, IRS Form W-7) if you're not SSN-eligible; "
        "several issuers accept ITIN in place of an SSN",
        "SSN — only if you're authorized to work in the US",
        "Note: your Canadian credit history does NOT transfer; US bureaus are separate. "
        "Amex Global Transfer / Nova Credit are the bridges.",
    ],
    "US — business": [
        "US entity (LLC or Corp) + registered agent",
        "EIN (Employer Identification Number, IRS Form SS-4)",
        "US business bank account",
        "D-U-N-S number (US) — build a PAYDEX score with net-30 vendors that report",
    ],
}

CROSSBORDER_PLAYBOOK = [
    "1. Open a US bank account through your Canadian bank's US affiliate (RBC Bank, "
    "TD Bank US, BMO, CIBC Bank USA, Natbank, Desjardins Bank) — typically no SSN required; "
    "they can use your Canadian relationship internally.",
    "2. Establish a US mailing address.",
    "3. Get your first US credit card via a legitimate bridge: Amex Global (Card) Transfer "
    "(leverages your existing Canadian Amex), a Nova Credit-enabled application, a Canadian-"
    "affiliate US-bank card, or an ITIN-friendly secured card (e.g. Capital One Platinum/"
    "Quicksilver Secured). A credit-builder account (e.g. Self) also works.",
    "4. Get an ITIN (Form W-7) if you'll file/earn in the US or an issuer requires it.",
    "5. Use the card lightly, pay in full and on time. US scores build over ~4–6 months to "
    "usable (~640) and ~9–12 months to good (670+). Canadian history does not carry over.",
    "6. For business: form a US LLC/Corp, get an EIN, open a US business bank account, get a "
    "US D-U-N-S number, and build PAYDEX by paying reporting net-30 vendors early.",
    "Everything here is standard and legal. It is NOT advice, rates/eligibility vary, and some "
    "options (e.g. many US credit unions) require US residency/SSN — verify before applying.",
]


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------
def _inst_line(i: dict) -> str:
    parts = [f"  - {i['name']} ({i.get('kind','credit union')})"]
    parts.append(f"      Personal: {i.get('personal','—')}")
    parts.append(f"      Business: {i.get('business','—')}")
    if i.get("us_affiliate") and i["us_affiliate"] != "—":
        parts.append(f"      US cross-border: {i['us_affiliate']}")
    if i.get("note"):
        parts.append(f"      Note: {i['note']}")
    return "\n".join(parts)


def section_canada_banks() -> str:
    out = ["CANADIAN MAJOR BANKS & DIGITAL BANKS", "(HISA leaders marked *)"]
    for b in CANADIAN_BANKS:
        star = " *" if b.get("hisa") else ""
        out.append(_inst_line({**b, "name": b["name"] + star}))
    return "\n".join(out)


def section_canada_cus() -> str:
    out = ["CANADIAN CREDIT UNIONS (full personal + business service)"]
    for c in CANADIAN_CREDIT_UNIONS:
        out.append(f"  - {c['name']}: personal {c['personal']}; business {c['business']}")
    return "\n".join(out)


def section_us() -> str:
    out = ["US BANKS (cross-border play for Canadians)"]
    for b in US_BANKS:
        out.append(_inst_line(b))
    out.append("\nUS CREDIT UNIONS (membership eligibility applies; usually need US residency/SSN)")
    for c in US_CREDIT_UNIONS:
        out.append(f"  - {c['name']} — {c['note']}")
    return "\n".join(out)


def section_bureaus() -> str:
    out = ["CREDIT BUREAUS (personal & business, both countries)"]
    for k, v in BUREAUS.items():
        out.append(f"  {k}:")
        out += [f"    - {x}" for x in v]
    return "\n".join(out)


def section_statutes() -> str:
    out = ["STATUTES / CONSUMER & FINANCIAL 'CODES'"]
    for k, v in STATUTES.items():
        out.append(f"  {k}:")
        out += [f"    - {x}" for x in v]
    return "\n".join(out)


def section_ids() -> str:
    out = ["IDENTIFIERS / NUMBERS A CANADIAN NEEDS"]
    for k, v in IDS_NEEDED.items():
        out.append(f"  {k}:")
        out += [f"    - {x}" for x in v]
    return "\n".join(out)


def section_crossborder() -> str:
    return "CANADIAN -> US CREDIT-BUILDING PLAYBOOK\n" + "\n".join("  " + s for s in CROSSBORDER_PLAYBOOK)


def product_categories() -> str:
    return ("PRODUCT CATEGORIES TRACKED\n  Personal: " + "; ".join(PERSONAL_CATEGORIES)
            + "\n  Business: " + "; ".join(BUSINESS_CATEGORIES))


SECTIONS = {
    "categories": product_categories,
    "canada_banks": section_canada_banks,
    "canada_credit_unions": section_canada_cus,
    "us": section_us,
    "bureaus": section_bureaus,
    "statutes": section_statutes,
    "ids": section_ids,
    "crossborder": section_crossborder,
}

DISCLAIMER = ("Reference only — not legal, tax, or financial advice. No interest rates/yields "
              "are listed because they change constantly; confirm products, rates, and "
              "eligibility with each institution. Verify statute citations before relying on them.")


def full_reference() -> str:
    blocks = [product_categories(), section_canada_banks(), section_canada_cus(),
              section_us(), section_bureaus(), section_statutes(), section_ids(),
              section_crossborder()]
    return "\n\n".join(blocks) + "\n\n---\n" + DISCLAIMER
