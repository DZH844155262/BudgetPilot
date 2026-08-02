from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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