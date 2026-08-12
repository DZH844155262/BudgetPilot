from typing import Any

from .reranker_service import (
    rerank_policy_chunks,
)
from .vector_repository import (
    search_policy_chunks,
)


def search_policy_chunks_with_rerank(
    query: str,
    top_k: int = 2,
    candidate_k: int = 6,
) -> list[dict[str, Any]]:
    """先用向量召回候选，再使用Reranker重排序。"""

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("检索问题不能为空")

    if top_k <= 0:
        raise ValueError("top_k必须大于0")

    if candidate_k < top_k:
        raise ValueError(
            "candidate_k不能小于top_k"
        )

    candidates = search_policy_chunks(
        query=cleaned_query,
        top_k=candidate_k,
    )

    return rerank_policy_chunks(
        query=cleaned_query,
        candidates=candidates,
        top_n=top_k,
    )


if __name__ == "__main__":
    results = search_policy_chunks_with_rerank(
        query=(
            "软件和服务类费用报销"
            "需要提供哪些材料？"
        ),
        top_k=2,
        candidate_k=6,
    )

    for index, result in enumerate(
        results,
        start=1,
    ):
        print("\n" + "=" * 60)
        print(f"排名：{index}")
        print(
            f"制度：{result['document_title']}"
        )
        print(
            f"章节：{result['section_title']}"
        )
        print(
            f"向量相似度："
            f"{result['similarity_score']}"
        )
        print(
            f"重排序分数："
            f"{result['rerank_score']}"
        )