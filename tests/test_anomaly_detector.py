from app.anomaly_detector import detect_budget_anomalies


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