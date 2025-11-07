import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# --- Title ---
st.title("💬 Offline Chatbot — Flan-T5")

# --- Load model once ---
@st.cache_resource
def load_model():
    model_name = "google/flan-t5-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()

# --- Initialize chat history ---
if "history" not in st.session_state:
    st.session_state["history"] = []

# --- Chat input ---
user_input = st.text_input("You:", key="user_input")

if st.button("Send") and user_input.strip():
    # Add user message
    st.session_state["history"].append({"role": "user", "text": user_input})

    # Prepare input
    prompt = f"The following is a conversation:\n"
    for msg in st.session_state["history"]:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['text']}\n"
    prompt += "Assistant:"

    # Generate response
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=120,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.4,
        do_sample=True
    )

    bot_reply = tokenizer.decode(outputs[0], skip_special_tokens=True).split("Assistant:")[-1].strip()
    st.session_state["history"].append({"role": "assistant", "text": bot_reply})

# --- Display chat ---
for msg in st.session_state["history"]:
    if msg["role"] == "user":
        st.markdown(f"🧑 **You:** {msg['text']}")
    else:
        st.markdown(f"🤖 **Bot:** {msg['text']}")
