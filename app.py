import streamlit as st
from db_manager import (
    get_user, create_user, 
    get_conversations, create_conversation,
    get_messages, save_message
)
from auth import hash_password, check_password
from ai_helpers import get_ai_response, extract_text_from_pdf, create_pdf_report

# --- 0. CUSTOM CSS TO MAKE IT LOOK BETTER ---
st.markdown("""
<style>
/* Hide Streamlit's hamburger menu and "Made with Streamlit" footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Style the sidebar */
[data-testid="stSidebar"] {
    background-color: #f8f9fa;
}

/* Style the sidebar buttons */
[data-testid="stSidebar"] button {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    color: #333;
    transition: background-color 0.3s ease, border-color 0.3s ease;
}
[data-testid="stSidebar"] button:hover {
    background-color: #f0f2f6;
    border-color: #c0c0c0;
}

/* Style the "New Chat" button differently */
[data-testid="stSidebar"] [data-testid="stButton"] button:first-of-type {
    background-color: #e6f0ff;
    color: #1a73e8;
    border: 1px solid #1a73e8;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:first-of-type:hover {
    background-color: #d0e0ff;
}

/* Style the chat input box */
[data-testid="stChatInput"] {
    border-top: 1px solid #e0e0e0;
    padding-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- 0. PAGE CONFIG ---
# Set the layout to centered
st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

# --- 1. SESSION STATE MANAGEMENT ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- 2. AUTHENTICATION (Full Page) ---
def show_login_page():
    st.title("🩺 AI Health Assistant")
    st.subheader("Please log in or sign up to continue")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        auth_choice = st.radio("Login or Sign Up", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        
        with st.form(key=auth_choice):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button(label=auth_choice)

            if submit_button:
                if auth_choice == "Sign Up":
                    if get_user(username):
                        st.error("Username already taken!")
                    else:
                        create_user(username, hash_password(password))
                        st.success("Account created! Please login.")
                
                elif auth_choice == "Login":
                    user = get_user(username)
                    if user and check_password(password, user["password"]):
                        st.session_state.logged_in = True
                        st.session_state.username = user["username"]
                        st.session_state.current_chat_id = None
                        st.session_state.messages = []
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

# --- 3. MAIN APPLICATION (Chat Interface) ---
def show_main_app():
    
    # --- SIDEBAR (Chat History) ---
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}!")
        
        if st.button("New Chat ➕", use_container_width=True):
            st.session_state.current_chat_id = None
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.subheader("Chat History")
        
        conversations = get_conversations(st.session_state.username)
        for conv in conversations:
            if st.button(conv["title"], key=conv["_id"], use_container_width=True):
                st.session_state.current_chat_id = str(conv["_id"])
                st.session_state.messages = get_messages(st.session_state.current_chat_id)
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.current_chat_id = None
            st.session_state.messages = []
            st.rerun()

    # --- MAIN CHAT AREA ---
    
    # Check if a chat is loaded. If not, show the "Hello" screen.
    if not st.session_state.current_chat_id:
        st.title(f"Hello, {st.session_state.username}")
        st.subheader("How can I help you today? Upload a report or ask a question to start.")
    else:
        st.title("🩺 AI Health Assistant")
        
    # File uploader at the top
    uploaded_file = st.file_uploader("Upload your medical report (PDF)", type="pdf")
    
    # Display chat messages (if a chat is active)
    if st.session_state.current_chat_id:
        for message in st.session_state.messages:
            with st.chat_message(message["message"]["role"]):
                st.markdown(message["message"]["content"])
    
    # Handle new chat input
    if prompt := st.chat_input("Describe your symptoms..."):
        
        new_chat_created = False
        if st.session_state.current_chat_id is None:
            new_title = prompt[:30] + "..."
            new_chat_id = create_conversation(st.session_state.username, new_title)
            st.session_state.current_chat_id = str(new_chat_id)
            new_chat_created = True # Flag that we made a new chat
        
        # Add user message to UI
        with st.chat_message("user"):
            st.markdown(prompt)
        
        user_msg = {"role": "user", "content": prompt}
        save_message(st.session_state.current_chat_id, user_msg)
        st.session_state.messages.append({"message": user_msg})

        # Process PDF (if any)
        report_text = ""
        if uploaded_file:
            report_text = extract_text_from_pdf(uploaded_file)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                ai_response = get_ai_response(prompt, report_text, st.session_state.username)
                st.markdown(ai_response)
        
        # Save AI message to DB
        ai_msg = {"role": "assistant", "content": ai_response}
        save_message(st.session_state.current_chat_id, ai_msg)
        st.session_state.messages.append({"message": ai_msg})
        
        # If we created a new chat, rerun to update the sidebar.
        if new_chat_created:
            st.rerun()

    # --- PDF DOWNLOAD BUTTON (Only show in an active chat) ---
    if st.session_state.current_chat_id and st.session_state.messages and st.session_state.messages[-1]["message"]["role"] == "assistant":
        last_response = st.session_state.messages[-1]["message"]["content"]
        pdf_data = create_pdf_report(last_response, st.session_state.username)
        
        st.download_button(
            label="Download Last Report",
            data=pdf_data,
            file_name=f"{st.session_state.username}_report.pdf",
            mime="application/pdf"
        )


# --- 4. MAIN APP ROUTER ---
if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()