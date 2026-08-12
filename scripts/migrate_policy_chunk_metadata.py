from sqlalchemy import text

from app.database import engine


def migrate_policy_chunk_metadata() -> None:
    """为制度向量表增加标题元数据字段。"""

    statements = [
        """
        ALTER TABLE policy_chunks
        ADD COLUMN IF NOT EXISTS document_title VARCHAR(255)
        """,
        """
        ALTER TABLE policy_chunks
        ADD COLUMN IF NOT EXISTS section_title VARCHAR(255)
        """,
        """
        ALTER TABLE policy_chunks
        ADD COLUMN IF NOT EXISTS subsection_title VARCHAR(255)
        """,
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

    print("policy_chunks 元数据字段迁移完成：")
    print("- document_title")
    print("- section_title")
    print("- subsection_title")


if __name__ == "__main__":
    migrate_policy_chunk_metadata()