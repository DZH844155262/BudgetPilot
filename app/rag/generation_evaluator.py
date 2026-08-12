import re
import time
from collections.abc import Callable
from typing import Any

from .rag_service import answer_policy_question
REFUSAL_TEXT = "现有制度资料不足以回答该问题"

AnswerFunction = Callable[
    [str, int],
    dict[str, Any],
]


def _check_required_keywords(
    answer: str,
    case: dict[str, Any],
) -> bool:
    """检查所有必需关键词和关键词组。"""

    required_keywords = case.get(
        "required_keywords_all",
        [],
    )

    all_keywords_pass = all(
        keyword in answer
        for keyword in required_keywords
    )

    keyword_groups = case.get(
        "required_keyword_groups",
        [],
    )

    groups_pass = all(
        any(
            keyword in answer
            for keyword in group
        )
        for group in keyword_groups
    )

    return all_keywords_pass and groups_pass


def _check_forbidden_keywords(
    answer: str,
    case: dict[str, Any],
) -> bool:
    """检查回答中是否出现禁止内容。"""

    forbidden_keywords = case.get(
        "forbidden_keywords",
        [],
    )

    return not any(
        keyword in answer
        for keyword in forbidden_keywords
    )


def _find_expected_source(
    sources: list[dict[str, Any]],
    case: dict[str, Any],
) -> dict[str, Any] | None:
    """从引用来源中查找人工标注的正确章节。"""

    expected_document = case.get(
        "expected_document_title"
    )
    expected_section = case.get(
        "expected_section_title"
    )

    if expected_document is None:
        return None

    for source in sources:
        if (
            source.get("document_title")
            == expected_document
            and source.get("section_title")
            == expected_section
        ):
            return source

    return None


def _check_citations(
    answer: str,
    sources: list[dict[str, Any]],
    case: dict[str, Any],
    expected_source: dict[str, Any] | None,
) -> bool:
    """检查引用编号是否存在且能够对应真实来源。"""

    citation_required = case.get(
        "citation_required",
        True,
    )

    citation_numbers = re.findall(
        r"\[(\d+)\]",
        answer,
    )

    if not citation_required:
        return True

    if not citation_numbers:
        return False

    valid_number_range = all(
        1 <= int(number) <= len(sources)
        for number in citation_numbers
    )

    if not valid_number_range:
        return False

    if expected_source is None:
        return False

    expected_citation = expected_source.get(
        "citation"
    )

    return (
        isinstance(expected_citation, str)
        and expected_citation in answer
    )


def evaluate_generation_cases(
    cases: list[dict[str, Any]],
    answer_function: AnswerFunction | None = None,
) -> dict[str, Any]:
    """执行制度回答确定性规则评测。"""

    if not cases:
        raise ValueError("生成评测用例不能为空")

    answerer = (
        answer_function
        or answer_policy_question
    )

    results: list[dict[str, Any]] = []

    pass_count = 0
    keyword_pass_count = 0
    forbidden_pass_count = 0
    source_pass_count = 0
    citation_pass_count = 0
    refusal_pass_count = 0
    refusal_case_count = 0
    total_latency = 0.0

    for case in cases:
        started_at = time.perf_counter()

        response = answerer(
            case["query"],
            case.get("top_k", 3),
        )

        latency_seconds = (
            time.perf_counter() - started_at
        )

        total_latency += latency_seconds

        answer = response["answer"]
        sources = response.get("sources", [])

        keyword_pass = _check_required_keywords(
            answer,
            case,
        )

        forbidden_pass = _check_forbidden_keywords(
            answer,
            case,
        )

        expected_source = _find_expected_source(
            sources,
            case,
        )

        should_refuse = case.get(
            "should_refuse",
            False,
        )

        if should_refuse:
            source_pass = True
        else:
            source_pass = expected_source is not None

        citation_pass = _check_citations(
            answer=answer,
            sources=sources,
            case=case,
            expected_source=expected_source,
        )
        contains_refusal = REFUSAL_TEXT in answer

        if should_refuse:
            refusal_case_count += 1
            refusal_pass = contains_refusal
            over_refusal_pass = True

            if refusal_pass:
                refusal_pass_count += 1
        else:
            refusal_pass = True
            over_refusal_pass = not contains_refusal

        case_pass = all(
            [
                keyword_pass,
                forbidden_pass,
                source_pass,
                citation_pass,
                refusal_pass,
                over_refusal_pass,
            ]
        )

        if case_pass:
            pass_count += 1

        if keyword_pass:
            keyword_pass_count += 1

        if forbidden_pass:
            forbidden_pass_count += 1

        if source_pass:
            source_pass_count += 1

        if citation_pass:
            citation_pass_count += 1

        results.append(
            {
                "case_id": case["case_id"],
                "query": case["query"],
                "answer": answer,
                "model": response.get("model"),
                "passed": case_pass,
                "keyword_pass": keyword_pass,
                "forbidden_pass": forbidden_pass,
                "source_pass": source_pass,
                "citation_pass": citation_pass,
                "refusal_pass": refusal_pass,
                "over_refusal_pass": over_refusal_pass,
                "latency_seconds": round(
                    latency_seconds,
                    3,
                ),
                "expected_document_title": (
                    case.get(
                        "expected_document_title"
                    )
                ),
                "expected_section_title": (
                    case.get(
                        "expected_section_title"
                    )
                ),
                "sources": sources,
            }
        )

    case_count = len(cases)

    return {
        "summary": {
            "case_count": case_count,
            "pass_count": pass_count,
            "pass_rate": round(
                pass_count / case_count,
                4,
            ),
            "keyword_pass_rate": round(
                keyword_pass_count / case_count,
                4,
            ),
            "forbidden_pass_rate": round(
                forbidden_pass_count / case_count,
                4,
            ),
            "source_pass_rate": round(
                source_pass_count / case_count,
                4,
            ),
            "citation_pass_rate": round(
                citation_pass_count / case_count,
                4,
            ),
            "refusal_pass_rate": (
                round(
                    refusal_pass_count
                    / refusal_case_count,
                    4,
                )
                if refusal_case_count
                else None
            ),
            "average_latency_seconds": round(
                total_latency / case_count,
                3,
            ),
        },
        "cases": results,
    }