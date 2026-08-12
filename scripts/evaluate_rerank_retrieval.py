import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.rag.retrieval_evaluator import (
    evaluate_retrieval_cases,
)
from app.rag.retrieval_pipeline import (
    search_policy_chunks_with_rerank,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "retrieval_cases.json"
)

VECTOR_BASELINE_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
    / "vector_retrieval_baseline.json"
)

RESULT_DIRECTORY = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
)

RERANK_RESULT_PATH = (
    RESULT_DIRECTORY
    / "rerank_retrieval_baseline.json"
)


def load_json_file(
    file_path: Path,
) -> dict[str, Any]:
    """读取JSON文件。"""

    if not file_path.exists():
        raise FileNotFoundError(
            f"找不到文件：{file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def rerank_search(
    query: str,
    top_k: int,
) -> list[dict[str, Any]]:
    """供评测器调用的Reranker检索函数。"""

    return search_policy_chunks_with_rerank(
        query=query,
        top_k=top_k,
        candidate_k=6,
    )


def save_result(
    dataset: dict[str, Any],
    evaluation: dict[str, Any],
) -> None:
    """保存Reranker检索评测结果。"""

    RESULT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "dataset_name": dataset["dataset_name"],
        "retrieval_method": (
            "vector_recall_plus_bge_reranker"
        ),
        "embedding_model": (
            "BAAI/bge-small-zh-v1.5"
        ),
        "reranker_model": (
            "BAAI/bge-reranker-base"
        ),
        "candidate_k": 6,
        "generated_at": (
            datetime.now()
            .astimezone()
            .isoformat(timespec="seconds")
        ),
        **evaluation,
    }

    with RERANK_RESULT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )


def print_metric_comparison(
    vector_result: dict[str, Any],
    rerank_result: dict[str, Any],
) -> None:
    """对比纯向量与Reranker检索指标。"""

    vector_summary = vector_result["summary"]
    rerank_summary = rerank_result["summary"]

    metrics = [
        (
            "Top-1 Accuracy",
            "top1_accuracy",
        ),
        (
            "Recall@3",
            "recall_at_k",
        ),
        (
            "MRR",
            "mrr",
        ),
        (
            "nDCG@3",
            "ndcg_at_k",
        ),
    ]

    print("\n检索方法A/B对比")
    print("=" * 72)
    print(
        f"{'指标':<20}"
        f"{'纯向量':>14}"
        f"{'Reranker':>14}"
        f"{'变化':>14}"
    )

    for display_name, field_name in metrics:
        vector_value = float(
            vector_summary[field_name]
        )

        rerank_value = float(
            rerank_summary[field_name]
        )

        difference = (
            rerank_value - vector_value
        )

        print(
            f"{display_name:<20}"
            f"{vector_value:>14.4f}"
            f"{rerank_value:>14.4f}"
            f"{difference:>+14.4f}"
        )


def print_changed_cases(
    vector_result: dict[str, Any],
    rerank_result: dict[str, Any],
) -> None:
    """打印加入Reranker后排名发生变化的题目。"""

    vector_cases = {
        case["case_id"]: case
        for case in vector_result["cases"]
    }

    print("\n正确章节排名发生变化的用例：")

    changed_count = 0

    for rerank_case in rerank_result["cases"]:
        case_id = rerank_case["case_id"]
        vector_case = vector_cases[case_id]

        old_rank = vector_case["expected_rank"]
        new_rank = rerank_case["expected_rank"]

        if old_rank == new_rank:
            continue

        changed_count += 1

        print("-" * 72)
        print(f"编号：{case_id}")
        print(f"问题：{rerank_case['query']}")
        print(f"原始排名：{old_rank}")
        print(f"重排序排名：{new_rank}")

        if rerank_case["retrieved_results"]:
            first_result = (
                rerank_case[
                    "retrieved_results"
                ][0]
            )

            print(
                "Reranker第一名："
                f"{first_result['section_title']}"
            )

    if changed_count == 0:
        print("- 没有用例发生排名变化")


def main() -> None:
    """运行向量召回加Reranker评测。"""

    dataset = load_json_file(DATASET_PATH)

    vector_result = load_json_file(
        VECTOR_BASELINE_PATH
    )

    cases = dataset.get("cases")

    if not isinstance(cases, list) or not cases:
        raise ValueError(
            "retrieval_cases.json中的cases不能为空"
        )

    rerank_evaluation = evaluate_retrieval_cases(
        cases=cases,
        top_k=3,
        search_function=rerank_search,
    )

    save_result(
        dataset=dataset,
        evaluation=rerank_evaluation,
    )

    print_metric_comparison(
        vector_result=vector_result,
        rerank_result=rerank_evaluation,
    )

    print_changed_cases(
        vector_result=vector_result,
        rerank_result=rerank_evaluation,
    )

    print("\nReranker完整结果已保存：")
    print(RERANK_RESULT_PATH)


if __name__ == "__main__":
    main()