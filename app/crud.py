from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas

# --- Book Operations ---

# Fetch a single book by its internal ID
def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

# Fetch all books with optional pagination (skip and limit)
def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

# Create a new book record in the database
def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        description=book.description
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# --- User Operations ---

# Find a user by their unique username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# Save a new user to the database
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Search & Delete ---

# Search for books by title or author using case-insensitive partial match
def search_books(db: Session, query: str):
    return db.query(models.Book).filter(
        (models.Book.title.ilike(f"%{query}%")) | 
        (models.Book.author.ilike(f"%{query}%"))
    ).all()

# Remove a book from the library using its ISBN
def delete_book(db: Session, isbn: str):
    db_book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if db_book:
        db.delete(db_book)
        db.commit()
        return True
    return False

# --- Transaction Management (Borrowing & Returning) ---

# Record a new book issuance to a user
def issue_book(db: Session, user_id: int, book_id: int):
    new_transaction = models.Transaction(user_id=user_id, book_id=book_id)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

# Mark a borrowed book as returned and update the timestamp
def return_book(db: Session, transaction_id: int):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if transaction:
        transaction.return_date = datetime.utcnow()
        transaction.status = "returned"
        db.commit()
        return True
    return False

# --- Reporting (Crucial for Frontend) ---

# Fetch all active (issued) transactions for a specific user to display in their dashboard
'''def get_user_transactions(db: Session, user_id: int):
    # This query joins the Transaction and Book tables to provide the book title for the UI
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.status == "issued"
    ).all()
    
    # Returning a formatted list for the frontend to easily display
    return [
        {
            "id": t.id,
            "book_title": t.book.title,
            "issue_date": t.issue_date.strftime("%Y-%m-%d %H:%M"),
            "status": t.status
        } for t in transactions
    ]'''

def get_user_transactions(db: Session, user_id: int):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.status == "issued"
    ).all()
    
    result = []
    for t in transactions:
        # Check if book exists before accessing title
        book_title = t.book.title if t.book else "Unknown Book"
        result.append({
            "id": t.id,
            "book_title": book_title,
            "issue_date": t.issue_date.strftime("%Y-%m-%d"),
            "status": t.status
        })
    return result         