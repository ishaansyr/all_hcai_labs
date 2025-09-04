import streamlit as st
from openai import OpenAI

st.title("📄 Lab 2: My Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, set your OpenAI API key in `.streamlit/secrets.toml` or in the app’s Secrets on Streamlit Cloud."
)

# 1) Read key from secrets
openai_api_key = st.secrets.get("API_KEY")

# 2) Guardrail if missing
if not openai_api_key:
    st.error("OpenAI API key not found in secrets. Add `openai_api_key` to `.streamlit/secrets.toml` or the app’s Secrets.")
    st.stop()

# 3) Create client once
client = OpenAI(api_key=openai_api_key)

# 4) Rest of your app logic stays the same
uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))
question = st.text_area(
    "Now ask a question about the document!",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if uploaded_file and question:
    document = uploaded_file.read().decode()
    messages = [
        {"role": "user", "content": f"Here's a document: {document} \n\n---\n\n {question}"}
    ]
    stream = client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages,
        stream=True,
    )
    st.write_stream(stream)
