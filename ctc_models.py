"""
CoreTrust System (CTC) -- Data Models & Local Store
===================================================
A personal financial tracker for a single Canadian consumer (Ontario / GTA).

SCOPE & COMPLIANCE
------------------
- Stores YOUR OWN financial data locally, on YOUR machine, in a SQLite file.
- Nothing is transmitted anywhere. No third-party credit files are accessed.
- This is a personal-finance and consumer-rights *education* tool. It is not
  legal, tax, or investment advice, and it is not a "credit repair" service or a
  bank-underwriting exploit.

Every figure you enter should be YOUR real, verified number:
  * account & card balances -> your statements
  * credit limits -> your statements / limit-change letters
  * registered-account room -> CRA MyAccount (this is the authoritative source)
  * income -> your pay stubs / T4 / payroll provider
  * credit score -> your Equifax CA / TransUnion CA dashboard
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


# CRA 2026 registered-account contribution limits (annual, current tax year).
# NOTE: RRSP room is 18% of prior-year earned income, capped at the dollar limit
# below. Always confirm YOUR personal room in CRA MyAccount.
CRA_2026_LIMITS = {
    "TFSA": 7000.0,
    "RRSP": 33810.0,
    "FHSA": 8000.0,
}

# Fallback APR used only to *estimate* card interest when you haven't entered the
# card's real rate. Clearly labelled wherever it is used.
ASSUMED_CARD_APR = 0.1999


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class PersonalAccount:
    id: str
    institution: str
    account_type: str          # 'Chequing', 'Savings', 'GIC', ...
    balance: float
    liquid: bool = True        # counts toward emergency-fund / liquidity
    last_updated: str = field(default_factory=lambda: date.today().isoformat())


@dataclass
class CreditCard:
    id: str
    institution: str
    secured: bool
    limit_amt: float
    current_balance: float
    statement_date: str        # 'YYYY-MM-DD'
    utilization_history: List[float] = field(default_factory=list)
    last_limit_increase: str = ""
    min_payment: float = 0.0
    apr: float = 0.0           # e.g. 0.1999 for 19.99%; 0 = unknown -> estimate

    def utilization(self) -> float:
        if self.limit_amt <= 0:
            return 0.0
        return round(self.current_balance / self.limit_amt, 4)

    def estimated_min_payment(self) -> float:
        if self.min_payment > 0:
            return round(self.min_payment, 2)
        if self.current_balance <= 0:
            return 0.0
        return round(max(10.0, 0.03 * self.current_balance), 2)

    def estimated_annual_interest(self) -> float:
        """Annual interest if you carry the current balance. Uses your real APR
        if entered, else a labelled assumed rate."""
        if self.current_balance <= 0:
            return 0.0
        rate = self.apr if self.apr > 0 else ASSUMED_CARD_APR
        return round(self.current_balance * rate, 2)


@dataclass
class InstallmentDebt:
    id: str
    lender: str
    debt_type: str
    balance: float
    monthly_payment: float
    interest_rate: float = 0.0


@dataclass
class RegisteredPortfolio:
    portfolio_type: str        # 'TFSA', 'RRSP', 'FHSA'
    contribution_limit: float  # YOUR room from CRA MyAccount
    contributed_ytd: float
    last_contribution: str = ""
    market_value: float = 0.0  # current value of holdings (for net worth)

    def remaining_room(self) -> float:
        return round(self.contribution_limit - self.contributed_ytd, 2)


@dataclass
class IncomeSource:
    source: str
    gross_monthly: float
    net_monthly: float
    next_pay_date: str = ""


@dataclass
class BusinessAccount:
    institution: str
    account_type: str
    balance: float
    transaction_history: List[dict] = field(default_factory=list)


@dataclass
class Asset:
    """Any balance-sheet asset: real estate, vehicle, equipment, crypto, IP,
    a domain/website, private shares, etc. Digital assets are just a category."""
    id: str
    name: str
    category: str              # 'Real Estate','Vehicle','Equipment','Crypto','IP','Other'
    market_value: float
    associated_debt: float = 0.0   # debt secured by THIS asset (e.g. a mortgage)
    liquid: bool = False

    def equity(self) -> float:
        return round(self.market_value - self.associated_debt, 2)


@dataclass
class CreditReportEntry:
    id: str
    bureau: str
    creditor: str
    entry_type: str
    status: str
    reported_balance: float
    date_of_last_activity: str


@dataclass
class UserProfile:
    """Single-row profile used by the readiness / dashboard engines."""
    equifax_score: int = 0
    transunion_score: int = 0
    monthly_housing_cost: float = 0.0   # rent or prospective mortgage PITI
    time_in_business_years: float = 0.0
    business_revenue_monthly: float = 0.0
    business_bank_months: int = 0        # months the business account has existed
    monthly_expenses: float = 0.0        # for emergency-fund months (optional)
    # US cross-border foundation (for matching US products honestly).
    us_bank_account: bool = False
    us_tax_id: bool = False              # ITIN or SSN on file
    us_address: bool = False

    def best_score(self) -> int:
        return max(self.equifax_score, self.transunion_score)

    def us_foundation(self) -> bool:
        return bool(self.us_bank_account and self.us_tax_id and self.us_address)


# ---------------------------------------------------------------------------
# Local SQLite store
# ---------------------------------------------------------------------------
class CTCDatabase:
    def __init__(self, db_path: str = "coretrust_system.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._initialize_database()
        self._migrate()

    def _initialize_database(self) -> None:
        self.cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY, institution TEXT, account_type TEXT,
                balance REAL, liquid INTEGER DEFAULT 1, last_updated TEXT
            );
            CREATE TABLE IF NOT EXISTS credit_cards (
                id TEXT PRIMARY KEY, institution TEXT, secured INTEGER,
                limit_amt REAL, current_balance REAL, statement_date TEXT,
                utilization_history TEXT, last_limit_increase TEXT,
                min_payment REAL, apr REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS installment_debts (
                id TEXT PRIMARY KEY, lender TEXT, debt_type TEXT,
                balance REAL, monthly_payment REAL, interest_rate REAL
            );
            CREATE TABLE IF NOT EXISTS portfolios (
                portfolio_type TEXT PRIMARY KEY, contribution_limit REAL,
                contributed_ytd REAL, last_contribution TEXT, market_value REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS income (
                source TEXT PRIMARY KEY, gross_monthly REAL, net_monthly REAL, next_pay_date TEXT
            );
            CREATE TABLE IF NOT EXISTS business_accounts (
                id TEXT PRIMARY KEY, institution TEXT, account_type TEXT,
                balance REAL, transaction_log TEXT
            );
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY, name TEXT, category TEXT,
                market_value REAL, associated_debt REAL DEFAULT 0, liquid INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS credit_report_entries (
                id TEXT PRIMARY KEY, bureau TEXT, creditor TEXT, entry_type TEXT,
                status TEXT, reported_balance REAL, date_of_last_activity TEXT
            );
            CREATE TABLE IF NOT EXISTS user_profile (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                equifax_score INTEGER, transunion_score INTEGER,
                monthly_housing_cost REAL, time_in_business_years REAL,
                business_revenue_monthly REAL, business_bank_months INTEGER,
                monthly_expenses REAL,
                us_bank_account INTEGER DEFAULT 0, us_tax_id INTEGER DEFAULT 0,
                us_address INTEGER DEFAULT 0
            );
            """
        )
        self.conn.commit()

    def _migrate(self) -> None:
        """Add columns/tables introduced after an earlier DB was created."""
        def cols(table: str) -> set:
            return {r["name"] for r in self.cursor.execute(f"PRAGMA table_info({table})")}
        if "apr" not in cols("credit_cards"):
            self.cursor.execute("ALTER TABLE credit_cards ADD COLUMN apr REAL DEFAULT 0")
        if "market_value" not in cols("portfolios"):
            self.cursor.execute("ALTER TABLE portfolios ADD COLUMN market_value REAL DEFAULT 0")
        if "liquid" not in cols("accounts"):
            self.cursor.execute("ALTER TABLE accounts ADD COLUMN liquid INTEGER DEFAULT 1")
        for col in ("us_bank_account", "us_tax_id", "us_address"):
            if col not in cols("user_profile"):
                self.cursor.execute(f"ALTER TABLE user_profile ADD COLUMN {col} INTEGER DEFAULT 0")
        self.conn.commit()

    # ---- upserts --------------------------------------------------------
    def sync_personal_account(self, a: PersonalAccount) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO accounts (id, institution, account_type, balance, liquid, last_updated)"
            " VALUES (?,?,?,?,?,?)",
            (a.id, a.institution, a.account_type, a.balance, int(a.liquid), a.last_updated))
        self.conn.commit()

    def sync_credit_card(self, c: CreditCard) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO credit_cards (id, institution, secured, limit_amt, current_balance,"
            " statement_date, utilization_history, last_limit_increase, min_payment, apr)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (c.id, c.institution, int(c.secured), c.limit_amt, c.current_balance, c.statement_date,
             json.dumps(c.utilization_history), c.last_limit_increase, c.min_payment, c.apr))
        self.conn.commit()

    def sync_installment_debt(self, d: InstallmentDebt) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO installment_debts (id, lender, debt_type, balance, monthly_payment, interest_rate)"
            " VALUES (?,?,?,?,?,?)",
            (d.id, d.lender, d.debt_type, d.balance, d.monthly_payment, d.interest_rate))
        self.conn.commit()

    def sync_portfolio(self, p: RegisteredPortfolio) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO portfolios (portfolio_type, contribution_limit, contributed_ytd,"
            " last_contribution, market_value) VALUES (?,?,?,?,?)",
            (p.portfolio_type, p.contribution_limit, p.contributed_ytd, p.last_contribution, p.market_value))
        self.conn.commit()

    def sync_income(self, i: IncomeSource) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO income (source, gross_monthly, net_monthly, next_pay_date) VALUES (?,?,?,?)",
            (i.source, i.gross_monthly, i.net_monthly, i.next_pay_date))
        self.conn.commit()

    def sync_business_account(self, a: BusinessAccount) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO business_accounts (id, institution, account_type, balance, transaction_log)"
            " VALUES (?,?,?,?,?)",
            (f"{a.institution}_{a.account_type}", a.institution, a.account_type, a.balance,
             json.dumps(a.transaction_history)))
        self.conn.commit()

    def sync_asset(self, a: Asset) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO assets (id, name, category, market_value, associated_debt, liquid)"
            " VALUES (?,?,?,?,?,?)",
            (a.id, a.name, a.category, a.market_value, a.associated_debt, int(a.liquid)))
        self.conn.commit()

    def sync_credit_report_entry(self, e: CreditReportEntry) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO credit_report_entries (id, bureau, creditor, entry_type, status,"
            " reported_balance, date_of_last_activity) VALUES (?,?,?,?,?,?,?)",
            (e.id, e.bureau, e.creditor, e.entry_type, e.status, e.reported_balance, e.date_of_last_activity))
        self.conn.commit()

    def sync_user_profile(self, p: UserProfile) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO user_profile (singleton, equifax_score, transunion_score,"
            " monthly_housing_cost, time_in_business_years, business_revenue_monthly, business_bank_months,"
            " monthly_expenses, us_bank_account, us_tax_id, us_address) VALUES (1,?,?,?,?,?,?,?,?,?,?)",
            (p.equifax_score, p.transunion_score, p.monthly_housing_cost, p.time_in_business_years,
             p.business_revenue_monthly, p.business_bank_months, p.monthly_expenses,
             int(p.us_bank_account), int(p.us_tax_id), int(p.us_address)))
        self.conn.commit()

    # ---- readers --------------------------------------------------------
    def get_personal_accounts(self) -> List[PersonalAccount]:
        rows = self.cursor.execute("SELECT * FROM accounts").fetchall()
        return [PersonalAccount(id=r["id"], institution=r["institution"], account_type=r["account_type"],
                                balance=r["balance"], liquid=bool(r["liquid"]),
                                last_updated=r["last_updated"] or "") for r in rows]

    def get_credit_cards(self) -> List[CreditCard]:
        rows = self.cursor.execute("SELECT * FROM credit_cards").fetchall()
        return [CreditCard(id=r["id"], institution=r["institution"], secured=bool(r["secured"]),
                           limit_amt=r["limit_amt"], current_balance=r["current_balance"],
                           statement_date=r["statement_date"],
                           utilization_history=json.loads(r["utilization_history"] or "[]"),
                           last_limit_increase=r["last_limit_increase"] or "",
                           min_payment=r["min_payment"] or 0.0, apr=r["apr"] or 0.0) for r in rows]

    def get_installment_debts(self) -> List[InstallmentDebt]:
        rows = self.cursor.execute("SELECT * FROM installment_debts").fetchall()
        return [InstallmentDebt(id=r["id"], lender=r["lender"], debt_type=r["debt_type"],
                                balance=r["balance"], monthly_payment=r["monthly_payment"],
                                interest_rate=r["interest_rate"] or 0.0) for r in rows]

    def get_portfolios(self) -> List[RegisteredPortfolio]:
        rows = self.cursor.execute("SELECT * FROM portfolios").fetchall()
        return [RegisteredPortfolio(portfolio_type=r["portfolio_type"], contribution_limit=r["contribution_limit"],
                                    contributed_ytd=r["contributed_ytd"], last_contribution=r["last_contribution"] or "",
                                    market_value=r["market_value"] or 0.0) for r in rows]

    def get_income_sources(self) -> List[IncomeSource]:
        rows = self.cursor.execute("SELECT * FROM income").fetchall()
        return [IncomeSource(source=r["source"], gross_monthly=r["gross_monthly"],
                             net_monthly=r["net_monthly"], next_pay_date=r["next_pay_date"] or "") for r in rows]

    def get_business_accounts(self) -> List[BusinessAccount]:
        rows = self.cursor.execute("SELECT * FROM business_accounts").fetchall()
        return [BusinessAccount(institution=r["institution"], account_type=r["account_type"], balance=r["balance"],
                                transaction_history=json.loads(r["transaction_log"] or "[]")) for r in rows]

    def get_assets(self) -> List[Asset]:
        rows = self.cursor.execute("SELECT * FROM assets").fetchall()
        return [Asset(id=r["id"], name=r["name"], category=r["category"], market_value=r["market_value"],
                      associated_debt=r["associated_debt"] or 0.0, liquid=bool(r["liquid"])) for r in rows]

    def get_credit_report_entries(self) -> List[CreditReportEntry]:
        rows = self.cursor.execute("SELECT * FROM credit_report_entries").fetchall()
        return [CreditReportEntry(id=r["id"], bureau=r["bureau"], creditor=r["creditor"], entry_type=r["entry_type"],
                                  status=r["status"], reported_balance=r["reported_balance"],
                                  date_of_last_activity=r["date_of_last_activity"]) for r in rows]

    def get_user_profile(self) -> UserProfile:
        r = self.cursor.execute("SELECT * FROM user_profile WHERE singleton = 1").fetchone()
        if not r:
            return UserProfile()
        return UserProfile(equifax_score=r["equifax_score"] or 0, transunion_score=r["transunion_score"] or 0,
                           monthly_housing_cost=r["monthly_housing_cost"] or 0.0,
                           time_in_business_years=r["time_in_business_years"] or 0.0,
                           business_revenue_monthly=r["business_revenue_monthly"] or 0.0,
                           business_bank_months=r["business_bank_months"] or 0,
                           monthly_expenses=r["monthly_expenses"] or 0.0,
                           us_bank_account=bool(r["us_bank_account"]), us_tax_id=bool(r["us_tax_id"]),
                           us_address=bool(r["us_address"]))

    # ---- metrics --------------------------------------------------------
    def get_aggregate_metrics(self) -> dict:
        cards = self.get_credit_cards()
        debts = self.get_installment_debts()
        income = self.get_income_sources()

        tot_bal = sum(c.current_balance for c in cards)
        tot_lim = sum(c.limit_amt for c in cards)
        utilization = round((tot_bal / tot_lim) * 100, 2) if tot_lim > 0 else 0.0
        gross_income = sum(i.gross_monthly for i in income)

        card_minimums = sum(c.estimated_min_payment() for c in cards)
        installment_payments = sum(d.monthly_payment for d in debts)
        monthly_debt = card_minimums + installment_payments
        dti = round((monthly_debt / gross_income) * 100, 2) if gross_income > 0 else None
        any_est = any(c.min_payment <= 0 and c.current_balance > 0 for c in cards)

        return {
            "total_card_balance": round(tot_bal, 2),
            "total_card_limit": round(tot_lim, 2),
            "aggregate_utilization_pct": utilization,
            "gross_monthly_income": round(gross_income, 2),
            "monthly_debt_obligations": round(monthly_debt, 2),
            "estimated_dti_pct": dti,
            "dti_uses_estimated_minimums": any_est,
        }

    def net_worth(self) -> dict:
        """Assets minus liabilities. To avoid double counting, record a debt in
        exactly one place: a standalone loan as an installment debt, or a debt
        secured by a tracked asset (e.g. a mortgage) as that asset's
        associated_debt -- not both."""
        accounts = self.get_personal_accounts()
        biz = self.get_business_accounts()
        ports = self.get_portfolios()
        assets = self.get_assets()
        cards = self.get_credit_cards()
        debts = self.get_installment_debts()

        cash = sum(a.balance for a in accounts)
        business_cash = sum(b.balance for b in biz)
        registered = sum(p.market_value for p in ports)
        other_assets = sum(a.market_value for a in assets)
        total_assets = cash + business_cash + registered + other_assets

        card_debt = sum(c.current_balance for c in cards)
        installment = sum(d.balance for d in debts)
        secured_on_assets = sum(a.associated_debt for a in assets)
        total_liabilities = card_debt + installment + secured_on_assets

        liquid = sum(a.balance for a in accounts if a.liquid) + sum(a.market_value for a in assets if a.liquid)

        return {
            "assets": {
                "cash_accounts": round(cash, 2),
                "business_cash": round(business_cash, 2),
                "registered_value": round(registered, 2),
                "other_assets": round(other_assets, 2),
                "total": round(total_assets, 2),
            },
            "liabilities": {
                "credit_cards": round(card_debt, 2),
                "installment_debts": round(installment, 2),
                "secured_on_assets": round(secured_on_assets, 2),
                "total": round(total_liabilities, 2),
            },
            "liquid_assets": round(liquid, 2),
            "net_worth": round(total_assets - total_liabilities, 2),
        }

    @staticmethod
    def cash_flow_summary(transactions: List[dict]) -> dict:
        if not transactions:
            return {"transaction_count": 0, "total_inflow": 0.0, "total_outflow": 0.0,
                    "net_flow": 0.0, "savings_rate_pct": None}
        inflow = sum(t["amount"] for t in transactions if t.get("type") == "credit")
        outflow = sum(t["amount"] for t in transactions if t.get("type") == "debit")
        net = inflow - outflow
        savings_rate = round((net / inflow) * 100, 2) if inflow > 0 else None
        return {"transaction_count": len(transactions), "total_inflow": round(inflow, 2),
                "total_outflow": round(outflow, 2), "net_flow": round(net, 2),
                "savings_rate_pct": savings_rate}

    # ---- bulk import ----------------------------------------------------
    def import_from_json(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        counts = {}
        for a in data.get("personal_accounts", []):
            self.sync_personal_account(PersonalAccount(**a))
        counts["personal_accounts"] = len(data.get("personal_accounts", []))
        for c in data.get("credit_cards", []):
            self.sync_credit_card(CreditCard(**c))
        counts["credit_cards"] = len(data.get("credit_cards", []))
        for d in data.get("installment_debts", []):
            self.sync_installment_debt(InstallmentDebt(**d))
        counts["installment_debts"] = len(data.get("installment_debts", []))
        for p in data.get("portfolios", []):
            self.sync_portfolio(RegisteredPortfolio(**p))
        counts["portfolios"] = len(data.get("portfolios", []))
        for i in data.get("income", []):
            self.sync_income(IncomeSource(**i))
        counts["income"] = len(data.get("income", []))
        for b in data.get("business_accounts", []):
            self.sync_business_account(BusinessAccount(**b))
        counts["business_accounts"] = len(data.get("business_accounts", []))
        for a in data.get("assets", []):
            self.sync_asset(Asset(**a))
        counts["assets"] = len(data.get("assets", []))
        for e in data.get("credit_report_entries", []):
            self.sync_credit_report_entry(CreditReportEntry(**e))
        counts["credit_report_entries"] = len(data.get("credit_report_entries", []))
        if "user_profile" in data:
            self.sync_user_profile(UserProfile(**data["user_profile"]))
            counts["user_profile"] = 1
        return counts

    def clear_all(self) -> None:
        """Wipe all editable tables. Used by the live dashboard's Save so the
        database mirrors the editor exactly (including rows you deleted)."""
        for t in ("accounts", "credit_cards", "installment_debts", "portfolios",
                  "income", "business_accounts", "assets", "credit_report_entries",
                  "user_profile"):
            self.cursor.execute(f"DELETE FROM {t}")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
