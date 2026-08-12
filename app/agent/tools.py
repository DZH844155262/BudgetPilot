from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.risk_service import generate_risk_overview
from app.budget_service import (
    analyze_department_budget,
)
from app.rag.rag_service import (
    answer_policy_question,
)
from app.report_service import (
    generate_budget_report,
)
class BudgetAnalysisInput(BaseModel):
    """预算分析工具的结构化输入。"""

    month: str = Field(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description=(
            "查询月份，格式必须为YYYY-MM，"
            "例如2026-07"
        ),
    )

    department_id: str = Field(
        ...,
        pattern=r"^D\d{3}$",
        description=(
            "部门编号，格式必须为D加三位数字，"
            "例如D001"
        ),
    )


@tool(
    "budget_analysis_tool",
    args_schema=BudgetAnalysisInput,
)
def budget_analysis_tool(
    month: str,
    department_id: str,
) -> dict[str, Any]:
    """查询指定部门和月份的预算执行情况。

    返回预算金额、实际支出、预算执行率和风险状态。
    本工具只读取数据，不修改预算和费用记录。
    """

    try:
        analysis_items = analyze_department_budget(
            month=month,
            department_id=department_id,
        )

    except ValueError as exc:
        return {
            "success": False,
            "month": month,
            "department_id": department_id,
            "error": str(exc),
            "data": [],
        }

    return {
        "success": True,
        "month": month,
        "department_id": department_id,
        "result_count": len(analysis_items),
        "data": analysis_items,
    }

class RiskOverviewInput(BaseModel):
    """风险概览工具的结构化输入。"""

    month: str = Field(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description=(
            "查询月份，格式必须为YYYY-MM，"
            "例如2026-07"
        ),
    )

    department_id: str = Field(
        ...,
        pattern=r"^D\d{3}$",
        description=(
            "部门编号，格式必须为D加三位数字，"
            "例如D001"
        ),
    )

    growth_threshold: float = Field(
        default=20.0,
        ge=0,
        description=(
            "费用环比增长异常阈值，"
            "默认20，表示增长达到20%时触发检查"
        ),
    )

    large_expense_threshold: float = Field(
        default=20000.0,
        ge=0,
        description=(
            "单笔大额费用阈值，"
            "默认20000元"
        ),
    )


@tool(
    "risk_overview_tool",
    args_schema=RiskOverviewInput,
)
def risk_overview_tool(
    month: str,
    department_id: str,
    growth_threshold: float = 20.0,
    large_expense_threshold: float = 20000.0,
) -> dict[str, Any]:
    """查询指定部门和月份的预算风险概览。

    综合预算异常、环比增长异常和大额费用异常，
    返回风险数量、风险等级及异常明细。
    本工具只读取和分析数据，不修改数据库记录。
    """

    try:
        overview = generate_risk_overview(
            month=month,
            department_id=department_id,
            growth_threshold=growth_threshold,
            large_expense_threshold=(
                large_expense_threshold
            ),
        )

    except ValueError as exc:
        return {
            "success": False,
            "month": month,
            "department_id": department_id,
            "error": str(exc),
            "data": {},
        }

    return {
        "success": True,
        "month": month,
        "department_id": department_id,
        "growth_threshold": growth_threshold,
        "large_expense_threshold": (
            large_expense_threshold
        ),
        "data": overview,
    }

class PolicyQuestionInput(BaseModel):
    """企业制度问答工具的结构化输入。"""

    query: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description=(
            "用户提出的企业预算、费用报销"
            "或审批制度问题"
        ),
    )

    top_k: int = Field(
        default=2,
        ge=1,
        le=5,
        description=(
            "经过重排序后提供给大模型的"
            "制度上下文数量，默认2"
        ),
    )


@tool(
    "policy_question_tool",
    args_schema=PolicyQuestionInput,
)
def policy_question_tool(
    query: str,
    top_k: int = 2,
) -> dict[str, Any]:
    """根据企业制度知识库回答预算和报销问题。

    回答只能依据已检索到的制度内容，
    并返回引用来源。制度资料不足时应明确拒答。
    """

    cleaned_query = query.strip()

    try:
        result = answer_policy_question(
            query=cleaned_query,
            top_k=top_k,
        )

    except ValueError as exc:
        return {
            "success": False,
            "query": cleaned_query,
            "error": str(exc),
            "data": {},
        }

    # 兼容Pydantic模型和普通字典
    if hasattr(result, "model_dump"):
        result_data = result.model_dump()

    elif isinstance(result, dict):
        result_data = result

    else:
        result_data = {
            "answer": str(result),
        }

    return {
        "success": True,
        "query": cleaned_query,
        "top_k": top_k,
        "data": result_data,
    }
class BudgetReportInput(BaseModel):
    """预算报告工具的结构化输入。"""

    month: str = Field(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description=(
            "报告月份，格式为YYYY-MM，"
            "例如2026-07"
        ),
    )

    department_id: str = Field(
        ...,
        pattern=r"^D\d{3}$",
        description=(
            "部门编号，例如D002"
        ),
    )


@tool(
    "budget_report_tool",
    args_schema=BudgetReportInput,
)
def budget_report_tool(
    month: str,
    department_id: str,
) -> dict[str, Any]:
    """生成指定部门和月份的预算分析报告。"""

    try:
        report = generate_budget_report(
            month=month,
            department_id=department_id,
        )

    except ValueError as exc:
        return {
            "success": False,
            "month": month,
            "department_id": department_id,
            "error": str(exc),
            "data": {},
        }

    return {
        "success": True,
        "month": month,
        "department_id": department_id,
        "data": report,
    }