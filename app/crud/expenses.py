from app.schemas.expense import *
from app.services.categorization import categorize
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreator
from app.services.categorization import categorize

def getExpenses(db: Session) -> list[Expense]:
    return db.query(Expense).all()

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
"""
class MemoryExpenses:
    def __init__(self):
        self._expenses:list[Expense] = []
        self._next_id = 1
    def getExpenses(self):
        return self._expenses

    def createExpense(self,payload:ExpenseCreator):
        category=categorize(payload.descr)
        expense=Expense(category,self._next_id,**payload.model_dump)

        self._expenses.append(expense)
        self._next_id+=1

        return expense

    def getExpense(self, expense_id:int):
        for expense in self._expenses:
            if expense_id==expense.id:
                return expense

        return None

    def deleteExpense(self,expense_id:int):
        if not any(e.id == expense_id for e in self._expenses):
            return False
        self._expenses = [e for e in self._expenses if e.id != expense_id]
        return True

"""


