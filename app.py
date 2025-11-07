# app.py
import streamlit as st
import openai
import os

# --- CONFIG ---
st.set_page_config(page_title="🤖 AI Chatbot", page_icon="💬")

# Read API key from Streamlit Secrets (secure)
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
for msg in st.session_state.messages[1:]:  # skip system message
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

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.write("**Model:**", MODEL)
    st.write("**Developer:** Nabeel")
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        st.experimental_rerun()

st.markdown("<br><hr><center>Made with ❤️ using Streamlit</center>", unsafe_allow_html=True)
      background: #1e88e5;
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      text-decoration: none;
      font-weight: 600;
    }
    a:hover { background: #1565c0; }
  </style>
</head>
<body>
  <h1>🚀 Nabeel's Project Hub</h1>
  <div class="projects">
    <div class="card">
      <h2>AI Gmail Sender</h2>
      <p>Automatically send emails with AI integration.</p>
      <a href="https://nabeel-gmail.streamlit.app" target="_blank">Open Project</a>
    </div>
    <div class="card">
      <h2>Best CV Ranker</h2>
      <p>Ranks CVs using AI-based keyword and score matching.</p>
      <a href="https://nabeel-cvranker.streamlit.app" target="_blank">Open Project</a>
    </div>
    <div class="card">
      <h2>PakGhar Laundry Capsules</h2>
      <p>Eco-friendly single-use detergent pods business plan.</p>
      <a href="https://nabeel-laundry.streamlit.app" target="_blank">Open Project</a>
    </div>
  </div>
</body>
</html>
