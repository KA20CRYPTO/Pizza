import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from time import sleep
import json
import io

# -------------------------------
# Firebase Service Account (JSON STRING)
# -------------------------------
FIREBASE_SERVICE_ACCOUNT_JSON = """
{
  "type": "service_account",
  "project_id": "project-1-7f58e",
  "private_key_id": "3f79740728d85ac5db9506383ef20f7348793b17",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC2PXR1zT9Smt9h\\n1FRgjVgHMHlYD2UQVAuunNxSzFdVSr/EVYSSMw0AA+c44S9qH3Vvfm6ucyOzHAyS\\n1Sp7gvn0FxRBFOh0uoGZhtVkL1e0QBtuCTxUCDbdCNEoR+tv1mHjOM3UgIz5YDcr\\nT2n/OZKcpgMn7rG9cmsGjIsULnou/PkGoYcqK0UGDpYXY6kr/OtXNCAq6lvgGgWC\\nPF4ujuFapzZvEqi2lexM74O7Ude6GLhTIGMTRV150K4VcrW7Y/DuVLKosdvz5wIj\\n5ZxY0Pm8Ilhv4+W2+85J+kabEHyu+p9Xx38dTHnM2sOf89c48BlsV/KLnotgsbqM\\nHFXevmV/AgMBAAECggEAAS6fF3AVnbw5OPHmF4zof0U4HSweK3xHMOYaP8Owc469\\nPJiSTZMkFqtFJVykIlE0JSRVeiEZ9YOw12k1rnKIKW1k5cue7J2UpoUu8EiJ44vg\\nr+TtOF1vDav+hnEIGUQP2LYkgW9DJYEv01DDAM+1rqQ5ez0NW288kSfdHjNIwdW0\\nTOS6UssE5CgKuHgfs+ClR5KErWJUdinfJWfG9c4Q3t4u3nTZb9IY0VvWOD1WmO+1\\nV7ffkiM4xGYq3FPOISkbn4wsswVLWddWXltVVfAFGGZX3196z1DW/JKGgK6ZMlEH\\nUiBL6ZNuY9R2YMtbJXkDMi3t/VkmMrZKG8KvrrJ64QKBgQD9UY11EMHg8DNfmwNT\\nA0VLmyL0P55Qa1a0/LlvVEK/WF7FYoLsgsyggaLuyF5S8m+Awq0fSwxRYoIhEy0E\\nXetZ6bdj5uPKFHDcFj/rvXrXN9Rn/g6EO1BQ8zpc4MuFp8FTBSoG09OrUUh1sSoS\\nr4f4p8fba9pmntcYGpJ3/gmxJwKBgQC4K0rfq2e1JGqK4wtBrv91UN07gE151D6U\\nAFavig5NVwbCkAJ790/v60ooxoVqQHN9QhuoW+K5FSNe8a3MWcgkm42AfOQPcw2k\\nTA24Z++KgsTgShPD5d4Gl4ucUimaz0jn7jZFPn4L0PivqxnUGKI0hlPE24Aq/x5B\\nZJ1WsCov6QKBgQCaxfsx7X0n3FrnLSUI0VTDbxQaO8yUwiCGEGuUM91cX7f3zcrE\\nit5PqyVL06yd7XZnK4rvNcFe8FslrjuxEVk85GmiZm4DCB40untvo6OsX3Yt27Iu\\n5Lab3yBnowl2rhqWiO82oLIRWGZ3UjmslQb0zD52OB2G2cH9/i5DljmBvQKBgQCO\\n181ABELwxWj5hjYB4Qh0Zp7g+pec6ZkL0+NoTWzgYaJ1n5q9qclPbbBcRfXOvmSU\\n/4RSJcqJATMo/cxuViic9CVhRfzhWrx29SIjKEIrrVekGvCPnaeCd2IqgbORRjrm\\n4OUo+dprsc5g+hWTYvPUR2eLpTAYqT0/PRmn1gUymQKBgQDKJnGRjFtmR2P7zBa8\\ny5zi9r34zMJlgu7KG771mqLKd97kzFh5vns0I2RYxKeg7NErtppCsg3puMJrEWvi\\nt9JbdlvqAVlWnUAyWiUmQQqL7uU5PIvJ+jx0vsxBst/yD3Au7LCjDjhK95hXDMhd\\n6Sve1e1EZvZrxuz/HtxfrpTRrg==\\n-----END PRIVATE KEY-----\\n",
  "client_email": "firebase-adminsdk-fbsvc@project-1-7f58e.iam.gserviceaccount.com",
  "client_id": "115773423468809114243",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40project-1-7f58e.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""


# -------------------------------
# Firebase Initialization
# -------------------------------
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            data = json.loads(FIREBASE_SERVICE_ACCOUNT_JSON.strip())
            fake_file = io.StringIO(json.dumps(data))

            cred = credentials.Certificate(fake_file)
            firebase_admin.initialize_app(cred)

        except Exception as e:
            st.error(f"Firebase initialization failed: {e}")
            st.stop()

initialize_firebase()

# -------------------------------
# Session State
# -------------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "page" not in st.session_state:
    st.session_state.page = "auth"

# -------------------------------
# Authentication Logic
# -------------------------------
def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        st.success("Account created successfully! Please log in.")
        return True
    except auth.EmailAlreadyExistsError:
        st.error("This email is already registered.")
    except Exception as e:
        st.error(f"Signup error: {e}")
    return False


def login_user(email, password):
    """Admin SDK cannot verify passwords. We simulate login by email lookup."""
    try:
        user = auth.get_user_by_email(email)
        st.session_state.user_id = user.uid
        st.session_state.page = "dashboard"
        st.success("Login successful!")
        sleep(0.5)
        st.rerun()

    except auth.UserNotFoundError:
        st.error("Invalid email or user does not exist.")
    except Exception as e:
        st.error(f"Login error: {e}")


def logout():
    st.session_state.user_id = None
    st.session_state.page = "auth"
    st.info("Logged out.")
    st.rerun()

# -------------------------------
# UI — Auth Page
# -------------------------------
def render_auth_page():
    st.title("🍕 Pizza Planet - Login")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # Login
    with tab1:
        with st.form("login"):
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if email and pwd:
                    login_user(email, pwd)
                else:
                    st.warning("Please fill all fields.")

    # Signup
    with tab2:
        with st.form("signup"):
            email = st.text_input("Email ")
            pwd = st.text_input("Password (min 6 chars)", type="password")
            if st.form_submit_button("Create Account"):
                if len(pwd) >= 6:
                    signup_user(email, pwd)
                else:
                    st.warning("Weak password — must be 6+ characters.")

# -------------------------------
# UI — Dashboard
# -------------------------------
def render_dashboard():
    st.title("✨ Pizza Planet Dashboard")
    st.sidebar.button("Logout", on_click=logout)

    st.success(f"Logged in as UID: {st.session_state.user_id}")

# -------------------------------
# MAIN APP
# -------------------------------
def main():
    st.set_page_config(page_title="Pizza App", page_icon="🍕", layout="wide")

    if st.session_state.page == "auth" or st.session_state.user_id is None:
        render_auth_page()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
