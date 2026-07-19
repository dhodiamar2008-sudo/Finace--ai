"""
Streamlit UI for FinPilot AI.

Run from the project root with:
    streamlit run streamlit_app.py
"""

import streamlit as st

from app.database import init_db
from app.auth import login, signup
from app.agent.gemini_agent import chat, reset_session
from app.agent.tools import (
    get_balance, list_transactions, get_anomalies,
    get_financial_health_score, list_savings_goals, list_upcoming_bills,
)

st.set_page_config(page_title="FinPilot AI", page_icon="💰", layout="wide")
init_db()

if "history" not in st.session_state:
    st.session_state.history = []
if "user" not in st.session_state:
    st.session_state.user = None


# ---------------- Auth screen ----------------

def render_auth():
    st.title("💰 FinPilot AI")
    st.caption("Sign in to your personal finance agent")

    tab_login, tab_signup = st.tabs(["Login", "Sign up"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary"):
            result = login(email, password)
            if result["status"] == "ok":
                st.session_state.user = result
                st.rerun()
            else:
                st.error(result["message"])

    with tab_signup:
        name = st.text_input("Name", key="signup_name")
        email2 = st.text_input("Email", key="signup_email")
        password2 = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create account", type="primary"):
            if not name or not email2 or not password2:
                st.error("Please fill in all fields.")
            else:
                result = signup(email2, name, password2)
                if result["status"] == "ok":
                    st.session_state.user = result
                    st.rerun()
                else:
                    st.error(result["message"])


# ---------------- Main app ----------------

def render_app():
    user = st.session_state.user
    user_id = user["user_id"]

    st.title("💰 FinPilot AI")
    st.caption(f"Welcome back, {user['name']} — powered by Gemini 2.5 Flash")

    with st.sidebar:
        st.subheader(f"👤 {user['name']}")
        if st.button("Log out"):
            st.session_state.user = None
            st.session_state.history = []
            st.rerun()

        st.divider()
        if st.button("🔄 Refresh data"):
            st.rerun()

        balance = get_balance(user_id)
        col1, col2 = st.columns(2)
        col1.metric("Income", f"₹{balance['total_income']:.0f}")
        col2.metric("Expenses", f"₹{balance['total_expense']:.0f}")
        st.metric("Net Balance", f"₹{balance['net_balance']:.0f}")

        st.divider()
        st.subheader("🩺 Financial Health")
        score = get_financial_health_score(user_id)
        if score["status"] == "ok":
            st.metric("Score", f"{score['score']}/100", score["rating"])
            with st.expander("Breakdown"):
                for k, v in score["breakdown"].items():
                    st.write(f"{k.replace('_', ' ').title()}: {v}")
        else:
            st.write(score["message"])

        st.divider()
        st.subheader("🎯 Savings Goals")
        goals = list_savings_goals(user_id)["goals"]
        if goals:
            for g in goals:
                st.write(f"**{g['name']}** — ₹{g['saved_amount']:.0f} / ₹{g['target_amount']:.0f}")
                st.progress(g["percent_complete"] / 100)
        else:
            st.write("No goals yet — ask the assistant to create one!")

        st.divider()
        st.subheader("📅 Upcoming Bills")
        bills = list_upcoming_bills(user_id)
        if bills["count"]:
            st.write(f"Monthly total: ₹{bills['monthly_total']:.0f}")
            for b in bills["bills"]:
                st.write(f"{b['name']} — ₹{b['amount']:.0f} (day {b['due_day']})")
        else:
            st.write("No bills tracked yet.")

        st.divider()
        st.subheader("📜 Recent Transactions")
        txns = list_transactions(user_id, limit=6)["transactions"]
        if txns:
            for t in txns:
                sign = "+" if t["type"] == "income" else "-"
                st.write(f"{sign}₹{t['amount']:.0f} — {t['category']} ({t['date']})")
        else:
            st.write("No transactions yet.")

        st.divider()
        st.subheader("⚠️ Anomalies")
        anomalies = get_anomalies(user_id)["anomalies"]
        if anomalies:
            for a in anomalies:
                st.write(f"₹{a['amount']:.0f} in {a['category']} on {a['date']} (z={a['z_score']})")
        else:
            st.write("None detected.")

        st.divider()
        if st.button("🗑️ Reset conversation"):
            reset_session(user_id)
            st.session_state.history = []
            st.rerun()

    # ---------------- Chat ----------------
    for role, msg in st.session_state.history:
        with st.chat_message(role):
            st.write(msg)

    user_msg = st.chat_input("Ask about your finances or log a transaction...")

    if user_msg:
        st.session_state.history.append(("user", user_msg))
        with st.chat_message("user"):
            st.write(user_msg)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = chat(user_id, user_msg)
            st.write(reply)
        st.session_state.history.append(("assistant", reply))
        st.rerun()

    if not st.session_state.history:
        st.info(
            "Try: **\"I spent 500 on groceries yesterday\"**, "
            "**\"How healthy are my finances?\"**, "
            "**\"I want to save ₹50000 for a laptop\"**, "
            "**\"Add Netflix bill, 500 rupees, due on the 5th\"**, "
            "**\"How much will I spend on groceries next month?\"**"
        )


# ---------------- Router ----------------

if st.session_state.user is None:
    render_auth()
else:
    render_app()
