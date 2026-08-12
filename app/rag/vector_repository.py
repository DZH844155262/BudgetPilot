from typing import Any

from sqlalchemy import select

from app.database import SessionLocal
from app.models import PolicyChunk

from .embedding_service import embed_query


def search_policy_chunks(
    query: str,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """根据用户问题检索最相关的制度文档块。"""

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("检索问题不能为空")

    if top_k <= 0:
        raise ValueError("top_k必须大于0")

    query_vector = embed_query(cleaned_query)

    distance_expression = (
        PolicyChunk.embedding
        .cosine_distance(query_vector)
        .label("distance")
    )

    statement = (
        select(
            PolicyChunk.chunk_id,
            PolicyChunk.source,
            PolicyChunk.path,
            PolicyChunk.content,
            PolicyChunk.document_title,
            PolicyChunk.section_title,
            PolicyChunk.subsection_title,
            distance_expression,
        )
        .order_by(distance_expression)
        .limit(top_k)
    )

    with SessionLocal() as session:
        rows = session.execute(statement).all()

    return [
    {
        "chunk_id": row.chunk_id,
        "source": row.source,
        "path": row.path,
        "document_title": row.document_title,
        "section_title": row.section_title,
        "subsection_title": row.subsection_title,
        "content": row.content,
        "similarity_score": round(
            1.0 - float(row.distance),
            4,
        ),
    }
    for row in rows
]


if __name__ == "__main__":
    results = search_policy_chunks(
        query="单笔费用达到20000元需要谁复核？",
        top_k=3,
    )

    for index, result in enumerate(
        results,
        start=1,
    ):
        print("\n" + "=" * 60)
        print(f"排名：{index}")
        print(f"相似度：{result['similarity_score']}")
        print(f"来源：{result['source']}")
        print(f"Chunk：{result['chunk_id']}")
        print(result["content"])