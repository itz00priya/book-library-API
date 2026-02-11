import streamlit as st
import requests


API_URL = "http://localhost:8000"

st.set_page_config(page_title="My Digital Library", layout="wide")

st.title("📚 My Digital Book Library")

# Sidebar for Login
st.sidebar.header("User Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        st.session_state["token"] = response.json()["access_token"]
        st.sidebar.success("Logged In!")
    else:
        st.sidebar.error("Invalid Credentials")

# Main Section: Add Book
st.subheader("Add a New Book")
isbn = st.text_input("Enter ISBN-13 (e.g., 9780143424888)")

if st.button("Add to Library"):
    if "token" in st.session_state:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        res = requests.post(f"{API_URL}/books/{isbn}", headers=headers)
        if res.status_code == 200:
            st.success(f"Book Added: {res.json()['title']}")
        else:
            st.error("Error adding book or unauthorized")
    else:
        st.warning("Please login first from the sidebar")

# Section: View Library
st.divider()
st.subheader("My Collection")
if st.button("Refresh Library"):
    books = requests.get(f"{API_URL}/books").json()
    for book in books:
        with st.expander(f"{book['title']} - {book['author']}"):
            st.write(f"**ISBN:** {book['isbn']}")
            st.write(f"**Description:** {book['description']}")