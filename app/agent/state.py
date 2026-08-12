from typing import Any, Literal, TypedDict


AgentIntent = Literal[
    "budget_analysis",
    "risk_overview",
    "policy_question",
    "budget_report",
    "unknown",
]


class AgentState(TypedDict, total=False):
    """BudgetPilot Agent在一次执行中共享的状态。"""

    # 用户输入的原始问题
    user_input: str

    # Agent识别出的业务意图
    intent: AgentIntent

    # 最终返回给用户的回答
    response: str

    # 执行过程中出现的错误
    error: str

    # 记录节点执行顺序，方便调试和展示
    trace: list[str]
    approval_status: str

class AgentState(TypedDict, total=False):
    """BudgetPilot Agent在一次执行中共享的状态。"""

    user_input: str
    intent: AgentIntent

    # 从问题中提取出的业务参数
    month: str
    department_id: str

    # Tool返回的原始结构化结果
    tool_result: dict[str, Any]

    response: str
    error: str
    trace: list[str]
        # 路由器的执行来源和判断说明
    routing_source: str
    route_reason: str
    approval_status: str

class AgentState(TypedDict, total=False):
    """BudgetPilot Agent在一次执行中共享的状态。"""

    user_input: str
    intent: AgentIntent

    month: str
    department_id: str

    # 风险检测阈值
    growth_threshold: float
    large_expense_threshold: float

    tool_result: dict[str, Any]

    response: str
    error: str
    trace: list[str]
        # 路由器的执行来源和判断说明
    routing_source: str
    route_reason: str
    approval_status: str
    skill_name: str | None
skill_content: str | None