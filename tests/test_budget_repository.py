from decimal import Decimal

from app.budget_repository import (
    fetch_available_months,
    fetch_budget_summary,
    fetch_departments,
)


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