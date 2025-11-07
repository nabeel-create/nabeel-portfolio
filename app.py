import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="Chatbot", page_icon="💬", layout="centered")

# --- Style ---
st.markdown("""
<style>
body, .stApp { background-color: white; color: black; }
</style>
""", unsafe_allow_html=True)

st.title("💬 Offline Chatbot (Flan-T5)")
st.caption("Runs entirely free — no API key required!")

# --- Load model once and cache it (to avoid reloads) ---
@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-base")

nlp = load_model()

# --- Keep chat history ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Display history ---
for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

# --- User input ---
user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = nlp(user_input, max_length=256, do_sample=True)
                answer = response[0]['generated_text']
            except Exception as e:
                answer = f"⚠️ Error: {e}"

            st.markdown(answer)
            st.session_state.history.append(("assistant", answer))

# --- Clear button ---
if st.sidebar.button("Clear Chat"):
    st.session_state.history = []
    st.rerun()
