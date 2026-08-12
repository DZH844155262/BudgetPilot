import math
from collections.abc import Callable
from typing import Any

from .vector_repository import search_policy_chunks


SearchFunction = Callable[
    [str, int],
    list[dict[str, Any]],
]


def _is_expected_result(
    result: dict[str, Any],
    case: dict[str, Any],
) -> bool:
    """判断当前结果是否为人工标注的正确章节。"""

    return (
        result.get("document_title")
        == case["expected_document_title"]
        and result.get("section_title")
        == case["expected_section_title"]
    )


def _find_expected_rank(
    results: list[dict[str, Any]],
    case: dict[str, Any],
) -> int | None:
    """查找正确章节在检索结果中的排名。"""

    for rank, result in enumerate(
        results,
        start=1,
    ):
        if _is_expected_result(result, case):
            return rank

    return None


def _calculate_ndcg(
    expected_rank: int | None,
) -> float:
    """计算单个正确章节场景下的nDCG。"""

    if expected_rank is None:
        return 0.0

    # 当前每道题只标注一个正确章节。
    # 理想排名为第1名，因此IDCG等于1。
    return 1.0 / math.log2(expected_rank + 1)


def evaluate_retrieval_cases(
    cases: list[dict[str, Any]],
    top_k: int = 3,
    search_function: SearchFunction | None = None,
) -> dict[str, Any]:
    """运行检索评测并计算核心指标。"""

    if not cases:
        raise ValueError("评测用例不能为空")

    if top_k <= 0:
        raise ValueError("top_k必须大于0")

    searcher = search_function or search_policy_chunks

    top1_hit_count = 0
    recall_hit_count = 0
    reciprocal_rank_total = 0.0
    ndcg_total = 0.0

    case_results: list[dict[str, Any]] = []

    for case in cases:
        retrieved_results = searcher(
            case["query"],
            top_k,
        )

        expected_rank = _find_expected_rank(
            retrieved_results,
            case,
        )

        top1_hit = expected_rank == 1
        recall_hit = expected_rank is not None

        reciprocal_rank = (
            1.0 / expected_rank
            if expected_rank is not None
            else 0.0
        )

        ndcg = _calculate_ndcg(expected_rank)

        if top1_hit:
            top1_hit_count += 1

        if recall_hit:
            recall_hit_count += 1

        reciprocal_rank_total += reciprocal_rank
        ndcg_total += ndcg

        case_results.append(
            {
                "case_id": case["case_id"],
                "query": case["query"],
                "expected_document_title": (
                    case["expected_document_title"]
                ),
                "expected_section_title": (
                    case["expected_section_title"]
                ),
                "expected_rank": expected_rank,
                "top1_hit": top1_hit,
                "recall_hit": recall_hit,
                "reciprocal_rank": round(
                    reciprocal_rank,
                    4,
                ),
                "ndcg": round(ndcg, 4),
                "retrieved_results": [
                    {
                        "rank": rank,
                        "document_title": result.get(
                            "document_title"
                        ),
                        "section_title": result.get(
                            "section_title"
                        ),
                        "chunk_id": result.get(
                            "chunk_id"
                        ),
                        "similarity_score": result.get(
                            "similarity_score"
                        ),
                    }
                    for rank, result in enumerate(
                        retrieved_results,
                        start=1,
                    )
                ],
            }
        )

    case_count = len(cases)

    return {
        "summary": {
            "case_count": case_count,
            "top_k": top_k,
            "top1_accuracy": round(
                top1_hit_count / case_count,
                4,
            ),
            "recall_at_k": round(
                recall_hit_count / case_count,
                4,
            ),
            "mrr": round(
                reciprocal_rank_total / case_count,
                4,
            ),
            "ndcg_at_k": round(
                ndcg_total / case_count,
                4,
            ),
            "top1_hit_count": top1_hit_count,
            "recall_hit_count": recall_hit_count,
        },
        "cases": case_results,
    }