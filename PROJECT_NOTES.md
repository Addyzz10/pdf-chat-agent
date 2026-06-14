# PDF Chat Agent – Complete Development Documentation

---

# 1. Project Overview

## Objective

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

```text
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
```

---

# 3. Technology Stack

## Frontend

### Streamlit

Used for:

* PDF upload interface
* User question input
* Displaying generated answers
* Displaying retrieved chunks
* Maintaining chat history

---

## PDF Processing

### pypdf

Used for:

* Reading uploaded PDF files
* Extracting text page by page

---

## Embedding Model

### Sentence Transformers

Model Used:

```text
all-MiniLM-L6-v2
```

Purpose:

* Convert text chunks into vector embeddings
* Convert user questions into embeddings
* Enable semantic similarity search

---

## Vector Database

### ChromaDB

Used for:

* Storing document embeddings
* Performing vector similarity search
* Retrieving relevant chunks for question answering

---

## Large Language Model

### Initial Plan

```text
Ollama
Qwen 2.5
```

### Final Implementation

```text
Groq API
Llama 3.3 70B Versatile
```

### Reason for Migration

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

```text
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
```

---

# 5. Environment Setup

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Environment

```bash
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install streamlit
pip install pypdf
pip install sentence-transformers
pip install chromadb
pip install groq
```

---

# 6. Streamlit Configuration

Configured application settings:

```python
st.set_page_config(
    page_title="PDF Chat Agent",
    page_icon="📄"
)
```

Application title:

```python
st.title("📄 PDF Chat Agent")
```

---

# 7. PDF Upload Implementation

Implemented PDF upload using:

```python
uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)
```

Purpose:

* Restrict uploads to PDF files only
* Allow users to provide documents dynamically

---

# 8. PDF Text Extraction

Created a PDF reader:

```python
reader = PdfReader(uploaded_file)
```

Looped through all pages:

```python
for page in reader.pages:
```

Extracted page text:

```python
page.extract_text()
```

Stored extracted content:

```python
full_text += page_text
```

Validation:

```python
if not full_text.strip():
    st.error(...)
```

Purpose:

Prevent processing PDFs with no readable text.

---

# 9. Text Chunking

## Problem

Large PDFs cannot be efficiently processed as a single block of text.

## Solution

Split the document into overlapping chunks.

Implementation:

```python
chunk_size = 800
overlap = 150
```

Chunk generation:

```python
for i in range(
    0,
    len(full_text),
    chunk_size - overlap
)
```

Benefits:

* Better retrieval accuracy
* Reduced context size
* Improved semantic search

---

# 10. Embedding Generation

Loaded embedding model:

```python
SentenceTransformer(
    "all-MiniLM-L6-v2"
)
```

Generated embeddings:

```python
embedding_model.encode(
    chunks
)
```

Purpose:

Convert text into vector representations that capture semantic meaning.

---

# 11. ChromaDB Integration

Created ChromaDB client:

```python
chromadb.Client()
```

Created collection:

```python
create_collection()
```

Stored:

* Documents
* Embeddings
* IDs

Purpose:

Persist vectorized document data for retrieval.

---

# 12. Semantic Search

Example Question:

```text
Who scored highest?
```

Question embedding:

```python
embedding_model.encode(
    [question]
)
```

Vector search:

```python
collection.query(
    query_embeddings=[
        query_embedding
    ],
    n_results=5
)
```

Result:

Returns the most semantically relevant chunks from the PDF.

---

# 13. Context Construction

Combined retrieved chunks:

```python
context = "\n\n".join(
    retrieved_chunks
)
```

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

```python
client_groq = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)
```

Stored secret key in:

```toml
.streamlit/secrets.toml
```

```toml
GROQ_API_KEY="YOUR_API_KEY"
```

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

```text
I could not find that information in the PDF.
```

---

# 17. Challenge 1: Chapter Formatting

## Issue

Chapter requests returned:

* Single paragraph output
* Broken formatting
* Lost code blocks

## Root Cause

Prompt did not explicitly preserve formatting.

## Solution

Added instructions:

* Preserve formatting
* Use markdown
* Use code blocks
* Display complete chapter structure

## Result

Chapters display correctly with:

* Headings
* Examples
* Exercises
* Solutions
* Code formatting

---

# 18. Challenge 2: Chat History Overflow

## Issue

Large chapter responses filled the chat history.

## Solution

Store shortened answers:

```python
answer[:150]
```

## Result

Cleaner interface and better readability.

---

# 19. Challenge 3: Repeated PDF Processing

## Issue

PDF embeddings were recreated on every Streamlit rerun.

## Solution

Implemented Session State.

Stored:

```python
current_pdf
```

## Result

PDF is processed only once per upload.

---

# 20. Session State Management

Created:

```python
if "chat_history" not in st.session_state:
```

Used for:

* Chat history
* Current PDF tracking

Benefits:

* Faster application performance
* Persistent UI state

---

# 21. Retrieved Chunks Viewer

Implemented:

```python
st.expander(
    "Retrieved Chunks"
)
```

Purpose:

Display retrieved chunks before answer generation.

Benefits:

* Easier debugging
* Better transparency
* Retrieval validation

---

# 22. Requirements File

Final dependencies:

```text
streamlit==1.35.0
pypdf==4.2.0

sentence-transformers==2.7.0
transformers==4.41.2
torch==2.2.2

chromadb==0.5.3
protobuf==4.25.3

groq==0.26.0
```

---

# 23. GitHub Workflow

Repository:

```text
pdf-chat-agent
```

Initialization:

```bash
git init
```

Connect Remote:

```bash
git remote add origin <repository-url>
```

Commit:

```bash
git add .
git commit -m "Initial commit"
```

Push:

```bash
git push origin main
```

---

# 24. Updating GitHub

Check status:

```bash
git status
```

View changes:

```bash
git diff
```

Commit updates:

```bash
git add app.py
git commit -m "Update PDF chat agent"
git push origin main
```

Verification:

```bash
git status
```

Output:

```text
working tree clean
```

---

# 25. Streamlit Deployment

Connected:

* GitHub Repository

Configured:

* Branch: main
* Main file: app.py

Added secret:

```toml
GROQ_API_KEY
```

Deployment completed successfully.

---

# 26. Testing

## Test Case 1 – Semantic Retrieval

Question:

```text
Who scored highest?
```

Expected Output:

```text
Riya scored the highest with 95 marks.
```

Actual Output:

```text
Riya scored the highest with 95 marks.
```

Status:

✅ PASS

---

## Test Case 2 – Numerical Retrieval

Question:

```text
What marks did Aman score?
```

Expected Output:

```text
80
```

Actual Output:

```text
80
```

Status:

✅ PASS

---

## Test Case 3 – Chapter Retrieval

Question:

```text
Chapter 5
```

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

```text
What is the capital of France?
```

Expected Output:

```text
I could not find that information in the PDF.
```

Actual Output:

```text
I could not find that information in the PDF.
```

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

## AI & Machine Learning

* Embeddings
* Semantic Search
* Vector Databases
* Retrieval-Augmented Generation (RAG)
* Prompt Engineering

## Backend Development

* PDF Parsing
* Text Processing
* Session State Management

## Databases

* ChromaDB
* Vector Storage

## LLM Integration

* Groq API
* Llama 3.3 70B Versatile

## Deployment

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
