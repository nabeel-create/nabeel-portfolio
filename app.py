import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Chatbot (Gemini)", page_icon="💬")

# --- STYLE ---
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

# --- API KEY INPUT ---
st.sidebar.header("🔑 Gemini API Key Setup")
api_key = st.sidebar.text_input("Enter your Gemini API key:", type="password")

if not api_key:
    st.warning("Please enter your Gemini API key to continue.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

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
        placeholder = st.empty()
        placeholder.markdown("Thinking...")

        try:
            response = model.generate_content(prompt)
            reply = response.text
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        placeholder.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# --- SIDEBAR ---
with st.sidebar:
    if st.button("Clear Chat"):
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        st.rerun()
