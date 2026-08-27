from fastapi import Depends,FastAPI,HTTPException
from app.crud import expenses as expense_store
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.schemas.expense import Expense,ExpenseCreator
app = FastAPI(title="Expense manager")

@app.get("/")
def root():
    return {"status":"ok"}

@app.get("/expenses", response_model=list[Expense])
def getExpenses(db: Session = Depends(get_db)):
    return expense_store.getExpenses(db)

@app.post("/expenses", response_model=Expense, status_code=201)
def createExpense(payload: ExpenseCreator,db: Session = Depends(get_db)):
    return expense_store.createExpense(db,payload)

@app.get("/expenses/{expense_id}", response_model=Expense)
def getExpense(expense_id:int,db: Session = Depends(get_db)):
    expense=expense_store.createExpense(db,expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.delete("/expenses/{expense_id}", status_code=204)
def deleteExpense(expense_id: int,db: Session = Depends(get_db)):
    deleted=expense_store.deleteExpense(db,expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
