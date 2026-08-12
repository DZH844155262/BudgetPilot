from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = PROJECT_ROOT / "knowledge" / "policies"


def load_policy_documents() -> list[Document]:
    """读取所有 Markdown 格式的预算制度文档。"""

    policy_files = sorted(POLICY_DIR.glob("*.md"))

    if not policy_files:
        raise ValueError("未找到预算制度文档")

    documents: list[Document] = []

    for file_path in policy_files:
        content = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": file_path.name,
                    "path": str(
                        file_path.relative_to(PROJECT_ROOT)
                    ),
                },
            )
        )

    return documents


def split_policy_documents(
    documents: list[Document],
    chunk_size: int = 350,
    chunk_overlap: int = 50,
) -> list[Document]:
    """先按Markdown标题切分，再处理过长章节。"""

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "document_title"),
            ("##", "section_title"),
            ("###", "subsection_title"),
        ],
        strip_headers=False,
    )

    length_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            "。",
            "；",
            "，",
            " ",
        ],
    )

    chunks: list[Document] = []
    source_counts: dict[str, int] = {}

    for document in documents:
        section_documents = header_splitter.split_text(
            document.page_content
        )

        for section_document in section_documents:
            # 保留原文件来源，同时保留标题切分产生的章节信息
            section_document.metadata = {
                **document.metadata,
                **section_document.metadata,
            }

            section_chunks = length_splitter.split_documents(
                [section_document]
            )

            for chunk in section_chunks:
                source = str(chunk.metadata["source"])
                chunk_index = source_counts.get(source, 0)

                chunk.metadata["chunk_id"] = (
                    f"{Path(source).stem}-{chunk_index:03d}"
                )

                source_counts[source] = chunk_index + 1
                chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    policy_documents = load_policy_documents()
    policy_chunks = split_policy_documents(policy_documents)

    print(f"原始制度文档：{len(policy_documents)}份")
    print(f"切分后的文档块：{len(policy_chunks)}个")

    for chunk in policy_chunks:
        print("\n" + "=" * 60)
        print(chunk.metadata)
        print(chunk.page_content)