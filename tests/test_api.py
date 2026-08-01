from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    """健康检查接口应正常返回。"""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "BudgetPilot",
    }


def test_budget_analysis_endpoint() -> None:
    """预算分析接口应返回市场部2026年7月分析结果。"""

    response = client.get(
        "/budget-analysis",
        params={
            "month": "2026-07",
            "department_id": "D001",
        },
    )

    assert response.status_code == 200

    results = response.json()

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


def test_missing_budget_returns_404() -> None:
    """不存在的预算数据应返回404。"""

    response = client.get(
        "/budget-analysis",
        params={
            "month": "2026-08",
            "department_id": "D001",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "未找到对应的预算数据",
    }