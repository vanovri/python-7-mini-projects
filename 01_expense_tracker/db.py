import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

DEFAULT_DB_PATH = Path(__file__).parent / "expenses.db"

CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Housing & Utilities",
    "Entertainment",
    "Shopping",
    "Health",
    "Education",
    "Other",
]


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                description TEXT DEFAULT ''
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                monthly_limit REAL NOT NULL CHECK(monthly_limit >= 0)
            )
            """
        )
        conn.commit()


def add_expense(
    date: str,
    category: str,
    amount: float,
    description: str = "",
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
            (date, category, float(amount), description),
        )
        conn.commit()
        return int(cursor.lastrowid)


def delete_expense(expense_id: int, db_path: Path = DEFAULT_DB_PATH) -> bool:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        return cursor.rowcount > 0


def set_budget(
    category: str, monthly_limit: float, db_path: Path = DEFAULT_DB_PATH
) -> None:
    init_db(db_path)
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO budgets (category, monthly_limit)
            VALUES (?, ?)
            ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
            """,
            (category, float(monthly_limit)),
        )
        conn.commit()


def get_expenses_df(
    month_prefix: Optional[str] = None, db_path: Path = DEFAULT_DB_PATH
) -> pd.DataFrame:
    init_db(db_path)
    with get_connection(db_path) as conn:
        if month_prefix:
            query = "SELECT id, date, category, amount, description FROM expenses WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC, id DESC"
            df = pd.read_sql_query(query, conn, params=(month_prefix,))
        else:
            query = "SELECT id, date, category, amount, description FROM expenses ORDER BY date DESC, id DESC"
            df = pd.read_sql_query(query, conn)
    return df


def get_category_summary(
    month_prefix: Optional[str] = None, db_path: Path = DEFAULT_DB_PATH
) -> pd.DataFrame:
    init_db(db_path)
    with get_connection(db_path) as conn:
        if month_prefix:
            query = """
                SELECT category, COUNT(*) as count, ROUND(SUM(amount), 2) as total
                FROM expenses
                WHERE strftime('%Y-%m', date) = ?
                GROUP BY category
                ORDER BY total DESC
            """
            return pd.read_sql_query(query, conn, params=(month_prefix,))
        query = """
            SELECT category, COUNT(*) as count, ROUND(SUM(amount), 2) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        """
        return pd.read_sql_query(query, conn)


def get_monthly_totals(db_path: Path = DEFAULT_DB_PATH) -> pd.DataFrame:
    init_db(db_path)
    with get_connection(db_path) as conn:
        query = """
            SELECT strftime('%Y-%m', date) as month, ROUND(SUM(amount), 2) as total
            FROM expenses
            GROUP BY month
            ORDER BY month ASC
        """
        return pd.read_sql_query(query, conn)


def check_budget_alerts(
    month_prefix: str, db_path: Path = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT b.category, b.monthly_limit, COALESCE(SUM(e.amount), 0) as spent
            FROM budgets b
            LEFT JOIN expenses e
              ON b.category = e.category AND strftime('%Y-%m', e.date) = ?
            GROUP BY b.category, b.monthly_limit
            """,
            (month_prefix,),
        ).fetchall()
    alerts = []
    for r in rows:
        limit_val = float(r["monthly_limit"])
        spent_val = float(r["spent"])
        pct = (spent_val / limit_val * 100.0) if limit_val > 0 else 0.0
        status = "OK"
        if spent_val > limit_val:
            status = "EXCEEDED"
        elif pct >= 80.0:
            status = "WARNING"
        alerts.append(
            {
                "category": r["category"],
                "limit": round(limit_val, 2),
                "spent": round(spent_val, 2),
                "percent": round(pct, 1),
                "status": status,
            }
        )
    return alerts


def seed_sample_data(db_path: Path = DEFAULT_DB_PATH) -> int:
    init_db(db_path)
    df = get_expenses_df(db_path=db_path)
    if not df.empty:
        return len(df)
    samples = [
        ("2026-09-05", "Housing & Utilities", 450.00, "Apartment rent & electricity"),
        ("2026-09-12", "Food & Dining", 85.50, "Weekly groceries"),
        ("2026-09-20", "Transportation", 40.00, "Metro pass & fuel"),
        ("2026-10-01", "Housing & Utilities", 460.00, "October rent & internet"),
        ("2026-10-04", "Food & Dining", 120.75, "Supermarket + coffee"),
        ("2026-10-10", "Entertainment", 65.00, "Concert ticket & streaming"),
        ("2026-10-15", "Food & Dining", 95.25, "Dinner with friends"),
        ("2026-10-18", "Shopping", 140.00, "Mechanical keyboard"),
        ("2026-10-22", "Transportation", 52.30, "Ride share & gas"),
    ]
    for date_str, cat, amt, desc in samples:
        add_expense(date_str, cat, amt, desc, db_path=db_path)

    set_budget("Food & Dining", 200.00, db_path=db_path)
    set_budget("Shopping", 150.00, db_path=db_path)
    set_budget("Entertainment", 100.00, db_path=db_path)
    return len(samples)
