"""
CoreTrust System (CTC) -- Business & Entity Layer
=================================================
Track your structure -- personal, operating company, holdco, IP holdco -- and
build a business credit file the legitimate way: net-30 vendors that report to
the business bureaus, paid early, until you have enough tradelines for a PAYDEX
score.

Reference/tracking only. Corporate structuring (holdco/opco, inter-company
agreements) must be set up with a CPA and lawyer; this does not create entities
or give tax advice.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional


ENTITY_TYPES = ["Personal", "Operating Co", "Holdco", "IP Holdco", "Other"]
BUREAUS = ["D&B (PAYDEX)", "Experian Business", "Equifax Business"]


def _ensure(db) -> None:
    db.cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, entity_type TEXT, jurisdiction TEXT, notes TEXT
        );
        CREATE TABLE IF NOT EXISTS business_credit_vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT, net_terms INTEGER, reports_to TEXT,
            account_opened TEXT, last_paid TEXT, paid_on_time INTEGER,
            balance REAL, entity TEXT
        );
        """
    )
    db.conn.commit()


# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------
def add_entity(db, name: str, entity_type: str, jurisdiction: str = "", notes: str = "") -> int:
    _ensure(db)
    if entity_type not in ENTITY_TYPES:
        entity_type = "Other"
    db.cursor.execute("INSERT INTO entities (name, entity_type, jurisdiction, notes) VALUES (?,?,?,?)",
                      (name, entity_type, jurisdiction, notes))
    db.conn.commit()
    return db.cursor.lastrowid


def list_entities(db) -> List[dict]:
    _ensure(db)
    return [dict(r) for r in db.cursor.execute("SELECT * FROM entities ORDER BY id").fetchall()]


# ---------------------------------------------------------------------------
# Business-credit vendor tracker
# ---------------------------------------------------------------------------
def add_vendor(db, vendor: str, net_terms: int, reports_to: str, entity: str = "",
               account_opened: str = "", balance: float = 0.0) -> int:
    _ensure(db)
    db.cursor.execute(
        "INSERT INTO business_credit_vendors (vendor, net_terms, reports_to, account_opened,"
        " last_paid, paid_on_time, balance, entity) VALUES (?,?,?,?,?,?,?,?)",
        (vendor, net_terms, reports_to, account_opened or date.today().isoformat(),
         "", 1, balance, entity))
    db.conn.commit()
    return db.cursor.lastrowid


def record_payment(db, vendor_id: int, on_time: bool, paid_on: Optional[str] = None) -> None:
    _ensure(db)
    db.cursor.execute("UPDATE business_credit_vendors SET last_paid=?, paid_on_time=? WHERE id=?",
                      (paid_on or date.today().isoformat(), int(on_time), vendor_id))
    db.conn.commit()


def list_vendors(db) -> List[dict]:
    _ensure(db)
    return [dict(r) for r in db.cursor.execute(
        "SELECT * FROM business_credit_vendors ORDER BY id").fetchall()]


def business_credit_readiness(db) -> dict:
    """A PAYDEX-readiness read: D&B wants several reporting tradelines paid on
    (or before) terms. Rough guidance: ~3+ reporting, on-time vendors to score."""
    vendors = list_vendors(db)
    reporting = [v for v in vendors if v.get("reports_to")]
    on_time = [v for v in reporting if v.get("paid_on_time")]
    ready = len(on_time) >= 3
    gaps = []
    if len(reporting) < 3:
        gaps.append(f"Add {3 - len(reporting)} more vendor(s) that report to a business bureau.")
    late = [v for v in reporting if not v.get("paid_on_time")]
    if late:
        gaps.append(f"{len(late)} vendor(s) reported late -- pay early (net-terms minus a few days).")
    return {
        "total_vendors": len(vendors),
        "reporting_vendors": len(reporting),
        "on_time_reporting": len(on_time),
        "paydex_ready": ready,
        "gaps": gaps or ["On track -- keep paying reporting vendors early."],
        "note": "Educational. A D-U-N-S number is required for a D&B file; pay before "
                "the due date to build a strong PAYDEX. Not advice.",
    }


def entity_summary(db) -> List[dict]:
    """Group tracked business accounts + vendors by entity name (best-effort;
    business accounts are tagged by institution/type today)."""
    _ensure(db)
    ents = list_entities(db)
    vendors = list_vendors(db)
    out = []
    for e in ents:
        ev = [v for v in vendors if (v.get("entity") or "") == e["name"]]
        out.append({"name": e["name"], "type": e["entity_type"],
                    "jurisdiction": e["jurisdiction"] or "—",
                    "vendors": len(ev), "notes": e["notes"] or ""})
    return out
