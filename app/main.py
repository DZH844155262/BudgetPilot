from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from .risk_service import generate_risk_overview
from .report_service import generate_budget_report
from .schemas import (
    BudgetAnalysisItem,
    BudgetAnomalyItem,
    BudgetReportResponse,
    DepartmentItem,
    LargeExpenseResponse,
    MonthOverMonthGrowthResponse,
    RiskOverviewResponse,
)

from .budget_service import (
    analyze_budget_anomalies,
    analyze_department_budget,
    analyze_large_expenses,
    analyze_month_over_month_growth,
    get_available_months,
    get_departments,
)



    
app = FastAPI(
    title="BudgetPilot API",
    description="企业预算与费用分析智能助手后端接口",
    version="0.1.0",
)

@app.get(
    "/risk-overview",
    response_model=RiskOverviewResponse,
)
def get_risk_overview(
    month: Annotated[
        str,
        Query(
            pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
            description="统计月份，格式为 YYYY-MM",
        ),
    ],
    department_id: Annotated[
        str,
        Query(
            pattern=r"^D\d{3}$",
            description="部门编号",
        ),
    ],
    growth_threshold: Annotated[
        float,
        Query(
            ge=0,
            description="环比增长异常阈值",
        ),
    ] = 20.0,
    large_expense_threshold: Annotated[
        float,
        Query(
            ge=0,
            description="单笔大额费用阈值",
        ),
    ] = 20000.0,
) -> dict[str, object]:
    """返回指定部门和月份的统一风险总览。"""

    try:
        return generate_risk_overview(
            month=month,
            department_id=department_id,
            growth_threshold=growth_threshold,
            large_expense_threshold=large_expense_threshold,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
@app.get(
    "/large-expense-anomalies",
    response_model=LargeExpenseResponse,
)
def get_large_expense_anomalies(
    month: Annotated[
        str,
        Query(
            pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
            description="统计月份，格式为 YYYY-MM",
        ),
    ],
    department_id: Annotated[
        str,
        Query(
            pattern=r"^D\d{3}$",
            description="部门编号",
        ),
    ],
    amount_threshold: Annotated[
        float,
        Query(
            ge=0,
            description="单笔大额费用阈值",
        ),
    ] = 20000.0,
) -> dict[str, object]:
    """查询单笔大额费用异常。"""

    try:
        return analyze_large_expenses(
            month=month,
            department_id=department_id,
            amount_threshold=amount_threshold,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    
@app.get(
    "/budget-report",
    response_model=BudgetReportResponse,
)
def get_budget_report(
    month: Annotated[
        str,
        Query(
            pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
            description="报告月份，格式为 YYYY-MM",
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
) -> dict[str, object]:
    """生成指定月份和部门的预算分析报告。"""

    try:
        return generate_budget_report(
            month=month,
            department_id=department_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

@app.get("/health")
def health_check() -> dict[str, str]:
    """检查后端服务是否正常运行。"""

    return {
        "status": "ok",
        "service": "BudgetPilot",
    }
@app.get(
    "/budget-anomalies",
    response_model=list[BudgetAnomalyItem],
)
def get_budget_anomalies(
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
) -> list[dict[str, object]]:
    """查询指定月份和部门的预算异常。"""

    try:
        return analyze_budget_anomalies(
            month=month,
            department_id=department_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

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

@app.get(
    "/departments",
    response_model=list[DepartmentItem],
)
def list_departments() -> list[dict[str, str]]:
    """返回所有可查询部门。"""

    return get_departments()


@app.get(
    "/available-months",
    response_model=list[str],
)
def list_available_months() -> list[str]:
    """返回所有可查询月份。"""

    return get_available_months()

@app.get(
    "/expense-growth-anomalies",
    response_model=MonthOverMonthGrowthResponse,
)
def get_expense_growth_anomalies(
    month: Annotated[
        str,
        Query(
            pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
            description="本月月份，格式为 YYYY-MM",
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
) -> dict[str, object]:
    """查询指定部门的费用环比异常增长。"""

    try:
        return analyze_month_over_month_growth(
            month=month,
            department_id=department_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc