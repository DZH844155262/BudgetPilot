from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def load_budget_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """读取部门、预算和费用数据。"""

    departments = pd.read_csv(DATA_DIR / "departments.csv")
    budgets = pd.read_csv(DATA_DIR / "budgets.csv")
    expenses = pd.read_csv(DATA_DIR / "expenses.csv")

    budgets["month"] = budgets["month"].astype(str)
    expenses["date"] = pd.to_datetime(expenses["date"])

    return departments, budgets, expenses


def get_budget_summary(
    month: str,
    department_id: str,
) -> pd.DataFrame:
    """汇总指定月份和部门的预算与实际费用。"""

    _, budgets, expenses = load_budget_data()

    selected_budgets = budgets[
        (budgets["month"] == month)
        & (budgets["department_id"] == department_id)
    ].copy()

    if selected_budgets.empty:
        raise ValueError("未找到对应的预算数据")

    selected_expenses = expenses[
        (expenses["department_id"] == department_id)
        & (expenses["date"].dt.strftime("%Y-%m") == month)
    ]

    expense_summary = (
        selected_expenses.groupby(
            "category",
            as_index=False,
        )["actual_amount"]
        .sum()
    )

    result = selected_budgets.merge(
        expense_summary,
        on="category",
        how="left",
    )

    result["actual_amount"] = result["actual_amount"].fillna(0)

    return result[
        [
            "month",
            "department_id",
            "category",
            "budget_amount",
            "actual_amount",
        ]
    ]


if __name__ == "__main__":
    summary = get_budget_summary(
        month="2026-07",
        department_id="D001",
    )

    print(summary.to_string(index=False))