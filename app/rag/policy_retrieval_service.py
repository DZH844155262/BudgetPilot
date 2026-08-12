from typing import Any

from .vector_repository import search_policy_chunks

from .retrieval_pipeline import (
    search_policy_chunks_with_rerank,
)
def retrieve_policy_context(
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """检索与用户问题最相关的预算制度内容。"""

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("检索问题不能为空")

    results = search_policy_chunks(
        query=cleaned_query,
        top_k=top_k,
    )

    return {
        "query": cleaned_query,
        "top_k": top_k,
        "result_count": len(results),
        "results": results,
    }


if __name__ == "__main__":
    response = retrieve_policy_context(
        query="单笔费用达到20000元需要谁复核？",
        top_k=3,
    )

    print(f"问题：{response['query']}")
    print(f"结果数量：{response['result_count']}")

    for index, item in enumerate(
        response["results"],
        start=1,
    ):
        print("\n" + "=" * 60)
        print(f"排名：{index}")
        print(f"相似度：{item['similarity_score']}")
        print(f"来源：{item['source']}")
        print(f"Chunk：{item['chunk_id']}")
        print(item["content"])

def retrieve_policy_context_with_rerank(
    query: str,
    top_k: int = 3,
    candidate_k: int = 6,
) -> dict[str, Any]:
    """使用向量召回和Reranker检索制度上下文。"""

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("检索问题不能为空")

    if top_k <= 0:
        raise ValueError("top_k必须大于0")

    if candidate_k < top_k:
        raise ValueError(
            "candidate_k不能小于top_k"
        )

    results = search_policy_chunks_with_rerank(
        query=cleaned_query,
        top_k=top_k,
        candidate_k=candidate_k,
    )

    return {
        "query": cleaned_query,
        "top_k": top_k,
        "candidate_k": candidate_k,
        "retrieval_method": (
            "vector_recall_plus_bge_reranker"
        ),
        "result_count": len(results),
        "results": results,
    }