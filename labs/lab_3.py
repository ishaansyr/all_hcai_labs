import streamlit as st
from openai import OpenAI

st.title("Lab 3: Chatbot")

# Sidebar: model selection
openAI_model = st.sidebar.selectbox("Which Model?", ("mini", "regular"))
model_to_use = "gpt-4o-mini" if openAI_model == "mini" else "gpt-4o"

# Initialize OpenAI client once per session
if "client" not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input box (chat input)
user_input = st.chat_input("Type your message here...")

# When user sends a message
if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Keep only the last 4 messages (2 user + 2 assistant)
    st.session_state.messages = st.session_state.messages[-4:]

    with st.chat_message("user"):
        st.markdown(user_input)

    # Call OpenAI model
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.client.chat.completions.create(
                model=model_to_use,
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": reply})
