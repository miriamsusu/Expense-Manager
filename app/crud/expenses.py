from datetime import date as date_type

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.schemas.expense import Category, ExpenseCreator
from app.services.categorization import categorize


def getExpenses(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    category: Category | None = None,
    start_date: date_type | None = None,
    end_date: date_type | None = None,
) -> list[Expense]:
    query = db.query(Expense).filter(Expense.user_id == user_id)

    if category is not None:
        query = query.filter(Expense.category == category)
    if start_date is not None:
        query = query.filter(Expense.date >= start_date)
    if end_date is not None:
        query = query.filter(Expense.date <= end_date)

    return query.offset(skip).limit(limit).all()


def createExpense(db: Session, payload: ExpenseCreator, user_id: int) -> Expense:
    category = categorize(payload.descr)
    db_expense = Expense(category=category, user_id=user_id, **payload.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def getExpense(db: Session, expense_id: int, user_id: int) -> Expense | None:
    return (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == user_id)
        .first()
    )


def deleteExpense(db: Session, expense_id: int, user_id: int) -> bool:
    db_expense = getExpense(db, expense_id, user_id)
    if db_expense is None:
        return False
    db.delete(db_expense)
    db.commit()
    return True


def getExpenseSummary(db: Session, user_id: int) -> list[dict]:
    results = (
        db.query(Expense.category, func.sum(Expense.amount).label("total"))
        .filter(Expense.user_id == user_id)
        .group_by(Expense.category)
        .all()
    )
    return [{"category": category, "total": total} for category, total in results]