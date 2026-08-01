import pytest

from app.budget_calculator import calculate_budget_metrics


def test_normal_budget_status() -> None:
    """预算执行率低于90%时，应判定为正常。"""

    result = calculate_budget_metrics(
        budget_amount=100000,
        actual_amount=85000,
    )

    assert result["execution_rate"] == 85.0
    assert result["variance"] == -15000
    assert result["remaining"] == 15000
    assert result["risk_status"] == "正常"


def test_warning_budget_status() -> None:
    """预算执行率达到90%但未超过100%时，应发出预警。"""

    result = calculate_budget_metrics(
        budget_amount=100000,
        actual_amount=95000,
    )

    assert result["execution_rate"] == 95.0
    assert result["risk_status"] == "预警"


def test_over_budget_status() -> None:
    """实际费用超过预算时，应判定为超预算。"""

    result = calculate_budget_metrics(
        budget_amount=100000,
        actual_amount=110000,
    )

    assert result["execution_rate"] == 110.0
    assert result["variance"] == 10000
    assert result["remaining"] == -10000
    assert result["risk_status"] == "超预算"


def test_zero_budget_raises_error() -> None:
    """预算金额为0时，应主动拒绝计算。"""

    with pytest.raises(
        ValueError,
        match="预算金额必须大于0",
    ):
        calculate_budget_metrics(
            budget_amount=0,
            actual_amount=5000,
        )


def test_negative_actual_amount_raises_error() -> None:
    """实际费用为负数时，应主动拒绝计算。"""

    with pytest.raises(
        ValueError,
        match="实际费用不能小于0",
    ):
        calculate_budget_metrics(
            budget_amount=100000,
            actual_amount=-5000,
        )