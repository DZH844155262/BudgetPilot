from app.report_service import generate_budget_report


def test_generate_budget_report() -> None:
    """应生成市场部2026年7月完整预算报告。"""

    report = generate_budget_report(
        month="2026-07",
        department_id="D001",
    )

    assert report["month"] == "2026-07"
    assert report["department_id"] == "D001"

    summary = report["summary"]

    assert summary["total_budget"] == 70000.0
    assert summary["total_actual"] == 75300.0
    assert summary["total_remaining"] == -5300.0
    assert summary["overall_execution_rate"] == 107.57
    assert summary["over_budget_count"] == 1
    assert summary["warning_count"] == 2

    assert len(report["details"]) == 3
    assert len(report["anomalies"]) == 3

    assert "1个超预算科目" in report["management_summary"]
    assert "2个科目接近预算上限" in report["management_summary"]


def test_missing_budget_report_raises_error() -> None:
    """预算数据不存在时应返回明确错误。"""

    try:
        generate_budget_report(
            month="2026-08",
            department_id="D001",
        )
    except ValueError as exc:
        assert str(exc) == "未找到对应的预算数据"
    else:
        raise AssertionError("预期产生ValueError")