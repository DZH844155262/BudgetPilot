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