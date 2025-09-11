import streamlit as st
from openai import OpenAI

st.title("Lab 3: Chatbot")

# Sidebar model selection
openAI_model = st.sidebar.selectbox("Which Model?", ("mini", "regular"))
model_to_use = "gpt-4o-mini" if openAI_model == "mini" else "gpt-4o"

# Initialize OpenAI client
if "client" not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

# Session state setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you?"}
    ]
if "info_stage" not in st.session_state:
    st.session_state.info_stage = 0  # 0 = normal, 1 = after first reply, 2 = second follow-up

# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Handle follow-up info stages
    if st.session_state.info_stage == 1 and user_input.strip().lower() == "yes":
        prompt = "Please expand with more detail. Build on the last answer, do not repeat the same information. If you don't know the answer, just say so"
        st.session_state.info_stage = 2
    elif st.session_state.info_stage == 2 and user_input.strip().lower() == "yes":
        prompt = "Please expand with even more detail. Build on the last 2 answers, do not repeat the same information"
        st.session_state.info_stage = 0
    elif st.session_state.info_stage in [1, 2] and user_input.strip().lower() != "yes":
        prompt = "What can I help you with?"
        st.session_state.info_stage = 0
    else:
        prompt = user_input
        st.session_state.info_stage = 1  # prepare for potential follow-up

    # Call OpenAI
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.client.chat.completions.create(
                model=model_to_use,
                messages=st.session_state.messages + [{"role": "user", "content": prompt}],
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Add follow-up question if in info flow
    if st.session_state.info_stage in [1, 2]:
        follow_up = "Do you want some more information?"
        st.session_state.messages.append({"role": "assistant", "content": follow_up})
        with st.chat_message("assistant"):
            st.markdown(follow_up)

    # Keep only recent messages (buffer)
    st.session_state.messages = st.session_state.messages[-10:]
