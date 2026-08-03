from app.risk_service import generate_risk_overview


def test_generate_risk_overview() -> None:
    """应汇总市场部2026年7月的全部风险。"""

    result = generate_risk_overview(
        month="2026-07",
        department_id="D001",
    )

    assert result["month"] == "2026-07"
    assert result["department_id"] == "D001"

    summary = result["summary"]

    assert summary["total_anomaly_count"] == 6
    assert summary["high_risk_count"] == 3
    assert summary["medium_risk_count"] == 3

    assert len(result["budget_anomalies"]) == 3
    assert len(result["growth_anomalies"]) == 1
    assert len(result["large_expense_anomalies"]) == 2