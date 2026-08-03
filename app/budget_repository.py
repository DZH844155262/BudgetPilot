from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from .database import SessionLocal
from .models import Budget, Department, Expense


def _get_month_date_range(
    month: str,
) -> tuple[date, date]:
    """返回指定月份的起始日期和下个月起始日期。"""

    year, month_number = map(int, month.split("-"))

    start_date = date(year, month_number, 1)

    if month_number == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month_number + 1, 1)

    return start_date, end_date
def fetch_monthly_actuals(
    month: str,
    department_id: str,
) -> dict[str, Decimal]:
    """查询指定月份和部门各费用科目的实际支出。"""

    start_date, end_date = _get_month_date_range(month)

    with SessionLocal() as session:
        statement = (
            select(
                Expense.category,
                func.sum(
                    Expense.actual_amount
                ).label("actual_amount"),
            )
            .where(
                Expense.department_id == department_id,
                Expense.date >= start_date,
                Expense.date < end_date,
            )
            .group_by(Expense.category)
            .order_by(Expense.category)
        )

        rows = session.execute(statement).all()

    return {
        row.category: row.actual_amount
        for row in rows
    }
def fetch_departments() -> list[dict[str, str]]:
    """从数据库查询全部部门。"""

    with SessionLocal() as session:
        statement = select(
            Department.department_id,
            Department.department_name,
        ).order_by(Department.department_id)

        rows = session.execute(statement).all()

    return [
        {
            "department_id": row.department_id,
            "department_name": row.department_name,
        }
        for row in rows
    ]


def fetch_available_months() -> list[str]:
    """从数据库查询全部可用预算月份。"""

    with SessionLocal() as session:
        statement = (
            select(Budget.month)
            .distinct()
            .order_by(Budget.month)
        )

        months = session.scalars(statement).all()

    return list(months)


def fetch_budget_summary(
    month: str,
    department_id: str,
) -> list[dict[str, str | Decimal]]:
    """查询指定月份和部门的预算及实际费用汇总。"""

    start_date, end_date = _get_month_date_range(month)

    with SessionLocal() as session:
        budget_statement = (
            select(Budget)
            .where(
                Budget.month == month,
                Budget.department_id == department_id,
            )
            .order_by(Budget.category)
        )

        budget_rows = session.scalars(
            budget_statement
        ).all()

        if not budget_rows:
            raise ValueError("未找到对应的预算数据")

        expense_statement = (
            select(
                Expense.category,
                func.sum(
                    Expense.actual_amount
                ).label("actual_amount"),
            )
            .where(
                Expense.department_id == department_id,
                Expense.date >= start_date,
                Expense.date < end_date,
            )
            .group_by(Expense.category)
        )

        expense_rows = session.execute(
            expense_statement
        ).all()

    actual_amounts = {
        row.category: row.actual_amount
        for row in expense_rows
    }

    return [
        {
            "month": budget.month,
            "department_id": budget.department_id,
            "category": budget.category,
            "budget_amount": budget.budget_amount,
            "actual_amount": actual_amounts.get(
                budget.category,
                Decimal("0.00"),
            ),
        }
        for budget in budget_rows
    ]


if __name__ == "__main__":
    print("部门：")
    print(fetch_departments())

    print("\n可用月份：")
    print(fetch_available_months())

    print("\nD001 2026-07 预算汇总：")
    for item in fetch_budget_summary(
        month="2026-07",
        department_id="D001",
    ):
        print(item)