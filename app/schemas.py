from typing import Literal

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