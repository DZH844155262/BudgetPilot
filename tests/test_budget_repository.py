from decimal import Decimal

from app.budget_repository import (
    fetch_available_months,
    fetch_budget_summary,
    fetch_departments,
    fetch_monthly_actuals,
    fetch_expense_details,
)

def test_fetch_monthly_actuals() -> None:
    """应正确汇总市场部不同月份的实际费用。"""

    july_actuals = fetch_monthly_actuals(
        month="2026-07",
        department_id="D001",
    )

    assert july_actuals == {
        "市场推广费": Decimal("56000.00"),
        "差旅费": Decimal("11500.00"),
        "软件服务费": Decimal("7800.00"),
    }

    june_actuals = fetch_monthly_actuals(
        month="2026-06",
        department_id="D001",
    )

    assert june_actuals == {
        "市场推广费": Decimal("48000.00"),
        "差旅费": Decimal("9000.00"),
        "软件服务费": Decimal("7000.00"),
    }

def test_fetch_departments() -> None:
    """应从PostgreSQL查询全部部门。"""

    departments = fetch_departments()

    assert departments == [
        {
            "department_id": "D001",
            "department_name": "市场部",
        },
        {
            "department_id": "D002",
            "department_name": "研发部",
        },
    ]


def test_fetch_available_months() -> None:
    """应从PostgreSQL查询全部预算月份。"""

    months = fetch_available_months()

    assert months == [
        "2026-06",
        "2026-07",
    ]


def test_fetch_budget_summary() -> None:
    """应正确汇总市场部2026年7月预算和费用。"""

    results = fetch_budget_summary(
        month="2026-07",
        department_id="D001",
    )

    results_by_category = {
        item["category"]: item
        for item in results
    }

    marketing = results_by_category["市场推广费"]
    assert marketing["budget_amount"] == Decimal("50000.00")
    assert marketing["actual_amount"] == Decimal("56000.00")

    travel = results_by_category["差旅费"]
    assert travel["budget_amount"] == Decimal("12000.00")
    assert travel["actual_amount"] == Decimal("11500.00")

    software = results_by_category["软件服务费"]
    assert software["budget_amount"] == Decimal("8000.00")
    assert software["actual_amount"] == Decimal("7800.00")

def test_fetch_expense_details() -> None:
    """应查询市场部2026年7月的全部费用明细。"""

    expenses = fetch_expense_details(
        month="2026-07",
        department_id="D001",
    )

    assert len(expenses) == 5

    expenses_by_id = {
        item["expense_id"]: item
        for item in expenses
    }

    assert expenses_by_id["E007"]["actual_amount"] == Decimal("30000.00")
    assert expenses_by_id["E008"]["actual_amount"] == Decimal("26000.00")
    assert expenses_by_id["E011"]["actual_amount"] == Decimal("7800.00")