from pydantic import BaseModel
from typing import Optional, List

# Base Schema:
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    description: Optional[str] = None

# Create Schema: 
class BookCreate(BookBase):
    pass

# Response Schema: 
class Book(BookBase):
    id: int

    class Config:
        from_attributes = True  

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True