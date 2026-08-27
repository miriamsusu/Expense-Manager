from pydantic import BaseModel,EmailStr,Field

class UserCreate(BaseModel):
    email: EmailStr
    phone_Number: str = Field(pattern=r"^\+?[0-9]{7,15}$")
    password: str = Field(min_length=8)

class User(BaseModel):
    id: int
    email: EmailStr
    phone_number: str
    model_config = {"from_attributes": True}