import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Chatbot (Gemini)", page_icon="💬")

# --- STYLE ---
st.markdown("""
<style>
body, .stApp {
    background-color: white;
    color: black;
    font-family: "Segoe UI", sans-serif;
}
</style>
""", unsafe_allow_html=True)

# --- API KEY INPUT ---
st.sidebar.header("🔑 Gemini API Key Setup")
api_key = st.sidebar.text_input("Enter your Gemini API key:", type="password")

if not api_key:
    st.warning("Please enter your Gemini API key to continue.")
    st.stop()

# --- CONFIGURE GEMINI ---
genai.configure(api_key=api_key)

# --- FIND AVAILABLE MODEL ---
try:
    available_models = [m.name for m in genai.list_models() if "gemini" in m.name.lower()]
    if not available_models:
        st.error("⚠️ No Gemini models found for this API key. Check your Google AI Studio access.")
        st.stop()
    MODEL = available_models[0]  # pick the first available model
except Exception as e:
    st.error(f"Error loading models: {e}")
    st.stop()

# --- SETUP CHAT ---
if "chat" not in st.session_state:
    model = genai.GenerativeModel(MODEL)
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.history = []

# --- DISPLAY CHAT HISTORY ---
for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

# --- USER INPUT ---
if prompt := st.chat_input("Type your message..."):
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")

        try:
            response = st.session_state.chat.send_message(prompt)
            reply = response.text
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        placeholder.markdown(reply)
        st.session_state.history.append(("assistant", reply))

# --- SIDEBAR ---
with st.sidebar:
    if st.button("Clear Chat"):
        model = genai.GenerativeModel(MODEL)
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.history = []
        st.rerun()
