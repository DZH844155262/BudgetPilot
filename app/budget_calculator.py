def calculate_budget_metrics(
    budget_amount: float,
    actual_amount: float,
) -> dict[str, float | str]:
    """计算预算执行指标和风险状态。"""

    if budget_amount <= 0:
        raise ValueError("预算金额必须大于0")

    if actual_amount < 0:
        raise ValueError("实际费用不能小于0")

    execution_rate = actual_amount / budget_amount * 100
    variance = actual_amount - budget_amount
    remaining = budget_amount - actual_amount

    if execution_rate > 100:
        risk_status = "超预算"
    elif execution_rate >= 90:
        risk_status = "预警"
    else:
        risk_status = "正常"

    return {
        "budget_amount": round(budget_amount, 2),
        "actual_amount": round(actual_amount, 2),
        "execution_rate": round(execution_rate, 2),
        "variance": round(variance, 2),
        "remaining": round(remaining, 2),
        "risk_status": risk_status,
    }


if __name__ == "__main__":
    result = calculate_budget_metrics(
        budget_amount=100000,
        actual_amount=85000,
    )
    print(result)