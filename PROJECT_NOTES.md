# PDF Chat Agent - Complete Development Documentation

---

# 1. Project Overview

# Objective

The goal of this project was to build an AI-powered PDF Question Answering system capable of:

* Uploading PDF documents
* Extracting text from uploaded PDFs
* Converting text into vector embeddings
* Storing embeddings in a vector database
* Performing semantic search on document content
* Retrieving relevant information based on user queries
* Generating accurate answers using a Large Language Model (LLM)
* Deploying the application on Streamlit Cloud

---

# 2. System Architecture


PDF Upload
    ↓
Text Extraction (pypdf)
    ↓
Text Chunking
    ↓
Embedding Generation
(Sentence Transformers)
    ↓
Store Embeddings
(ChromaDB)
    ↓
User Question
    ↓
Question Embedding
    ↓
Semantic Search
    ↓
Retrieve Relevant Chunks
    ↓
Prompt Construction
    ↓
Groq Llama 3.3
    ↓
Final Answer

---

# 3. Technology Stack

# Frontend

Streamlit

Used for:

* PDF upload interface
* User question input
* Displaying generated answers
* Displaying retrieved chunks
* Maintaining chat history

---

# PDF Processing

pypdf

Used for:

* Reading uploaded PDF files
* Extracting text page by page

---

# Embedding Model

 Sentence Transformers

Model Used:

all-MiniLM-L6-v2


Purpose:

* Convert text chunks into vector embeddings
* Convert user questions into embeddings
* Enable semantic similarity search

---

# Vector Database

ChromaDB

Used for:

* Storing document embeddings
* Performing vector similarity search
* Retrieving relevant chunks for question answering

---

# Large Language Model

Initial Plan

Ollama
Qwen 2.5


# Final Implementation

Groq API
Llama 3.3 70B Versatile


# Reason for Migration

The project was initially designed using Ollama and Qwen 2.5 as a locally hosted LLM.

However:

* Large model downloads were required
* Local inference consumed significant resources
* Deployment became more difficult

The application was migrated to Groq's hosted API using Llama 3.3 70B Versatile.

Benefits:

* Faster inference
* No local model downloads
* Easier deployment
* Free developer tier

---

# 4. Project Structure

pdf-chat-agent/
│
├── app.py
├── requirements.txt
├── README.md
├── PROJECT_NOTES.md
├── .gitignore
│
├── .streamlit/
│   └── secrets.toml
│
└── chroma_db/

---

# 5. Environment Setup

Create Virtual Environment

python -m venv venv


# Activate Environment

venv\Scripts\activate


# Install Dependencies


pip install streamlit
pip install pypdf
pip install sentence-transformers
pip install chromadb
pip install groq

---

# 6. Streamlit Configuration

Configured application settings:


st.set_page_config(
    page_title="PDF Chat Agent",
    page_icon="📄"
)

Application title:

st.title("📄 PDF Chat Agent")

---

# 7. PDF Upload Implementation

Implemented PDF upload using:

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

Purpose:

* Restrict uploads to PDF files only
* Allow users to provide documents dynamically

---

# 8. PDF Text Extraction

Created a PDF reader:

reader = PdfReader(uploaded_file)


Looped through all pages:


for page in reader.pages:


Extracted page text:


page.extract_text()


Stored extracted content:


full_text += page_text


Validation:

if not full_text.strip():
    st.error(...)

Purpose:

Prevent processing PDFs with no readable text.

---

# 9. Text Chunking

# Problem

Large PDFs cannot be efficiently processed as a single block of text.

# Solution

Split the document into overlapping chunks.

Implementation:


chunk_size = 800
overlap = 150


Chunk generation:


for i in range(
    0,
    len(full_text),
    chunk_size - overlap
)


Benefits:

* Better retrieval accuracy
* Reduced context size
* Improved semantic search

---

# 10. Embedding Generation

Loaded embedding model:


SentenceTransformer(
    "all-MiniLM-L6-v2"
)


Generated embeddings:


embedding_model.encode(
    chunks
)


Purpose:

Convert text into vector representations that capture semantic meaning.

---

# 11. ChromaDB Integration

Created ChromaDB client:


chromadb.Client()


Created collection:


create_collection()


Stored:

* Documents
* Embeddings
* IDs

Purpose:

Persist vectorized document data for retrieval.

---

# 12. Semantic Search

Example Question:

Who scored highest?


Question embedding:


embedding_model.encode(
    [question]
)


Vector search:


collection.query(
    query_embeddings=[
        query_embedding
    ],
    n_results=5
)


Result:

Returns the most semantically relevant chunks from the PDF.

---

# 13. Context Construction

Combined retrieved chunks:

context = "\n\n".join(
    retrieved_chunks
)


Purpose:

Provide only relevant information to the language model.

---

# 14. Retrieval-Augmented Generation (RAG)

Instead of sending the entire PDF to the LLM, the application:

1. Retrieves relevant chunks using semantic search
2. Builds context from retrieved content
3. Sends only that context to the model

Benefits:

* Reduced token usage
* Faster responses
* Better accuracy
* Reduced hallucinations

---

# 15. Groq Integration

Created Groq client:


client_groq = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


Stored secret key in:

.streamlit/secrets.toml


GROQ_API_KEY="YOUR_API_KEY"


---

# 16. Prompt Engineering

Prompt was designed to enforce:

* Context-only answers
* Direct factual responses
* Proper chapter formatting
* Markdown support
* Code block preservation
* Hallucination prevention

Fallback response:


I could not find that information in the PDF.


---

# 17. Challenge 1: Chapter Formatting

# Issue

Chapter requests returned:

* Single paragraph output
* Broken formatting
* Lost code blocks

# Root Cause

Prompt did not explicitly preserve formatting.

# Solution

Added instructions:

* Preserve formatting
* Use markdown
* Use code blocks
* Display complete chapter structure

# Result

Chapters display correctly with:

* Headings
* Examples
* Exercises
* Solutions
* Code formatting

---

# 18. Challenge 2: Chat History Overflow

# Issue

Large chapter responses filled the chat history.

# Solution

Store shortened answers:


answer[:150]

# Result

Cleaner interface and better readability.

---

# 19. Challenge 3: Repeated PDF Processing

# Issue

PDF embeddings were recreated on every Streamlit rerun.

# Solution

Implemented Session State.

Stored:

current_pdf

# Result

PDF is processed only once per upload.

---

# 20. Session State Management

Created:

if "chat_history" not in st.session_state:

Used for:

* Chat history
* Current PDF tracking

Benefits:

* Faster application performance
* Persistent UI state

---

# 21. Retrieved Chunks Viewer

Implemented:

st.expander(
    "Retrieved Chunks"
)

Purpose:

Display retrieved chunks before answer generation.

Benefits:

* Easier debugging
* Better transparency
* Retrieval validation

---

# 22. Requirements File

Final dependencies:

streamlit==1.58.0
pypdf==6.13.2
sentence-transformers==5.5.1
chromadb==1.5.9
groq==1.4.0

---

# 23. GitHub Workflow

Repository:


pdf-chat-agent


Initialization:

git init


Connect Remote:


git remote add origin <repository-url>


Commit:


git add .
git commit -m "Initial commit"


Push:


git push origin main


---

# 24. Updating GitHub

Check status:


git status


View changes:


git diff


Commit updates:


git add app.py
git commit -m "Update PDF chat agent"
git push origin main


Verification:


git status


Output:


working tree clean


---

# 25. Streamlit Deployment

Connected:

* GitHub Repository

Configured:

* Branch: main
* Main file: app.py

Added secret:


GROQ_API_KEY


Deployment completed successfully.

---

# 26. Testing

# Test Case 1 - Semantic Retrieval

Question:

Who scored highest?

Expected Output:

Riya scored the highest with 95 marks.

Actual Output:

Riya scored the highest with 95 marks.

Status:

✅ PASS

---

## Test Case 2 – Numerical Retrieval

Question:

What marks did Aman score?

Expected Output:

80

Actual Output:

80

Status:

✅ PASS

---

# Test Case 3 – Chapter Retrieval

Question:

Chapter 5

Expected Output:

* Complete chapter content
* Formatted code
* Exercises
* Solutions

Actual Output:

* Complete chapter content
* Formatted code
* Exercises
* Solutions

Status:

✅ PASS

---

## Test Case 4 – Out-of-Context Question

Question:

What is the capital of France?

Expected Output:

I could not find that information in the PDF.

Actual Output:

I could not find that information in the PDF.

Status:

✅ PASS

---

# 27. Future Enhancements

Potential improvements:

* Support multiple PDFs
* Add page citations
* Add source references
* Support DOCX files
* Support TXT files
* Add user authentication
* Store chat history in a database
* Stream responses in real-time
* Add conversational memory

---

# 28. Concepts Learned

# AI & Machine Learning

* Embeddings
* Semantic Search
* Vector Databases
* Retrieval-Augmented Generation (RAG)
* Prompt Engineering

# Backend Development

* PDF Parsing
* Text Processing
* Session State Management

# Databases

* ChromaDB
* Vector Storage

# LLM Integration

* Groq API
* Llama 3.3 70B Versatile

# Deployment

* Git
* GitHub
* Streamlit Cloud

---

# 29. Project Outcome

Successfully developed and deployed a Retrieval-Augmented Generation (RAG) based PDF Question Answering system using:

* Streamlit
* ChromaDB
* Sentence Transformers
* Groq
* Llama 3.3 70B Versatile

The application can:

* Upload PDFs
* Extract document text
* Generate semantic embeddings
* Perform vector search
* Retrieve relevant content
* Generate context-aware answers
* Preserve chapter formatting
* Preserve code blocks
* Reduce hallucinations through context-only prompting
* Operate successfully on Streamlit Cloud

---

# 30. Interview Explanation (30 Seconds)

I built a PDF Chat Agent using Streamlit, ChromaDB, Sentence Transformers, and Groq's Llama 3.3 70B model. The application extracts text from uploaded PDFs, splits the content into chunks, generates embeddings, and stores them in ChromaDB. When a user asks a question, the system performs semantic search to retrieve the most relevant chunks and sends only that context to the language model. This Retrieval-Augmented Generation approach improves answer accuracy and reduces hallucinations. I also implemented session state management, prompt engineering, chat history, debugging tools, GitHub integration, and deployed the application on Streamlit Cloud.
