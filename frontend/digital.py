import streamlit as st
import requests


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


      