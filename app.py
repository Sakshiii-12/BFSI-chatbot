# app.py
import streamlit as st
import json, os, time
from config import APP_TITLE
from ui.auth_page import render_auth
from ui.customer_page import render_customer_ui
from ui.manager_page import render_manager_ui

# ensure outputs folder exists
os.makedirs("outputs/sanction_letters", exist_ok=True)

def load_demo_customers(path="data/demo_customers.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

demo_customers = load_demo_customers()

# Initialize session
if "role" not in st.session_state:
    st.session_state["role"] = None
if "email" not in st.session_state:
    st.session_state["email"] = None

st.set_page_config(page_title=APP_TITLE, layout="wide")

if not st.session_state.get("role"):
    render_auth()
else:
    if st.session_state["role"] == "customer":
        render_customer_ui(demo_customers)
    elif st.session_state["role"] == "manager":
        render_manager_ui()
