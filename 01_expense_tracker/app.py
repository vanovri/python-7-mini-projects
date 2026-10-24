import argparse
from datetime import date
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from db import (
    CATEGORIES,
    DEFAULT_DB_PATH,
    init_db,
    add_expense,
    delete_expense,
    set_budget,
    get_expenses_df,
    get_category_summary,
    get_monthly_totals,
    check_budget_alerts,
    seed_sample_data,
)


def generate_charts(db_path: Path = DEFAULT_DB_PATH, output_path: Path | None = None):
    cat_df = get_category_summary(db_path=db_path)
    mon_df = get_monthly_totals(db_path=db_path)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    fig.patch.set_facecolor("#ffffff")

    if not cat_df.empty:
        axes[0].barh(cat_df["category"], cat_df["total"], color="#e1306c")
        axes[0].set_title("Spending by Category ($)", fontweight="bold")
        axes[0].invert_yaxis()
        axes[0].grid(axis="x", linestyle="--", alpha=0.4)
    else:
        axes[0].text(0.5, 0.5, "No category data", ha="center", va="center")

    if not mon_df.empty:
        axes[1].plot(
            mon_df["month"],
            mon_df["total"],
            marker="o",
            linewidth=2.5,
            color="#2563eb",
        )
        axes[1].fill_between(mon_df["month"], mon_df["total"], color="#2563eb", alpha=0.12)
        axes[1].set_title("Monthly Totals ($)", fontweight="bold")
        axes[1].grid(True, linestyle="--", alpha=0.4)
    else:
        axes[1].text(0.5, 0.5, "No monthly data", ha="center", va="center")

    plt.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150)
    return fig


def run_cli_demo() -> None:
    init_db()
    count = seed_sample_data()
    print(f"[01 Expense Tracker] Database initialized ({count} records).")
    cat_df = get_category_summary("2026-10")
    print("\n--- Category Breakdown (2026-10) ---")
    print(cat_df.to_string(index=False))

    mon_df = get_monthly_totals()
    print("\n--- Monthly Totals ---")
    print(mon_df.to_string(index=False))

    alerts = check_budget_alerts("2026-10")
    print("\n--- Budget Alerts (2026-10) ---")
    for a in alerts:
        print(
            f"  [{a['status']}] {a['category']}: ${a['spent']:.2f} / ${a['limit']:.2f} ({a['percent']}%)"
        )

    chart_file = Path(__file__).parent / "expense_report.png"
    generate_charts(output_path=chart_file)
    print(f"\nSaved Matplotlib chart to: {chart_file}")


def run_streamlit_ui() -> None:
    import streamlit as st

    st.set_page_config(page_title="01 - Expense Tracker", page_icon="💸", layout="wide")
    init_db()
    seed_sample_data()

    st.title("💸 Project 01: Expense Tracker")
    st.caption("SQLite + Pandas + Matplotlib + Streamlit | CRUD, SQL Queries & Budget Alerts")

    col_form, col_budget = st.columns([2, 1])
    with col_form:
        with st.form("add_expense_form", clear_on_submit=True):
            st.subheader("Add New Expense")
            c1, c2, c3 = st.columns(3)
            exp_date = c1.date_input("Date", value=date.today())
            exp_cat = c2.selectbox("Category", CATEGORIES)
            exp_amt = c3.number_input("Amount ($)", min_value=0.01, value=25.0, step=1.0)
            exp_desc = st.text_input("Description", placeholder="Lunch, groceries, bill...")
            if st.form_submit_button("Save to SQLite", type="primary"):
                add_expense(str(exp_date), exp_cat, exp_amt, exp_desc)
                st.success(f"Added ${exp_amt:.2f} under {exp_cat}!")
                st.rerun()

    with col_budget:
        with st.form("budget_form"):
            st.subheader("Set Monthly Budget Alert")
            b_cat = st.selectbox("Budget Category", CATEGORIES)
            b_lim = st.number_input("Monthly Limit ($)", min_value=10.0, value=200.0, step=10.0)
            if st.form_submit_button("Save Budget"):
                set_budget(b_cat, b_lim)
                st.success(f"Budget set: {b_cat} = ${b_lim:.2f}")
                st.rerun()

    st.divider()
    alerts = check_budget_alerts("2026-10")
    if alerts:
        st.subheader("🎯 Budget Alerts (2026-10)")
        cols = st.columns(len(alerts))
        for idx, a in enumerate(alerts):
            delta_color = "inverse" if a["status"] == "EXCEEDED" else "normal"
            cols[idx].metric(
                label=f"{a['category']} ({a['status']})",
                value=f"${a['spent']:.2f}",
                delta=f"{a['percent']}% of ${a['limit']:.2f}",
                delta_color=delta_color,
            )

    fig = generate_charts()
    st.pyplot(fig)

    st.subheader("📋 All Logged Expenses")
    df = get_expenses_df()
    st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project 01: Expense Tracker")
    parser.add_argument("--cli", action="store_true", help="Run CLI demo & chart generation")
    args, _ = parser.parse_known_args()
    if args.cli:
        run_cli_demo()
    else:
        run_streamlit_ui()
