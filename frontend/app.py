import streamlit as st
import requests

# Docker network service name
API_URL = "http://app:8000"

st.set_page_config(page_title="My Digital Library", layout="wide")
st.title("📚 My Digital Book Library")

# --- SIDEBAR: LOGIN ---
st.sidebar.header("User Login")
# Persist login state
if "token" not in st.session_state:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state["token"] = response.json()["access_token"]
            st.sidebar.success("Logged In!")
            st.rerun()
        else:
            st.sidebar.error("Invalid Credentials")
else:
    st.sidebar.success("✅ Currently Logged In")
    if st.sidebar.button("Logout"):
        del st.session_state["token"]
        st.rerun()

# --- SECTION 1: ADD BOOK ---
st.header("📖 Add a New Book")
isbn_input = st.text_input("Enter ISBN-13 (e.g., 9780143424888)")
if st.button("Add to Library"):
    if "token" in st.session_state:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        res = requests.post(f"{API_URL}/books/{isbn_input}", headers=headers)
        if res.status_code == 200:
            st.success(f"Book Added: {res.json()['title']}")
        else:
            st.error("Error adding book or unauthorized")
    else:
        st.warning("Please login first from the sidebar")

# --- SECTION 2: SEARCH ---
st.divider()
st.header("🔍 Search in Library")
search_query = st.text_input("Search by Title or Author")
if st.button("Search"):
    results = requests.get(f"{API_URL}/books/search?q={search_query}").json()
    if results:
        for book in results:
            st.write(f"📖 {book['title']} by {book['author']}")
    else:
        st.info("No books found matching your search.")

# --- SECTION 3: MY COLLECTION & BORROW ---
st.divider()
st.header("📚 My Collection")

# Logic to keep books visible after clicking 'Borrow'
if st.button("Refresh Library List"):
    books_res = requests.get(f"{API_URL}/books")
    if books_res.status_code == 200:
        st.session_state["library_books"] = books_res.json()

if "library_books" in st.session_state:
    for book in st.session_state["library_books"]:
        with st.expander(f"{book['title']} - {book['author']}"):
            st.write(f"**ISBN:** {book['isbn']}")
            st.write(f"**Description:** {book['description']}")
            
            # Borrow Button Integration
            if st.button(f"📖 Borrow This Book", key=f"issue_{book['isbn']}"):
                if "token" in st.session_state:
                    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                    # Calling the issue endpoint from main.py
                    res = requests.post(f"{API_URL}/books/issue/{book['isbn']}", headers=headers)
                    if res.status_code == 200:
                        st.success(f"Success! Issued to you.")
                        st.rerun() # Refresh to update borrowed list
                    else:
                        st.error("Already borrowed or system error.")
                else:
                    st.warning("Login to borrow books")

# --- SECTION 4: MY BORROWED BOOKS (RETURN FEATURE) ---
st.divider()
st.header("📦 My Borrowed Books")

if "token" in st.session_state:
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    # Fetching active transactions from get_user_transactions in crud.py
    borrowed_res = requests.get(f"{API_URL}/users/me/books", headers=headers)
    
    if borrowed_res.status_code == 200:
        my_borrowed = borrowed_res.json()
        if not my_borrowed:
            st.info("You haven't borrowed any books yet.")
        else:
            for trans in my_borrowed:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"🏷️ **{trans['book_title']}**")
                    st.caption(f"Issued on: {trans['issue_date']}")
                with col2:
                    if st.button("🔄 Return", key=f"ret_{trans['id']}"):
                        ret_res = requests.post(f"{API_URL}/books/return/{trans['id']}", headers=headers)
                        if ret_res.status_code == 200:
                            st.success("Returned!")
                            st.rerun()
    else:
        st.error("Could not fetch your borrowed list.")

# --- SECTION 5: LIBRARIAN ACTIONS ---
if "token" in st.session_state:
    st.divider()
    st.subheader("🗑️ Librarian Actions")
    isbn_del = st.text_input("Enter ISBN to Remove", key="del_isbn")
    if st.button("Delete From Library"):
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        d_res = requests.delete(f"{API_URL}/books/{isbn_del}", headers=headers)
        if d_res.status_code == 200:
            st.success("Book removed from catalog!")
            if "library_books" in st.session_state:
                del st.session_state["library_books"] # Clear cache to refresh
            st.rerun()
        else:
            st.error("Failed to delete. Check ISBN or permissions.")