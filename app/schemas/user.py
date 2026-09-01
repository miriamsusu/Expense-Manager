from pydantic import BaseModel,EmailStr,Field

class UserCreate(BaseModel):
    email: EmailStr
    phone_number: str = Field(pattern=r"^\+?[0-9]{7,15}$")
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    id: int
    email: EmailStr
    phone_number: str
    model_config = {"from_attributes": True}