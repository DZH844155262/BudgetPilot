from typing import Any
from decimal import Decimal

def detect_budget_anomalies(
    analysis_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """根据预算分析结果识别超预算和预算预警。"""

    anomalies: list[dict[str, Any]] = []

    for item in analysis_results:
        execution_rate = float(item["execution_rate"])
        remaining = float(item["remaining"])
        category = str(item["category"])

        if execution_rate > 100:
            anomalies.append(
                {
                    "anomaly_type": "over_budget",
                    "severity": "high",
                    "category": category,
                    "execution_rate": execution_rate,
                    "amount": abs(remaining),
                    "message": (
                        f"{category}已超预算"
                        f"{abs(remaining):.2f}元，"
                        f"执行率为{execution_rate:.2f}%"
                    ),
                }
            )

        elif execution_rate >= 90:
            anomalies.append(
                {
                    "anomaly_type": "near_budget_limit",
                    "severity": "medium",
                    "category": category,
                    "execution_rate": execution_rate,
                    "amount": remaining,
                    "message": (
                        f"{category}接近预算上限，"
                        f"剩余预算{remaining:.2f}元，"
                        f"执行率为{execution_rate:.2f}%"
                    ),
                }
            )

    return anomalies

from decimal import Decimal
from typing import Any


def detect_month_over_month_growth(
    current_actuals: dict[str, Decimal],
    previous_actuals: dict[str, Decimal],
    threshold: float = 20.0,
) -> list[dict[str, Any]]:
    """识别费用环比异常增长。"""

    anomalies: list[dict[str, Any]] = []

    for category, current_amount in current_actuals.items():
        previous_amount = previous_actuals.get(
            category,
            Decimal("0.00"),
        )

        if previous_amount <= 0:
            continue

        growth_rate = round(
            float(
                (current_amount - previous_amount)
                / previous_amount
                * 100
            ),
            2,
        )

        if growth_rate >= threshold:
            anomalies.append(
                {
                    "anomaly_type": "month_over_month_growth",
                    "severity": "medium",
                    "category": category,
                    "current_amount": float(current_amount),
                    "previous_amount": float(previous_amount),
                    "growth_rate": growth_rate,
                    "message": (
                        f"{category}本月费用为"
                        f"{current_amount:.2f}元，"
                        f"较上月增长{growth_rate:.2f}%"
                    ),
                }
            )

    return anomalies