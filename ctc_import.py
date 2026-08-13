"""
CoreTrust System (CTC) -- CSV Statement Importer
================================================
Pull your real data out of bank/card CSV exports instead of typing it in.

Handles the common Canadian/US export shapes:
  * transactions with separate Debit/Credit (or Withdrawal/Deposit) columns
  * transactions with a single signed Amount column
  * a spreadsheet of cards (limit/balance/apr/...) or accounts

Everything runs locally on files you already have. Auto-detection covers most
exports; if a file is unusual you can pass explicit column names/indices.
"""

from __future__ import annotations

import csv
from datetime import datetime
from typing import List, Optional, Union

from ctc_models import CreditCard, PersonalAccount, BusinessAccount

_DATE_FORMATS = (
    "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%d-%m-%Y",
    "%b %d, %Y", "%b %d %Y", "%d-%b-%Y", "%d %b %Y", "%B %d, %Y", "%B %d %Y",
    "%m/%d/%y", "%d/%m/%y",
)

# Header aliases (lowercased) -> logical field.
_DATE_KEYS = ("date", "transaction date", "posting date", "posted", "trans date")
_DESC_KEYS = ("description", "memo", "details", "narration", "payee", "name", "transaction")
_AMOUNT_KEYS = ("amount", "value", "transaction amount")
_DEBIT_KEYS = ("debit", "withdrawal", "withdrawals", "money out", "out", "withdrawal amount")
_CREDIT_KEYS = ("credit", "deposit", "deposits", "money in", "in", "deposit amount")


def _norm_amount(raw: str) -> Optional[float]:
    if raw is None:
        return None
    s = str(raw).strip().replace("$", "").replace(",", "").replace(" ", "")
    if s in ("", "-", "--"):
        return None
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg, s = True, s[1:-1]
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def _norm_date(raw: str, date_format: Optional[str] = None) -> str:
    s = str(raw).strip()
    fmts = (date_format,) if date_format else _DATE_FORMATS
    for f in fmts:
        if not f:
            continue
        try:
            return datetime.strptime(s, f).date().isoformat()
        except ValueError:
            continue
    return s  # leave as-is if unrecognised


def _match(headers: List[str], keys) -> Optional[int]:
    low = [h.strip().lower() for h in headers]
    for i, h in enumerate(low):
        if h in keys:
            return i
    for i, h in enumerate(low):       # loose contains match
        if any(k in h for k in keys):
            return i
    return None


def _read_rows(path: str):
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        reader = csv.reader(fh, dialect)
        return [r for r in reader if any(c.strip() for c in r)]


def parse_transactions_csv(
    path: str,
    debit_positive: bool = False,
    date_format: Optional[str] = None,
    has_header: Optional[bool] = None,
    date_col: Optional[int] = None,
    amount_col: Optional[int] = None,
    debit_col: Optional[int] = None,
    credit_col: Optional[int] = None,
) -> List[dict]:
    """Return [{'date','amount','type'}] from a transactions CSV.

    Sign convention for a single Amount column: by default a negative amount is a
    debit (money out) and positive is a credit (money in). Set debit_positive=True
    if your bank exports debits as positive numbers.
    """
    rows = _read_rows(path)
    if not rows:
        return []

    header = rows[0]
    header_present = has_header
    if header_present is None:
        # header if the "amount-ish" cells in row 0 are non-numeric
        header_present = not any(_norm_amount(c) is not None for c in header)

    if header_present:
        d_i = date_col if date_col is not None else _match(header, _DATE_KEYS)
        amt_i = amount_col if amount_col is not None else _match(header, _AMOUNT_KEYS)
        deb_i = debit_col if debit_col is not None else _match(header, _DEBIT_KEYS)
        cred_i = credit_col if credit_col is not None else _match(header, _CREDIT_KEYS)
        data_rows = rows[1:]
    else:
        d_i, amt_i, deb_i, cred_i = date_col, amount_col, debit_col, credit_col
        data_rows = rows

    if d_i is None:
        raise ValueError("Could not find a date column. Pass date_col=<index>.")
    if amt_i is None and deb_i is None and cred_i is None:
        raise ValueError("Could not find amount or debit/credit columns.")

    txns: List[dict] = []
    for r in data_rows:
        if d_i >= len(r):
            continue
        d = _norm_date(r[d_i], date_format)
        if deb_i is not None or cred_i is not None:
            deb = _norm_amount(r[deb_i]) if (deb_i is not None and deb_i < len(r)) else None
            cred = _norm_amount(r[cred_i]) if (cred_i is not None and cred_i < len(r)) else None
            if cred and cred != 0:
                txns.append({"date": d, "amount": round(abs(cred), 2), "type": "credit"})
            elif deb and deb != 0:
                txns.append({"date": d, "amount": round(abs(deb), 2), "type": "debit"})
        else:
            v = _norm_amount(r[amt_i]) if amt_i < len(r) else None
            if v is None or v == 0:
                continue
            is_credit = (v > 0) if not debit_positive else (v < 0)
            txns.append({"date": d, "amount": round(abs(v), 2),
                         "type": "credit" if is_credit else "debit"})
    return txns


def import_transactions_csv(db, path: str, institution: str, account_type: str,
                            **kwargs) -> int:
    """Parse a transactions CSV and append it to a business account (created if
    it doesn't exist). Returns the number of transactions imported."""
    txns = parse_transactions_csv(path, **kwargs)
    existing = {(a.institution, a.account_type): a for a in db.get_business_accounts()}
    key = (institution, account_type)
    if key in existing:
        acct = existing[key]
        acct.transaction_history = acct.transaction_history + txns
    else:
        acct = BusinessAccount(institution=institution, account_type=account_type,
                               balance=0.0, transaction_history=txns)
    db.sync_business_account(acct)
    return len(txns)


def _row_dict(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _get(row: dict, *aliases, default=""):
    low = {k.strip().lower(): v for k, v in row.items() if k}
    for a in aliases:
        if a in low and str(low[a]).strip() != "":
            return low[a]
    for a in aliases:                 # loose contains
        for k, v in low.items():
            if a in k and str(v).strip() != "":
                return v
    return default


def import_cards_csv(db, path: str) -> int:
    """Import credit cards from a spreadsheet. Recognised headers (any case):
    id/name, institution/bank, limit/credit limit, balance/current balance,
    statement date, apr/rate, min/minimum payment, secured."""
    n = 0
    for row in _row_dict(path):
        cid = _get(row, "id", "name", "card", "label")
        inst = _get(row, "institution", "bank", "issuer")
        if not cid and not inst:
            continue
        db.sync_credit_card(CreditCard(
            id=cid or inst, institution=inst or cid,
            secured=str(_get(row, "secured", default="")).strip().lower() in ("y", "yes", "true", "1"),
            limit_amt=_norm_amount(_get(row, "limit", "credit limit")) or 0.0,
            current_balance=_norm_amount(_get(row, "balance", "current balance")) or 0.0,
            statement_date=_get(row, "statement date", "statement", "date"),
            utilization_history=[],
            last_limit_increase=_get(row, "last limit increase", "last increase"),
            min_payment=_norm_amount(_get(row, "min payment", "minimum payment", "minimum")) or 0.0,
            apr=(_norm_amount(_get(row, "apr", "rate", "interest")) or 0.0)))
        n += 1
    return n


def import_accounts_csv(db, path: str) -> int:
    """Import personal bank accounts. Headers: id/name, institution/bank,
    type (Chequing/Savings), balance, liquid."""
    n = 0
    for row in _row_dict(path):
        aid = _get(row, "id", "name", "account", "label")
        inst = _get(row, "institution", "bank")
        if not aid and not inst:
            continue
        db.sync_personal_account(PersonalAccount(
            id=aid or inst, institution=inst or aid,
            account_type=_get(row, "type", "account type", default="Chequing"),
            balance=_norm_amount(_get(row, "balance")) or 0.0,
            liquid=str(_get(row, "liquid", default="yes")).strip().lower() not in ("n", "no", "false", "0")))
        n += 1
    return n
