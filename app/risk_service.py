from typing import Any

from .budget_service import (
    analyze_budget_anomalies,
    analyze_large_expenses,
    analyze_month_over_month_growth,
)


def generate_risk_overview(
    month: str,
    department_id: str,
    growth_threshold: float = 20.0,
    large_expense_threshold: float = 20000.0,
) -> dict[str, Any]:
    """生成指定部门和月份的统一风险总览。"""

    budget_anomalies = analyze_budget_anomalies(
        month=month,
        department_id=department_id,
    )

    growth_result = analyze_month_over_month_growth(
        month=month,
        department_id=department_id,
        threshold=growth_threshold,
    )
    growth_anomalies = growth_result["anomalies"]

    large_expense_result = analyze_large_expenses(
        month=month,
        department_id=department_id,
        amount_threshold=large_expense_threshold,
    )
    large_expense_anomalies = large_expense_result["anomalies"]

    all_anomalies = [
        *budget_anomalies,
        *growth_anomalies,
        *large_expense_anomalies,
    ]

    high_risk_count = sum(
        1
        for item in all_anomalies
        if item["severity"] == "high"
    )

    medium_risk_count = sum(
        1
        for item in all_anomalies
        if item["severity"] == "medium"
    )

    return {
        "month": month,
        "department_id": department_id,
        "summary": {
            "total_anomaly_count": len(all_anomalies),
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
        },
        "budget_anomalies": budget_anomalies,
        "growth_anomalies": growth_anomalies,
        "large_expense_anomalies": large_expense_anomalies,
    }