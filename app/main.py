from fastapi import Depends,FastAPI,HTTPException
from app.crud import expenses as expense_store
from app.crud import user as user_store
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.schemas.expense import Expense,ExpenseCreator
from app.schemas.user import Token, User as UserOut, UserCreate, UserLogin
from app.auth.oauth2 import create_access_token, get_current_user
from app.auth.security import verify_password
from app.models.user import User
app = FastAPI(title="Expense manager")

@app.get("/")
def root():
    return {"status":"ok"}

@app.post("/auth/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if user_store.getUserByEmail(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_store.createUser(db, payload)

@app.post("/auth/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = user_store.getUserByEmail(db, payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token(data={"sub": user.email})
    return Token(access_token=token)

@app.get("/users/me", response_model=UserOut)
def readCurrentUser(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/expenses", response_model=list[Expense])
def getExpenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return expense_store.getExpenses(db, current_user.id)

@app.post("/expenses", response_model=Expense, status_code=201)
def createExpense(payload: ExpenseCreator,db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return expense_store.createExpense(db,payload, current_user.id)

@app.get("/expenses/{expense_id}", response_model=Expense)
def getExpense(expense_id:int,db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense=expense_store.getExpense(db,expense_id, current_user.id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.delete("/expenses/{expense_id}", status_code=204)
def deleteExpense(expense_id: int,db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted=expense_store.deleteExpense(db,expense_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")