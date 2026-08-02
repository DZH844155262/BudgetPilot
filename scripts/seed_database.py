from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlalchemy import delete, func, select

from app.database import SessionLocal
from app.models import Budget, Department, Expense


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def seed_database() -> None:
    """将 CSV 模拟数据导入 PostgreSQL。"""

    departments = pd.read_csv(
        DATA_DIR / "departments.csv",
        dtype={"department_id": str},
    )
    budgets = pd.read_csv(
        DATA_DIR / "budgets.csv",
        dtype={
            "month": str,
            "department_id": str,
        },
    )
    expenses = pd.read_csv(
        DATA_DIR / "expenses.csv",
        dtype={
            "expense_id": str,
            "department_id": str,
        },
        parse_dates=["date"],
    )

    with SessionLocal.begin() as session:
        # 按外键依赖顺序清空开发数据
        session.execute(delete(Expense))
        session.execute(delete(Budget))
        session.execute(delete(Department))

        department_objects = [
            Department(
                department_id=str(row.department_id),
                department_name=str(row.department_name),
            )
            for row in departments.itertuples(index=False)
        ]

        session.add_all(department_objects)
        session.flush()

        budget_objects = [
            Budget(
                month=str(row.month),
                department_id=str(row.department_id),
                category=str(row.category),
                budget_amount=Decimal(str(row.budget_amount)),
            )
            for row in budgets.itertuples(index=False)
        ]

        expense_objects = [
            Expense(
                expense_id=str(row.expense_id),
                date=row.date.date(),
                department_id=str(row.department_id),
                category=str(row.category),
                actual_amount=Decimal(str(row.actual_amount)),
                description=(
                    None
                    if pd.isna(row.description)
                    else str(row.description)
                ),
            )
            for row in expenses.itertuples(index=False)
        ]

        session.add_all(budget_objects)
        session.add_all(expense_objects)

    with SessionLocal() as session:
        department_count = session.scalar(
            select(func.count()).select_from(Department)
        )
        budget_count = session.scalar(
            select(func.count()).select_from(Budget)
        )
        expense_count = session.scalar(
            select(func.count()).select_from(Expense)
        )

    print("数据库初始化完成：")
    print(f"- departments：{department_count} 条")
    print(f"- budgets：{budget_count} 条")
    print(f"- expenses：{expense_count} 条")


if __name__ == "__main__":
    seed_database()