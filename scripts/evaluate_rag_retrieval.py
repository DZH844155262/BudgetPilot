import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.rag.retrieval_evaluator import (
    evaluate_retrieval_cases,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "retrieval_cases.json"
)

RESULT_DIRECTORY = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
)

RESULT_PATH = (
    RESULT_DIRECTORY
    / "vector_retrieval_baseline.json"
)


def load_evaluation_dataset() -> dict[str, Any]:
    """读取制度检索评测集。"""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"找不到评测文件：{DATASET_PATH}"
        )

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    cases = dataset.get("cases")

    if not isinstance(cases, list) or not cases:
        raise ValueError(
            "retrieval_cases.json中的cases不能为空"
        )

    return dataset


def save_evaluation_result(
    dataset: dict[str, Any],
    evaluation: dict[str, Any],
) -> None:
    """保存完整评测结果。"""

    RESULT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "dataset_name": dataset["dataset_name"],
        "retrieval_method": "vector_only",
        "embedding_model": (
            "BAAI/bge-small-zh-v1.5"
        ),
        "generated_at": (
            datetime.now()
            .astimezone()
            .isoformat(timespec="seconds")
        ),
        **evaluation,
    }

    with RESULT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )


def print_evaluation_result(
    evaluation: dict[str, Any],
) -> None:
    """打印评测摘要和未命中用例。"""

    summary = evaluation["summary"]

    print("\n纯向量检索基线评测")
    print("=" * 60)
    print(f"问题数量：{summary['case_count']}")
    print(f"Top-K：{summary['top_k']}")
    print(
        "Top-1 Accuracy："
        f"{summary['top1_accuracy']:.2%}"
    )
    print(
        f"Recall@{summary['top_k']}："
        f"{summary['recall_at_k']:.2%}"
    )
    print(f"MRR：{summary['mrr']:.4f}")
    print(
        f"nDCG@{summary['top_k']}："
        f"{summary['ndcg_at_k']:.4f}"
    )

    failed_cases = [
        case
        for case in evaluation["cases"]
        if not case["top1_hit"]
    ]

    print("\nTop-1未命中问题：")

    if not failed_cases:
        print("- 无，全部问题第一名命中")
        return

    for case in failed_cases:
        print("-" * 60)
        print(f"编号：{case['case_id']}")
        print(f"问题：{case['query']}")
        print(
            "正确章节："
            f"{case['expected_section_title']}"
        )
        print(
            "正确章节排名："
            f"{case['expected_rank']}"
        )

        retrieved_results = case[
            "retrieved_results"
        ]

        if retrieved_results:
            first_result = retrieved_results[0]

            print(
                "实际第一名："
                f"{first_result['section_title']}"
            )


def main() -> None:
    """执行纯向量检索基线评测。"""

    dataset = load_evaluation_dataset()

    evaluation = evaluate_retrieval_cases(
        cases=dataset["cases"],
        top_k=3,
    )

    save_evaluation_result(
        dataset=dataset,
        evaluation=evaluation,
    )

    print_evaluation_result(evaluation)

    print("\n完整结果已保存：")
    print(RESULT_PATH)


if __name__ == "__main__":
    main()