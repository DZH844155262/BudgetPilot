from sqlalchemy import inspect

from .database import engine
from .models import Base


def create_tables() -> None:
    """根据 SQLAlchemy 模型创建数据库表."""

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()

    table_names = inspect(engine).get_table_names()

    print("数据库表创建完成：")
    for table_name in table_names:
        print(f"- {table_name}")