import streamlit as st
import requests
from time import sleep

# --- CONFIGURATION ---
# IMPORTANT: Replace this with your actual Firebase Web API Key for production use.
API_KEY = "AIzaSyAYOROctBoSyJ3aeHafUm-62zDl8uA2TQU" 
MODEL_NAME = "gemini-2.5-flash-preview-09-2025" 

# --- SESSION STATE SETUP ---
if "id_token" not in st.session_state:
    st.session_state.id_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_display_name" not in st.session_state:
    # Simulating a user profile feature
    st.session_state.user_display_name = "Space Cadet" 
if "page" not in st.session_state:
    st.session_state.page = "auth"
if "order_status" not in st.session_state:
    st.session_state.order_status = "Pending"
if "order_items" not in st.session_state:
    st.session_state.order_items = [
        {"item": "Pepperoni Deep Dish", "qty": 1, "price": 19.99},
        {"item": "Cosmic Cola", "qty": 2, "price": 3.00},
    ]


# --- FIREBASE REST API FUNCTIONS ---

def signup_user(email, password):
    """Registers a new user using Firebase Identity Toolkit."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Network error during signup: {e}")
        return False

    if "idToken" in data:
        st.balloons() # Added effect for success!
        st.success("🚀 Account created successfully! Please proceed to log in.")
        return True
    else:
        # Improved error handling for common Firebase error messages
        error_message = data.get("error", {}).get("message", "Signup failed. Check details.")
        if "EMAIL_EXISTS" in error_message:
            st.error("Email already in use. Please log in or use a different email.")
        else:
            st.error(f"Signup failed: {error_message}")
        return False


def login_user(email, password):
    """Authenticates a user and sets session state."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        with st.spinner('Authenticating...'):
            response = requests.post(url, json=payload)
            data = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Network error during login: {e}")
        return

    if "idToken" in data:
        st.session_state.id_token = data["idToken"]
        st.session_state.user_email = data["email"]
        st.session_state.page = "dashboard"
        # Simulate fetching user profile name
        st.session_state.user_display_name = email.split('@')[0].capitalize()
        
        st.success(f"Welcome back, {st.session_state.user_display_name}! 🪐")
        sleep(0.5)
        st.rerun()
    else:
        error_message = data.get("error", {}).get("message", "Login failed. Check email/password.")
        if "EMAIL_NOT_FOUND" in error_message or "INVALID_PASSWORD" in error_message:
            st.error("Invalid email or password.")
        else:
            st.error(f"Login failed: {error_message}")


def logout():
    """Clears session state and returns to the auth page."""
    for key in ["id_token", "user_email", "page"]:
        if key in st.session_state:
            del st.session_state[key]
    st.info("👋 See you next time! Logged out successfully.")
    sleep(0.5)
    st.rerun()


# --- UI: AUTH PAGE (Enhanced Styling) ---
def render_auth_page():
    st.markdown(
        """
        <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.1rem;
            font-weight: 600;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    st.markdown(
        "<h1 style='text-align: center; color: #ff4b4b;'>🍕 Pizza Planet Secure Portal 🚀</h1>", 
        unsafe_allow_html=True
    )
    st.markdown("<p style='text-align: center; margin-bottom: 2rem;'>The fastest delivery across the galaxy. Please sign in or create an account.</p>", unsafe_allow_html=True)


    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Login", "✍️ Sign Up"])

        # LOGIN TAB
        with tab1:
            st.subheader("Login to your Space Account")
            with st.form("login_form", clear_on_submit=True):
                email = st.text_input("Email", placeholder="user@galaxy.com")
                password = st.text_input("Password", type="password", placeholder="min 6 characters")
                st.markdown("---")
                submit = st.form_submit_button("Sign In to Planet 🪐", type="primary")

                if submit:
                    if email and password:
                        login_user(email, password)
                    else:
                        st.warning("Please enter both email and password.")

        # SIGNUP TAB
        with tab2:
            st.subheader("Create a New Account")
            with st.form("signup_form", clear_on_submit=True):
                email = st.text_input("Email ")
                password = st.text_input("Password (min 6 chars)", type="password")
                st.markdown("---")
                submit = st.form_submit_button("Launch New Account 🚀")

                if submit:
                    if len(password) >= 6 and email:
                        signup_user(email, password)
                    elif not email:
                        st.warning("Please enter your email.")
                    else:
                        st.warning("Password must be at least 6 characters long.")


# --- UI: DASHBOARD PAGE (Rich Content & Animation) ---
def render_dashboard():
    # Header and Sidebar
    st.markdown(f"## 🛰️ Welcome, {st.session_state.user_display_name}! (Beta Access)", unsafe_allow_html=True)
    st.markdown("Your command center for intergalactic pizza orders.")

    st.sidebar.markdown(f"**Current User:**\n`{st.session_state.user_email}`")
    if st.sidebar.button("Logout 🚪", type="secondary"):
        logout()

    # --- Metrics Bar (Animation via color and icon updates) ---
    col_a, col_b, col_c = st.columns(3)

    col_a.metric("Total Order Value", "$25.99", "1.5% from last order")
    col_b.metric("Reward Stars", "450", "50 points earned today")
    col_c.metric("Delivery ETA", "23 Min", "Faster than light!")
    st.markdown("---")

    # --- Main Content Area ---
    tab1, tab2, tab3 = st.tabs(["🍕 Current Order Status", "📊 Delivery Statistics", "👤 Profile Settings"])

    with tab1:
        st.subheader(f"Order #PP-9001 Tracking")
        
        # Simulated Progress/Animation
        status_steps = ["Pending", "Preparing", "Quality Check", "In Transit", "Delivered"]
        try:
            current_index = status_steps.index(st.session_state.order_status)
        except ValueError:
             current_index = 0

        # Simple progression logic on button click
        def update_order_status():
            next_index = (current_index + 1) % len(status_steps)
            st.session_state.order_status = status_steps[next_index]
            if st.session_state.order_status == "Delivered":
                st.balloons()
                st.toast('Order Delivered! Enjoy your space meal!', icon='🎉')

        st.progress((current_index + 1) / len(status_steps), text=f"Status: **{st.session_state.order_status}**")
        
        st.button(f"Simulate Next Phase ({status_steps[(current_index + 1) % len(status_steps)]})", 
                  on_click=update_order_status, disabled=st.session_state.order_status == "Delivered")
        
        st.subheader("Order Details")
        st.table(st.session_state.order_items)


    with tab2:
        st.subheader("Intergalactic Delivery Performance")
        
        # Mock data visualization (using st.bar_chart for simplicity)
        import pandas as pd
        chart_data = pd.DataFrame(
            {
                "Planet": ["Mars", "Jupiter", "Venus", "Neptune"],
                "Average Time (Mins)": [35, 120, 45, 250],
            }
        ).set_index("Planet")
        
        st.bar_chart(chart_data)
        
        st.info("Delivery to Neptune is slower due to gravitational distortions.")

        st.expander("Expand for Raw Log Data").code(
            """
            [2025-10-27 09:30:00] Dispatcher 404: Order PP-9001 initialized.
            [2025-10-27 09:45:12] Chef Zorp: Deep Dish completed. 
            [2025-10-27 10:00:00] Drone 77: Departing Earth orbit. ETA 23 minutes.
            """
        )

    with tab3:
        st.subheader("Update Your Planetary Profile")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.text_input("Display Name", value=st.session_state.user_display_name)
            st.text_input("Planet Address", value="Sector Alpha 7")
        with col_p2:
            st.text_input("Emergency Contact", value="N/A", disabled=True)
            st.selectbox("Preferred Sauce", ["Tomato", "Pesto", "White Garlic", "Alien Slime"])

        st.button("Save Profile Updates", type="primary")

        st.markdown("---")
        st.warning("⚠️ **Security Note:** Your Firebase ID Token is sensitive and used for authenticated API calls.")
        st.code(st.session_state.id_token, language="text")


# --- MAIN APP LOGIC ---
def main():
    """Renders the appropriate page based on the current authentication state."""
    # Set a professional wide layout configuration
    st.set_page_config(
        page_title="Pizza Planet Intergalactic Delivery", 
        page_icon="🍕", 
        layout="wide"
    )

    if st.session_state.id_token:
        render_dashboard()
    else:
        render_auth_page()


if __name__ == "__main__":
    main()
