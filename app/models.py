from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# --- Book Model ---
# Represents the catalog of books in the library
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    isbn = Column(String, unique=True, index=True) # Unique ISBN as primary identifier
    description = Column(Text, nullable=True)

    # Relationship to track transactions for this book
    transactions = relationship("Transaction", back_populates="book")
    

# --- User Model ---
# Stores member login details and hashed passwords

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # Default role is 'member'
    role = Column(String, default="member") 
    
    transactions = relationship("Transaction", back_populates="user")
# --- Transaction Model ---
# Tracks the borrowing (issuing) and returning of books
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    
    # Timestamps for book movement
    issue_date = Column(DateTime, default=datetime.utcnow) # Auto-sets current time
    return_date = Column(DateTime, nullable=True) # Filled only when book is returned
    
    # Status can be 'issued' or 'returned'
    status = Column(String, default="issued")

    # Links back to User and Book models
    book = relationship("Book", back_populates="transactions")
    user = relationship("User", back_populates="transactions") 