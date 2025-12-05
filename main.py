import streamlit as st
import requests
from time import sleep

# -----------------------------
# Firebase Web API Key
# -----------------------------
API_KEY = "AIzaSyAYOROctBoSyJ3aeHafUm-62zDl8uA2TQU"

# -----------------------------
# Session State Setup
# -----------------------------
if "id_token" not in st.session_state:
    st.session_state.id_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "page" not in st.session_state:
    st.session_state.page = "auth"


# -----------------------------
# Firebase REST API FUNCTIONS
# -----------------------------

def signup_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "idToken" in data:
        st.success("Account created successfully! Please log in.")
        return True
    else:
        st.error(data.get("error", {}).get("message", "Signup failed."))
        return False


def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "idToken" in data:
        st.session_state.id_token = data["idToken"]
        st.session_state.user_email = data["email"]
        st.session_state.page = "dashboard"
        st.success("Login successful!")
        sleep(0.5)
        st.rerun()
    else:
        st.error(data.get("error", {}).get("message", "Login failed."))


def logout():
    st.session_state.id_token = None
    st.session_state.user_email = None
    st.session_state.page = "auth"
    st.info("Logged out.")
    st.rerun()


# -----------------------------
# UI: Auth Page
# -----------------------------
def render_auth_page():
    st.title("🍕 Pizza Planet - Login")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # LOGIN TAB
    with tab1:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if email and password:
                    login_user(email, password)
                else:
                    st.warning("Please enter both fields.")

    # SIGNUP TAB
    with tab2:
        with st.form("signup"):
            email = st.text_input("Email ")
            password = st.text_input("Password (min 6 chars)", type="password")
            submit = st.form_submit_button("Create Account")

            if submit:
                if len(password) >= 6:
                    signup_user(email, password)
                else:
                    st.warning("Password too short.")


# -----------------------------
# Dashboard Page
# -----------------------------
def render_dashboard():
    st.title("✨ Pizza Planet Dashboard")

    st.sidebar.button("Logout", on_click=logout)

    st.success(f"Logged in as: {st.session_state.user_email}")

    st.write("Your ID Token:")
    st.code(st.session_state.id_token[:60] + "...")


# -----------------------------
# Main App Logic
# -----------------------------
def main():
    st.set_page_config(page_title="Pizza App", page_icon="🍕", layout="wide")

    if st.session_state.id_token:
        render_dashboard()
    else:
        render_auth_page()


if __name__ == "__main__":
    main()
