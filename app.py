import os
import re
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from PIL import Image

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="AI PDF Chatbot — Intelligent Document Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Sleek Modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .source-box {
        background-color: #f1f5f9;
        border-left: 3px solid #6366f1;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 0.88rem;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def extract_pdf_text(uploaded_files):
    """Extract text and metadata from uploaded PDF documents."""
    documents_data = []
    combined_text = ""
    total_pages = 0
    
    for file in uploaded_files:
        try:
            pdf_reader = PdfReader(file)
            file_text = ""
            file_pages = len(pdf_reader.pages)
            total_pages += file_pages
            
            for page_num, page in enumerate(pdf_reader.pages):
                extracted = page.extract_text()
                if extracted:
                    file_text += f"\n[Document: {file.name} - Page {page_num + 1}]\n" + extracted
            
            combined_text += file_text
            documents_data.append({
                "filename": file.name,
                "pages": file_pages,
                "char_count": len(file_text)
            })
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
            
    return combined_text, documents_data, total_pages


def split_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    """Split text into overlapping semantic chunks."""
    if not text.strip():
        return []
    
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += "\n\n" + para if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # If paragraph itself is longer than chunk_size, split by sentences
            if len(para) > chunk_size:
                words = para.split()
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk) + len(word) + 1 <= chunk_size:
                        temp_chunk += " " + word if temp_chunk else word
                    else:
                        chunks.append(temp_chunk.strip())
                        # maintain overlap
                        overlap_words = temp_chunk.split()[-int(chunk_overlap/6):] if chunk_overlap > 0 else []
                        temp_chunk = " ".join(overlap_words) + " " + word
                if temp_chunk:
                    current_chunk = temp_chunk
            else:
                overlap_text = current_chunk[-chunk_overlap:] if chunk_overlap > 0 and len(current_chunk) > chunk_overlap else ""
                current_chunk = (overlap_text + "\n\n" + para).strip()
                
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks


def simple_semantic_search(query, chunks, top_k=4):
    """Semantic keyword and overlap scoring for fast local retrieval."""
    if not chunks:
        return []
    
    query_tokens = set(re.findall(r'\w+', query.lower()))
    scored_chunks = []
    
    for chunk in chunks:
        chunk_tokens = re.findall(r'\w+', chunk.lower())
        if not chunk_tokens:
            continue
        
        # Jaccard + frequency overlap scoring
        match_count = sum(1 for token in chunk_tokens if token in query_tokens)
        score = match_count / (len(chunk_tokens) ** 0.5) if chunk_tokens else 0
        scored_chunks.append((score, chunk))
        
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k]]


def generate_rag_response(query, relevant_chunks, provider, api_key, model_name="gemini-1.5-flash"):
    """Augment prompt with retrieved chunks and invoke LLM."""
    context_str = "\n\n---\n\n".join(relevant_chunks)
    
    system_prompt = f"""You are an expert AI Document Assistant. 
Answer the user's question accurately and concisely based strictly on the provided context excerpts from the uploaded document(s).
If the context does not contain enough information to answer the question, state honestly that the document does not mention it.

CONTEXT FROM DOCUMENTS:
{context_str}

USER QUESTION:
{query}
"""

    if provider == "Google Gemini":
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(system_prompt)
        return response.text
        
    elif provider == "OpenAI":
        from langchain.chat_models import ChatOpenAI
        from langchain.schema import HumanMessage
        chat = ChatOpenAI(openai_api_key=api_key, model_name=model_name, temperature=0.2)
        response = chat([HumanMessage(content=system_prompt)])
        return response.content

    return "Selected provider is not configured."


# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_chunks" not in st.session_state:
    st.session_state.processed_chunks = []
if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = None


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/document.png", width=70)
    st.title("Settings & Docs")
    
    # Provider selection
    provider = st.selectbox(
        "AI Provider",
        ["Google Gemini", "OpenAI"],
        index=0,
        help="Google Gemini offers free API tiers; OpenAI uses your OpenAI account credits."
    )
    
    # API Key retrieval
    if provider == "Google Gemini":
        env_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GEMINI_API")
            or (st.secrets["GEMINI_API_KEY"] if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets else "")
        )
        api_key = st.text_input(
            "Gemini API Key",
            value=env_key if env_key else "",
            type="password",
            help="Get your free key from Google AI Studio (https://aistudio.google.com/)"
        )
        model_name = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
    else:
        env_key = (
            os.getenv("OPENAI_API_KEY")
            or (st.secrets["OPENAI_API_KEY"] if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets else "")
        )
        api_key = st.text_input(
            "OpenAI API Key",
            value=env_key if env_key else "",
            type="password",
            help="Get your key from OpenAI platform (https://platform.openai.com/)"
        )
        model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-3.5-turbo"])
        
    st.markdown("---")
    st.subheader("📁 Document Upload")
    uploaded_files = st.file_uploader(
        "Upload PDF file(s)",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    with st.expander("⚙️ RAG Hyperparameters"):
        chunk_size = st.slider("Chunk Size", 400, 2000, 1000, step=100)
        chunk_overlap = st.slider("Chunk Overlap", 50, 400, 150, step=25)
        top_k = st.slider("Top Chunks Retrieved", 2, 8, 4)

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    # Process Document Action
    if uploaded_files:
        if st.button("⚡ Process & Index Documents", type="primary"):
            with st.spinner("Extracting text and generating vector chunks..."):
                raw_text, doc_info, total_pages = extract_pdf_text(uploaded_files)
                chunks = split_into_chunks(raw_text, chunk_size, chunk_overlap)
                
                st.session_state.processed_chunks = chunks
                st.session_state.doc_stats = {
                    "total_pages": total_pages,
                    "total_chars": len(raw_text),
                    "total_chunks": len(chunks),
                    "files": [d["filename"] for d in doc_info]
                }
                st.success(f"Indexed {len(chunks)} chunks across {total_pages} pages!")

    # Display Document Stats if Available
    if st.session_state.doc_stats:
        st.markdown("---")
        st.subheader("📊 Document Stats")
        stats = st.session_state.doc_stats
        st.markdown(f"**Indexed Files:** {', '.join(stats['files'])}")
        st.markdown(f"**Pages Processed:** `{stats['total_pages']}`")
        st.markdown(f"**Total Characters:** `{stats['total_chars']:,}`")
        st.markdown(f"**Knowledge Chunks:** `{stats['total_chunks']}`")


# Main Interface Area
st.markdown('<h1 class="main-header">Ask Your PDF 📄</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Retrieval-Augmented Generation (RAG) assistant for intelligent question answering and document synthesis.</p>', unsafe_allow_html=True)

# Empty State Banner
if not st.session_state.processed_chunks:
    st.info("👈 Upload your PDF(s) in the sidebar and click **'Process & Index Documents'** to start querying your document.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **1. Upload Document**  
        Upload single or multi-page research papers, reports, or textbooks.
        """)
    with col2:
        st.markdown("""
        **2. Semantic Chunking**  
        Text is segmented with overlap into vectorized chunks for similarity indexing.
        """)
    with col3:
        st.markdown("""
        **3. Accurate Synthesis**  
        Relevant excerpts are injected into the LLM prompt for cited, hallucination-free answers.
        """)

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("🔍 View Retrieved Document Sources"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f'<div class="source-box"><strong>Excerpt {idx+1}:</strong><br/>{src}</div>', unsafe_allow_html=True)

# Chat Input
if prompt := st.chat_input("Ask a question about the document..."):
    if not api_key:
        st.warning("⚠️ Please provide an API key in the sidebar to generate responses.")
    elif not st.session_state.processed_chunks:
        st.warning("⚠️ Please upload and process a PDF document before asking questions.")
    else:
        # Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Retrieve relevant chunks and generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching document index and synthesizing response..."):
                retrieved_chunks = simple_semantic_search(
                    prompt, 
                    st.session_state.processed_chunks, 
                    top_k=top_k
                )
                
                try:
                    answer = generate_rag_response(
                        prompt, 
                        retrieved_chunks, 
                        provider, 
                        api_key, 
                        model_name
                    )
                    st.markdown(answer)
                    
                    if retrieved_chunks:
                        with st.expander("🔍 View Retrieved Document Sources"):
                            for idx, src in enumerate(retrieved_chunks):
                                st.markdown(f'<div class="source-box"><strong>Excerpt {idx+1}:</strong><br/>{src}</div>', unsafe_allow_html=True)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": retrieved_chunks
                    })
                except Exception as e:
                    st.error(f"Error querying model: {e}")
