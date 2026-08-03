import pytest

from app.budget_service import analyze_department_budget,analyze_month_over_month_growth,analyze_large_expenses

def test_analyze_month_over_month_growth() -> None:
    """应识别市场部2026年7月的环比增长异常。"""

    result = analyze_month_over_month_growth(
        month="2026-07",
        department_id="D001",
    )

    assert result["month"] == "2026-07"
    assert result["previous_month"] == "2026-06"
    assert result["department_id"] == "D001"
    assert result["threshold"] == 20.0
    assert result["previous_data_available"] is True

    anomalies = result["anomalies"]

    assert len(anomalies) == 1

    anomaly = anomalies[0]

    assert anomaly["category"] == "差旅费"
    assert anomaly["current_amount"] == 11500.0
    assert anomaly["previous_amount"] == 9000.0
    assert anomaly["growth_rate"] == 27.78

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

def test_analyze_large_expenses() -> None:
    """应识别市场部2026年7月的两笔大额费用。"""

    result = analyze_large_expenses(
        month="2026-07",
        department_id="D001",
        amount_threshold=20000.0,
    )

    assert result["month"] == "2026-07"
    assert result["department_id"] == "D001"
    assert result["amount_threshold"] == 20000.0
    assert result["expense_count"] == 5
    assert result["anomaly_count"] == 2

    anomalies = result["anomalies"]

    assert {
        item["expense_id"]
        for item in anomalies
    } == {
        "E007",
        "E008",
    }