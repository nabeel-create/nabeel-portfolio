# app.py
import streamlit as st
import openai
import os

st.set_page_config(page_title="AI Chatbot", page_icon="💬")

# --- CUSTOM STYLE (white background) ---
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: white;
        color: black;
        font-family: "Segoe UI", sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- API KEY ---
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.stop()

MODEL = "gpt-4o-mini"

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

# --- DISPLAY CHAT ---
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- USER INPUT ---
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=512,
            )
            reply = response["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"Error: {e}"
        message_placeholder.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

# --- SIDEBAR ---
with st.sidebar:
    if st.button("Clear Chat"):
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        st.rerun()
