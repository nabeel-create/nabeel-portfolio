# app.py
import streamlit as st
from transformers import pipeline
import re

st.set_page_config(page_title="Chatbot (Flan-T5, improved)", page_icon="💬", layout="centered")

# --- Style ---
st.markdown("""
<style>
body, .stApp { background-color: white; color: black; }
</style>
""", unsafe_allow_html=True)

st.title("💬 Chatbot — Flan-T5 (repetition reduced)")
st.caption("Local model with safer generation parameters to avoid repeating output.")

# --- Load model once and cache it (to avoid reloads) ---
@st.cache_resource
def load_model():
    # Use flan-t5-base for better quality; change to google/flan-t5-small for faster loads if needed
    return pipeline("text2text-generation", model="google/flan-t5-base")

nlp = load_model()

# --- Keep chat history ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Helper: clean repeated characters and trivial repeats ---
def clean_answer(text: str) -> str:
    if not text:
        return text
    # collapse long repeated characters (e.g., "!!!!!!" or "????")
    text = re.sub(r'(.)\1{10,}', r'\1', text)
    # collapse repeated phrases that occur more than twice in immediate succession
    # e.g., "Is there anything I can help you with? Is there anything I can help you with?"
    parts = text.split()
    if len(parts) > 40:
        # basic check to avoid extreme repetition: if many repeated substrings, trim
        joined = " ".join(parts)
        # detect a short phrase repeated many times (naive)
        for L in range(2, 8):
            phrase = " ".join(parts[:L])
            if phrase and joined.count(phrase) > 3:
                # keep a single instance
                return phrase + " " + " ".join(parts[L: L+50])
    return text.strip()

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

    # generation settings tuned to reduce repetition
    gen_kwargs = {
        "max_new_tokens": 128,         # length of generated reply
        "do_sample": False,            # deterministic decoding
        "num_beams": 4,                # beam search for better output
        "no_repeat_ngram_size": 3,     # avoid repeating n-grams
        "repetition_penalty": 1.2,     # penalize repeated tokens
        # "early_stopping": True       # pipeline may accept this via generate
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # The pipeline will accept these kwargs and pass to model.generate
                outputs = nlp(user_input, **gen_kwargs)
                raw_answer = outputs[0].get("generated_text") or outputs[0].get("text") or str(outputs[0])
                answer = clean_answer(raw_answer)
            except Exception as e:
                answer = f"⚠️ Error: {e}"

            st.markdown(answer)
            st.session_state.history.append(("assistant", answer))

# --- Clear button ---
if st.sidebar.button("Clear Chat"):
    st.session_state.history = []
    st.rerun()
