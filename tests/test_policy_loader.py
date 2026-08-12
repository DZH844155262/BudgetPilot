from app.rag.policy_loader import (
    load_policy_documents,
    split_policy_documents,
)


def test_load_policy_documents() -> None:
    """应读取全部预算制度文档。"""

    documents = load_policy_documents()

    assert len(documents) == 2

    sources = {
        document.metadata["source"]
        for document in documents
    }

    assert sources == {
        "budget_management_policy.md",
        "expense_reimbursement_policy.md",
    }

    assert all(
        document.page_content.strip()
        for document in documents
    )


def test_split_policy_documents() -> None:
    """应将制度文档切分并保留来源信息。"""

    documents = load_policy_documents()
    chunks = split_policy_documents(documents)

    assert len(chunks) >= len(documents)

    assert all(
        chunk.page_content.strip()
        for chunk in chunks
    )

    assert all(
        "source" in chunk.metadata
        for chunk in chunks
    )

    assert all(
        "chunk_id" in chunk.metadata
        for chunk in chunks
    )

    chunk_ids = [
        chunk.metadata["chunk_id"]
        for chunk in chunks
    ]

    assert len(chunk_ids) == len(set(chunk_ids))