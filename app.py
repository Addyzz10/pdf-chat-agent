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
# Session State
# ==================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


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

    # ==============================================
    # Extract PDF Text
    # ==============================================

    reader = PdfReader(uploaded_file)

    full_text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            full_text += page_text + "\n"

    if not full_text.strip():

        st.error(
            "No readable text found in PDF."
        )

        st.stop()

    st.success(
        "PDF Loaded Successfully ✅"
    )

    collection_name = (
        uploaded_file.name
        .replace(".pdf", "")
        .replace(" ", "_")
        .lower()
    )

    # ==============================================
    # Process PDF Only Once
    # ==============================================

    if (
        "current_pdf" not in st.session_state
        or st.session_state.current_pdf != collection_name
    ):

        st.session_state.current_pdf = (
            collection_name
        )

        # ------------------------------------------
        # Better Chunking (Paragraph Based)
        # ------------------------------------------

        paragraphs = full_text.split("\n\n")

        chunks = []
        current_chunk = ""

        for para in paragraphs:

            para = para.strip()

            if not para:
                continue

            if (
                len(current_chunk)
                + len(para)
                < 800
            ):

                current_chunk += (
                    "\n\n" + para
                )

            else:

                chunks.append(
                    current_chunk.strip()
                )

                current_chunk = para

        if current_chunk:
            chunks.append(
                current_chunk.strip()
            )

        # ------------------------------------------
        # Create Embeddings
        # ------------------------------------------

        with st.spinner(
            "Creating embeddings..."
        ):

            embeddings = (
                embedding_model.encode(
                    chunks,
                    batch_size=32,
                    show_progress_bar=True
                ).tolist()
            )

        try:

            chroma_client.delete_collection(
                collection_name
            )

        except:
            pass

        collection = (
            chroma_client.create_collection(
                name=collection_name,
                metadata={
                    "hnsw:space": "cosine"
                }
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

    # ==============================================
    # Question Form
    # ==============================================

    with st.form(
        "question_form",
        clear_on_submit=False
    ):

        question = st.text_input(
            "Ask a question about the PDF"
        )

        ask_button = st.form_submit_button(
            "Ask"
        )

    # ==============================================
    # Run Query Only After Button Click
    # ==============================================

    if ask_button and question:

        collection = (
            chroma_client.get_collection(
                collection_name
            )
        )

        query_embedding = (
            embedding_model.encode(
                [question]
            ).tolist()[0]
        )

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=5
        )

        retrieved_chunks = (
            results["documents"][0]
        )

        context = "\n\n".join(
            retrieved_chunks
        )

        # ==========================================
        # Show Retrieved Chunks
        # ==========================================

        with st.expander(
            "Retrieved Chunks"
        ):

            for index, chunk in enumerate(
                retrieved_chunks,
                start=1
            ):

                st.markdown(
                    f"### Chunk {index}"
                )

                st.write(chunk)

                st.divider()

        # ==========================================
        # Prompt
        # ==========================================

        prompt = f"""
You are a PDF Question Answering Assistant.

Use ONLY the provided context.

RULES:

1. If the user asks a factual question
(names, marks, values, topper, definitions),
return ONLY the direct answer.

Examples:

Question: What marks did Aman score?
Answer: 80

Question: Who scored highest?
Answer: Riya scored the highest with 95 marks.

2. If the user asks for a chapter,
topic, notes, explanation, summary,
exercise, or examples:

- Return the complete information.
- Use markdown headings.
- Preserve formatting.
- Preserve code blocks.
- Do not compress everything into one paragraph.

3. Preserve code exactly.

4. Use markdown code blocks
for code snippets.

5. If the answer is not present
in the context, reply exactly:

I could not find that information in the PDF.

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

            response = (
                client_groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0
                )
            )

        answer = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        # ==========================================
        # Save History
        # ==========================================

        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": (
                    answer[:150] + "..."
                    if len(answer) > 150
                    else answer
                )
            }
        )

        st.session_state.chat_history = (
            st.session_state.chat_history[-10:]
        )

        # ==========================================
        # Display Answer
        # ==========================================

        st.subheader("Answer")

        st.markdown(answer)

    # ==============================================
    # Chat History
    # ==============================================

    if st.session_state.chat_history:

        st.subheader(
            "Chat History"
        )

        for item in reversed(
            st.session_state.chat_history
        ):

            st.markdown(
                f"**Q:** {item['question']}"
            )

            st.markdown(
                f"**A:** {item['answer']}"
            )

            st.divider()