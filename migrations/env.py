from logging.config import fileConfig

from alembic import context

from app.database import engine
from app.models import Base


# Alembic Config 对象
config = context.config


# 配置 Alembic 日志
if config.config_file_name is not None:
    fileConfig(
        config.config_file_name
    )


# SQLAlchemy ORM 模型元数据
# Alembic autogenerate 会拿它与真实数据库进行比较
target_metadata = Base.metadata


# 这些表由 LangGraph PostgresSaver 自己维护，
# 不属于 BudgetPilot 业务 Schema。
LANGGRAPH_TABLES = {
    "checkpoints",
    "checkpoint_blobs",
    "checkpoint_writes",
    "checkpoint_migrations",
}


def include_object(
    object_,
    name,
    type_,
    reflected,
    compare_to,
):
    """排除不应由 Alembic 管理的数据库对象。"""

    if (
        type_ == "table"
        and name in LANGGRAPH_TABLES
    ):
        return False

    return True


def run_migrations_offline() -> None:
    """离线模式运行迁移。"""

    database_url = (
        engine.url.render_as_string(
            hide_password=False
        )
    )

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式运行迁移。"""

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()