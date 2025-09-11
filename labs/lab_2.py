import streamlit as st
from openai import OpenAI

st.title("Lab 2: Document Summariser")

api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found in secrets. Add `API_KEY` to `.streamlit/secrets.toml`.")
    st.stop()

client = OpenAI(api_key=api_key)

# Sidebar controls
summary_choice = st.sidebar.radio(
    "Summary Type",
    [
        "Summarize the document in 100 words",
        "Summarize the document in 2 connecting paragraphs",
        "Summarize the document in 5 bullet points",
    ],
    index=0,
)

use_advanced = st.sidebar.checkbox("Use Advanced Model", value=False)

# Default: gpt-4o-mini; if advanced is selected: gpt-4o
model_name = "gpt-4o" if use_advanced else "gpt-4o-mini"


uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))

def build_instruction(choice: str) -> str:
    if "100 words" in choice:
        return (
            "Summarise the document in exactly 100 words as a single paragraph. "
            "No title or bullets. Use only information from the document."
        )
    if "2 connecting paragraphs" in choice:
        return (
            "Summarise the document in two connected paragraphs. "
            "Paragraph 1: core thesis and key evidence. "
            "Paragraph 2: implications, limitations, or next steps linking back to paragraph 1. "
            "No headings or bullets. Use only information from the document."
        )
    return (
        "Summarise the document in exactly five bullet points. "
        "Each point must be 25 words or fewer, factual, and non-overlapping. "
        "No introduction or conclusion. Use only information from the document."
    )

if uploaded_file:
    document = uploaded_file.read().decode("utf-8", errors="ignore")
    instruction = build_instruction(summary_choice)
    messages = [
        {"role": "system", "content": "You are a careful, concise summariser. Follow the requested format exactly and do not invent facts."},
        {"role": "user", "content": f"{instruction}\n\n--- DOCUMENT START ---\n{document}\n--- DOCUMENT END ---"},
    ]
    stream = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.3,
        stream=True,
    )
    st.write_stream(stream)



    '''
    4o-mini should be the default model for a task such as this, as the stark increase in the cost isn't worth the marginal improvement in asnwers from 4o to 40-mini
    '''
