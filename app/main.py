import time
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database
from .services.google_books import fetch_book_details
from .database import engine
from . import models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import auth, schemas, crud
from fastapi import Depends

app = FastAPI(title="Book Library API")

time.sleep(3) 
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def home():
    return {"message": "Book Library API is Live!"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pw = auth.get_password_hash(user.password)
    user.password = hashed_pw
    return crud.create_user(db=db, user=user)

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/books/{isbn}")
async def add_book(
    isbn: str, 
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme)  
):
    # Check if book already exists
    db_book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Book already exists in library")
    
    # Fetch from Google
    book_data = await fetch_book_details(isbn)
    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found on Google Books")
    
    # Save to DB
    new_book = models.Book(**book_data)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/books")
def list_books(db: Session = Depends(database.get_db)):
    return db.query(models.Book).all()

# 1. Search Feature
@app.get("/books/search", response_model=list[schemas.Book])
def search_books(q: str, db: Session = Depends(database.get_db)):
    return crud.search_books(db, query=q)

# 2. Remove Feature (Search Librarian/Authorized for user)
@app.delete("/books/{isbn}")
def remove_book(
    isbn: str, 
    db: Session = Depends(database.get_db), 
    token: str = Depends(oauth2_scheme) # Lock laga diya
):
    success = crud.delete_book(db, isbn)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book removed successfully"}


@app.post("/books/issue/{book_id}")
def issue_a_book(book_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.issue_book(db, user_id=current_user.id, book_id=book_id)

@app.post("/books/return/{transaction_id}")
def return_a_book(transaction_id: int, db: Session = Depends(get_db)):
    success = crud.return_book(db, transaction_id=transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Book returned successfully"}






