"""
CoreTrust System (CTC) -- Compliance Backbone
=============================================
The rigor that makes this an *auditor*, per the CoreTrust CLAUDE.md:

  * append-only AUDIT LOG (documentation-as-protection; metadata only, no PII)
  * PIPEDA CONSENT record (consent required before handling consumer data)
  * DISPUTE CASE MANAGEMENT with the 30-day clock and the escalation ladder
    (bureau -> Ontario Ministry -> OPC -> the 2025 statutory civil-damages right)
  * STATUTE / RATE CURRENCY registry (flags anything not recently verified)
  * ENCRYPTED BACKUP at rest via AES-256 (openssl), for PIPEDA "encrypt at rest"

Everything here is local. The audit log stores what happened, never sensitive
values (no SIN, no full account numbers).
"""

from __future__ import annotations

import os
import subprocess
from datetime import date, datetime, timedelta
from typing import List, Optional


# ---------------------------------------------------------------------------
# Table bootstrap (owned by this module; never cleared by profile saves)
# ---------------------------------------------------------------------------
def _ensure(db) -> None:
    db.cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT, action TEXT, detail TEXT
        );
        CREATE TABLE IF NOT EXISTS compliance_consent (
            singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
            consent_obtained INTEGER, method TEXT, ts TEXT
        );
        CREATE TABLE IF NOT EXISTS dispute_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creditor TEXT, bureau TEXT, dispute_type TEXT,
            date_sent TEXT, response_due TEXT, status TEXT,
            escalation_stage INTEGER DEFAULT 0, notes TEXT
        );
        """
    )
    db.conn.commit()


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------
def log_event(db, action: str, detail: str = "") -> None:
    """Append an event. Keep `detail` to metadata (e.g. a creditor name or a
    count) -- never a SIN, full card number, or other raw PII."""
    _ensure(db)
    db.cursor.execute("INSERT INTO audit_log (ts, action, detail) VALUES (?,?,?)",
                      (datetime.now().isoformat(timespec="seconds"), action, detail))
    db.conn.commit()


def get_audit_log(db, limit: int = 50) -> List[dict]:
    _ensure(db)
    rows = db.cursor.execute(
        "SELECT ts, action, detail FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [{"ts": r["ts"], "action": r["action"], "detail": r["detail"]} for r in rows]


# ---------------------------------------------------------------------------
# PIPEDA consent
# ---------------------------------------------------------------------------
def set_consent(db, obtained: bool, method: str) -> None:
    _ensure(db)
    db.cursor.execute(
        "INSERT OR REPLACE INTO compliance_consent (singleton, consent_obtained, method, ts)"
        " VALUES (1,?,?,?)",
        (int(obtained), method, datetime.now().isoformat(timespec="seconds")))
    db.conn.commit()
    log_event(db, "consent_set", f"obtained={obtained} method={method}")


def get_consent(db) -> dict:
    _ensure(db)
    r = db.cursor.execute("SELECT * FROM compliance_consent WHERE singleton=1").fetchone()
    if not r:
        return {"consent_obtained": False, "method": "", "ts": ""}
    return {"consent_obtained": bool(r["consent_obtained"]), "method": r["method"], "ts": r["ts"]}


def consent_ok(db) -> bool:
    return get_consent(db)["consent_obtained"]


# ---------------------------------------------------------------------------
# Dispute case management
# ---------------------------------------------------------------------------
ESCALATION_LADDER = [
    "Bureau investigation (30-day statutory window)",
    "Ontario Ministry of Public and Business Service Delivery complaint",
    "Office of the Privacy Commissioner (OPC) complaint",
    "Statutory civil-damages claim (Ontario CRA, 2025 amendment)",
]


def create_dispute_case(db, creditor: str, bureau: str, dispute_type: str,
                        date_sent: Optional[str] = None, notes: str = "") -> int:
    _ensure(db)
    ds = date_sent or date.today().isoformat()
    due = (datetime.strptime(ds, "%Y-%m-%d").date() + timedelta(days=30)).isoformat()
    db.cursor.execute(
        "INSERT INTO dispute_cases (creditor, bureau, dispute_type, date_sent, response_due,"
        " status, escalation_stage, notes) VALUES (?,?,?,?,?,?,?,?)",
        (creditor, bureau, dispute_type, ds, due, "open", 0, notes))
    db.conn.commit()
    cid = db.cursor.lastrowid
    log_event(db, "dispute_case_opened", f"#{cid} {creditor} via {bureau}")
    return cid


def list_dispute_cases(db) -> List[dict]:
    _ensure(db)
    rows = db.cursor.execute("SELECT * FROM dispute_cases ORDER BY id DESC").fetchall()
    out = []
    for r in rows:
        due = datetime.strptime(r["response_due"], "%Y-%m-%d").date()
        days = (due - date.today()).days
        stage = r["escalation_stage"] or 0
        out.append({
            "id": r["id"], "creditor": r["creditor"], "bureau": r["bureau"],
            "dispute_type": r["dispute_type"], "date_sent": r["date_sent"],
            "response_due": r["response_due"], "days_remaining": days,
            "status": r["status"], "escalation_stage": stage,
            "current_step": ESCALATION_LADDER[min(stage, len(ESCALATION_LADDER) - 1)],
            "next_step": (ESCALATION_LADDER[stage + 1] if stage + 1 < len(ESCALATION_LADDER) else "—"),
            "overdue": (r["status"] == "open" and days < 0),
            "notes": r["notes"] or "",
        })
    return out


def update_dispute_case(db, case_id: int, status: Optional[str] = None,
                        escalate: bool = False, notes: Optional[str] = None) -> None:
    _ensure(db)
    r = db.cursor.execute("SELECT * FROM dispute_cases WHERE id=?", (case_id,)).fetchone()
    if not r:
        raise ValueError(f"No dispute case #{case_id}")
    st = status or r["status"]
    stage = (r["escalation_stage"] or 0) + (1 if escalate else 0)
    stage = min(stage, len(ESCALATION_LADDER) - 1)
    nt = notes if notes is not None else r["notes"]
    db.cursor.execute("UPDATE dispute_cases SET status=?, escalation_stage=?, notes=? WHERE id=?",
                      (st, stage, nt, case_id))
    db.conn.commit()
    log_event(db, "dispute_case_updated", f"#{case_id} status={st} stage={stage}")


# ---------------------------------------------------------------------------
# Statute / rate currency registry
# ---------------------------------------------------------------------------
CURRENCY_REGISTRY = [
    {"item": "Ontario Consumer Reporting Act (RSO 1990 c.C.33)", "kind": "statute",
     "source": "ontario.ca/laws/statute/90c33", "last_verified": "2026-03"},
    {"item": "Bank Act s.455.1 (tied selling)", "kind": "statute",
     "source": "laws-lois.justice.gc.ca", "last_verified": "2026-03"},
    {"item": "2026 federal & Ontario income-tax brackets", "kind": "rate",
     "source": "canada.ca / ontario.ca", "last_verified": "2026-07"},
    {"item": "2026 CPP/CPP2/EI limits", "kind": "rate",
     "source": "canada.ca", "last_verified": "2026-07"},
    {"item": "CRA 2026 registered-account limits (TFSA/RRSP/FHSA)", "kind": "rate",
     "source": "CRA MyAccount", "last_verified": "2026-07"},
    {"item": "Ontario CRA maximum reporting periods", "kind": "statute",
     "source": "Ontario CRA", "last_verified": "2026-03"},
]


def statute_currency(stale_after_months: int = 6) -> List[dict]:
    today = date.today()
    out = []
    for e in CURRENCY_REGISTRY:
        y, m = (int(x) for x in e["last_verified"].split("-"))
        age_months = (today.year - y) * 12 + (today.month - m)
        out.append({**e, "age_months": age_months, "stale": age_months > stale_after_months})
    return out


# ---------------------------------------------------------------------------
# Encrypted backup at rest (AES-256 via openssl -- no Python dependency)
# ---------------------------------------------------------------------------
def _openssl() -> str:
    from shutil import which
    p = which("openssl")
    if not p:
        raise RuntimeError("openssl not found on PATH; cannot encrypt/decrypt.")
    return p


def encrypt_backup(db, passphrase: str, out_path: Optional[str] = None) -> str:
    """Write an AES-256 encrypted copy of the database file. Satisfies PIPEDA's
    'encrypt at rest' for backups. Keep the passphrase safe -- it cannot be
    recovered."""
    if not passphrase:
        raise ValueError("A passphrase is required.")
    src = None
    # Find the db file path from the connection.
    for _, name, filename in db.conn.execute("PRAGMA database_list"):
        if name == "main" and filename:
            src = filename
            break
    if not src or not os.path.exists(src):
        raise RuntimeError("Could not locate the database file to back up.")
    out = out_path or (src + ".enc")
    subprocess.run([_openssl(), "enc", "-aes-256-cbc", "-pbkdf2", "-salt",
                    "-in", src, "-out", out, "-pass", "stdin"],
                   input=(passphrase + "\n").encode(), check=True)
    log_event(db, "encrypted_backup", os.path.basename(out))
    return out


def decrypt_backup(enc_path: str, passphrase: str, out_path: Optional[str] = None) -> str:
    out = out_path or (enc_path[:-4] if enc_path.endswith(".enc") else enc_path + ".dec")
    subprocess.run([_openssl(), "enc", "-d", "-aes-256-cbc", "-pbkdf2",
                    "-in", enc_path, "-out", out, "-pass", "stdin"],
                   input=(passphrase + "\n").encode(), check=True)
    return out
