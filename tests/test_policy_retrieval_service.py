from app.rag.policy_retrieval_service import (
    retrieve_policy_context,
)


def test_retrieve_large_expense_policy() -> None:
    """应返回与单笔大额费用相关的制度。"""

    response = retrieve_policy_context(
        query="单笔费用达到20000元需要谁复核？",
        top_k=2,
    )

    assert response["query"] == (
        "单笔费用达到20000元需要谁复核？"
    )
    assert response["top_k"] == 2
    assert response["result_count"] == 2

    first_result = response["results"][0]

    assert (
        first_result["source"]
        == "expense_reimbursement_policy.md"
    )
    assert "20000元" in first_result["content"]


def test_empty_policy_query_raises_error() -> None:
    """空白问题不应进入向量检索。"""

    try:
        retrieve_policy_context(
            query="   ",
            top_k=3,
        )
    except ValueError as exc:
        assert str(exc) == "检索问题不能为空"
    else:
        raise AssertionError("预期产生ValueError")