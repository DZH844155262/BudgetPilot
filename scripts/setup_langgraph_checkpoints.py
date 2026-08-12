from langgraph.checkpoint.postgres import (
    PostgresSaver,
)

from app.database import engine


def get_checkpoint_db_uri() -> str:
    """复用BudgetPilot现有数据库连接。"""

    database_url = (
        engine.url.render_as_string(
            hide_password=False
        )
    )

    # SQLAlchemy:
    # postgresql+psycopg://...
    #
    # PostgresSaver / psycopg:
    # postgresql://...
    database_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

    return database_url


def setup_checkpointer() -> None:
    """初始化LangGraph checkpoint表。"""

    db_uri = get_checkpoint_db_uri()

    with PostgresSaver.from_conn_string(
        db_uri
    ) as checkpointer:
        checkpointer.setup()

    print(
        "LangGraph checkpoint tables setup OK"
    )


if __name__ == "__main__":
    setup_checkpointer()