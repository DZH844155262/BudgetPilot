from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import VECTOR

class Base(DeclarativeBase):
    """所有数据库表模型的基础类."""


class Department(Base):
    """企业部门表."""

    __tablename__ = "departments"

    department_id: Mapped[str] = mapped_column(
        String(10),
        primary_key=True,
    )
    department_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )


class Budget(Base):
    """部门月度预算表."""

    __tablename__ = "budgets"

    __table_args__ = (
        UniqueConstraint(
            "month",
            "department_id",
            "category",
            name="uq_budget_month_department_category",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    month: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
    )
    department_id: Mapped[str] = mapped_column(
        ForeignKey("departments.department_id"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    budget_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )


class Expense(Base):
    """实际费用明细表."""

    __tablename__ = "expenses"

    expense_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    department_id: Mapped[str] = mapped_column(
        ForeignKey("departments.department_id"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    actual_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

class PolicyChunk(Base):
    """预算制度文档块及其语义向量。"""

    __tablename__ = "policy_chunks"

    chunk_id: Mapped[str] = mapped_column(
        String(150),
        primary_key=True,
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    document_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    section_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    subsection_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        VECTOR(512),
        nullable=False,
    )