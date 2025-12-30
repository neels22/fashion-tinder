from datetime import datetime
from sqlmodel import Field, SQLModel


class USER(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name : str 
    email: str = Field(unique=True, index=True)
    password : str
    image_url: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
