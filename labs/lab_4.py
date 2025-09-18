import streamlit as st
import os
import sys
import chromadb
from openai import OpenAI
from PyPDF2 import PdfReader

# --- Fix for ChromaDB with Streamlit (sqlite3 conflict) ---
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

st.title("Lab 4: RAG with ChromaDB")

# ---------------- OpenAI Client ----------------
if "openai_client" not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.openai_client = OpenAI(api_key=api_key)

# ---------------- Initialize ChromaDB ----------------
if "Lab4_vectorDB" not in st.session_state:
    chromaDB_path = "./ChromaDB_for_lab"
    chroma_client = chromadb.PersistentClient(path=chromaDB_path)
    collection = chroma_client.get_or_create_collection("Lab4Collection")
    st.session_state.Lab4_vectorDB = collection
else:
    collection = st.session_state.Lab4_vectorDB

# ---------------- Helper: Add PDF to Collection ----------------
def add_to_collection(collection, text, filename):
    """Create embedding and add a document to ChromaDB"""
    openai_client = st.session_state.openai_client

    # Create embedding
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding

    # Add embedding + text to ChromaDB
    collection.add(
        documents=[text],
        ids=[filename],
        embeddings=[embedding]
    )

# ---------------- Load PDFs into Vector DB ----------------
def load_pdfs_into_chromadb(pdf_files):
    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        filename = os.path.basename(pdf_file.name)
        add_to_collection(collection, text, filename)

# ---------------- PDF Upload ----------------
uploaded_pdfs = st.file_uploader("Upload the 7 PDF files", type="pdf", accept_multiple_files=True)
if uploaded_pdfs:
    if st.button("Process PDFs"):
        load_pdfs_into_chromadb(uploaded_pdfs)
        st.success("PDFs processed and added to ChromaDB collection!")

# ---------------- Test the Vector DB ----------------
topic = st.text_input("Enter a search topic (e.g. Generative AI, Text Mining, Data Science Overview)")

if st.button("Run Test Search") and topic:
    openai_client = st.session_state.openai_client
    # Embed the query
    response = openai_client.embeddings.create(
        input=topic,
        model="text-embedding-3-small"
    )
    query_embedding = response.data[0].embedding

    # Query collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    st.subheader("Top 3 Matching Documents")
    for i in range(len(results['documents'][0])):
        doc_id = results['ids'][0][i]
        st.write(f"{i+1}. {doc_id}")

