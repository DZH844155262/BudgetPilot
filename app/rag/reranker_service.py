from functools import lru_cache
from typing import Any

from sentence_transformers import CrossEncoder


RERANKER_MODEL_NAME = "BAAI/bge-reranker-base"


@lru_cache(maxsize=1)
def get_reranker_model() -> CrossEncoder:
    """加载并缓存BGE重排序模型。"""

    return CrossEncoder(
        RERANKER_MODEL_NAME,
        max_length=512,
    )


def rerank_policy_chunks(
    query: str,
    candidates: list[dict[str, Any]],
    top_n: int = 2,
) -> list[dict[str, Any]]:
    """根据问题与候选Chunk的相关性重新排序。"""

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("重排序问题不能为空")

    if not candidates:
        return []

    if top_n <= 0:
        raise ValueError("top_n必须大于0")

    pairs = [
        [
            cleaned_query,
            candidate["content"],
        ]
        for candidate in candidates
    ]

    scores = get_reranker_model().predict(
        pairs,
        show_progress_bar=False,
    )

    reranked_results: list[dict[str, Any]] = []

    for candidate, score in zip(
        candidates,
        scores,
        strict=True,
    ):
        reranked_results.append(
            {
                **candidate,
                "rerank_score": round(
                    float(score),
                    4,
                ),
            }
        )

    reranked_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return reranked_results[:top_n]


if __name__ == "__main__":
    from .vector_repository import (
        search_policy_chunks,
    )

    test_query = (
        "软件和服务类费用报销需要提供哪些材料？"
    )

    candidate_results = search_policy_chunks(
        query=test_query,
        top_k=6,
    )

    reranked_results = rerank_policy_chunks(
        query=test_query,
        candidates=candidate_results,
        top_n=3,
    )

    print(f"问题：{test_query}")

    for index, result in enumerate(
        reranked_results,
        start=1,
    ):
        print("\n" + "=" * 60)
        print(f"重排序名次：{index}")
        print(f"章节：{result['section_title']}")
        print(
            f"向量相似度："
            f"{result['similarity_score']}"
        )
        print(
            f"Reranker分数："
            f"{result['rerank_score']}"
        )