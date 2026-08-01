import pytest

from app.budget_service import analyze_department_budget


def test_analyze_department_budget() -> None:
    """应正确分析市场部2026年7月预算执行情况。"""

    results = analyze_department_budget(
        month="2026-07",
        department_id="D001",
    )

    assert len(results) == 3

    results_by_category = {
        item["category"]: item
        for item in results
    }

    marketing = results_by_category["市场推广费"]

    assert marketing["budget_amount"] == 50000
    assert marketing["actual_amount"] == 56000
    assert marketing["execution_rate"] == 112.0
    assert marketing["risk_status"] == "超预算"

    travel = results_by_category["差旅费"]

    assert travel["budget_amount"] == 12000
    assert travel["actual_amount"] == 11500
    assert travel["execution_rate"] == 95.83
    assert travel["risk_status"] == "预警"

    software = results_by_category["软件服务费"]

    assert software["budget_amount"] == 8000
    assert software["actual_amount"] == 7800
    assert software["execution_rate"] == 97.5
    assert software["risk_status"] == "预警"


def test_missing_budget_data_raises_error() -> None:
    """不存在对应预算数据时，应返回明确错误。"""

    with pytest.raises(
        ValueError,
        match="未找到对应的预算数据",
    ):
        analyze_department_budget(
            month="2026-08",
            department_id="D001",
        )