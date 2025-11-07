# app.py
import streamlit as st
import time
import requests

# Try to import transformers for local fallback
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    HAS_TRANSFORMERS = True
except Exception:
    HAS_TRANSFORMERS = False

st.set_page_config(page_title="Local / HF Chatbot", page_icon="💬", layout="centered")

# --- STYLE (white background, minimal) ---
st.markdown(
    """
    <style>
    body, .stApp { background-color: white; color: black; font-family: "Segoe UI", sans-serif; }
    .streamlit-expanderHeader { font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💬 Chatbot — Hugging Face (optional) + Local fallback")
st.caption("Enter a Hugging Face API token in the sidebar to use HF Inference, otherwise the app will run a small local model.")

# --- Sidebar: token + settings ---
st.sidebar.header("Settings")
hf_token = st.sidebar.text_input("Hugging Face API token (optional)", type="password")
model_choice = st.sidebar.selectbox(
    "Cloud model (used if HF token provided)",
    options=[
        "bigscience/bloom",         # placeholder (HF inference may map)
        "facebook/opt-1.3b",        # placeholder
        "gpt2"                      # small default cloud fallback
    ],
    index=2
)
max_tokens = st.sidebar.slider("Max tokens (output)", 64, 1024, 256)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)

st.sidebar.write("")
st.sidebar.write("Local fallback model:", "google/flan-t5-small" if HAS_TRANSFORMERS else "transformers not installed")
if not HAS_TRANSFORMERS:
    st.sidebar.warning("Install `transformers` to enable local fallback.")

# --- session state for chat history ---
if "history" not in st.session_state:
    st.session_state.history = []  # list of (role, text)

# --- helper: query HF Inference API ---
def query_hf_inference(token: str, model_id: str, prompt: str, max_new_tokens: int, temp: float):
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_new_tokens, "temperature": temp, "return_full_text": False},
        "options": {"wait_for_model": True}
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # HF Inference returns different shapes; handle common ones
        if isinstance(data, dict) and "error" in data:
            return None, f"HF error: {data['error']}"
        if isinstance(data, list):
            # many models return [{'generated_text': '...'}]
            text = data[0].get("generated_text") or data[0].get("text") or str(data[0])
            return text, None
        # fallback
        return str(data), None
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP error: {e.response.text if e.response is not None else e}"
    except Exception as e:
        return None, f"Request error: {e}"

# --- helper: local model generation using transformers (seq2seq) ---
_local_pipe = None
def local_generate(prompt: str, max_new_tokens: int, temp: float):
    global _local_pipe
    # model chosen for local fallback: google/flan-t5-small (seq2seq)
    model_name = "google/flan-t5-small"
    if not HAS_TRANSFORMERS:
        return None, "transformers not installed in environment."
    try:
        if _local_pipe is None:
            # load tokenizer + model (may download on first run)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            _local_pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device_map="auto" if hasattr(model, "is_loaded_in_8bit") else None)
        # generate
        outputs = _local_pipe(prompt, max_length=max_new_tokens, do_sample=temp > 0.0, num_return_sequences=1)
        text = outputs[0].get("generated_text") or outputs[0].get("generated_text")
        return text, None
    except Exception as e:
        return None, f"Local model error: {e}"

# --- Display chat history ---
for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

# --- Input area ---
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # assistant placeholder
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")

        reply_text = None
        error_msg = None

        # 1) Try HF Inference if token provided
        if hf_token:
            reply_text, error_msg = query_hf_inference(hf_token, model_choice, user_input, max_tokens, temperature)
            if reply_text is None:
                # clear HF error and fall back
                placeholder.markdown(f"HF error: {error_msg}\n\nFalling back to local model...")
                time.sleep(1.0)
        # 2) Local fallback
        if not reply_text:
            reply_text, local_err = local_generate(user_input, max_tokens, temperature)
            if reply_text is None:
                # If local failed, show combined error
                combined = error_msg or ""
                combined_local = local_err or ""
                final_err = " / ".join([p for p in (combined, combined_local) if p])
                placeholder.markdown(f"Error: {final_err}")
                st.session_state.history.append(("assistant", f"Error: {final_err}"))
            else:
                placeholder.markdown(reply_text)
                st.session_state.history.append(("assistant", reply_text))
        else:
            # HF succeeded
            placeholder.markdown(reply_text)
            st.session_state.history.append(("assistant", reply_text))

# --- Sidebar Clear button ---
with st.sidebar:
    if st.button("Clear Chat"):
        st.session_state.history = []
        st.experimental_rerun()
