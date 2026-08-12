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

def test_invalid_month_format_returns_422() -> None:
    """月份格式错误时应返回422。"""

    response = client.get(
        "/budget-analysis",
        params={
            "month": "2026/07",
            "department_id": "D001",
        },
    )

    assert response.status_code == 422


def test_invalid_department_id_returns_422() -> None:
    """部门编号格式错误时应返回422。"""

    response = client.get(
        "/budget-analysis",
        params={
            "month": "2026-07",
            "department_id": "市场部",
        },
    )

    assert response.status_code == 422

def test_departments_endpoint() -> None:
    """部门接口应返回全部可查询部门。"""

    response = client.get("/departments")

    assert response.status_code == 200
    assert response.json() == [
        {
            "department_id": "D001",
            "department_name": "市场部",
        },
        {
            "department_id": "D002",
            "department_name": "研发部",
        },
    ]


def test_available_months_endpoint() -> None:
    """月份接口应返回全部可查询月份。"""

    response = client.get("/available-months")

    assert response.status_code == 200
    assert response.json() == [
        "2026-06",
        "2026-07",
    ]
def test_budget_anomalies_endpoint() -> None:
    """异常接口应返回市场部2026年7月预算异常。"""

    response = client.get(
        "/budget-anomalies",
        params={
            "month": "2026-07",
            "department_id": "D001",
        },
    )

    assert response.status_code == 200

    anomalies = response.json()
    assert len(anomalies) == 3

    anomalies_by_category = {
        item["category"]: item
        for item in anomalies
    }

    marketing = anomalies_by_category["市场推广费"]

    assert marketing["anomaly_type"] == "over_budget"
    assert marketing["severity"] == "high"
    assert marketing["amount"] == 6000.0

    travel = anomalies_by_category["差旅费"]

    assert travel["anomaly_type"] == "near_budget_limit"
    assert travel["severity"] == "medium"


def test_missing_budget_anomalies_returns_404() -> None:
    """预算数据不存在时，异常接口应返回404。"""

    response = client.get(
        "/budget-anomalies",
        params={
            "month": "2026-08",
            "department_id": "D001",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "未找到对应的预算数据",
    }
def test_budget_report_endpoint() -> None:
    """报告接口应返回完整预算分析报告。"""

    response = client.get(
        "/budget-report",
        params={
            "month": "2026-07",
            "department_id": "D001",
        },
    )

    assert response.status_code == 200

    report = response.json()
    summary = report["summary"]

    assert report["month"] == "2026-07"
    assert report["department_id"] == "D001"

    assert summary["total_budget"] == 70000.0
    assert summary["total_actual"] == 75300.0
    assert summary["total_remaining"] == -5300.0
    assert summary["overall_execution_rate"] == 107.57
    assert summary["over_budget_count"] == 1
    assert summary["warning_count"] == 2

    assert len(report["details"]) == 3
    assert len(report["anomalies"]) == 3


def test_missing_budget_report_returns_404() -> None:
    """预算数据不存在时，报告接口应返回404。"""

    response = client.get(
        "/budget-report",
        params={
            "month": "2026-08",
            "department_id": "D001",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "未找到对应的预算数据",
    }
def test_expense_growth_anomalies_endpoint() -> None:
    """环比异常接口应返回费用增长异常。"""

    response = client.get(
        "/expense-growth-anomalies",
        params={
            "month": "2026-07",
            "department_id": "D001",
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["month"] == "2026-07"
    assert result["previous_month"] == "2026-06"
    assert result["previous_data_available"] is True

    anomalies = result["anomalies"]

    assert len(anomalies) == 1
    assert anomalies[0]["category"] == "差旅费"
    assert anomalies[0]["growth_rate"] == 27.78


def test_missing_expense_growth_data_returns_404() -> None:
    """当前月份预算不存在时应返回404。"""

    response = client.get(
        "/expense-growth-anomalies",
        params={
            "month": "2026-08",
            "department_id": "D001",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "未找到对应的预算数据",
    }

def test_large_expense_anomalies_endpoint() -> None:
    """大额费用接口应返回两笔异常记录。"""

    response = client.get(
        "/large-expense-anomalies",
        params={
            "month": "2026-07",
            "department_id": "D001",
            "amount_threshold": 20000,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["expense_count"] == 5
    assert result["anomaly_count"] == 2

    anomaly_ids = {
        item["expense_id"]
        for item in result["anomalies"]
    }

    assert anomaly_ids == {
        "E007",
        "E008",
    }


def test_missing_large_expense_data_returns_404() -> None:
    """预算数据不存在时应返回404。"""

    response = client.get(
        "/large-expense-anomalies",
        params={
            "month": "2026-08",
            "department_id": "D001",
            "amount_threshold": 20000,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "未找到对应的预算数据",
    }

def test_risk_overview_endpoint() -> None:
    """风险总览接口应返回全部异常分类。"""

    response = client.get(
        "/risk-overview",
        params={
            "month": "2026-07",
            "department_id": "D001",
        },
    )

    assert response.status_code == 200

    result = response.json()
    summary = result["summary"]

    assert summary["total_anomaly_count"] == 6
    assert summary["high_risk_count"] == 3
    assert summary["medium_risk_count"] == 3

    assert len(result["budget_anomalies"]) == 3
    assert len(result["growth_anomalies"]) == 1
    assert len(result["large_expense_anomalies"]) == 2


def test_missing_risk_overview_returns_404() -> None:
    """预算数据不存在时风险总览应返回404。"""

    response = client.get(
        "/risk-overview",
        params={
            "month": "2026-08",
            "department_id": "D001",
        },
    )

    assert response.status_code == 404

def test_policy_search_endpoint() -> None:
    """制度检索接口应返回相关制度及来源。"""

    response = client.get(
        "/policy-search",
        params={
            "query": "单笔费用达到20000元需要谁复核？",
            "top_k": 2,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["query"] == (
        "单笔费用达到20000元需要谁复核？"
    )
    assert result["result_count"] == 2

    first_result = result["results"][0]

    assert (
        first_result["source"]
        == "expense_reimbursement_policy.md"
    )
    assert "20000元" in first_result["content"]
    assert first_result["similarity_score"] > 0


def test_invalid_policy_search_top_k_returns_422() -> None:
    """非法top_k应在进入业务层前返回422。"""

    response = client.get(
        "/policy-search",
        params={
            "query": "超预算如何处理？",
            "top_k": 0,
        },
    )

    assert response.status_code == 422


def test_blank_policy_search_returns_400() -> None:
    """空白制度问题应返回400。"""

    response = client.get(
        "/policy-search",
        params={
            "query": "   ",
            "top_k": 3,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "检索问题不能为空",
    }

def test_policy_answer_endpoint(
    monkeypatch,
) -> None:
    """制度问答接口应返回回答和引用来源。"""

    def fake_answer_policy_question(
        query: str,
        top_k: int,
    ) -> dict[str, object]:
        return {
            "query": query,
            "answer": (
                "单笔费用达到20000元时，"
                "应由部门负责人和财务人员复核。[1]"
            ),
            "model": "test-model",
            "source_count": 1,
            "sources": [
                {
                    "citation": "[1]",
                    "chunk_id": (
                        "expense_reimbursement_policy-002"
                    ),
                    "source": (
                        "expense_reimbursement_policy.md"
                    ),
                    "document_title": (
                        "企业费用报销管理制度"
                    ),
                    "section_title": (
                        "二、单笔大额费用"
                    ),
                    "similarity_score": 0.7197,
                }
            ],
        }

    monkeypatch.setattr(
        "app.main.answer_policy_question",
        fake_answer_policy_question,
    )

    response = client.post(
        "/policy-answer",
        json={
            "query": (
                "单笔费用达到20000元需要谁复核？"
            ),
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert "部门负责人" in result["answer"]
    assert "[1]" in result["answer"]
    assert result["source_count"] == 1

    first_source = result["sources"][0]

    assert (
        first_source["document_title"]
        == "企业费用报销管理制度"
    )
    assert (
        first_source["section_title"]
        == "二、单笔大额费用"
    )


def test_policy_answer_invalid_top_k_returns_422() -> None:
    """非法top_k应返回422。"""

    response = client.post(
        "/policy-answer",
        json={
            "query": "超预算以后如何处理？",
            "top_k": 0,
        },
    )

    assert response.status_code == 422