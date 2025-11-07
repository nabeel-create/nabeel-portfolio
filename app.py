# app.py
import streamlit as st
import openai
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="🤖 AI Chatbot", page_icon="💬")

# --- CUSTOM CSS STYLING ---
st.markdown(
    """
    <style>
    body {
        background-color: #1e88e5; /* blue background */
        color: white;
        font-family: "Segoe UI", sans-serif;
    }
    .stApp {
        background-color: #1e88e5;
    }
    .stChatMessage {
        background-color: #1565c0;
        border-radius: 10px;
        padding: 8px;
        margin-bottom: 6px;
    }
    .stChatMessage.user {
        background-color: #42a5f5;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- OPENAI API KEY SETUP ---
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.warning("⚠️ Please set your OpenAI API key in Streamlit secrets to use this app.")
    st.stop()

MODEL = "gpt-4o-mini"

# --- APP TITLE ---
st.title("💬 AI Chatbot")
st.caption("Built with Python + Streamlit + OpenAI")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- USER INPUT ---
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 Thinking...")

        try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=512,
            )
            reply = response["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"❌ Error: {e}"

        message_placeholder.markdown(reply)

    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": reply})

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.write("**Model:**", MODEL)
    st.write("**Developer:** Nabeel")
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        st.experimental_rerun()

st.markdown("<br><hr><center>Made with ❤️ by Nabeel</center>", unsafe_allow_html=True)
