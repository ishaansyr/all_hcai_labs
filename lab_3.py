import streamlit as st
from openai import OpenAI

st.title("Lab 3: Chatbot")
openAI_model = st. sidebar.selectbox("Which Model?",
( "mini", "regular"))

if openAI_model == "mini":
    model_to_use = "gpt-4o-mini"
else:
    model_to_use = "gpt-40"

if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state ["messages"] = \
        [{"role": "assistant", "content": "How can I help you?"}]