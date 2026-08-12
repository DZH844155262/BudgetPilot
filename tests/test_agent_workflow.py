from types import SimpleNamespace
from uuid import uuid4

from app.agent import agent_service, workflow

def unique_thread_id() -> str:
    """为每个测试创建独立会话，避免状态互相污染。"""

    return f"test-{uuid4()}"

def test_keyword_router_budget_report():
    """报告请求应优先识别为budget_report。"""

    intent = (
        workflow.classify_intent_by_keywords(
            "帮我生成研发部预算报告"
        )
    )

    assert intent == "budget_report"


def test_keyword_router_risk():
    """风险请求应识别为risk_overview。"""

    intent = (
        workflow.classify_intent_by_keywords(
            "这个部门有哪些高风险异常？"
        )
    )

    assert intent == "risk_overview"


def test_keyword_router_unknown():
    """非业务问题应进入unknown。"""

    intent = (
        workflow.classify_intent_by_keywords(
            "今天天气怎么样？"
        )
    )

    assert intent == "unknown"

def test_extract_analysis_parameters():
    """应从中文自然文本中提取标准部门编号和月份。"""

    state = {
        "user_input": (
            "帮我分析D002部门2026-07"
            "的预算执行情况"
        ),
        "intent": "budget_analysis",
        "trace": [],
    }

    result = (
        workflow
        .extract_analysis_parameters_node(
            state
        )
    )

    assert result["department_id"] == "D002"
    assert result["month"] == "2026-07"
    assert (
        "extract_analysis_parameters"
        in result["trace"]
    )

def test_extract_parameters_missing_month():
    """月份缺失时不应静默猜测。"""

    state = {
        "user_input": "帮我分析D002部门预算",
        "intent": "budget_analysis",
        "trace": [],
    }

    result = (
        workflow
        .extract_analysis_parameters_node(
            state
        )
    )

    assert "error" in result
    assert "查询月份" in result["error"]

def test_short_term_memory_same_thread(
    monkeypatch,
):
    """同一个thread_id应继承上一轮的部门和月份。"""

    thread_id = unique_thread_id()

    def fake_route_user_request(
        user_input: str,
    ):
        if "预算" in user_input:
            return SimpleNamespace(
                intent="budget_analysis",
                department_id="D002",
                month="2026-07",
                growth_threshold=None,
                large_expense_threshold=None,
                reason="测试预算路由",
            )

        return SimpleNamespace(
            intent="risk_overview",
            department_id=None,
            month=None,
            growth_threshold=None,
            large_expense_threshold=None,
            reason="测试风险追问",
        )

    monkeypatch.setattr(
        workflow,
        "route_user_request",
        fake_route_user_request,
    )

    monkeypatch.setattr(
    workflow,
    "budget_analysis_tool",
    SimpleNamespace(
        invoke=lambda _: {
            "success": True,
            "month": "2026-07",
            "department_id": "D002",
            "result_count": 1,
            "data": [
                {
                    "category": "软件服务费",
                    "execution_rate": 96.0,
                }
            ],
        }
    ),
)

    monkeypatch.setattr(
    workflow,
    "risk_overview_tool",
    SimpleNamespace(
        invoke=lambda _: {
            "success": True,
            "month": "2026-07",
            "department_id": "D002",
            "data": {
                "summary": {
                    "total_anomaly_count": 3,
                }
            },
        }
    ),
)

    first_result = (
        agent_service.run_budget_agent(
            user_input=(
                "帮我看看研发部2026-07的预算"
            ),
            thread_id=thread_id,
        )
    )

    assert (
        first_result["department_id"]
        == "D002"
    )
    assert first_result["month"] == "2026-07"

    # 第二轮故意不再提供部门和月份
    second_result = (
        agent_service.run_budget_agent(
            user_input="那风险呢？",
            thread_id=thread_id,
        )
    )

    assert (
        second_result["intent"]
        == "risk_overview"
    )
    assert (
        second_result["department_id"]
        == "D002"
    )
    assert (
        second_result["month"]
        == "2026-07"
    )

def test_hitl_pause_and_resume(
    monkeypatch,
):
    """预算报告应先暂停，批准后才真正执行Tool。"""

    thread_id = unique_thread_id()

    monkeypatch.setattr(
        workflow,
        "route_user_request",
        lambda _: SimpleNamespace(
            intent="budget_report",
            department_id="D002",
            month="2026-07",
            growth_threshold=None,
            large_expense_threshold=None,
            reason="测试报告生成",
        ),
    )

    tool_call_count = {
        "count": 0,
    }

    def fake_report_tool_invoke(_):
        tool_call_count["count"] += 1

        return {
            "success": True,
            "month": "2026-07",
            "department_id": "D002",
            "data": {
                "report": "测试预算报告",
            },
        }

    monkeypatch.setattr(
    workflow,
    "budget_report_tool",
    SimpleNamespace(
        invoke=fake_report_tool_invoke,
    ),
)

    # 第一次执行，应停在interrupt
    first_result = (
        agent_service.run_budget_agent(
            user_input=(
                "帮我生成研发部2026-07"
                "的预算报告"
            ),
            thread_id=thread_id,
        )
    )

    assert (
        first_result["status"]
        == "waiting_for_approval"
    )

    assert (
        first_result["requires_approval"]
        is True
    )

    # 人工批准前，Tool绝对不能执行
    assert tool_call_count["count"] == 0

    # 使用相同thread_id恢复
    second_result = (
        agent_service.resume_budget_agent(
            thread_id=thread_id,
            approved=True,
        )
    )

    assert (
        second_result["status"]
        == "completed"
    )

    assert (
        second_result["requires_approval"]
        is False
    )

    # 批准后才真正执行一次
    assert tool_call_count["count"] == 1