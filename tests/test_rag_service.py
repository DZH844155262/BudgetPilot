from app.rag.rag_service import (
    answer_policy_question,
)


def fake_text_generator(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """测试用假模型，不调用真实API。"""

    assert "只能依据" in system_prompt
    assert "20000元" in user_prompt

    return (
        "单笔费用达到20000元时，"
        "应由部门负责人和财务人员复核。[1]"
    )


def test_answer_policy_question() -> None:
    """应检索制度并生成带引用的回答。"""

    result = answer_policy_question(
        query="单笔费用达到20000元需要谁复核？",
        top_k=2,
        text_generator=fake_text_generator,
    )

    assert result["query"] == (
        "单笔费用达到20000元需要谁复核？"
    )

    assert "部门负责人" in result["answer"]
    assert "[1]" in result["answer"]

    assert result["source_count"] == 2

    first_source = result["sources"][0]

    assert (
        first_source["document_title"]
        == "企业费用报销管理制度"
    )

    assert (
        first_source["section_title"]
        == "二、单笔大额费用"
    )


def test_empty_policy_question_raises_error() -> None:
    """空制度问题应被拒绝。"""

    try:
        answer_policy_question(
            query="   ",
            text_generator=fake_text_generator,
        )
    except ValueError as exc:
        assert str(exc) == "制度问题不能为空"
    else:
        raise AssertionError("预期产生ValueError")