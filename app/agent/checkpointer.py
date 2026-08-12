from langgraph.checkpoint.postgres import (
    PostgresSaver,
)
from psycopg import Connection
from psycopg.rows import dict_row

from app.database import engine


def get_checkpoint_db_uri() -> str:
    """复用BudgetPilot现有PostgreSQL连接配置。"""

    database_url = (
        engine.url.render_as_string(
            hide_password=False
        )
    )

    return database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )


checkpoint_connection = Connection.connect(
    get_checkpoint_db_uri(),
    autocommit=True,
    prepare_threshold=0,
    row_factory=dict_row,
)

checkpointer = PostgresSaver(
    checkpoint_connection
)