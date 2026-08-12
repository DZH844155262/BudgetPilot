from app.rag.vector_repository import search_policy_chunks


def test_search_large_expense_policy() -> None:
    """应检索到单笔大额费用相关制度及章节。"""

    results = search_policy_chunks(
        query="单笔费用达到20000元需要谁复核？",
        top_k=2,
    )

    assert len(results) == 2

    first_result = results[0]

    assert (
        first_result["source"]
        == "expense_reimbursement_policy.md"
    )
    assert (
        first_result["document_title"]
        == "企业费用报销管理制度"
    )
    assert (
        first_result["section_title"]
        == "二、单笔大额费用"
    )
    assert "20000元" in first_result["content"]
    assert first_result["similarity_score"] > 0

def test_search_over_budget_policy() -> None:
    """应检索到超预算处理相关制度及章节。"""

    results = search_policy_chunks(
        query="部门超预算以后应该怎样处理？",
        top_k=2,
    )

    first_result = results[0]

    assert (
        first_result["source"]
        == "budget_management_policy.md"
    )
    assert (
        first_result["document_title"]
        == "企业预算管理制度"
    )
    assert (
        first_result["section_title"]
        == "二、预算执行预警"
    )
    assert "超预算" in first_result["content"]


def test_invalid_policy_search_input() -> None:
    """空问题和非法top_k应被拒绝。"""

    try:
        search_policy_chunks(
            query="   ",
            top_k=3,
        )
    except ValueError as exc:
        assert str(exc) == "检索问题不能为空"
    else:
        raise AssertionError("预期产生ValueError")

    try:
        search_policy_chunks(
            query="超预算如何处理？",
            top_k=0,
        )
    except ValueError as exc:
        assert str(exc) == "top_k必须大于0"
    else:
        raise AssertionError("预期产生ValueError")