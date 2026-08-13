"""
CoreTrust System (CTC) -- PDF Statement Parsing (best effort)
=============================================================
Extracts transactions from a PDF bank/card statement using `pdftotext` (poppler),
then parses each line for a date + amount. PDF statements vary wildly, so this is
BEST EFFORT: review the parsed rows before you rely on them.

Falls back with a clear message if `pdftotext` isn't installed
(brew install poppler / apt-get install poppler-utils), in which case export a
CSV from your bank and use the CSV importer instead.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from datetime import datetime
from typing import List, Optional

from ctc_models import BusinessAccount

_DATE_RE = re.compile(
    r"\b("
    r"\d{4}-\d{2}-\d{2}"                       # 2026-07-01
    r"|\d{1,2}/\d{1,2}/\d{2,4}"                # 07/01/2026
    r"|[A-Za-z]{3}\.?\s+\d{1,2},?\s+\d{4}"     # Jul 1, 2026
    r"|\d{1,2}\s+[A-Za-z]{3}\.?\s+\d{4}"       # 1 Jul 2026
    r"|[A-Za-z]{3}\.?\s+\d{1,2}"               # Jul 1  (year-less)
    r")\b")
_AMT_RE = re.compile(r"-?\$?\(?\d{1,3}(?:,\d{3})*(?:\.\d{2})\)?-?")
_CREDIT_HINT = re.compile(r"\b(deposit|credit|payment received|refund|received|interest|e-transfer in|reversal)\b", re.I)

_DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%b %d, %Y", "%b %d %Y",
                 "%d %b %Y", "%b. %d, %Y", "%b %d", "%b. %d")


def _norm_date(s: str, year_hint: Optional[int]) -> str:
    s = s.strip().replace(".", "")
    for f in _DATE_FORMATS:
        try:
            d = datetime.strptime(s, f)
            if "%Y" not in f and "%y" not in f and year_hint:
                d = d.replace(year=year_hint)
            return d.date().isoformat()
        except ValueError:
            continue
    return s


def _norm_amount(tok: str) -> Optional[float]:
    neg = tok.strip().startswith("-") or tok.strip().endswith("-") or ("(" in tok and ")" in tok)
    v = tok.replace("$", "").replace(",", "").replace("(", "").replace(")", "").replace("-", "").strip()
    if not v:
        return None
    try:
        f = float(v)
    except ValueError:
        return None
    return -f if neg else f


def pdftotext_available() -> bool:
    return shutil.which("pdftotext") is not None


def extract_text(path: str) -> str:
    if not pdftotext_available():
        raise RuntimeError("pdftotext (poppler) not found. Install poppler, or export a CSV "
                           "from your bank and use the CSV importer (menu 13 -> j).")
    out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, check=True)
    return out.stdout.decode("utf-8", errors="replace")


def parse_pdf_statement(path: str, year_hint: Optional[int] = None) -> List[dict]:
    text = extract_text(path)
    if year_hint is None:
        y = re.search(r"\b(20\d{2})\b", text)
        year_hint = int(y.group(1)) if y else datetime.now().year
    txns = []
    for line in text.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        dm = _DATE_RE.search(line)
        if not dm:
            continue
        amts = _AMT_RE.findall(line)
        amts = [a for a in amts if _norm_amount(a) is not None and abs(_norm_amount(a)) >= 0.01]
        if not amts:
            continue
        val = _norm_amount(amts[-1])          # last money token = the transaction amount
        if val is None or val == 0:
            continue
        is_credit = bool(_CREDIT_HINT.search(line)) or val > 0
        desc = line[dm.end():].strip()[:60]
        txns.append({"date": _norm_date(dm.group(1), year_hint),
                     "amount": round(abs(val), 2),
                     "type": "credit" if is_credit else "debit",
                     "description": desc})
    return txns


def import_pdf_statement(db, path: str, institution: str, account_type: str,
                         year_hint: Optional[int] = None) -> dict:
    txns = parse_pdf_statement(path, year_hint)
    stripped = [{"date": t["date"], "amount": t["amount"], "type": t["type"]} for t in txns]
    existing = {(a.institution, a.account_type): a for a in db.get_business_accounts()}
    key = (institution, account_type)
    if key in existing:
        acct = existing[key]
        acct.transaction_history = acct.transaction_history + stripped
    else:
        acct = BusinessAccount(institution=institution, account_type=account_type,
                               balance=0.0, transaction_history=stripped)
    db.sync_business_account(acct)
    return {"imported": len(stripped), "sample": txns[:8],
            "note": "Best-effort PDF parse -- review the sample rows; correct any wrong "
                    "date/amount/type. For precision, prefer a CSV export."}
