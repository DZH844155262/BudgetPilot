import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.rag.generation_evaluator import (
    evaluate_generation_cases,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "generation_cases.json"
)

RESULT_DIRECTORY = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
)

RESULT_PATH = (
    RESULT_DIRECTORY
    / "generation_rule_reranker_top2.json"
)


def load_dataset() -> dict[str, Any]:
    """读取生成回答评测集。"""

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    cases = dataset.get("cases")

    if not isinstance(cases, list) or not cases:
        raise ValueError(
            "generation_cases.json中的cases不能为空"
        )

    return dataset


def save_result(
    dataset: dict[str, Any],
    evaluation: dict[str, Any],
) -> None:
    """保存生成回答评测结果。"""

    RESULT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "dataset_name": dataset["dataset_name"],
        "evaluation_method": (
            "deterministic_rule_evaluation"
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


def print_result(
    evaluation: dict[str, Any],
) -> None:
    """打印评测摘要和失败用例。"""

    summary = evaluation["summary"]

    print("\nRAG生成回答规则评测")
    print("=" * 60)
    print(f"问题数量：{summary['case_count']}")
    print(
        "总体通过率："
        f"{summary['pass_rate']:.2%}"
    )
    print(
        "关键事实通过率："
        f"{summary['keyword_pass_rate']:.2%}"
    )
    print(
        "禁止内容通过率："
        f"{summary['forbidden_pass_rate']:.2%}"
    )
    print(
        "正确来源通过率："
        f"{summary['source_pass_rate']:.2%}"
    )
    print(
        "引用一致性通过率："
        f"{summary['citation_pass_rate']:.2%}"
    )
    print(
        "无答案拒答率："
        f"{summary['refusal_pass_rate']:.2%}"
    )
    print(
        "平均响应时间："
        f"{summary['average_latency_seconds']}秒"
    )

    failed_cases = [
        case
        for case in evaluation["cases"]
        if not case["passed"]
    ]

    print("\n未通过用例：")

    if not failed_cases:
        print("- 无")
        return

    for case in failed_cases:
        print("-" * 60)
        print(f"编号：{case['case_id']}")
        print(f"问题：{case['query']}")
        print(f"回答：{case['answer']}")
        print(
            "事实检查："
            f"{case['keyword_pass']}"
        )
        print(
            "禁止内容："
            f"{case['forbidden_pass']}"
        )
        print(
            "来源检查："
            f"{case['source_pass']}"
        )
        print(
            "引用检查："
            f"{case['citation_pass']}"
        )
        print(
            "拒答检查："
            f"{case['refusal_pass']}"
        )


def main() -> None:
    """运行真实DeepSeek生成回答基线评测。"""

    dataset = load_dataset()

    top2_cases = [
    {
        **case,
        "top_k": 2,
    }
    for case in dataset["cases"]
]

    evaluation = evaluate_generation_cases(
    cases=top2_cases,
)

    save_result(
        dataset=dataset,
        evaluation=evaluation,
    )

    print_result(evaluation)

    print("\n完整结果已保存：")
    print(RESULT_PATH)


if __name__ == "__main__":
    main()