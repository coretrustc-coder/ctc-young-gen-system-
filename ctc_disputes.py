"""
CoreTrust System (CTC) -- Reporting-Period Auditor & Dispute Letter Drafting
===========================================================================
Ontario Consumer Reporting Act, RSO 1990, c. C.33.

COMPLIANCE POSTURE (read this)
------------------------------
This module helps YOU exercise real, statutory consumer rights on YOUR OWN
credit file. It does NOT:
  * invent or manufacture "discrepancies",
  * ask you to swear anything you have not personally verified,
  * claim a $1 error deletes an entire accurate tradeline (that is a myth, not
    the law), or
  * guarantee deletion of any item.

A dispute is legitimate when the entry is genuinely (and ideally documentably):
  * past the Ontario maximum reporting period,
  * reporting a balance/status you can show is wrong,
  * not yours (mixed file / identity theft),
  * a duplicate, or
  * something the creditor cannot verify on investigation.

Under s.12 of the Act the bureau must investigate a disputed item and correct or
delete what it cannot verify. That is the mechanism -- accuracy, not gamesmanship.

Every generated letter carries the mandatory CoreTrust disclaimer.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional


DISCLAIMER = (
    "For informational and educational purposes only. Not legal advice. "
    "CoreTrust is not a law firm and does not provide legal representation. "
    "Consult a licensed Ontario lawyer or paralegal for legal advice. Only "
    "dispute information you genuinely believe to be inaccurate, incomplete, or "
    "outdated -- knowingly filing a false dispute is itself an offence."
)


# ---------------------------------------------------------------------------
# Ontario maximum reporting periods for negative information.
# Mapping: entry_type -> (max_years, description of the start date)
# Source: Ontario Consumer Reporting Act framework (per CoreTrust CLAUDE.md).
# ---------------------------------------------------------------------------
ONTARIO_MAX_PERIODS = {
    "late_payment":        (6,  "date of last activity"),
    "collection":          (6,  "date of last activity"),
    "judgment":            (6,  "date of judgment"),
    "bankruptcy_first":    (6,  "date of discharge"),
    "bankruptcy_second":   (14, "date of discharge"),
    "consumer_proposal":   (3,  "date the proposal was completed"),
    "secured_chargeoff":   (6,  "date of last activity"),
    "hard_inquiry":        (3,  "date of the inquiry"),
}


def _years_between(start_iso: str, end: Optional[date] = None) -> float:
    end = end or date.today()
    start = datetime.strptime(start_iso, "%Y-%m-%d").date()
    return (end - start).days / 365.25


def audit_reporting_periods(entries: List["object"]) -> List[dict]:
    """Given your CreditReportEntry records, flag those that appear to exceed the
    Ontario maximum reporting period and are therefore legitimately disputable
    as outdated. Returns one result dict per entry."""
    results = []
    for e in entries:
        rule = ONTARIO_MAX_PERIODS.get(e.entry_type)
        if not rule:
            results.append({
                "id": e.id, "creditor": e.creditor, "entry_type": e.entry_type,
                "known_rule": False, "disputable_as_outdated": False,
                "note": "No maximum-period rule mapped for this entry type; "
                        "review manually.",
            })
            continue
        max_years, start_desc = rule
        age = _years_between(e.date_of_last_activity)
        outdated = age > max_years
        results.append({
            "id": e.id, "creditor": e.creditor, "entry_type": e.entry_type,
            "known_rule": True,
            "age_years": round(age, 2),
            "max_years": max_years,
            "clock_starts": start_desc,
            "disputable_as_outdated": outdated,
            "note": (f"Appears to exceed the {max_years}-year Ontario limit "
                     f"(measured from {start_desc}); disputable as outdated."
                     if outdated else
                     f"Within the {max_years}-year Ontario reporting window."),
        })
    return results


# ---------------------------------------------------------------------------
# Letter drafting. Each letter states a GENUINE issue you supply -- the tool
# never fabricates the substance of the dispute.
# ---------------------------------------------------------------------------
LETTER_TYPES = (
    "standard",          # a specific, documentable inaccuracy
    "aged_item",         # entry exceeds Ontario maximum reporting period
    "debt_validation",   # ask a collector to validate before it collects
    "goodwill",          # ask a creditor to remove an ACCURATE isolated late
    "method_of_verification",  # how did the bureau "verify" it?
)


def _header(consumer_name: str, consumer_address: str, file_number: str) -> str:
    today = date.today().strftime("%B %d, %Y")
    fn = f"\nCredit file / reference no.: {file_number}" if file_number else ""
    return (
        f"{consumer_name}\n{consumer_address}{fn}\n\n{today}\n\n"
    )


def generate_dispute_letter(
    letter_type: str,
    consumer_name: str,
    consumer_address: str,
    recipient: str,              # 'Equifax Canada' | 'TransUnion Canada' | collector name
    creditor_name: str,
    account_number: str,
    factual_basis: str,          # YOUR description of the real issue
    file_number: str = "",
    documents_enclosed: Optional[List[str]] = None,
) -> str:
    """Draft a dispute/validation/goodwill letter.

    `factual_basis` is REQUIRED and must describe the genuine problem in your own
    words (e.g. "the balance shows $4,210 but my statement shows $0 as of
    2026-05-01, copy enclosed" or "this collection's date of last activity is
    2018-02-11, which is past the 6-year Ontario limit"). The tool will not
    invent this for you.
    """
    letter_type = letter_type.lower().strip()
    if letter_type not in LETTER_TYPES:
        raise ValueError(f"letter_type must be one of {LETTER_TYPES}")
    if not factual_basis or not factual_basis.strip():
        raise ValueError(
            "factual_basis is required -- describe the real, specific issue. "
            "This tool does not manufacture disputes."
        )

    docs = documents_enclosed or []
    docs_block = ""
    if docs:
        docs_block = "\nEnclosed documentation:\n" + "\n".join(f"  - {d}" for d in docs) + "\n"

    head = _header(consumer_name, consumer_address, file_number)

    if letter_type == "debt_validation":
        body = f"""{recipient}
RE: Debt Validation Request -- {creditor_name}, account no. {account_number}

To Whom It May Concern,

I am requesting validation of the debt referenced above. Please cease collection
activity on this account until you have provided validation, as is my right on a
timely written request.

Please provide:
  1. Confirmation of the amount owed and how it was calculated;
  2. The name of the original creditor;
  3. Documentation establishing your authority to collect this debt.

Reason for this request (in my own words):
{factual_basis.strip()}
{docs_block}
Until I receive this validation, please communicate with me only in writing.

Sincerely,

____________________________________
{consumer_name}
"""
    elif letter_type == "goodwill":
        body = f"""{creditor_name}
RE: Goodwill Adjustment Request -- account no. {account_number}

To Whom It May Concern,

I am writing to request a goodwill adjustment to the reporting on the account
above. I acknowledge the entry is accurate; I am asking you to consider removing
it as a gesture of goodwill given my overall history with you.

Context (in my own words):
{factual_basis.strip()}
{docs_block}
I value our relationship and would be grateful for your consideration. Thank you
for reviewing this request.

Sincerely,

____________________________________
{consumer_name}
"""
    else:
        # standard / aged_item / method_of_verification -> bureau dispute
        if letter_type == "aged_item":
            subject = "Dispute -- Outdated Information (Exceeds Ontario Reporting Period)"
            legal = (
                "Under the Ontario Consumer Reporting Act, R.S.O. 1990, c. C.33, "
                "negative information may only be reported for the periods set out "
                "in the Act. The entry below appears to exceed the applicable "
                "maximum reporting period and should be removed as outdated."
            )
        elif letter_type == "method_of_verification":
            subject = "Request for Method of Verification"
            legal = (
                "I previously disputed this item and it was reported as 'verified'. "
                "Under s.12 of the Ontario Consumer Reporting Act I am asking you to "
                "describe the method of verification used -- specifically, what was "
                "checked with the source creditor to confirm the accuracy of this "
                "entry. If the entry cannot be verified with the original creditor, "
                "it must be corrected or deleted."
            )
        else:  # standard
            subject = "Dispute -- Inaccurate Information"
            legal = (
                "Under s.9 of the Ontario Consumer Reporting Act, a consumer "
                "reporting agency must adopt all procedures reasonable to ensure "
                "the highest possible accuracy. Under s.12, on my dispute you must "
                "investigate this entry with the source creditor and correct or "
                "delete any information that is inaccurate or that cannot be "
                "verified."
            )

        body = f"""{recipient}
Attn: Consumer Dispute / Investigation Department

RE: {subject}
Consumer: {consumer_name}
Disputed entry: {creditor_name}, account no. {account_number}

To Whom It May Concern,

I am disputing the accuracy of the entry identified above.

{legal}

The specific issue (in my own words):
{factual_basis.strip()}
{docs_block}
Please investigate this entry and provide the results of your investigation in
writing. If the information cannot be verified as accurate and complete, please
correct or delete it, and notify any parties who received a report containing
the disputed entry of the correction.

Sincerely,

____________________________________
{consumer_name}
"""

    return head + body + "\n---\n" + DISCLAIMER + "\n"
