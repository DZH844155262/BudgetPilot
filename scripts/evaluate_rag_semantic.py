import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from app.rag.deepeval_judge import (
    DeepSeekEvaluationModel,
)
from app.rag.policy_retrieval_service import (
    retrieve_policy_context_with_rerank,
)
from app.rag.rag_service import (
    answer_policy_question,
)
EVALUATION_TOP_K = 2
EVALUATION_CANDIDATE_K = 6

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
    / "generation_semantic_reranker_top2.json"
)


def load_cases() -> list[dict[str, Any]]:
    """读取生成评测用例。"""

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

    return cases


def measure_metric(
    metric: Any,
    test_case: LLMTestCase,
) -> dict[str, Any]:
    """执行单个DeepEval指标并整理结果。"""

    metric.measure(test_case)

    score = (
        round(float(metric.score), 4)
        if metric.score is not None
        else None
    )

    return {
        "score": score,
        "passed": metric.is_successful(),
        "reason": metric.reason,
    }


def build_metrics(
    judge: DeepSeekEvaluationModel,
    should_refuse: bool,
) -> dict[str, Any]:
    """根据用例类型创建语义评测指标。"""

    # 无答案问题已经由确定性拒答规则负责评测。
    # 通用Answer Relevancy会把正确拒答误判为没有回答问题。
    if should_refuse:
        return {}

    return {
        "faithfulness": FaithfulnessMetric(
            threshold=0.7,
            model=judge,
            include_reason=True,
            async_mode=False,
        ),
        "answer_relevancy": AnswerRelevancyMetric(
            threshold=0.7,
            model=judge,
            include_reason=True,
            async_mode=False,
        ),
        "contextual_relevancy": (
            ContextualRelevancyMetric(
                threshold=0.7,
                model=judge,
                include_reason=True,
                async_mode=False,
            )
        ),
    }
    """根据用例类型创建语义评测指标。"""

    metrics: dict[str, Any] = {
        "faithfulness": FaithfulnessMetric(
            threshold=0.7,
            model=judge,
            include_reason=True,
            async_mode=False,
        ),
        "answer_relevancy": AnswerRelevancyMetric(
            threshold=0.7,
            model=judge,
            include_reason=True,
            async_mode=False,
        ),
    }

    # 无答案问题会故意检索到低相关内容，
    # Contextual Relevancy作为检索诊断，不纳入该类用例。
    if not should_refuse:
        metrics["contextual_relevancy"] = (
            ContextualRelevancyMetric(
                threshold=0.7,
                model=judge,
                include_reason=True,
                async_mode=False,
            )
        )

    return metrics


def evaluate_semantic_quality() -> dict[str, Any]:
    """运行RAG语义质量基线评测。"""

    cases = load_cases()
    judge = DeepSeekEvaluationModel()

    case_results: list[dict[str, Any]] = []

    score_collection: dict[
        str,
        list[float],
    ] = defaultdict(list)

    pass_collection: dict[
        str,
        list[bool],
    ] = defaultdict(list)

    for index, case in enumerate(
        cases,
        start=1,
    ):
        query = case["query"]
        top_k = EVALUATION_TOP_K
        should_refuse = case.get(
            "should_refuse",
            False,
        )

        print(
            f"\n[{index}/{len(cases)}] "
            f"正在评测：{case['case_id']}"
        )

        retrieval = (
    retrieve_policy_context_with_rerank(
        query=query,
        top_k=top_k,
        candidate_k=max(6, top_k),
    )
)

        response = answer_policy_question(
            query=query,
            top_k=top_k,
        )

        retrieval_context = [
            result["content"]
            for result in retrieval["results"]
        ]

        test_case = LLMTestCase(
            input=query,
            actual_output=response["answer"],
            retrieval_context=retrieval_context,
        )

        metrics = build_metrics(
            judge=judge,
            should_refuse=should_refuse,
        )

        metric_results: dict[
            str,
            dict[str, Any],
        ] = {}

        for metric_name, metric in metrics.items():
            print(f"  - {metric_name}")

            result = measure_metric(
                metric=metric,
                test_case=test_case,
            )

            metric_results[metric_name] = result

            if result["score"] is not None:
                score_collection[
                    metric_name
                ].append(result["score"])

            if result["passed"] is not None:
                pass_collection[
                    metric_name
                ].append(bool(result["passed"]))

        case_results.append(
            {
                "case_id": case["case_id"],
                "query": query,
                "should_refuse": should_refuse,
                "answer": response["answer"],
                "generator_model": response["model"],
                "judge_model": (
                    judge.get_model_name()
                ),
                "retrieved_sources": [
                    {
                        "citation": source[
                            "citation"
                        ],
                        "document_title": source[
                            "document_title"
                        ],
                        "section_title": source[
                            "section_title"
                        ],
                        "similarity_score": source[
                            "similarity_score"
                        ],
                    }
                    for source in response["sources"]
                ],
                "metrics": metric_results,
            }
        )

    metric_summary: dict[
        str,
        dict[str, Any],
    ] = {}

    for metric_name, scores in (
        score_collection.items()
    ):
        passed_values = pass_collection[
            metric_name
        ]

        metric_summary[metric_name] = {
            "case_count": len(scores),
            "average_score": round(
                sum(scores) / len(scores),
                4,
            ),
            "pass_rate": round(
                sum(passed_values)
                / len(passed_values),
                4,
            ),
        }

    return {
        "generated_at": (
            datetime.now()
            .astimezone()
            .isoformat(timespec="seconds")
        ),
        "evaluation_method": "deepeval_llm_judge",
        "threshold": 0.7,
        "summary": metric_summary,
        "cases": case_results,
    }


def save_result(
    result: dict[str, Any],
) -> None:
    """保存DeepEval语义评测结果。"""

    RESULT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    with RESULT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2,
        )


def print_summary(
    result: dict[str, Any],
) -> None:
    """打印语义评测摘要。"""

    print("\nDeepEval语义评测完成")
    print("=" * 60)

    for metric_name, summary in (
        result["summary"].items()
    ):
        print(
            f"{metric_name}: "
            f"平均分={summary['average_score']:.4f}, "
            f"通过率={summary['pass_rate']:.2%}, "
            f"用例数={summary['case_count']}"
        )

    print("\n完整结果已保存：")
    print(RESULT_PATH)


def main() -> None:
    """执行DeepEval语义评测。"""

    result = evaluate_semantic_quality()
    save_result(result)
    print_summary(result)


if __name__ == "__main__":
    main()