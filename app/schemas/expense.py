from pydantic import BaseModel,Field
from typing import Optional
from datetime import date
from enum import Enum

class Category(str,Enum):
    groceries = "groceries"
    entertainment = "entertainment"
    gas = "gas"
    housing = "housing"
    dining = "dining"
    utilities = "utilities"
    other = "other"

class ExpenseCreator(BaseModel):
    amount: float = Field(gt=0)
    descr: str = Field(min_length=1, max_length=200)
    notes: Optional[str]=None
    date: date

class Expense(ExpenseCreator):
    category: Category
    id: int

    model_config = {"from_attributes": True}
