from decimal import Decimal
from app.anomaly_detector import (
    detect_budget_anomalies,
    detect_month_over_month_growth,
)
def test_detect_month_over_month_growth() -> None:
    """环比增长达到20%时应识别为异常。"""

    current_actuals = {
        "市场推广费": Decimal("56000.00"),
        "差旅费": Decimal("11500.00"),
        "软件服务费": Decimal("7800.00"),
    }

    previous_actuals = {
        "市场推广费": Decimal("48000.00"),
        "差旅费": Decimal("9000.00"),
        "软件服务费": Decimal("7000.00"),
    }

    anomalies = detect_month_over_month_growth(
        current_actuals=current_actuals,
        previous_actuals=previous_actuals,
    )

    assert len(anomalies) == 1

    anomaly = anomalies[0]

    assert anomaly["category"] == "差旅费"
    assert anomaly["anomaly_type"] == "month_over_month_growth"
    assert anomaly["severity"] == "medium"
    assert anomaly["current_amount"] == 11500.0
    assert anomaly["previous_amount"] == 9000.0
    assert anomaly["growth_rate"] == 27.78


def test_zero_previous_amount_is_skipped() -> None:
    """上月金额为0时暂不计算环比增长率。"""

    anomalies = detect_month_over_month_growth(
        current_actuals={
            "培训费": Decimal("5000.00"),
        },
        previous_actuals={
            "培训费": Decimal("0.00"),
        },
    )

    assert anomalies == []
def test_detect_over_budget_anomaly() -> None:
    """执行率超过100%时应识别为高风险异常。"""

    results = [
        {
            "category": "市场推广费",
            "execution_rate": 112.0,
            "remaining": -6000.0,
        }
    ]

    anomalies = detect_budget_anomalies(results)

    assert len(anomalies) == 1
    assert anomalies[0]["anomaly_type"] == "over_budget"
    assert anomalies[0]["severity"] == "high"
    assert anomalies[0]["amount"] == 6000.0


def test_detect_near_budget_limit() -> None:
    """执行率达到90%但未超预算时应识别为中风险。"""

    results = [
        {
            "category": "差旅费",
            "execution_rate": 95.83,
            "remaining": 500.0,
        }
    ]

    anomalies = detect_budget_anomalies(results)

    assert len(anomalies) == 1
    assert anomalies[0]["anomaly_type"] == "near_budget_limit"
    assert anomalies[0]["severity"] == "medium"
    assert anomalies[0]["amount"] == 500.0


def test_normal_budget_has_no_anomaly() -> None:
    """执行率低于90%时不应生成异常。"""

    results = [
        {
            "category": "办公费",
            "execution_rate": 70.0,
            "remaining": 3000.0,
        }
    ]

    anomalies = detect_budget_anomalies(results)

    assert anomalies == []