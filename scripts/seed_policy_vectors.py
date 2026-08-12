from sqlalchemy import delete, func, select

from app.database import SessionLocal
from app.models import PolicyChunk
from app.rag.embedding_service import (
    embed_documents,
    get_embedding_dimension,
)
from app.rag.policy_loader import (
    load_policy_documents,
    split_policy_documents,
)


def seed_policy_vectors() -> None:
    """将制度文档块及其向量写入PostgreSQL。"""

    documents = load_policy_documents()
    chunks = split_policy_documents(documents)

    contents = [
        chunk.page_content
        for chunk in chunks
    ]

    vectors = embed_documents(contents)

    if get_embedding_dimension() != 512:
        raise ValueError("Embedding模型维度不是512")

    with SessionLocal.begin() as session:
        # 开发阶段重新构建制度向量数据
        session.execute(delete(PolicyChunk))

        policy_chunk_objects = [
            PolicyChunk(
    chunk_id=str(chunk.metadata["chunk_id"]),
    source=str(chunk.metadata["source"]),
    path=str(chunk.metadata["path"]),
    document_title=(
        str(chunk.metadata["document_title"])
        if chunk.metadata.get("document_title")
        else None
    ),
    section_title=(
        str(chunk.metadata["section_title"])
        if chunk.metadata.get("section_title")
        else None
    ),
    subsection_title=(
        str(chunk.metadata["subsection_title"])
        if chunk.metadata.get("subsection_title")
        else None
    ),
    content=chunk.page_content,
    embedding=vector,
)
            for chunk, vector in zip(
                chunks,
                vectors,
                strict=True,
            )
        ]

        session.add_all(policy_chunk_objects)

    with SessionLocal() as session:
        chunk_count = session.scalar(
            select(func.count()).select_from(PolicyChunk)
        )

    print("制度向量初始化完成：")
    print(f"- 原始文档：{len(documents)}份")
    print(f"- 文档块：{len(chunks)}个")
    print(f"- 数据库记录：{chunk_count}条")
    print(f"- 向量维度：{get_embedding_dimension()}")


if __name__ == "__main__":
    seed_policy_vectors()