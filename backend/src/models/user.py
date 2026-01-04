from datetime import datetime
from sqlmodel import Field, SQLModel
from pydantic import EmailStr


class USER(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name : str 
    email: str = Field(unique=True, index=True)
    password : str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)




class UserCreate(SQLModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(SQLModel):
    id: int
    name: str
    email: str


class Token(SQLModel):
    access_token: str
    token_type: str