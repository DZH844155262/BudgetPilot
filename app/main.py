from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

from .budget_service import analyze_department_budget

from .schemas import BudgetAnalysisItem
app = FastAPI(
    title="BudgetPilot API",
    description="企业预算与费用分析智能助手后端接口",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """检查后端服务是否正常运行。"""

    return {
        "status": "ok",
        "service": "BudgetPilot",
    }


@app.get(
    "/budget-analysis",
    response_model=list[BudgetAnalysisItem],
)
def get_budget_analysis(
    month: Annotated[
        str,
        Query(
            pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
            description="统计月份，格式为 YYYY-MM",
            examples=["2026-07"],
        ),
    ],
    department_id: Annotated[
        str,
        Query(
            pattern=r"^D\d{3}$",
            description="部门编号，格式为D加三位数字",
            examples=["D001"],
        ),
    ],
) -> list[dict[str, float | str]]:
    """查询指定月份和部门的预算执行情况。"""

    try:
        return analyze_department_budget(
            month=month,
            department_id=department_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc