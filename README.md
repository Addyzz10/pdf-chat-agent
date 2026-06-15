# PDF Chat Agent

A Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions about their content.

# Features

* Upload PDF documents
* Automatic text extraction
* Semantic search using embeddings
* Context-aware question answering
* Chat history
* Retrieval chunk inspection
* Groq Llama 3.3 integration
* ChromaDB vector storage

# Tech Stack

* Streamlit
* PyPDF
* Sentence Transformers
* ChromaDB
* Groq API
* Llama 3.3 70B Versatile

# How It Works

1. Upload a PDF file.
2. Text is extracted from the document.
3. The document is split into chunks.
4. Embeddings are generated using Sentence Transformers.
5. Chunks are stored in ChromaDB.
6. User questions are converted into embeddings.
7. Relevant chunks are retrieved.
8. Groq Llama 3.3 generates answers using only the retrieved context.

PDF
 ↓
Text Extraction (PyPDF)
 ↓
Chunking
 ↓
Embeddings (Sentence Transformers)
 ↓
ChromaDB Vector Store
 ↓
Semantic Retrieval
 ↓
Groq Llama 3.3
 ↓
Answer

# Installation

pip install -r requirements.txt


# Run


streamlit run app.py


# Environment Variables

Create `.streamlit/secrets.toml`

GROQ_API_KEY="your_groq_api_key"

# Deployment

The application can be deployed directly on Streamlit Community Cloud.
