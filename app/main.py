from fastapi import FastAPI, HTTPException

from .budget_service import analyze_department_budget


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


@app.get("/budget-analysis")
def get_budget_analysis(
    month: str,
    department_id: str,
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