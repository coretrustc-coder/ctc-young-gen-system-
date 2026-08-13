"""
CoreTrust System (CTC) -- Rate Watch (Bank of Canada)
=====================================================
Pulls the Bank of Canada policy rate and prime rate from the official Valet API
and caches them locally. A published dashboard can't fetch anything, so the CLI
fetches and stores the values in your database; the Advisor widget then shows the
cached "rate watch" line.

Source: Bank of Canada Valet API (public).
  V39079      = Target for the overnight rate (policy rate)
  V80691311   = Prime rate

Stdlib only (urllib) -- no extra dependencies. Fails quietly (returns cached /
None) if there's no network.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime
from typing import Optional

_VALET = "https://www.bankofcanada.ca/valet/observations/{code}/json?recent=1"
_OVERNIGHT = "V39079"
_PRIME = "V80691311"
# Historical policy->prime spread, used only if the prime series can't be fetched.
_PRIME_SPREAD = 2.20


def _ensure(db) -> None:
    db.cursor.execute(
        "CREATE TABLE IF NOT EXISTS rate_watch ("
        "singleton INTEGER PRIMARY KEY CHECK (singleton = 1),"
        "overnight REAL, prime REAL, as_of TEXT, fetched_ts TEXT, prime_derived INTEGER DEFAULT 0)")
    db.conn.commit()


def _fetch_series(code: str, timeout: float = 12.0):
    try:
        req = urllib.request.Request(_VALET.format(code=code),
                                     headers={"User-Agent": "CoreTrust/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
        obs = data.get("observations", [])
        if not obs:
            return None, None
        last = obs[-1]
        return float(last[code]["v"]), last.get("d")
    except Exception:  # noqa: BLE001 -- offline / API change -> caller falls back
        return None, None


def fetch() -> Optional[dict]:
    overnight, d1 = _fetch_series(_OVERNIGHT)
    if overnight is None:
        return None
    prime, d2 = _fetch_series(_PRIME)
    derived = False
    if prime is None:
        prime = round(overnight + _PRIME_SPREAD, 2)
        derived = True
    return {"overnight": overnight, "prime": prime,
            "as_of": d2 or d1, "prime_derived": derived}


def refresh(db) -> Optional[dict]:
    _ensure(db)
    r = fetch()
    if not r:
        return None
    db.cursor.execute(
        "INSERT OR REPLACE INTO rate_watch (singleton, overnight, prime, as_of, fetched_ts, prime_derived)"
        " VALUES (1,?,?,?,?,?)",
        (r["overnight"], r["prime"], r["as_of"],
         datetime.now().isoformat(timespec="seconds"), int(r["prime_derived"])))
    db.conn.commit()
    return r


def get(db) -> Optional[dict]:
    _ensure(db)
    row = db.cursor.execute("SELECT * FROM rate_watch WHERE singleton = 1").fetchone()
    if not row:
        return None
    return {"overnight": row["overnight"], "prime": row["prime"], "as_of": row["as_of"],
            "fetched_ts": row["fetched_ts"], "prime_derived": bool(row["prime_derived"])}


def rate_impact(db, move: float = 0.0025) -> dict:
    """Estimate the dollar effect of a Bank of Canada policy-rate move on the
    user's prime-linked (variable) debt and their high-interest savings.

    Variable debt = installment debts whose type/lender reads as a line of
    credit / HELOC / variable / prime-linked product (Canadian credit cards are
    typically fixed-rate, so they're excluded). Rate-sensitive savings = liquid
    savings/HISA accounts. `move` is the size of the move (0.0025 = 0.25%)."""
    import re
    var = sum(d.balance for d in db.get_installment_debts()
              if re.search(r"loc|heloc|line|variable|prime", (d.debt_type + " " + d.lender), re.I))
    hisa = sum(a.balance for a in db.get_personal_accounts()
               if a.liquid and re.search(r"sav|hisa|high.?interest", (a.account_type + " " + a.institution), re.I))
    return {"variable_debt": round(var, 2), "hisa_savings": round(hisa, 2),
            "move_pct": move * 100, "debt_cost_change": round(var * move, 2),
            "hisa_earn_change": round(hisa * move, 2), "net_annual": round((hisa - var) * move, 2)}


def impact_line(imp: Optional[dict]) -> str:
    if not imp:
        return ""
    vd, hs, dc, he = imp["variable_debt"], imp["hisa_savings"], imp["debt_cost_change"], imp["hisa_earn_change"]
    if vd == 0 and hs == 0:
        return ("Rate impact: no prime-linked debt or high-interest savings tracked -- a policy-rate "
                "move barely touches your tracked balances.")
    if vd == 0:
        return (f"Rate impact: a 0.25% BoC hike lifts the yield on your ${hs:,.0f} in savings by "
                f"~${he:,.0f}/yr (a cut lowers it); you have no prime-linked debt exposed.")
    if hs == 0:
        return (f"Rate impact: a 0.25% BoC hike raises interest on your ${vd:,.0f} prime-linked debt by "
                f"~${dc:,.0f}/yr (a cut lowers it); no rate-sensitive savings tracked.")
    net = imp["net_annual"]
    return (f"Rate impact: a 0.25% BoC hike -- prime-linked debt (${vd:,.0f}) costs ~${dc:,.0f}/yr more, "
            f"savings (${hs:,.0f}) earns ~${he:,.0f}/yr more -> net ~${abs(net):,.0f}/yr "
            f"{'ahead' if net >= 0 else 'behind'}. A cut is the reverse.")


def summary_line(rw: Optional[dict]) -> str:
    if not rw:
        return "Rate watch: run the advisor (CLI menu 27) to pull current Bank of Canada rates."
    d = " (est.)" if rw.get("prime_derived") else ""
    return (f"Bank of Canada overnight rate {rw['overnight']:.2f}% · prime {rw['prime']:.2f}%{d}"
            f" (as of {rw['as_of']})")
