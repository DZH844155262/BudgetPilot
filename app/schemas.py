from typing import Any, Literal

from pydantic import BaseModel, Field


class BudgetAnalysisItem(BaseModel):
    """单个费用科目的预算分析结果。"""

    month: str = Field(
        description="统计月份，格式为 YYYY-MM",
        examples=["2026-07"],
    )
    department_id: str = Field(
        description="部门编号",
        examples=["D001"],
    )
    category: str = Field(
        description="费用科目",
        examples=["市场推广费"],
    )
    budget_amount: float = Field(
        description="预算金额",
        ge=0,
    )
    actual_amount: float = Field(
        description="实际费用",
        ge=0,
    )
    execution_rate: float = Field(
        description="预算执行率，单位为百分比",
        ge=0,
    )
    variance: float = Field(
        description="预算差异：实际费用减预算金额",
    )
    remaining: float = Field(
        description="剩余预算：预算金额减实际费用",
    )
    risk_status: Literal[
        "正常",
        "预警",
        "超预算",
    ] = Field(
        description="预算风险状态",
    )
class DepartmentItem(BaseModel):
    """企业部门基础信息。"""

    department_id: str = Field(
        description="部门编号",
        examples=["D001"],
    )
    department_name: str = Field(
        description="部门名称",
        examples=["市场部"],
    )
class BudgetAnomalyItem(BaseModel):
    """单个预算异常事件。"""

    anomaly_type: Literal[
        "over_budget",
        "near_budget_limit",
    ] = Field(description="异常类型")

    severity: Literal[
        "high",
        "medium",
    ] = Field(description="严重程度")

    category: str = Field(description="费用科目")

    execution_rate: float = Field(
        description="预算执行率",
        ge=0,
    )

    amount: float = Field(
        description="超支金额或剩余预算",
        ge=0,
    )

    message: str = Field(description="异常说明")

class BudgetReportSummary(BaseModel):
    """预算报告汇总指标。"""

    total_budget: float = Field(
        description="总预算金额",
        ge=0,
    )
    total_actual: float = Field(
        description="总实际费用",
        ge=0,
    )
    total_remaining: float = Field(
        description="总剩余预算，负数表示整体超预算",
    )
    overall_execution_rate: float = Field(
        description="总体预算执行率",
        ge=0,
    )
    over_budget_count: int = Field(
        description="超预算科目数量",
        ge=0,
    )
    warning_count: int = Field(
        description="预算预警科目数量",
        ge=0,
    )


class BudgetReportResponse(BaseModel):
    """完整预算分析报告。"""

    month: str = Field(
        description="报告月份",
        examples=["2026-07"],
    )
    department_id: str = Field(
        description="部门编号",
        examples=["D001"],
    )
    summary: BudgetReportSummary
    details: list[BudgetAnalysisItem]
    anomalies: list[BudgetAnomalyItem]
    management_summary: str = Field(
        description="管理层关注摘要",
    )
class MonthOverMonthGrowthItem(BaseModel):
    """单个费用环比异常事件。"""

    anomaly_type: Literal[
        "month_over_month_growth"
    ] = Field(description="异常类型")

    severity: Literal[
        "medium"
    ] = Field(description="严重程度")

    category: str = Field(
        description="费用科目"
    )

    current_amount: float = Field(
        description="本月实际费用",
        ge=0,
    )

    previous_amount: float = Field(
        description="上月实际费用",
        ge=0,
    )

    growth_rate: float = Field(
        description="环比增长率，单位为百分比",
        ge=0,
    )

    message: str = Field(
        description="异常说明"
    )


class MonthOverMonthGrowthResponse(BaseModel):
    """费用环比异常分析结果。"""

    month: str = Field(
        description="本月月份",
        examples=["2026-07"],
    )

    previous_month: str = Field(
        description="对比月份",
        examples=["2026-06"],
    )

    department_id: str = Field(
        description="部门编号",
        examples=["D001"],
    )

    threshold: float = Field(
        description="环比异常阈值",
        ge=0,
    )

    previous_data_available: bool = Field(
        description="是否存在上月费用数据"
    )

    anomalies: list[MonthOverMonthGrowthItem]

class LargeExpenseItem(BaseModel):
    """单笔大额费用异常。"""

    anomaly_type: Literal["large_expense"]
    severity: Literal["high"]
    expense_id: str
    date: str
    category: str
    amount: float = Field(ge=0)
    threshold: float = Field(ge=0)
    description: str | None
    message: str


class LargeExpenseResponse(BaseModel):
    """大额费用异常分析结果。"""

    month: str
    department_id: str
    amount_threshold: float = Field(ge=0)
    expense_count: int = Field(ge=0)
    anomaly_count: int = Field(ge=0)
    anomalies: list[LargeExpenseItem]

class RiskOverviewSummary(BaseModel):
    """统一风险总览统计。"""

    total_anomaly_count: int = Field(ge=0)
    high_risk_count: int = Field(ge=0)
    medium_risk_count: int = Field(ge=0)


class RiskOverviewResponse(BaseModel):
    """部门预算统一风险总览。"""

    month: str
    department_id: str
    summary: RiskOverviewSummary
    budget_anomalies: list[BudgetAnomalyItem]
    growth_anomalies: list[MonthOverMonthGrowthItem]
    large_expense_anomalies: list[LargeExpenseItem]

class PolicySearchItem(BaseModel):
    """单个制度检索结果。"""

    chunk_id: str = Field(
        description="制度文档块唯一编号",
    )

    source: str = Field(
        description="来源文件名",
    )

    path: str = Field(
        description="来源文件相对路径",
    )

    content: str = Field(
        description="检索到的制度原文",
    )

    similarity_score: float = Field(
        description="语义相似度，数值越大表示越相关",
        ge=-1,
        le=1,
    )
    document_title: str | None = Field(
    default=None,
    description="制度名称",
)

    section_title: str | None = Field(
    default=None,
    description="制度章节名称",
)

    subsection_title: str | None = Field(
    default=None,
    description="制度子章节名称",
)


class PolicySearchResponse(BaseModel):
    """预算制度语义检索结果。"""

    query: str = Field(
        description="用户原始检索问题",
    )

    top_k: int = Field(
        description="请求返回的最大结果数量",
        ge=1,
        le=10,
    )

    result_count: int = Field(
        description="实际返回的结果数量",
        ge=0,
    )

    results: list[PolicySearchItem]

class PolicyAnswerRequest(BaseModel):
    """制度问答请求。"""

    query: str = Field(
        min_length=1,
        max_length=500,
        description="用户提出的制度问题",
        examples=[
            "单笔费用达到20000元需要谁复核？"
        ],
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="用于回答的制度片段数量",
    )


class PolicyAnswerSource(BaseModel):
    """制度回答引用来源。"""

    citation: str = Field(
        description="回答中的引用编号，例如[1]",
    )

    chunk_id: str = Field(
        description="制度文档块唯一编号",
    )

    source: str = Field(
        description="制度来源文件名",
    )

    document_title: str | None = Field(
        default=None,
        description="制度名称",
    )

    section_title: str | None = Field(
        default=None,
        description="制度章节名称",
    )

    similarity_score: float = Field(
        description="检索相似度",
        ge=-1,
        le=1,
    )


class PolicyAnswerResponse(BaseModel):
    """带制度引用的RAG回答。"""

    query: str = Field(
        description="用户提出的问题",
    )

    answer: str = Field(
        description="大模型依据制度生成的回答",
    )

    model: str = Field(
        description="生成回答所使用的模型",
    )

    source_count: int = Field(
        ge=0,
        description="引用来源数量",
    )

    sources: list[PolicyAnswerSource]

class AgentChatResponse(BaseModel):
    """BudgetPilot Agent统一响应。"""

    thread_id: str

    status: str

    requires_approval: bool = False

    approval_request: dict[str, Any] | None = None

    answer: str

    intent: Literal[
        "budget_analysis",
        "risk_overview",
        "policy_question",
        "budget_report",
        "unknown",
    ]

    routing_source: str | None = None
    route_reason: str | None = None

    department_id: str | None = None
    month: str | None = None

    trace: list[str] = Field(
        default_factory=list,
    )

    details: dict[str, Any] | None = None




class AgentChatRequest(BaseModel):
    """BudgetPilot Agent聊天请求。"""

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="用户发送给Agent的自然语言问题",
    )

    thread_id: str | None = Field(
        default=None,
        description=(
            "会话ID。首次请求为空，"
            "后续请求使用服务端返回的同一个thread_id。"
        ),
    )




class AgentResumeRequest(BaseModel):
    """恢复一个等待人工确认的Agent任务。"""

    thread_id: str = Field(
        ...,
        min_length=1,
        description="等待恢复的LangGraph会话ID",
    )

    approved: bool = Field(
        ...,
        description=(
            "true表示批准执行，"
            "false表示拒绝执行"
        ),
    )