# --- Fix for sqlite3 in Streamlit with ChromaDB ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from openai import OpenAI
import chromadb
import fitz  # PyMuPDF

st.title("Lab 4 - RAG Chatbot")

# Initialize OpenAI client once
if "openai_client" not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.openai_client = OpenAI(api_key=api_key)

# Path for persistent ChromaDB
CHROMA_DB_PATH = "./ChromaDB_for_lab4"

# Initialize or reuse collection
if "Lab4_vectorDB" not in st.session_state:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = chroma_client.get_or_create_collection("Lab4Collection")
    st.session_state.Lab4_vectorDB = collection
else:
    collection = st.session_state.Lab4_vectorDB


def extract_text_from_pdf(uploaded_file):
    """Extract all text from a PDF file using PyMuPDF."""
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text")
    return text


def add_pdfs_to_chromadb(uploaded_files):
    """Embed and add uploaded PDFs into ChromaDB."""
    openai_client = st.session_state.openai_client
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
            if text.strip():
                # Create embedding
                resp = openai_client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                embedding = resp.data[0].embedding
                collection.add(
                    documents=[text],
                    ids=[uploaded_file.name],
                    embeddings=[embedding],
                    metadatas=[{"filename": uploaded_file.name}]
                )


# ---- File uploader ----
uploaded_files = st.file_uploader(
    "Upload PDF files (knowledge base)",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Add to Knowledge Base"):
        add_pdfs_to_chromadb(uploaded_files)
        st.success("PDFs added to ChromaDB collection")

# ---- Chatbot ----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask me anything. I’ll use the knowledge base if relevant."}
    ]

# Display past chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type your question here...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Embed query for retrieval
    openai_client = st.session_state.openai_client
    resp = openai_client.embeddings.create(
        input=user_input,
        model="text-embedding-3-small"
    )
    query_embedding = resp.data[0].embedding

    results = collection.query(query_embeddings=[query_embedding], n_results=2)

    # Retrieved docs
    retrieved_docs = results["documents"][0] if results and results["documents"] else []
    context_text = "\n\n".join(retrieved_docs)

    # Prompt engineering
    system_prompt = (
        "You are a helpful chatbot. "
        "If relevant context is provided, use it to answer. "
        "Be explicit whether your answer is based on the knowledge base or from your own reasoning."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Question: {user_input}\n\nContext from knowledge base:\n{context_text}"}
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = openai_client.chat.completions.create(
                model="gpt-5-nano",
                messages=messages
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
