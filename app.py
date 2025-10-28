import streamlit as st
from db_manager import (
    get_user, create_user,
    get_conversations, create_conversation,
    get_messages, save_message
)
from auth import hash_password, check_password
from ai_helpers import get_ai_response, extract_text_from_pdf, create_pdf_report
import datetime # Import datetime for filename

# --- 0. CUSTOM CSS TO MAKE IT LOOK BETTER ---
st.markdown("""
<style>
/* Hide ONLY the Streamlit "Made with Streamlit" footer */
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
/* Adjust selector if needed based on Streamlit version / structure */
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
st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed" # Keep sidebar initially collapsed
)

# --- 1. SESSION STATE MANAGEMENT ---
# Initialize session state variables if they don't exist
default_states = {
    "logged_in": False,
    "username": "",
    "current_chat_id": None,
    "messages": [],
    "conversations": [] # To store conversation list
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 2. AUTHENTICATION (Full Page Logic) ---
def show_login_page():
    st.title("🩺 AI Health Assistant")
    st.subheader("Please log in or sign up to continue")

    col1, col2, col3 = st.columns([1, 1.5, 1]) # Centering columns

    with col2:
        auth_choice = st.radio(
            "Select Action",
            ["Login", "Sign Up"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_choice_radio" # Add unique key
        )

        with st.form(key=f"{auth_choice}_form"): # Dynamic key based on choice
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button(label=auth_choice)

            if submit_button:
                if auth_choice == "Sign Up":
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif get_user(username):
                        st.error("Username already taken!")
                    else:
                        hashed = hash_password(password)
                        if hashed: # Check if hashing was successful
                            create_user(username, hashed)
                            st.success("Account created! Please switch to Login.")
                        else:
                            st.error("Failed to hash password during signup.")


                elif auth_choice == "Login":
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        user = get_user(username)
                        if user and user.get("password") and check_password(password, user["password"]):
                            st.session_state.logged_in = True
                            st.session_state.username = user["username"]
                            st.session_state.current_chat_id = None
                            st.session_state.messages = []
                            # Load conversations on successful login
                            st.session_state.conversations = get_conversations(user["username"])
                            st.rerun() # Rerun to show the main app
                        else:
                            st.error("Invalid username or password")

# --- 3. MAIN APPLICATION (Chat Interface Logic) ---
def show_main_app():

    # --- SIDEBAR (Chat History) ---
    with st.sidebar:
        st.title(f"Welcome,\n{st.session_state.username}!")

        if st.button("New Chat ➕", use_container_width=True, key="new_chat_sidebar_button"):
            st.session_state.current_chat_id = None
            st.session_state.messages = []
            # Rerun to clear the main chat area and show welcome message
            st.rerun()

        st.divider()
        st.subheader("Chat History")

        # Refresh conversation list if needed (e.g., after new chat created)
        # Check if conversations is in state AND if the content matches DB (simple length check for now)
        db_convos = get_conversations(st.session_state.username)
        if 'conversations' not in st.session_state or len(st.session_state.conversations) != len(db_convos):
             st.session_state.conversations = db_convos

        # Display conversations
        if not st.session_state.conversations:
             st.caption("No past conversations.")
        else:
             for conv in st.session_state.conversations:
                 # Ensure _id is present and use it as key
                 conv_id_str = str(conv.get('_id', ''))
                 if not conv_id_str: continue # Skip if no ID
                 button_key = f"conv_{conv_id_str}"
                 # Use markdown for potentially longer titles to wrap
                 button_label = conv.get("title", "Untitled Chat")

                 if st.button(button_label, key=button_key, use_container_width=True):
                     if st.session_state.current_chat_id != conv_id_str:
                         st.session_state.current_chat_id = conv_id_str
                         # Fetch messages when a chat is selected
                         st.session_state.messages = get_messages(st.session_state.current_chat_id)
                         # Rerun needed to update the main chat display
                         st.rerun()

        st.divider()
        if st.button("Logout", use_container_width=True, key="logout_sidebar_button"):
            # Clear all session state keys we set
            keys_to_clear = list(default_states.keys())
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun() # Rerun to show the login page

    # --- MAIN CHAT AREA ---
    # Determine uploader key based on whether a chat is active
    uploader_key = f"uploader_{st.session_state.current_chat_id}" if st.session_state.current_chat_id else "uploader_welcome"

    if not st.session_state.current_chat_id:
        st.title(f"Hello, {st.session_state.username}")
        st.subheader("How can I help you today? Upload a report or ask a question below to start a new chat.")
        uploaded_file = st.file_uploader("Upload your medical report (PDF)", type="pdf", key=uploader_key)
    else:
        # Try to find current chat title more reliably
        current_title = "Chat"
        for conv in st.session_state.conversations:
             if str(conv.get('_id', '')) == st.session_state.current_chat_id:
                  current_title = conv.get('title', 'Chat')
                  break
        st.title(f"🩺 {current_title}")
        uploaded_file = st.file_uploader("Upload your medical report (PDF)", type="pdf", key=uploader_key)


    # Display chat messages (if a chat is active)
    if st.session_state.current_chat_id and st.session_state.messages:
        for message_doc in st.session_state.messages:
            message = message_doc.get("message", {})
            role = message.get("role")
            content = message.get("content")
            if role and content is not None: # Ensure content exists, even if empty string
                 with st.chat_message(role):
                      st.markdown(content)


    # Handle new chat input using st.chat_input
    if prompt := st.chat_input("Describe your symptoms...", key="chat_input_main"):
        new_chat_created = False
        current_chat_id_to_use = st.session_state.current_chat_id

        # --- Handle New Chat Creation ---
        if current_chat_id_to_use is None:
            # Only create if there's actual input
            if prompt.strip():
                new_title = prompt[:30] + ("..." if len(prompt) > 30 else "")
                new_chat_mongo_id = create_conversation(st.session_state.username, new_title)

                if new_chat_mongo_id: # Check if conversation creation succeeded
                    current_chat_id_to_use = str(new_chat_mongo_id)
                    st.session_state.current_chat_id = current_chat_id_to_use
                    # Add new conversation to state for immediate display in sidebar
                    new_conv_obj = {"_id": new_chat_mongo_id, "title": new_title}
                    # Ensure conversations list exists before inserting
                    if 'conversations' not in st.session_state: st.session_state.conversations = []
                    st.session_state.conversations.insert(0, new_conv_obj)
                    st.session_state.messages = [] # Start with empty messages for new chat
                    new_chat_created = True
                else:
                    st.error("Failed to create a new conversation in the database.")
                    st.stop() # Stop execution if we can't create the chat context

            else:
                 st.warning("Please enter a message to start a chat.")
                 st.stop() # Don't proceed if only whitespace was entered

        # --- Process Message if Chat Exists (or was just created) ---
        if current_chat_id_to_use:
            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(prompt)

            user_msg_obj = {"role": "user", "content": prompt}
            # Add to session state for display
            st.session_state.messages.append({"message": user_msg_obj})
            # Save user message to the database
            save_message(current_chat_id_to_use, user_msg_obj)

            # Process PDF (use the uploader key relevant to the current context)
            report_text = ""
            # Check if the uploader widget actually has a file in Streamlit's internal state
            if uploader_key in st.session_state and st.session_state[uploader_key] is not None:
                actual_uploaded_file = st.session_state[uploader_key]
                report_text = extract_text_from_pdf(actual_uploaded_file)
                # Clear the uploader state after processing (important!)
                # Note: Direct assignment might not always work as expected, test thoroughly
                st.session_state[uploader_key] = None


            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("AI is thinking..."):
                    ai_response = get_ai_response(prompt, report_text, st.session_state.username)
                st.markdown(ai_response)

            # Save AI message to DB
            ai_msg_obj = {"role": "assistant", "content": ai_response}
            save_message(current_chat_id_to_use, ai_msg_obj)
            # Add to session state
            st.session_state.messages.append({"message": ai_msg_obj})

            # Rerun ONLY if a new chat was created to fully refresh UI state
            if new_chat_created:
                st.rerun()
            else:
                 # For existing chats, we need to rerun to clear the chat input box
                 st.rerun()


    # --- PDF DOWNLOAD BUTTON ---
    # Show only if a chat is active and there's at least one assistant message
    if st.session_state.current_chat_id and st.session_state.messages:
        # Find the last assistant message
        last_assistant_message_content = None
        for msg_doc in reversed(st.session_state.messages):
            msg = msg_doc.get("message", {})
            if msg.get("role") == "assistant":
                last_assistant_message_content = msg.get("content")
                break

        if last_assistant_message_content:
            try:
                pdf_data = create_pdf_report(last_assistant_message_content, st.session_state.username)
                if pdf_data: # Check if PDF generation was successful
                    st.download_button(
                        label="Download Last AI Report",
                        data=pdf_data,
                        file_name=f"{st.session_state.username}_AI_Report_{datetime.date.today()}.pdf",
                        mime="application/pdf",
                        key="download_button_main"
                    )
            except Exception as e:
                # Error should ideally be handled within create_pdf_report
                # but adding a failsafe here
                st.error(f"Could not prepare PDF for download: {e}")


# --- 4. MAIN APP ROUTER ---
# Checks if the user is logged in and shows the appropriate page.
if not st.session_state.logged_in:
    show_login_page()
else:
    # Ensure database connection is valid before showing main app
    #if db is None:
        # st.error("Database connection failed. Please contact support or try again later.")
         # Optionally add a logout button here
         #if st.button("Logout"):
             # for key in default_states.keys():
                  # if key in st.session_state: del st.session_state[key]
             # st.rerun()
  #  else:
         show_main_app()