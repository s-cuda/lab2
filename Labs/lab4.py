import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
import sqlite3
import os

# Folder with PDFs
PDF_FOLDER = "lab_4_pdfs"  

# Helper: read PDF and extract text
def read_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# Build vector DB once per session
def build_Lab4_vectorDB():
    st.write("🔄 Building ChromaDB collection (this may take a moment)...")

    # Remove old collection if exists in session
    if "Lab4_vectorDB" in st.session_state:
        st.session_state.pop("Lab4_vectorDB")

    # Initialize ChromaDB client + collection
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="Lab4Collection")

    # OpenAI client
    api_key = st.secrets["openai"]["api_key"]
    openai_client = OpenAI(api_key=api_key)

    texts, metadatas, ids, embeddings = [], [], [], []

    for i, filename in enumerate(os.listdir(PDF_FOLDER)):
        if filename.endswith(".pdf"):
            file_path = os.path.join(PDF_FOLDER, filename)
            pdf_text = read_pdf(file_path)
            if not pdf_text.strip():
                continue

            texts.append(pdf_text)
            doc_id = f"doc_{i}"
            ids.append(doc_id)
            metadatas.append({"filename": filename})

            # Create embedding
            embedding_response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=pdf_text
            )
            embeddings.append(embedding_response.data[0].embedding)

    # Add to ChromaDB
    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )

    # Store collection in session state
    st.session_state.Lab4_vectorDB = collection
    st.write("✅ ChromaDB collection created.")

    # Store metadata in SQLite
    db_path = "lab4_metadata.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_docs (
            doc_id TEXT PRIMARY KEY,
            filename TEXT
        )
    """)

    for doc_id, meta in zip(ids, metadatas):
        cursor.execute("""
            INSERT OR REPLACE INTO pdf_docs (doc_id, filename)
            VALUES (?, ?)
        """, (doc_id, meta["filename"]))

    conn.commit()
    conn.close()
    st.write(f"✅ Metadata stored in SQLite database at {db_path}")

# Conversation buffer helper (keep last 2 messages)
def keep_last_n_messages(messages, n=2):
    return messages[-n*2:]

# Streamlit Lab4 page
def app():
    st.title("🤖 LAB 4 – RAG Chatbot with PDFs")

    # Build vector DB once per session
    if "Lab4_vectorDB" not in st.session_state:
        build_Lab4_vectorDB()

    collection = st.session_state.Lab4_vectorDB
    api_key = st.secrets["openai"]["api_key"]
    client = OpenAI(api_key=api_key)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! Ask me anything about the course PDFs."}
        ]

    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- RAG retrieval ---
        # Compute embedding for user query
        query_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=prompt
        ).data[0].embedding

        # Query ChromaDB for top 3 relevant documents
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )

        # Combine retrieved documents into context text
        context_texts = []
        if results and "documents" in results:
            for doc in results["documents"][0]:
                context_texts.append(doc)
        context = "\n\n".join(context_texts)

        # Construct prompt for LLM with context
        rag_prompt = f"""
You are a helpful assistant. Use the following documents to answer the user's question.
Only use information from these documents.

Documents:
{context}

User question:
{prompt}

Answer clearly and concisely:
"""

        # Get LLM response
        completion = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": rag_prompt}]
        )
        response = completion.choices[0].message.content

        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response)

        # Add to session history
        st.session_state.messages.append({"role": "assistant", "content": response})

