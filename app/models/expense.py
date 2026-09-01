from datetime import date as date_type

from sqlalchemy import Date, Enum, Float, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.schemas.expense import Category


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float)
    descr: Mapped[str] = mapped_column(String(200))  # matches ExpenseCreator.descr
    notes: Mapped[str | None] = mapped_column(String, nullable=True)  # matches ExpenseCreator.notes, optional
    category: Mapped[Category] = mapped_column(Enum(Category))
    date: Mapped[date_type] = mapped_column(Date)