# chat/chat_ui.py
import streamlit as st
import html
import os
from agents.master_agent import MasterAgent
from chat.nlu import detect_intent

def _init_chat_state(demo_customers):
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = [
            {"who": "bot", "text": "Hello — I'm your Loan Assistant. Tell me the amount you'd like or your loan reason."}
        ]
    if "chat_app_top" not in st.session_state and demo_customers:
        st.session_state["chat_app_top"] = demo_customers[0]["name"]
    if "chat_last_processed_index" not in st.session_state:
        st.session_state.chat_last_processed_index = 0

def _add_message(who, text):
    st.session_state.chat_log.append({"who": who, "text": text})

def _render_messages_block():
    # --- EMBEDDED CSS TO FORCE SINGLE-LINE LAYOUT ---
    # This ensures avatars and text stay on the same line (display: flex)
    custom_css = """
    <style>
        .chat-row {
            display: flex !important;
            align-items: flex-end !important;
            margin-bottom: 12px;
            width: 100%;
        }
        .chat-row.user {
            justify-content: flex-end;
            flex-direction: row;
        }
        .chat-row.bot {
            justify-content: flex-start;
            flex-direction: row;
        }
        .chat-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            flex-shrink: 0;
            font-size: 14px;
        }
        .bot-avatar { background-color: #113382; margin-right: 8px; }
        .user-avatar { background-color: #444444; margin-left: 8px; }
        
        .chat-bubble {
            padding: 10px 14px;
            border-radius: 12px;
            max-width: 75%;
            font-size: 15px;
            line-height: 1.4;
            position: relative;
            word-wrap: break-word;
        }
        .bot-bubble { 
            background-color: #F0F2F6; 
            color: #31333F;
            border-bottom-left-radius: 2px;
        }
        .user-bubble { 
            background-color: #E8F6EA; 
            color: #063020;
            border-bottom-right-radius: 2px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # --- RENDER MESSAGES ---
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for m in st.session_state.chat_log:
        who = m.get("who")
        text = html.escape(m.get("text", "")).replace("\n", "<br/>")
        
        if who == "bot":
            # Bot: Avatar Left, Text Right
            html_content = f"""
            <div class='chat-row bot'>
                <div class='chat-avatar bot-avatar'>B</div>
                <div class='chat-bubble bot-bubble'>{text}</div>
            </div>
            """
        else:
            # User: Text Left, Avatar Right
            html_content = f"""
            <div class='chat-row user'>
                <div class='chat-bubble user-bubble'>{text}</div>
                <div class='chat-avatar user-avatar'>U</div>
            </div>
            """
        st.markdown(html_content, unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)

def _process_new_user_messages(demo_customers):
    if st.session_state.chat_last_processed_index < len(st.session_state.chat_log):
        idx = st.session_state.chat_last_processed_index
        msg = st.session_state.chat_log[idx]
        
        if msg.get("who") == "user":
            text = msg.get("text", "")
            
            names = [c["name"] for c in demo_customers] if demo_customers else ["Demo User"]
            cust_name = st.session_state.get("chat_app_top", names[0])
            cust = next((c for c in demo_customers if c["name"] == cust_name), demo_customers[0])

            intent = detect_intent(text)
            
            if intent["intent"] == "request_amount":
                amount = intent["amount"]
                _add_message("bot", f"Processing Rs {amount} for {cust['name']}...")
                
                try:
                    agent = MasterAgent()
                    dec, trace, pdf = agent.start_chat(cust, amount, 12.0, 60, out_folder="outputs", docs_payload=None)
                    
                    _add_message("bot", f"Decision: {dec}. EMI: Rs {trace['decision_details'].get('EMI')} (~{trace['decision_details'].get('EMI_pct_salary')}% of salary).")
                    
                    if pdf:
                        filename = os.path.basename(pdf)
                        _add_message("bot", f"Sanction letter generated: {filename}")
                        
                except Exception as e:
                    _add_message("bot", f"Error running pipeline: {e}")

            elif intent["intent"] == "loan_reason":
                _add_message("bot", "Thanks — noted. Do you have a preferred loan amount?")
            
            elif intent["intent"] == "clear":
                st.session_state.chat_log = [{"who": "bot", "text": "Conversation cleared. Hello — I'm your Loan Assistant."}]
                st.session_state.chat_last_processed_index = 0
                st.rerun()
                return
            else:
                _add_message("bot", "I didn't fully understand — try 'I need 300000' or mention a reason (e.g. 'medical').")

        st.session_state.chat_last_processed_index += 1
        st.rerun()

def render_chat_page(demo_customers):
    _init_chat_state(demo_customers)
    
    names = [c["name"] for c in demo_customers] if demo_customers else ["Demo User"]
    st.selectbox("Applicant", names, key="chat_app_top", help="Which applicant to simulate the chat for")
    
    _render_messages_block()

    def handle_submit():
        user_text = st.session_state.chat_input_box
        if user_text and user_text.strip():
            _add_message("user", user_text.strip())
            st.session_state.chat_input_box = ""

    cols = st.columns([6,1])
    cols[0].text_input("Type your message", placeholder="E.g. 'I need 300000'", key="chat_input_box", on_change=handle_submit)
    cols[1].button("Send", key="chat_send_btn", on_click=handle_submit)

    _process_new_user_messages(demo_customers)