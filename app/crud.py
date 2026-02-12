from sqlalchemy.orm import Session
from . import models, schemas, datetime


def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

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

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# search book
def search_books(db: Session, query: str):
    return db.query(models.Book).filter(
        (models.Book.title.ilike(f"%{query}%")) | 
        (models.Book.author.ilike(f"%{query}%"))
    ).all()

# Remove book
def delete_book(db: Session, isbn: str):
    db_book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if db_book:
        db.delete(db_book)
        db.commit()
        return True
    return False


# Book Issue karne ka logic
def issue_book(db: Session, user_id: int, book_id: int):
    new_transaction = models.Transaction(user_id=user_id, book_id=book_id)
    db.add(new_transaction)
    db.commit()
    return new_transaction

# Book Return karne ka logic
def return_book(db: Session, transaction_id: int):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if transaction:
        transaction.return_date = datetime.utcnow()
        transaction.status = "returned"
        db.commit()
        return True
    return False