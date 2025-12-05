import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from time import sleep # Used for simulating loading delays

# --- Configuration & Setup ---

# IMPORTANT: You must replace 'path/to/your/serviceAccountKey.json' 
# with the actual path to your Firebase Service Account file.
# This file contains the private keys and should be handled securely.
SERVICE_ACCOUNT_FILE = '.streamlit/project-1-7f58e-firebase-adminsdk-fbsvc-3f79740728'

def initialize_firebase():
    """Initializes the Firebase Admin SDK if it hasn't been initialized."""
    if not firebase_admin._apps:
        # Check if the placeholder path is used and warn the user
        if SERVICE_ACCOUNT_FILE == '.streamlit/project-1-7f58e-firebase-adminsdk-fbsvc-3f79740728':
            st.error("🚨 Firebase Setup Required: Please replace 'path/to/your/serviceAccountKey.json' with your actual service account file path.")
            st.stop()
        
        try:
            cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
            firebase_admin.initialize_app(cred)
            st.success("Firebase initialized successfully!")
        except FileNotFoundError:
            st.error(f"Error: Firebase service account file not found at '{SERVICE_ACCOUNT_FILE}'.")
            st.stop()
        except Exception as e:
            st.error(f"Error initializing Firebase: {e}")
            st.stop()

# Initialize Firebase early
initialize_firebase()

# --- Session State Management ---

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'auth' # 'auth' or 'dashboard'

# --- Authentication Functions (Server-Side Logic) ---

def signup_user(email, password):
    """Creates a new user in Firebase Authentication."""
    try:
        user = auth.create_user(
            email=email,
            password=password,
            email_verified=False
        )
        st.success(f"Account created successfully for {user.email}! Please log in.")
        return True
    except firebase_admin._auth_utils.EmailAlreadyExistsError:
        st.error("Error: This email address is already in use.")
    except Exception as e:
        st.error(f"Error creating user: {e}")
    return False

def login_user(email, password):
    """Simulates login validation (Firebase Admin SDK cannot directly validate client passwords, 
    but we use this structure to handle the *user ID* after a successful login, 
    often verified client-side or via a Cloud Function in a real app). 
    
    NOTE: In a real-world Streamlit app, you usually need a separate client-side 
    library (like `streamlit-firebase-auth` or a custom approach) 
    to handle the password validation and token exchange securely. 
    For this demo, we use a known-good user for a successful login simulation, 
    or you would implement a custom secure token exchange."""
    
    # We will try to get the user by email as a validation proxy for the admin SDK.
    try:
        # In a production app, you would use a secured client-side login 
        # to get a valid ID token, which you would then verify on the server.
        # This is a simulation using the Admin SDK's ability to fetch user data.
        user = auth.get_user_by_email(email)
        
        # In a real app, the token verification would happen here. 
        # If the token is valid, you get the UID.
        # Since we cannot validate the password securely here, we proceed with the UID 
        # assuming client-side authentication succeeded.
        st.session_state['user_id'] = user.uid
        st.session_state['page'] = 'dashboard'
        st.success("Login successful! Redirecting...")
        sleep(1) # Pause for 1 second to show success message
        st.rerun()
        return True
    except firebase_admin._auth_utils.UserNotFoundError:
        st.error("Error: Invalid email or user not found. (Note: Password validation is simulated.)")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    return False

def logout():
    """Logs out the current user."""
    st.session_state['user_id'] = None
    st.session_state['page'] = 'auth'
    st.info("You have been logged out.")
    st.rerun()

# --- UI Components ---

def render_auth_page():
    """Renders the Login and Sign-up tabs."""
    st.title("🍕 Pizza Planet - Secure Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Welcome Back!")
        with st.form("login_form"):
            login_email = st.text_input("Email Address", key="le")
            login_password = st.text_input("Password", type="password", key="lp")
            login_submitted = st.form_submit_button("Login")
            
            if login_submitted:
                if login_email and login_password:
                    with st.spinner("Logging in..."):
                        login_user(login_email, login_password)
                else:
                    st.warning("Please enter both email and password.")

    with tab2:
        st.subheader("Create Your Account")
        with st.form("signup_form"):
            signup_email = st.text_input("Email Address", key="se")
            signup_password = st.text_input("Password", type="password", key="sp")
            signup_submitted = st.form_submit_button("Sign Up")
            
            if signup_submitted:
                if signup_email and signup_password and len(signup_password) >= 6:
                    with st.spinner("Creating account..."):
                        signup_user(signup_email, signup_password)
                elif len(signup_password) < 6:
                    st.warning("Password must be at least 6 characters long.")
                else:
                    st.warning("Please enter both email and password.")

def render_pizza_dashboard():
    """Renders the main content after successful authentication."""
    st.title("✨ The Pizza Story Dashboard")
    st.markdown(f"**Welcome, User:** `{st.session_state['user_id']}`")
    st.sidebar.button("Logout", on_click=logout, type="secondary")

    st.header("The Artisan's Corner")
    st.markdown("Discover the history and passion behind the world's best pies.")

    col1, col2, col3 = st.columns(3)

    # Pizza Card 1
    with col1:
        st.subheader("Margherita: The Queen's Pie")
        st.image("https://placehold.co/600x400/FF5733/FFFFFF?text=Margherita", caption="Simplicity is the ultimate sophistication.")
        st.write("""
        The iconic Margherita pizza was created in 1889 by Raffaele Esposito to honor 
        Queen Margherita of Savoy. Its colors represent the Italian flag: red (tomato), 
        white (mozzarella), and green (basil). A true classic that defines Italian cuisine.
        """)
        st.button("Read Full Story ➡️", key="story1")

    # Pizza Card 2
    with col2:
        st.subheader("Neapolitan: The Original")
        st.image("https://placehold.co/600x400/1D4ED8/FFFFFF?text=Neapolitan+Pizza", caption="Thin crust, minimal toppings, maximum flavor.")
        st.write("""
        True Neapolitan pizza (Pizza Napoletana) is protected by a Traditional Speciality 
        Guaranteed (TSG) certification. It must be cooked in a wood-fired oven for no more 
        than 60-90 seconds, making the dough exceptionally soft and elastic.
        """)
        st.button("Read Full Story ➡️", key="story2")

    # Pizza Card 3
    with col3:
        st.subheader("Deep Dish: Chicago's Pride")
        st.image("https://placehold.co/600x400/34D399/000000?text=Deep+Dish", caption="A hearty meal disguised as a pie.")
        st.write("""
        The Deep Dish is baked in a pan, giving it a high crust that allows for a thick 
        layer of toppings, cheese, and tomato sauce (often layered in reverse order). 
        It's more of a savory pie than a traditional pizza.
        """)
        st.button("Read Full Story ➡️", key="story3")
        
    st.divider()
    
    st.header("Daily Flavor Poll")
    st.info("Your ID: " + st.session_state['user_id'])
    
    # Simple form to simulate user interaction
    with st.form("pizza_poll"):
        favorite = st.radio(
            "What's your current favorite pizza style?",
            ('Classic New York', 'Roman Al Taglio', 'Detroit Style', 'Calzone')
        )
        submit_poll = st.form_submit_button("Vote")
        
        if submit_poll:
            st.success(f"Thanks for voting! We registered your preference for: {favorite}.")

# --- Main Application Logic ---

def main():
    st.set_page_config(
        page_title="Pizza App",
        page_icon="🍕",
        layout="wide"
    )
    
    # Route based on session state
    if st.session_state['page'] == 'auth' or st.session_state['user_id'] is None:
        render_auth_page()
    else:
        render_pizza_dashboard()

if __name__ == "__main__":
    main()
