from typing import Any


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