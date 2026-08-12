from collections.abc import Callable
from typing import Any

from .llm_client import (
    generate_text,
    get_llm_model_name,
)
from .policy_retrieval_service import (
    retrieve_policy_context_with_rerank,
)


SYSTEM_PROMPT = """
你是企业预算与费用制度问答助手。

必须遵守以下规则：

1. 只能依据用户提供的制度上下文回答。
2. 不得使用上下文以外的企业制度或自行编造规定。
3. 每个关键结论后使用[1]、[2]等编号标明来源。
4. 先判断制度上下文能否回答用户问题：
   - 只要上下文中存在足以回答问题的明确规定，就直接回答。
   - 已经给出实质答案后，禁止再追加“现有制度资料不足以回答该问题”。
   - 只有全部制度上下文都无法支持答案时，才只输出：
     “现有制度资料不足以回答该问题。”
5. 只回答用户实际提出的问题，不主动扩展无关制度、其他业务场景或额外处理流程。
6. 回答应简洁、明确，适合普通企业员工阅读。
7. 不得修改制度中的金额、期限、审批人或处理要求。
8. 引用编号必须与制度上下文中的编号完全对应。
""".strip()

def _build_context(
    results: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    """将检索结果转换成提示词上下文和引用信息。"""

    context_blocks: list[str] = []
    sources: list[dict[str, Any]] = []

    for index, item in enumerate(
        results,
        start=1,
    ):
        citation = f"[{index}]"

        document_title = (
            item.get("document_title")
            or item["source"]
        )

        section_title = (
            item.get("section_title")
            or "未标注章节"
        )

        context_blocks.append(
            "\n".join(
                [
                    citation,
                    f"制度：{document_title}",
                    f"章节：{section_title}",
                    f"原文：{item['content']}",
                ]
            )
        )

        sources.append(
            {
                "citation": citation,
                "chunk_id": item["chunk_id"],
                "source": item["source"],
                "document_title": item.get(
                    "document_title"
                ),
                "section_title": item.get(
                    "section_title"
                ),
                "similarity_score": item[
                    "similarity_score"
                ],
            }
        )

    return "\n\n".join(context_blocks), sources


def answer_policy_question(
    query: str,
    top_k: int = 3,
    text_generator: (
        Callable[[str, str], str] | None
    ) = None,
) -> dict[str, Any]:
    """基于检索到的制度内容回答用户问题。"""

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("制度问题不能为空")

    retrieval_result = (
    retrieve_policy_context_with_rerank(
        query=cleaned_query,
        top_k=top_k,
        candidate_k=max(6, top_k),
    )
)

    context, sources = _build_context(
        retrieval_result["results"]
    )

    user_prompt = f"""
用户问题：
{cleaned_query}

制度上下文：
{context}

请根据制度上下文回答，并在关键结论后标注对应的引用编号。
""".strip()

    generator = text_generator or generate_text

    answer = generator(
        SYSTEM_PROMPT,
        user_prompt,
    )

    return {
        "query": cleaned_query,
        "answer": answer,
        "model": get_llm_model_name(),
        "source_count": len(sources),
        "sources": sources,
    }


if __name__ == "__main__":
    result = answer_policy_question(
        query="单笔费用达到20000元需要谁复核？",
        top_k=3,
    )

    print("\n回答：")
    print(result["answer"])

    print("\n引用来源：")
    for source in result["sources"]:
        print(source)