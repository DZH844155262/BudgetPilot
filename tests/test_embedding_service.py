import math

from app.rag.embedding_service import (
    cosine_similarity,
    embed_documents,
    embed_query,
    get_embedding_dimension,
)


def test_embedding_dimension_and_normalization() -> None:
    """应生成512维且已归一化的查询向量。"""

    vector = embed_query(
        "超预算后应该如何处理？"
    )

    assert get_embedding_dimension() == 512
    assert len(vector) == 512

    vector_length = math.sqrt(
        sum(value * value for value in vector)
    )

    assert abs(vector_length - 1.0) < 1e-5


def test_relevant_policy_has_higher_similarity() -> None:
    """相关制度的语义相似度应高于无关制度。"""

    query_vector = embed_query(
        "单笔费用达到20000元需要谁复核？"
    )

    document_vectors = embed_documents(
        [
            (
                "单笔费用达到20000元时，"
                "应提交部门负责人和财务人员复核。"
            ),
            "软件自动续费前应进行必要性评估。",
        ]
    )

    relevant_score = cosine_similarity(
        query_vector,
        document_vectors[0],
    )

    irrelevant_score = cosine_similarity(
        query_vector,
        document_vectors[1],
    )

    assert relevant_score > irrelevant_score


def test_empty_embedding_input_raises_error() -> None:
    """空查询和空文档不应生成向量。"""

    try:
        embed_query("   ")
    except ValueError as exc:
        assert str(exc) == "查询内容不能为空"
    else:
        raise AssertionError("预期产生ValueError")

    try:
        embed_documents([])
    except ValueError as exc:
        assert str(exc) == "文档列表不能为空"
    else:
        raise AssertionError("预期产生ValueError")