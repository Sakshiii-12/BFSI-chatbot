# chat/chat_ui.py
import streamlit as st
from agents.master_agent import MasterAgent
from chat.nlu import detect_intent
import html

def _init_chat_state(demo_customers):
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = [
            {"who":"bot", "text":"Hello — I'm your Loan Assistant. Tell me the amount you'd like or your loan reason."}
        ]
    if "chat_app_top" not in st.session_state and demo_customers:
        st.session_state["chat_app_top"] = demo_customers[0]["name"]
    if "chat_last_processed_index" not in st.session_state:
        st.session_state.chat_last_processed_index = 0

def _add_message(who, text):
    st.session_state.chat_log.append({"who":who, "text": text})

def _render_messages_block():
    # Shows messages in vertical flow so no extra columns are required
    st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
    for m in st.session_state.chat_log:
        who = m.get("who")
        text = html.escape(m.get("text", "")).replace("\n", "<br/>")
        if who == "bot":
            md = f"""
            <div class='msg-row'>
              <div class='avatar avatar-bot'>B</div>
              <div>
                <div class='bubble-bot'>{text}</div>
              </div>
            </div>
            """
            st.markdown(md, unsafe_allow_html=True)
        else:
            md = f"""
            <div class='msg-row' style='justify-content:flex-end'>
              <div style='text-align:right'>
                <div class='bubble-user'>{text}</div>
              </div>
              <div class='avatar avatar-user'>U</div>
            </div>
            """
            st.markdown(md, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def _process_new_user_messages(demo_customers):
    # process messages since last processed index
    while st.session_state.chat_last_processed_index < len(st.session_state.chat_log):
        idx = st.session_state.chat_last_processed_index
        msg = st.session_state.chat_log[idx]
        if msg.get("who") == "user":
            text = msg.get("text","")
            names = [c["name"] for c in demo_customers] if demo_customers else ["Demo User"]
            cust_name = st.session_state.get("chat_app_top", names[0])
            cust = next((c for c in demo_customers if c["name"] == cust_name), demo_customers[0] if demo_customers else {"id":0,"name":"Demo User","salary":30000,"pre_approved_limit":100000,"credit_score":700})

            intent = detect_intent(text)
            if intent["intent"] == "request_amount":
                amount = intent["amount"]
                _add_message("bot", f"Processing Rs {amount} for {cust['name']}...")
                try:
                    agent = MasterAgent()
                    dec, trace, pdf = agent.start_chat(cust, amount, 12.0, 60, out_folder="outputs", docs_payload=None)
                    _add_message("bot", f"Decision: {dec}. EMI: Rs {trace['decision_details'].get('EMI')} (~{trace['decision_details'].get('EMI_pct_salary')}% of salary).")
                    if pdf:
                        _add_message("bot", f"Sanction letter generated: {pdf}")
                except Exception as e:
                    _add_message("bot", f"Error running pipeline: {e}")
            elif intent["intent"] == "loan_reason":
                _add_message("bot", "Thanks — noted. Do you have a preferred loan amount?")
            elif intent["intent"] == "clear":
                st.session_state.chat_log = [{"who":"bot", "text":"Conversation cleared. Hello — I'm your Loan Assistant."}]
                st.session_state.chat_last_processed_index = 0
                return
            else:
                _add_message("bot", "I didn't fully understand — try 'I need 300000' or mention a reason (e.g. 'medical').")
        st.session_state.chat_last_processed_index += 1

def render_chat_page(demo_customers):
    _init_chat_state(demo_customers)
    # Applicant selector + messages + input (all stacked vertically)
    names = [c["name"] for c in demo_customers] if demo_customers else ["Demo User"]
    sel = st.selectbox("Applicant", names, key="chat_app_top", help="Which applicant to simulate the chat for")
    _render_messages_block()

    # Input row: text input + send button
    cols = st.columns([6,1])
    msg = cols[0].text_input("Type your message", placeholder="E.g. 'I need 300000' or 'for medical'", key="chat_input_box")
    send = cols[1].button("Send", key="chat_send_btn")

    if send and msg and msg.strip():
        _add_message("user", msg.strip())
        # clear input box
        st.session_state["chat_input_box"] = ""
        # process the new message(s) synchronously
        _process_new_user_messages(demo_customers)
        try:
            st.experimental_rerun()
        except Exception:
            pass

    # short help on the side, but keep as block to avoid creating nested columns
    st.markdown("<div class='micro-card'><strong>How to chat</strong><br/>• Type an amount (e.g. 'I need 300000') or a reason (medical/wedding/education).<br/>• Use Compare or Simulate for structured runs.</div>", unsafe_allow_html=True)
