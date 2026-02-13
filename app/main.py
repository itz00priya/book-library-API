import time
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import auth

# Internal module imports
from . import models, database, auth, schemas, crud
from .database import engine, get_db
from .services.google_books import fetch_book_details

app = FastAPI(title="Book Library API")

# Wait for the database to be ready and create tables
time.sleep(3) 
models.Base.metadata.create_all(bind=engine)

# Security scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Dependency to get the current logged-in user ---
'''async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid authentication credentials"
        )
    user = crud.get_user_by_username(db, username=payload.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user'''

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    user = crud.get_user_by_username(db, username=payload.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Basic Routes ---
@app.get("/")
def home():
    return {"message": "Book Library API is Live!"}

# --- Authentication Routes ---
@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash the password before saving
    user.password = auth.get_password_hash(user.password)
    return crud.create_user(db=db, user=user)

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Generate JWT token
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Book Management Routes ---
@app.post("/books/{isbn}")
async def add_book(
    isbn: str, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)  
):
    # Check if book already exists in local database
    db_book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Book already exists in library")
    
    # Fetch metadata from Google Books API
    book_data = await fetch_book_details(isbn)
    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found on Google Books")
    
    # Save fetched book to database
    new_book = models.Book(**book_data)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/books", response_model=list[schemas.Book])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

@app.get("/books/search", response_model=list[schemas.Book])
def search_books(q: str, db: Session = Depends(get_db)):
    return crud.search_books(db, query=q)

@app.delete("/books/{isbn}")
def remove_book(
    isbn: str, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    success = crud.delete_book(db, isbn)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book removed successfully"}

# --- Transaction Management Routes (Borrowing & Returning) ---

# Borrow/Issue a book using its ISBN
'''@app.post("/books/issue/{isbn}")
def issue_a_book(isbn: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return crud.issue_book(db, user_id=current_user.id, book_id=book.id)'''

@app.post("/books/issue/{isbn}") # Ensure 'isbn' is used, not 'book_id'
def issue_a_book(isbn: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return crud.issue_book(db, user_id=current_user.id, book_id=book.id)

# Return a book using the transaction ID
@app.post("/books/return/{transaction_id}")
def return_a_book(transaction_id: int, db: Session = Depends(get_db)):
    success = crud.return_book(db, transaction_id=transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Book returned successfully"}

# Get list of books borrowed by the current logged-in user
@app.get("/users/me/books")
def get_my_borrowed_books(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_transactions(db, user_id=current_user.id)

def role_required(required_role: str):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user
    return role_checker

# Example: Only Admin or Librarian can delete a book
@app.delete("/books/{isbn}")
def delete_book(isbn: str, db: Session = Depends(get_db), admin_user = Depends(role_required("librarian"))):
    return crud.delete_book(db, isbn)