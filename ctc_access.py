"""
CoreTrust System (CTC) -- Access List Generator
===============================================
A filterable catalog of what you can actually access as a Canadian: major banks,
secondary/challenger banks, credit unions, loan & financing systems, the US
cross-border options, and -- because you asked -- programs built specifically for
Black entrepreneurs in Canada, plus Black-owned banks / MDIs / CDFIs in the US.

Filter by country (CA/US), segment (personal/business), category, or the
`black_focus` flag. Every entry carries an honest ELIGIBILITY note, because a lot
of US minority programs require US citizenship/residency that a Canadian doesn't
have without building the cross-border foundation first (and some, like SBA 8(a),
require US citizenship outright).

Reference only -- amounts/terms/eligibility change; confirm with each provider.
Not legal, tax, or financial advice.
"""

from __future__ import annotations

from typing import List, Optional

# category constants
MAJOR = "Major bank"
SECONDARY = "Secondary / challenger bank"
CU = "Credit union"
LOAN = "Loan / financing system"
XBORDER = "Cross-border (US)"
BLACK_CA = "Black entrepreneur program (Canada)"
BLACK_US = "Black-owned bank / MDI / CDFI (US)"

CATEGORIES = [MAJOR, SECONDARY, CU, LOAN, XBORDER, BLACK_CA, BLACK_US]


def _e(id, name, category, country, segment, eligibility, access, url="", black=False):
    return {"id": id, "name": name, "category": category, "country": country,
            "segment": segment, "eligibility": eligibility, "access": access,
            "url": url, "black_focus": black}


ACCESS_CATALOG: List[dict] = [
    # ---- Canada · major banks ----
    _e("rbc", "RBC Royal Bank", MAJOR, "CA", "both", "Canadian resident + ID",
       "Full personal + business banking, cards, loans, mortgages; US arm (RBC Bank).", "rbcroyalbank.com"),
    _e("td", "TD Canada Trust", MAJOR, "CA", "both", "Canadian resident + ID",
       "Full service; cross-border TD Bank (US).", "td.com"),
    _e("scotia", "Scotiabank", MAJOR, "CA", "both", "Canadian resident + ID", "Full service.", "scotiabank.com"),
    _e("bmo", "BMO", MAJOR, "CA", "both", "Canadian resident + ID", "Full service; BMO Bank N.A. (US).", "bmo.com"),
    _e("cibc", "CIBC", MAJOR, "CA", "both", "Canadian resident + ID", "Full service; CIBC Bank USA.", "cibc.com"),
    _e("nbc", "National Bank of Canada", MAJOR, "CA", "both", "Canadian resident + ID",
       "Full service; Natbank (Florida).", "nbc.ca"),
    _e("desjardins", "Desjardins", MAJOR, "CA", "both", "Membership (co-op)",
       "Full service co-operative; Desjardins Bank (Florida).", "desjardins.com"),

    # ---- Canada · secondary / challenger ----
    _e("eq", "EQ Bank", SECONDARY, "CA", "both", "Canadian resident + ID",
       "High-interest savings, some mortgages (Equitable), growing business.", "eqbank.ca"),
    _e("tangerine", "Tangerine (Scotia)", SECONDARY, "CA", "personal", "Canadian resident + ID",
       "HISA, cards, loans, mortgages, LOC.", "tangerine.ca"),
    _e("simplii", "Simplii Financial (CIBC)", SECONDARY, "CA", "personal", "Canadian resident + ID",
       "HISA, cards, loans, mortgages, LOC; US-dollar account.", "simplii.com"),
    _e("neo", "Neo Financial", SECONDARY, "CA", "both", "Canadian resident + ID",
       "HISA, credit + secured cards (good credit-builder).", "neofinancial.com"),
    _e("wealthsimple", "Wealthsimple", SECONDARY, "CA", "personal", "Canadian resident + ID",
       "Cash (HISA-like), investing, some credit.", "wealthsimple.com"),
    _e("manulife", "Manulife Bank", SECONDARY, "CA", "both", "Canadian resident + ID",
       "HISA, Manulife One, mortgages, LOC.", "manulifebank.ca"),
    _e("motusbank", "Motive Financial / motusbank", SECONDARY, "CA", "personal", "Canadian resident + ID",
       "HISA, mortgages, loans.", "motusbank.ca"),

    # ---- Canada · credit unions ----
    _e("meridian", "Meridian (ON)", CU, "CA", "both", "Membership (ON resident/ties)",
       "Full service; Tier-2 manual underwriting.", "meridiancu.ca"),
    _e("vancity", "Vancity (BC)", CU, "CA", "both", "Membership (BC)", "Full service; values-based lender.", "vancity.com"),
    _e("coastcapital", "Coast Capital (BC)", CU, "CA", "both", "Membership (BC)", "Full service.", "coastcapitalsavings.com"),
    _e("servus", "Servus / Connect First (AB)", CU, "CA", "both", "Membership (AB)", "Full service.", "servus.ca"),
    _e("alterna", "Alterna Savings (ON)", CU, "CA", "both", "Membership (ON)", "Full service.", "alterna.ca"),
    _e("duca", "DUCA (ON)", CU, "CA", "both", "Membership (ON)", "Full service.", "duca.com"),
    _e("firstontario", "FirstOntario (ON)", CU, "CA", "both", "Membership (ON)", "Full service.", "firstontario.com"),

    # ---- Canada · loan / financing systems ----
    _e("bdc", "BDC (Business Development Bank of Canada)", LOAN, "CA", "business",
       "Canadian for-profit business", "Government business bank: term loans, working capital, advisory.", "bdc.ca"),
    _e("futurpreneur", "Futurpreneur", LOAN, "CA", "business", "Age 18-39, Canadian business",
       "Startup loans + mentoring for young founders.", "futurpreneur.ca"),
    _e("cebn", "Canada Small Business Financing Program (CSBFP)", LOAN, "CA", "business",
       "Small business < $10M revenue", "Government-backed term loans/LOC via your bank.", "ised-isde.canada.ca"),
    _e("factoring", "A/R factoring & merchant advances", LOAN, "CA", "business",
       "Business with receivables/revenue", "Advance 85-95% of invoices; fast working capital (watch cost).", ""),
    _e("fairstone", "Fairstone / goeasy (near-prime)", LOAN, "CA", "personal",
       "Near-prime borrowers", "Personal loans when banks decline (higher rates -- compare).", ""),

    # ---- Cross-border (US) ----
    _e("rbcbank", "RBC Bank (US)", XBORDER, "US", "both",
       "Canadian; no SSN required (uses Canadian relationship)",
       "US accounts, credit cards, mortgages built for Canadians.", "rbcbank.com"),
    _e("tdus", "TD Bank, N.A. (US)", XBORDER, "US", "both", "Canadian cross-border client",
       "Links CA + US TD accounts; US cards.", "td.com"),
    _e("amexgt", "Amex Global Card Transfer", XBORDER, "US", "personal",
       "Existing Canadian Amex + US address/bank",
       "First US card with no US credit history -- the main on-ramp.", "americanexpress.com"),
    _e("capone_itin", "Capital One (ITIN) secured cards", XBORDER, "US", "personal",
       "ITIN accepted in place of SSN", "Platinum/Quicksilver Secured -- ITIN-friendly bootstrap cards.", "capitalone.com"),
    _e("mercury", "Mercury / Relay (US business banking)", XBORDER, "US", "business",
       "US entity (LLC/Corp) + EIN", "Digital US business banking for a US entity you form.", "mercury.com"),
    _e("sba", "US SBA loans (7(a) / microloans)", XBORDER, "US", "business",
       "US business; SBA 8(a) requires US CITIZENSHIP -- generally NOT open to a Canadian",
       "Federal small-business lending; build US business credit (D-U-N-S/PAYDEX) first.", "sba.gov"),

    # ---- Canada · Black entrepreneur programs ----
    _e("bep", "Black Entrepreneurship Program (BEP)", BLACK_CA, "CA", "business",
       "Black-led, majority Black-owned Canadian business",
       "Federal program (renewed $189M, Oct 2025): loan fund + ecosystem + knowledge hub.",
       "ised-isde.canada.ca", black=True),
    _e("face", "FACE — Black Entrepreneurship Loan Fund", BLACK_CA, "CA", "business",
       "Black-led, majority Black-owned for-profit business",
       "Loans $10k-$250k (with BDC) up to 7-yr terms; also a Micro-Loan Program $10k-$25k.",
       "facecoalition.com", black=True),
    _e("bdc_black", "BDC — Black Entrepreneur financing & advice", BLACK_CA, "CA", "business",
       "Black entrepreneurs", "Dedicated financing, advisory, and resources.", "bdc.ca/en/i-am/black-entrepreneur", black=True),
    _e("futur_black", "Futurpreneur — Black Entrepreneur Startup Program", BLACK_CA, "CA", "business",
       "Black founders, age-eligible", "Up to $75k loan financing + mentoring.",
       "futurpreneur.ca/en/offering/black-entrepreneur-startup", black=True),
    _e("rbc_black", "RBC Black Entrepreneur Program", BLACK_CA, "CA", "business",
       "Black entrepreneurs / RBC business clients", "Access to capital, mentorship, and resources.",
       "rbcroyalbank.com/business/advice/blackentrepreneur.html", black=True),
    _e("fbc", "Foundation for Black Communities", BLACK_CA, "CA", "both",
       "Black-led organizations / community initiatives", "Grants & funding for Black communities (org-focused).",
       "forblackcommunities.org", black=True),
    _e("bof", "Black Opportunity Fund", BLACK_CA, "CA", "both",
       "Black-led businesses & non-profits", "Capital + support to Black communities/entrepreneurs.",
       "blackopportunityfund.ca", black=True),
    _e("rise", "Rise Asset Development", BLACK_CA, "CA", "business",
       "Entrepreneurs facing barriers (incl. Black founders)", "Microloans, low-interest financing, mentorship.",
       "riseassetdevelopment.com", black=True),

    # ---- US · Black-owned banks / MDIs / CDFIs ----
    _e("oneunited", "OneUnited Bank", BLACK_US, "US", "both",
       "US resident/account (cross-border foundation needed for a Canadian)",
       "Largest US Black-owned bank (Boston); online.", "oneunited.com", black=True),
    _e("industrial", "Industrial Bank", BLACK_US, "US", "both", "US account (esp. DC/MD area)",
       "Black-owned bank founded 1913 (Washington DC).", "industrial-bank.com", black=True),
    _e("liberty", "Liberty Bank & Trust", BLACK_US, "US", "both", "US account",
       "One of the largest Black-owned banks (New Orleans).", "libertybank.net", black=True),
    _e("carver", "Carver Federal Savings", BLACK_US, "US", "both", "US account (NY area)",
       "Harlem-based Black-owned savings bank.", "carverbank.com", black=True),
    _e("citizenstrust", "Citizens Trust Bank", BLACK_US, "US", "both", "US account (Atlanta area)",
       "Black-owned bank (Atlanta).", "ctbconnect.com", black=True),
    _e("hope", "HOPE Credit Union (CDFI)", BLACK_US, "US", "both", "Membership (Deep South focus)",
       "Black-serving CDFI credit union.", "hopecu.org", black=True),
    _e("fdic_mdi", "FDIC Minority Depository Institutions list", BLACK_US, "US", "both",
       "Directory (research resource)", "Official list of Black-owned & minority banks to choose from.",
       "fdic.gov/minority-depository-institutions-program", black=True),
    _e("cdfi_fund", "US Treasury CDFI Fund directory", BLACK_US, "US", "both",
       "Directory (research resource)", "Certified Community Development Financial Institutions incl. Black-owned MDIs.",
       "cdfifund.gov", black=True),
]


def generate_access_list(country: Optional[str] = None, segment: Optional[str] = None,
                         category: Optional[str] = None, black_focus: Optional[bool] = None) -> List[dict]:
    """Filter the catalog. country in {CA,US}; segment in {personal,business}
    (matches 'both' too); category from CATEGORIES; black_focus True/False/None."""
    out = []
    for e in ACCESS_CATALOG:
        if country and e["country"] != country:
            continue
        if segment and e["segment"] not in (segment, "both"):
            continue
        if category and e["category"] != category:
            continue
        if black_focus is not None and bool(e["black_focus"]) != black_focus:
            continue
        out.append(e)
    return out


def _availability(e: dict, ctx: dict):
    """Return (status, reason) for one access item given the user's context.
    status in {'available','prerequisite','not_eligible'}."""
    if e["id"] == "sba":
        return ("not_eligible", "SBA 8(a) requires US citizenship; 7(a)/microloans still need a US business")
    if e["country"] == "US" and not ctx.get("us_foundation"):
        return ("prerequisite", "Build the US cross-border foundation first (US bank + ITIN/SSN + US address)")
    if e["segment"] == "business" and not ctx.get("business_exists"):
        return ("prerequisite", "Register a business and open a business account first")
    return ("available", "Available now with standard KYC/verification")


def personalize(items: List[dict], ctx: dict) -> List[dict]:
    """Rank access options by how ready the user is for each, most-ready first.
    ctx keys: us_foundation (bool), business_exists (bool)."""
    rank = {"available": 0, "prerequisite": 1, "not_eligible": 2}
    out = []
    for e in items:
        status, reason = _availability(e, ctx)
        out.append({**e, "availability": status, "availability_reason": reason})
    out.sort(key=lambda x: (rank[x["availability"]], x["category"], x["name"]))
    return out


def context_from_db(db) -> dict:
    p = db.get_user_profile()
    return {"us_foundation": p.us_foundation(),
            "business_exists": bool(db.get_business_accounts()) or p.business_bank_months > 0
            or p.business_revenue_monthly > 0}


def render_personalized(items: List[dict]) -> str:
    lines = []
    for e in items:
        tag = {"available": "[READY]", "prerequisite": "[prereq]", "not_eligible": "[not eligible]"}[e["availability"]]
        bf = " (Black-focused)" if e["black_focus"] else ""
        lines.append(f"  {tag} {e['name']} — {e['category']}{bf}")
        lines.append(f"        {e['availability_reason']}")
    return "\n".join(lines)


def render_text(items: List[dict]) -> str:
    if not items:
        return "  (no matches for that filter)"
    lines = []
    cat = None
    for e in sorted(items, key=lambda x: (x["category"], x["name"])):
        if e["category"] != cat:
            cat = e["category"]
            lines.append(f"\n  == {cat} ==")
        flag = " [Black-focused]" if e["black_focus"] else ""
        lines.append(f"  - {e['name']} ({e['country']}/{e['segment']}){flag}")
        lines.append(f"      Access:      {e['access']}")
        lines.append(f"      Eligibility: {e['eligibility']}")
        if e["url"]:
            lines.append(f"      {e['url']}")
    return "\n".join(lines)


DISCLAIMER = ("Reference only. Amounts, terms, and eligibility change -- confirm with each provider. "
              "Many US options require a US cross-border foundation (address + ITIN/SSN + often a US "
              "entity), and some US minority programs (e.g. SBA 8(a)) require US citizenship. "
              "Not legal, tax, or financial advice.")
