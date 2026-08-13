"""
CoreTrust System (CTC) -- History, Trends, Goals & Deadline Radar
=================================================================
Turns the snapshot tool into a system of record over time:

  * SNAPSHOTS: capture score, net worth, utilization, DTI, liquidity on a date,
    and chart the trajectory (an auditor shows change, not just a moment).
  * GOALS: set targets (score, net worth, utilization, down payment) and track
    progress, with a projected date from your own trend.
  * DEADLINE RADAR: statement dates, credit-limit-increase eligibility, RRSP/
    TFSA/FHSA dates, and open dispute response deadlines -- surfaced before they
    lapse.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Optional

from ctc_dashboard import compute_scorecard


def _ensure(db) -> None:
    db.cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, composite_score REAL, net_worth REAL,
            utilization REAL, dti REAL, best_score INTEGER, liquid REAL
        );
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, metric TEXT, target REAL, deadline TEXT, created TEXT
        );
        """
    )
    db.conn.commit()


# ---------------------------------------------------------------------------
# Snapshots & trends
# ---------------------------------------------------------------------------
def take_snapshot(db, on: Optional[str] = None) -> dict:
    _ensure(db)
    sc = compute_scorecard(db)
    m = db.get_aggregate_metrics()
    nw = db.net_worth()
    row = {
        "date": on or date.today().isoformat(),
        "composite_score": sc["composite_score"],
        "net_worth": nw["net_worth"],
        "utilization": m["aggregate_utilization_pct"],
        "dti": m["estimated_dti_pct"] if m["estimated_dti_pct"] is not None else 0.0,
        "best_score": db.get_user_profile().best_score(),
        "liquid": nw["liquid_assets"],
    }
    db.cursor.execute(
        "INSERT INTO snapshots (date, composite_score, net_worth, utilization, dti, best_score, liquid)"
        " VALUES (?,?,?,?,?,?,?)",
        (row["date"], row["composite_score"], row["net_worth"], row["utilization"],
         row["dti"], row["best_score"], row["liquid"]))
    db.conn.commit()
    return row


def get_snapshots(db) -> List[dict]:
    _ensure(db)
    rows = db.cursor.execute("SELECT * FROM snapshots ORDER BY date, id").fetchall()
    return [dict(r) for r in rows]


_SPARK = "▁▂▃▄▅▆▇█"


def sparkline(values: List[float]) -> str:
    vals = [v for v in values if v is not None]
    if not vals:
        return ""
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return _SPARK[3] * len(vals)
    return "".join(_SPARK[int((v - lo) / (hi - lo) * (len(_SPARK) - 1))] for v in vals)


def trend(db, metric: str = "composite_score") -> dict:
    snaps = get_snapshots(db)
    series = [s[metric] for s in snaps]
    delta = None
    if len(series) >= 2 and series[0] is not None and series[-1] is not None:
        delta = round(series[-1] - series[0], 2)
    return {"metric": metric, "points": len(series), "series": series,
            "spark": sparkline(series), "change": delta,
            "first": series[0] if series else None, "last": series[-1] if series else None}


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------
# Which direction counts as progress for each supported metric.
GOAL_METRICS = {
    "composite_score": "up", "net_worth": "up", "best_score": "up",
    "liquid": "up", "utilization": "down", "dti": "down",
}


def add_goal(db, name: str, metric: str, target: float, deadline: str = "") -> int:
    _ensure(db)
    if metric not in GOAL_METRICS:
        raise ValueError(f"metric must be one of {list(GOAL_METRICS)}")
    db.cursor.execute("INSERT INTO goals (name, metric, target, deadline, created) VALUES (?,?,?,?,?)",
                      (name, metric, target, deadline, date.today().isoformat()))
    db.conn.commit()
    return db.cursor.lastrowid


def _current_value(db, metric: str):
    sc = compute_scorecard(db)
    m = db.get_aggregate_metrics()
    nw = db.net_worth()
    return {"composite_score": sc["composite_score"], "net_worth": nw["net_worth"],
            "best_score": db.get_user_profile().best_score(),
            "liquid": nw["liquid_assets"], "utilization": m["aggregate_utilization_pct"],
            "dti": m["estimated_dti_pct"] or 0.0}[metric]


def list_goals(db) -> List[dict]:
    _ensure(db)
    rows = db.cursor.execute("SELECT * FROM goals ORDER BY id").fetchall()
    snaps = get_snapshots(db)
    out = []
    for r in rows:
        metric, target, direction = r["metric"], r["target"], GOAL_METRICS[r["metric"]]
        cur = _current_value(db, metric)
        if direction == "up":
            reached = cur >= target
            pct = 100.0 if target == 0 else round(min(100.0, cur / target * 100), 1)
        else:
            reached = cur <= target
            pct = 100.0 if cur <= target else round(max(0.0, (target / cur) * 100), 1) if cur else 0.0
        projected = _project(snaps, metric, target, direction)
        out.append({"id": r["id"], "name": r["name"], "metric": metric, "target": target,
                    "current": cur, "direction": direction, "reached": reached,
                    "progress_pct": pct, "deadline": r["deadline"] or "—",
                    "projected_date": projected})
    return out


def _project(snaps: List[dict], metric: str, target: float, direction: str) -> str:
    pts = [(datetime.strptime(s["date"], "%Y-%m-%d").date(), s[metric])
           for s in snaps if s.get(metric) is not None]
    if len(pts) < 2:
        return "need >=2 snapshots"
    (d0, v0), (d1, v1) = pts[0], pts[-1]
    days = (d1 - d0).days or 1
    rate = (v1 - v0) / days   # units per day
    if rate == 0:
        return "flat trend"
    remaining = target - v1
    if (direction == "up" and remaining <= 0) or (direction == "down" and remaining >= 0):
        return "already met"
    if (direction == "up" and rate <= 0) or (direction == "down" and rate >= 0):
        return "trend moving away"
    eta_days = remaining / rate
    if eta_days <= 0 or eta_days > 3650:
        return ">10 yrs at current pace"
    return (d1 + timedelta(days=int(eta_days))).isoformat()


# ---------------------------------------------------------------------------
# Deadline radar
# ---------------------------------------------------------------------------
def _next_statement(iso: str) -> Optional[date]:
    try:
        d = datetime.strptime(iso, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    today = date.today()
    nxt = d
    while nxt < today:
        # advance ~1 month
        month = nxt.month % 12 + 1
        year = nxt.year + (1 if nxt.month == 12 else 0)
        day = min(d.day, 28)
        nxt = date(year, month, day)
    return nxt


def deadline_radar(db, within_days: int = 120) -> List[dict]:
    from ctc_compliance import list_dispute_cases
    today = date.today()
    items = []

    for c in db.get_credit_cards():
        ns = _next_statement(c.statement_date) if c.statement_date else None
        if ns:
            items.append((ns, f"{c.institution} statement date"))
        if c.last_limit_increase:
            try:
                elig = datetime.strptime(c.last_limit_increase, "%Y-%m-%d").date() + timedelta(days=180)
                if elig >= today:
                    items.append((elig, f"{c.institution} limit-increase eligible"))
            except ValueError:
                pass

    # Registered-account milestones
    rrsp_deadline = date(today.year + (1 if today.month > 3 else 0), 3, 1)
    items.append((rrsp_deadline, "RRSP contribution deadline (prior tax year)"))
    tfsa_reset = date(today.year + 1, 1, 1)
    items.append((tfsa_reset, "New TFSA room (annual reset)"))

    # Open dispute deadlines
    for case in list_dispute_cases(db):
        if case["status"] == "open":
            try:
                due = datetime.strptime(case["response_due"], "%Y-%m-%d").date()
                items.append((due, f"Dispute #{case['id']} response due ({case['creditor']})"))
            except ValueError:
                pass

    out = []
    for d, label in sorted(items):
        days = (d - today).days
        if -30 <= days <= within_days:
            out.append({"date": d.isoformat(), "days": days, "label": label,
                        "overdue": days < 0})
    return out
