# ui/auth_page.py
import streamlit as st
import time
from config import validate_customer_login, validate_manager_login, APP_TITLE
from ui.theme import render_css

def _safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        params = dict(st.query_params)
        params["_rerun"] = str(int(time.time()))
        st.query_params = params
        return

def render_auth():
    # Do not pin the sidebar for the login screen (keeps login centered)
    render_css(pin_sidebar=False)

    st.title(APP_TITLE or "BFSI Personal Loan Assistant")
    st.header("Sign in")
    st.write("Use the provided NBFC demo credentials to enter the Customer or Manager dashboard.")

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@nbfc.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")
        if submitted:
            email_val = (email or "").strip()
            if validate_manager_login(email_val, password):
                st.session_state['role'] = "manager"
                st.session_state['email'] = email_val
                _safe_rerun()
            elif validate_customer_login(email_val, password):
                st.session_state['role'] = "customer"
                st.session_state['email'] = email_val
                _safe_rerun()
            else:
                st.error("Invalid credentials. Try the demo credentials.")
