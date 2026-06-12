import streamlit as st
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import ollama

st.set_page_config(
    page_title="PDF Chat Agent",
    page_icon="📄"
)

st.title("PDF Chat Agent")


# ==========================================
# Cached Resources
# ==========================================

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


@st.cache_resource
def get_chroma_client():
    return chromadb.PersistentClient(
        path="./chroma_db"
    )


model = load_embedding_model()
client = get_chroma_client()


# ==========================================
# Upload PDF
# ==========================================

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file:

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    st.success("PDF Loaded")

    # ==========================================
    # Collection Name
    # ==========================================

    collection_name = (
        uploaded_file.name
        .replace(".pdf", "")
        .replace(" ", "_")
        .lower()
    )

    # ==========================================
    # Process PDF Only Once
    # ==========================================

    if (
        "current_pdf" not in st.session_state
        or st.session_state.current_pdf
        != collection_name
    ):

        st.session_state.current_pdf = (
            collection_name
        )

        # ==========================================
        # Chunking
        # ==========================================

        chunk_size = 1000
        overlap = 200

        chunks = []

        for i in range(
            0,
            len(text),
            chunk_size - overlap
        ):

            chunks.append(
                text[i:i + chunk_size]
            )

        # ==========================================
        # Embeddings
        # ==========================================

        with st.spinner(
            "Creating embeddings..."
        ):

            embeddings = model.encode(
                chunks,
                show_progress_bar=True,
                batch_size=32
            ).tolist()

        # ==========================================
        # Create Collection
        # ==========================================

        try:

            client.delete_collection(
                collection_name
            )

        except:
            pass

        collection = (
            client.create_collection(
                name=collection_name
            )
        )

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[
                str(i)
                for i in range(
                    len(chunks)
                )
            ]
        )

    # ==========================================
    # Ask Question
    # ==========================================

    question = st.text_input(
        "Ask a question"
    )

    if question:

        collection = client.get_collection(
            collection_name
        )

        query_embedding = (
            model.encode(
                [question]
            )
            .tolist()[0]
        )

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=5
        )

        context = "\n\n".join(
            results["documents"][0]
        )

        # ==========================================
        # Debug Retrieved Context
        # ==========================================

        with st.expander(
            "Retrieved Context"
        ):
            st.write(context)

        # ==========================================
        # Prompt
        # ==========================================

        prompt = f"""
You are a PDF assistant.

Answer ONLY using the provided context.

If the answer is not present in the context, reply exactly:

"I could not find that information in the PDF."

Rules:
1. Preserve code formatting.
2. Preserve line breaks.
3. Preserve examples exactly as shown.
4. Use markdown code blocks for code.
5. Do not summarize examples.

Context:
{context}

Question:
{question}

Answer:
"""

        # ==========================================
        # Generate Answer
        # ==========================================

        with st.spinner(
            "Generating answer..."
        ):

            response = ollama.chat(
                model="qwen2.5:1.5b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0,
                    "num_predict": 500
                }
            )

        st.subheader("Answer")

        st.markdown(
            response["message"]["content"]
        )