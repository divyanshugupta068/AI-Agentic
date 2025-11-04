import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Recommender Agent",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI E-commerce Assistant")

# --- API Configuration ---
API_URL = "http://127.0.0.1:8000/agent_recommend"

# --- User Selection ---
# We still need to know who the user is
user_id = st.sidebar.selectbox(
    "Select User Profile:",
    ("user123", "user456")
)

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What are you looking for?"):
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Send to Agent API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # We don't send the full history for this simple demo, but you could
            response = requests.post(
                API_URL,
                json={"user_id": user_id, "query": prompt, "chat_history": []}
            )
            response.raise_for_status()
            
            full_response = response.json().get("response", "I'm sorry, I encountered an error.")
            message_placeholder.markdown(full_response)
            
        except requests.exceptions.RequestException as e:
            full_response = f"Error connecting to API: {e}"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})