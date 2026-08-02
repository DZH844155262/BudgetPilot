import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def create_database_engine() -> Engine:
    """创建 PostgreSQL 数据库连接引擎。"""

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


engine = create_database_engine()
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

def check_database_connection() -> dict[str, str]:
    """检查数据库连接并返回当前数据库和用户。"""

    with engine.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT
                    current_database() AS database_name,
                    current_user AS user_name
                """
            )
        ).one()

    return {
    "database_name": row.database_name,
    "user_name": row.user_name,
}


if __name__ == "__main__":
    print(check_database_connection())