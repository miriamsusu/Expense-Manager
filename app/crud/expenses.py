from app.schemas.expense import *
from app.services.categorization import categorize
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreator
from app.services.categorization import categorize

def getExpenses(db: Session, user_id:int) -> list[Expense]:
    return db.query(Expense).filter(Expense.user_id == user_id).all()

def createExpense(db: Session, payload: ExpenseCreator) -> Expense:
    category = categorize(payload.descr)
    db_expense = Expense( category=category,**payload.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def getExpense(db: Session, expense_id: int)->Expense | None:
    return db.query(Expense).filter(Expense.id == expense_id).first()

def deleteExpense(db: Session, expense_id: int) -> bool:
    db_expense = getExpense(db,expense_id)
    if db_expense is None:
        return False
    db.delete(db_expense)
    db.commit()
    return True
