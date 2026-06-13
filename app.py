import streamlit as st
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

# ==================================================
# Page Config
# ==================================================

st.set_page_config(
    page_title="PDF Chat Agent",
    page_icon="📄"
)

st.title("📄 PDF Chat Agent")

# ==================================================
# Groq Client
# ==================================================

client_groq = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# ==================================================
# Cached Resources
# ==================================================

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


@st.cache_resource
def get_chroma_client():
    return chromadb.Client()


embedding_model = load_embedding_model()
chroma_client = get_chroma_client()

# ==================================================
# Upload PDF
# ==================================================

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file:

    reader = PdfReader(uploaded_file)

    full_text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            full_text += page_text + "\n"

    st.success("PDF Loaded Successfully ✅")

    collection_name = (
        uploaded_file.name
        .replace(".pdf", "")
        .replace(" ", "_")
        .lower()
    )

    # ==================================================
    # Process PDF Only Once
    # ==================================================

    if (
        "current_pdf" not in st.session_state
        or st.session_state.current_pdf != collection_name
    ):

        st.session_state.current_pdf = collection_name

        chunk_size = 800
        overlap = 150

        chunks = []

        for i in range(
            0,
            len(full_text),
            chunk_size - overlap
        ):
            chunk = full_text[i:i + chunk_size]

            if chunk.strip():
                chunks.append(chunk)

        with st.spinner(
            "Creating embeddings..."
        ):

            embeddings = embedding_model.encode(
                chunks,
                batch_size=32,
                show_progress_bar=True
            ).tolist()

        try:
            chroma_client.delete_collection(
                collection_name
            )
        except:
            pass

        collection = chroma_client.create_collection(
            name=collection_name
        )

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[
                str(i)
                for i in range(len(chunks))
            ]
        )

    # ==================================================
    # Ask Question
    # ==================================================

    question = st.text_input(
        "Ask a question about the PDF"
    )

    if question:

        collection = chroma_client.get_collection(
            collection_name
        )

        query_embedding = embedding_model.encode(
            [question]
        ).tolist()[0]

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=5
        )

        retrieved_chunks = results["documents"][0]

        context = "\n\n".join(
            retrieved_chunks
        )

        with st.expander(
            "Retrieved Context"
        ):
            st.write(context)

        prompt = f"""
You are a PDF Question Answering Assistant.

Answer ONLY using the information found inside the provided context.

If the answer is not explicitly present in the context, respond EXACTLY with:

I could not find that information in the PDF.

Rules:
- Never make up information.
- Never use outside knowledge.
- If names, numbers, marks, code, examples, chapters, or definitions exist in the context, answer directly.
- Preserve code formatting.
- Use markdown code blocks when showing code.

Context:
{context}

Question:
{question}

Answer:
"""

        with st.spinner(
            "Generating answer..."
        ):

            response = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        st.subheader("Answer")
        st.markdown(answer)