from .budget_calculator import calculate_budget_metrics
from .data_loader import get_budget_summary, load_budget_data


def analyze_department_budget(
    month: str,
    department_id: str,
) -> list[dict[str, float | str]]:
    """分析指定月份和部门的预算执行情况。"""

    summary = get_budget_summary(
        month=month,
        department_id=department_id,
    )

    analysis_results: list[dict[str, float | str]] = []

    for row in summary.itertuples(index=False):
        metrics = calculate_budget_metrics(
            budget_amount=float(row.budget_amount),
            actual_amount=float(row.actual_amount),
        )

        analysis_results.append(
            {
                "month": str(row.month),
                "department_id": str(row.department_id),
                "category": str(row.category),
                **metrics,
            }
        )

    return analysis_results
def get_departments() -> list[dict[str, str]]:
    """返回所有可查询部门。"""

    departments, _, _ = load_budget_data()

    return departments[
        [
            "department_id",
            "department_name",
        ]
    ].to_dict(orient="records")


def get_available_months() -> list[str]:
    """返回预算数据中所有可查询月份。"""

    _, budgets, _ = load_budget_data()

    months = sorted(
        budgets["month"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return months

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