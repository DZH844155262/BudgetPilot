from typing import Any

from .budget_service import (
    analyze_budget_anomalies,
    analyze_department_budget,
)


def generate_budget_report(
    month: str,
    department_id: str,
) -> dict[str, Any]:
    """生成指定部门和月份的预算分析报告。"""

    details = analyze_department_budget(
        month=month,
        department_id=department_id,
    )

    anomalies = analyze_budget_anomalies(
        month=month,
        department_id=department_id,
    )

    total_budget = sum(
        float(item["budget_amount"])
        for item in details
    )

    total_actual = sum(
        float(item["actual_amount"])
        for item in details
    )

    total_remaining = round(
        total_budget - total_actual,
        2,
    )

    overall_execution_rate = round(
        total_actual / total_budget * 100,
        2,
    )

    over_budget_count = sum(
        1
        for item in anomalies
        if item["anomaly_type"] == "over_budget"
    )

    warning_count = sum(
        1
        for item in anomalies
        if item["anomaly_type"] == "near_budget_limit"
    )

    if over_budget_count > 0:
        management_summary = (
            f"本月发现{over_budget_count}个超预算科目，"
            f"另有{warning_count}个科目接近预算上限，"
            "建议优先核查超预算项目。"
        )
    elif warning_count > 0:
        management_summary = (
            f"本月暂无超预算科目，"
            f"但有{warning_count}个科目接近预算上限，"
            "建议持续关注后续支出。"
        )
    else:
        management_summary = (
            "本月预算执行情况正常，"
            "暂未发现超预算或预算预警事项。"
        )

    return {
        "month": month,
        "department_id": department_id,
        "summary": {
            "total_budget": round(total_budget, 2),
            "total_actual": round(total_actual, 2),
            "total_remaining": total_remaining,
            "overall_execution_rate": overall_execution_rate,
            "over_budget_count": over_budget_count,
            "warning_count": warning_count,
        },
        "details": details,
        "anomalies": anomalies,
        "management_summary": management_summary,
    }


if __name__ == "__main__":
    report = generate_budget_report(
        month="2026-07",
        department_id="D001",
    )

    print(report)