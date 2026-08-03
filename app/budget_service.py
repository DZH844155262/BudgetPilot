from .budget_calculator import calculate_budget_metrics
from datetime import date, timedelta
from decimal import Decimal
from .budget_repository import (
    fetch_available_months,
    fetch_budget_summary,
    fetch_departments,
    fetch_monthly_actuals,
    fetch_expense_details,
)
from .anomaly_detector import (
    detect_budget_anomalies,
    detect_month_over_month_growth,
    detect_large_expenses,
)
def _get_previous_month(month: str) -> str:
    """根据当前月份计算上一个自然月。"""

    current_month_first_day = date.fromisoformat(
        f"{month}-01"
    )

    previous_month_last_day = (
        current_month_first_day - timedelta(days=1)
    )

    return previous_month_last_day.strftime("%Y-%m")
def analyze_month_over_month_growth(
    month: str,
    department_id: str,
    threshold: float = 20.0,
) -> dict[str, object]:
    """分析指定部门费用的月度环比异常增长。"""

    previous_month = _get_previous_month(month)

    current_summary = fetch_budget_summary(
        month=month,
        department_id=department_id,
    )

    current_actuals = {
        str(item["category"]): Decimal(
            str(item["actual_amount"])
        )
        for item in current_summary
    }

    previous_actuals = fetch_monthly_actuals(
        month=previous_month,
        department_id=department_id,
    )

    anomalies = detect_month_over_month_growth(
        current_actuals=current_actuals,
        previous_actuals=previous_actuals,
        threshold=threshold,
    )

    return {
        "month": month,
        "previous_month": previous_month,
        "department_id": department_id,
        "threshold": threshold,
        "previous_data_available": bool(previous_actuals),
        "anomalies": anomalies,
    }
def analyze_budget_anomalies(
    month: str,
    department_id: str,
) -> list[dict[str, object]]:
    """分析指定部门和月份的预算异常。"""

    analysis_results = analyze_department_budget(
        month=month,
        department_id=department_id,
    )

    return detect_budget_anomalies(analysis_results)
def analyze_department_budget(
    month: str,
    department_id: str,
) -> list[dict[str, float | str]]:
    """分析指定月份和部门的预算执行情况。"""

    summary = fetch_budget_summary(
        month=month,
        department_id=department_id,
    )

    analysis_results: list[dict[str, float | str]] = []

    for row in summary:
        metrics = calculate_budget_metrics(
            budget_amount=float(row["budget_amount"]),
            actual_amount=float(row["actual_amount"]),
        )

        analysis_results.append(
            {
                "month": str(row["month"]),
                "department_id": str(row["department_id"]),
                "category": str(row["category"]),
                **metrics,
            }
        )

    return analysis_results


def get_departments() -> list[dict[str, str]]:
    """返回所有可查询部门。"""

    return fetch_departments()


def get_available_months() -> list[str]:
    """返回所有可查询月份。"""

    return fetch_available_months()


if __name__ == "__main__":
    results = analyze_department_budget(
        month="2026-07",
        department_id="D001",
    )

    for item in results:
        print(
            f"{item['category']}："
            f"预算 {item['budget_amount']:.2f} 元，"
            f"实际 {item['actual_amount']:.2f} 元，"
            f"执行率 {item['execution_rate']:.2f}%，"
            f"状态：{item['risk_status']}"
        )

def analyze_large_expenses(
    month: str,
    department_id: str,
    amount_threshold: float = 20000.0,
) -> dict[str, object]:
    """分析指定部门和月份的单笔大额费用。"""

    # 先验证当前月份确实有预算数据
    fetch_budget_summary(
        month=month,
        department_id=department_id,
    )

    expenses = fetch_expense_details(
        month=month,
        department_id=department_id,
    )

    anomalies = detect_large_expenses(
        expenses=expenses,
        amount_threshold=amount_threshold,
    )

    return {
        "month": month,
        "department_id": department_id,
        "amount_threshold": amount_threshold,
        "expense_count": len(expenses),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }