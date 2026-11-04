import os
import re
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from PIL import Image

# Load environment variables
load_dotenv()

# Page Configuration — Enterprise Grade
st.set_page_config(
    page_title="PaperMind AI · Enterprise Document Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End SaaS Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Palette */
    html, body, [class*="css"], .stMarkdown, .stText {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        letter-spacing: -0.012em;
    }

    code, pre, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Backgrounds & Surface Elevation */
    .stApp {
        background-color: #080B11 !important;
        color: #F8FAFC !important;
    }

    [data-testid="stSidebar"] {
        background-color: #0D121D !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Brand Header Component */
    .hero-container {
        padding: 24px 0 16px 0;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        flex-wrap: wrap;
        gap: 16px;
    }

    .hero-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .hero-logo-box {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, rgba(0, 229, 153, 0.16) 0%, rgba(99, 102, 241, 0.2) 100%);
        border: 1px solid rgba(0, 229, 153, 0.35);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #00E599;
        box-shadow: 0 4px 16px rgba(0, 229, 153, 0.18);
    }

    .hero-title {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #F8FAFC !important;
        margin: 0 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.03em !important;
    }

    .hero-subtitle {
        font-size: 0.92rem !important;
        color: #94A3B8 !important;
        margin: 4px 0 0 0 !important;
        line-height: 1.5 !important;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 229, 153, 0.08);
        border: 1px solid rgba(0, 229, 153, 0.25);
        color: #00E599;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        padding: 6px 14px;
        border-radius: 9999px;
        font-variant-numeric: tabular-nums;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #00E599;
        box-shadow: 0 0 8px #00E599;
        animation: pulseDot 2s infinite ease-in-out;
    }

    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.85); }
    }

    /* Telemetry KPI Cards */
    .telemetry-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
        margin: 16px 0;
    }

    .telemetry-card {
        background-color: #121824;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 12px 14px;
        display: flex;
        flex-direction: column;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }

    .telemetry-card:hover {
        border-color: rgba(0, 229, 153, 0.3);
        transform: translateY(-1px);
    }

    .telemetry-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 4px;
    }

    .telemetry-value {
        font-size: 1.35rem;
        font-weight: 800;
        color: #F8FAFC;
        font-variant-numeric: tabular-nums;
        line-height: 1.1;
    }

    /* Citation Card Component */
    .citation-card {
        background-color: #0E1420;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        font-size: 0.88rem;
        line-height: 1.6;
        color: #CBD5E1;
        transition: all 0.15s ease;
    }

    .citation-card:hover {
        border-color: rgba(0, 229, 153, 0.35);
        background-color: #121A2A;
    }

    .citation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .citation-tag {
        font-size: 0.75rem;
        font-weight: 700;
        color: #00E599;
        letter-spacing: 0.02em;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .citation-meta {
        font-size: 0.74rem;
        color: #64748B;
        font-variant-numeric: tabular-nums;
    }

    /* Pipeline Architecture Step Cards */
    .pipeline-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 16px;
        margin: 20px 0 32px 0;
    }

    .pipeline-card {
        background-color: #0F1522;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px 20px;
        display: flex;
        flex-direction: column;
        transition: all 0.25s ease;
    }

    .pipeline-card:hover {
        border-color: rgba(0, 229, 153, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.4);
    }

    .pipeline-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #00E599;
        margin-bottom: 14px;
    }

    .pipeline-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 8px;
    }

    .pipeline-desc {
        font-size: 0.88rem;
        color: #94A3B8;
        line-height: 1.55;
        margin: 0;
    }

    /* Custom Streamlit Component Styling Overrides */
    .stButton>button {
        background-color: #141C2E !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 9999px !important;
        padding: 8px 18px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stButton>button:hover {
        background-color: #1C273E !important;
        border-color: #00E599 !important;
        color: #00E599 !important;
        transform: translateY(-1px) !important;
    }

    .stButton>button[kind="primary"] {
        background-color: #00E599 !important;
        color: #080B11 !important;
        border: 1px solid #00E599 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(0, 229, 153, 0.25) !important;
    }

    .stButton>button[kind="primary"]:hover {
        background-color: #00C882 !important;
        color: #080B11 !important;
        border-color: #00C882 !important;
        box-shadow: 0 6px 20px rgba(0, 229, 153, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* Input Fields */
    .stTextInput>div>div>input {
        background-color: #0A0F18 !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        font-size: 0.92rem !important;
        padding: 10px 14px !important;
    }

    .stTextInput>div>div>input:focus {
        border-color: #00E599 !important;
        box-shadow: 0 0 0 2px rgba(0, 229, 153, 0.2) !important;
    }

    /* File Uploader Container */
    [data-testid="stFileUploader"] {
        background-color: #0B101A !important;
        border: 1px dashed rgba(255, 255, 255, 0.14) !important;
        border-radius: 16px !important;
        padding: 14px !important;
        transition: border-color 0.2s ease !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(0, 229, 153, 0.4) !important;
    }

    /* Chat Input Bar */
    [data-testid="stChatInput"] {
        background-color: #0C111C !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 9999px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5) !important;
    }

    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background-color: #0F1522 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
    }

    [data-testid="stExpander"] {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# Helper Functions — Robust Ingestion & Local Semantic Search
# ==============================================================================
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
            
            if len(para) > chunk_size:
                words = para.split()
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk) + len(word) + 1 <= chunk_size:
                        temp_chunk += " " + word if temp_chunk else word
                    else:
                        chunks.append(temp_chunk.strip())
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
    """Fast semantic token and term-density scoring for contextual retrieval."""
    if not chunks:
        return []
    
    query_tokens = set(re.findall(r'\w+', query.lower()))
    scored_chunks = []
    
    for chunk in chunks:
        chunk_tokens = re.findall(r'\w+', chunk.lower())
        if not chunk_tokens:
            continue
        
        match_count = sum(1 for token in chunk_tokens if token in query_tokens)
        score = match_count / (len(chunk_tokens) ** 0.5) if chunk_tokens else 0
        scored_chunks.append((score, chunk))
        
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k]]


def generate_rag_response(query, relevant_chunks, provider, api_key, model_name="gemini-1.5-flash"):
    """Augment prompt with retrieved chunks and invoke LLM."""
    context_str = "\n\n---\n\n".join(relevant_chunks)
    
    system_prompt = f"""You are PaperMind, an enterprise document intelligence and research assistant.
Answer the user's question accurately, deeply, and concisely based strictly on the provided context excerpts from the uploaded document(s).

Guidelines:
1. Ground every claim directly in the context.
2. If the context does not contain sufficient details to answer, clearly and honestly state that the uploaded documents do not address it.
3. Organize structured findings with clear bullet points, bold headers, and exact citations where applicable.

DOCUMENT CONTEXT:
{context_str}

USER INQUIRY:
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


# ==============================================================================
# Session State Initialization
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_chunks" not in st.session_state:
    st.session_state.processed_chunks = []
if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = None
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# ==============================================================================
# Sidebar — Control Center & Document Telemetry
# ==============================================================================
with st.sidebar:
    # Sidebar Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
        <div style="width: 36px; height: 36px; border-radius: 10px; background: rgba(0, 229, 153, 0.15); border: 1px solid rgba(0, 229, 153, 0.3); display: flex; align-items: center; justify-content: center; color: #00E599;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
        </div>
        <div>
            <h4 style="margin: 0; font-weight: 800; font-size: 1.1rem; color: #F8FAFC;">Control Center</h4>
            <small style="color: #64748B;">Neural Ingestion & RAG Tuning</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Provider & Model Settings
    provider = st.selectbox(
        "Neural Engine Provider",
        ["Google Gemini", "OpenAI"],
        index=0,
        help="Google Gemini includes a generous free tier via AI Studio. OpenAI uses your platform credits."
    )
    
    if provider == "Google Gemini":
        env_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GEMINI_API")
            or (st.secrets["GEMINI_API_KEY"] if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets else "")
        )
        api_key = st.text_input(
            "Gemini Studio API Key",
            value=env_key if env_key else "",
            type="password",
            help="Acquire your API key from Google AI Studio (https://aistudio.google.com/)"
        )
        model_name = st.selectbox("Model Architecture", ["gemini-1.5-flash", "gemini-1.5-pro"])
    else:
        env_key = (
            os.getenv("OPENAI_API_KEY")
            or (st.secrets["OPENAI_API_KEY"] if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets else "")
        )
        api_key = st.text_input(
            "OpenAI API Key",
            value=env_key if env_key else "",
            type="password",
            help="Obtain your API key from https://platform.openai.com/"
        )
        model_name = st.selectbox("Model Architecture", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
        
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Document Upload Section
    st.markdown("<h5 style='margin: 0 0 10px 0; font-weight: 700; color: #F8FAFC; font-size: 0.95rem;'>Source Documents</h5>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    # Process Trigger
    if uploaded_files:
        if st.button("Index Knowledge Base", type="primary", use_container_width=True):
            with st.spinner("Partitioning vector chunks & parsing layout..."):
                raw_text, doc_info, total_pages = extract_pdf_text(uploaded_files)
                chunks = split_into_chunks(raw_text, 1000, 150)
                
                st.session_state.processed_chunks = chunks
                st.session_state.doc_stats = {
                    "total_pages": total_pages,
                    "total_chars": len(raw_text),
                    "total_chunks": len(chunks),
                    "files": [d["filename"] for d in doc_info]
                }
                st.rerun()

    # Document Telemetry Bar
    if st.session_state.doc_stats:
        stats = st.session_state.doc_stats
        st.markdown(f"""
        <div class="telemetry-grid">
            <div class="telemetry-card">
                <span class="telemetry-label">Pages</span>
                <span class="telemetry-value">{stats['total_pages']}</span>
            </div>
            <div class="telemetry-card">
                <span class="telemetry-label">Chunks</span>
                <span class="telemetry-value">{stats['total_chunks']}</span>
            </div>
            <div class="telemetry-card">
                <span class="telemetry-label">Characters</span>
                <span class="telemetry-value">{stats['total_chars']:,}</span>
            </div>
        </div>
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 12px; margin-top: 8px;">
            <small style="color: #94A3B8; font-size: 0.78rem;">Active Files: <strong style="color: #F8FAFC;">{', '.join(stats['files'])}</strong></small>
        </div>
        """, unsafe_allow_html=True)

    # RAG Hyperparameters Accordion
    with st.expander("RAG Partitioning Parameters"):
        chunk_size = st.slider("Chunk Size (Characters)", 400, 2000, 1000, step=100)
        chunk_overlap = st.slider("Chunk Overlap (Characters)", 50, 400, 150, step=25)
        top_k = st.slider("Top Chunks Retrieved", 2, 8, 4)
    if "top_k" not in locals():
        top_k = 4

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 20px 0;'>", unsafe_allow_html=True)

    # Session Management Actions
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_s2:
        if st.button("Reset All", use_container_width=True):
            st.session_state.messages = []
            st.session_state.processed_chunks = []
            st.session_state.doc_stats = None
            st.rerun()


# ==============================================================================
# Main Interface Surface
# ==============================================================================
has_documents = bool(st.session_state.processed_chunks)
status_label = f"{len(st.session_state.processed_chunks)} Chunks Indexed" if has_documents else "Engine Standby"

st.markdown(f"""
<div class="hero-container">
    <div class="hero-brand">
        <div class="hero-logo-box">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                <polyline points="2 17 12 22 22 17"></polyline>
                <polyline points="2 12 12 17 22 12"></polyline>
            </svg>
        </div>
        <div>
            <h1 class="hero-title">PaperMind<span style="color: #00E599;">.</span></h1>
            <p class="hero-subtitle">High-precision Retrieval-Augmented Generation for complex technical and enterprise documents.</p>
        </div>
    </div>
    <div class="status-pill">
        <div class="status-dot"></div>
        <span>{status_label}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# Empty State: Pipeline Blueprint Canvas
# ==============================================================================
if not has_documents:
    st.markdown("""
    <div class="pipeline-container">
        <div class="pipeline-card">
            <div class="pipeline-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
            </div>
            <div class="pipeline-title">1. Neural Ingestion</div>
            <p class="pipeline-desc">Upload research papers, quarterly financial disclosures, or technical manuals. Text and structure are parsed accurately.</p>
        </div>
        <div class="pipeline-card">
            <div class="pipeline-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
                    <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
                    <line x1="6" y1="6" x2="6.01" y2="6"></line>
                    <line x1="6" y1="18" x2="6.01" y2="18"></line>
                </svg>
            </div>
            <div class="pipeline-title">2. Semantic Partitioning</div>
            <p class="pipeline-desc">Documents are segmented into overlapping vector chunks, preventing context boundary loss and preserving continuity.</p>
        </div>
        <div class="pipeline-card">
            <div class="pipeline-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 14 14"></polyline>
                </svg>
            </div>
            <div class="pipeline-title">3. Verified Synthesis</div>
            <p class="pipeline-desc">Relevant excerpts are retrieved and injected into the prompt, guaranteeing factual, cited answers with zero hallucinations.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Upload one or more PDF files in the sidebar and click 'Index Knowledge Base' to launch your query session.")
else:
    # Quick Starter Prompt Pills
    st.markdown("<p style='font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94A3B8; margin-bottom: 8px;'>Suggested Inquiries</p>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        if st.button("Summarize Key Findings", use_container_width=True):
            st.session_state.pending_prompt = "Provide an executive summary of the key findings, arguments, and conclusions in this document."
            st.rerun()
    with p_col2:
        if st.button("Extract Data & Metrics", use_container_width=True):
            st.session_state.pending_prompt = "Extract all key metrics, quantitative statistics, and experimental figures mentioned in the document."
            st.rerun()
    with p_col3:
        if st.button("List Actionable Items", use_container_width=True):
            st.session_state.pending_prompt = "Identify the main recommendations, next steps, and actionable items described in the document."
            st.rerun()
    with p_col4:
        if st.button("Identify Risk Factors", use_container_width=True):
            st.session_state.pending_prompt = "What are the primary limitations, risks, or potential caveats highlighted by the authors?"
            st.rerun()


# ==============================================================================
# Chat Conversation Stream
# ==============================================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander(f"Verifiable Document Citations ({len(message['sources'])} Sources)"):
                for idx, src in enumerate(message["sources"]):
                    # Extract document name and page if available
                    match = re.search(r'\[Document: (.*?) - Page (\d+)\]', src)
                    doc_label = match.group(1) if match else "Document"
                    page_label = f"Page {match.group(2)}" if match else f"Chunk #{idx+1}"
                    clean_content = re.sub(r'\[Document: .*? - Page \d+\]\n?', '', src).strip()
                    
                    st.markdown(f"""
                    <div class="citation-card">
                        <div class="citation-header">
                            <span class="citation-tag">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                    <polyline points="20 6 9 17 4 12"></polyline>
                                </svg>
                                {doc_label}
                            </span>
                            <span class="citation-meta">{page_label}</span>
                        </div>
                        <div style="font-size: 0.86rem; color: #94A3B8;">{clean_content}</div>
                    </div>
                    """, unsafe_allow_html=True)


# ==============================================================================
# Query Input & Retrieval Execution
# ==============================================================================
user_query = st.chat_input("Query your document knowledge base...")

# Check for pending clicked quick prompt
if st.session_state.pending_prompt:
    user_query = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if user_query:
    if not api_key:
        st.warning("Please supply an API key in the sidebar Control Center to generate grounded responses.")
    elif not has_documents:
        st.warning("Please upload and index a PDF document before issuing inquiries.")
    else:
        # Append & display User Message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Retrieve relevant chunks & synthesize
        with st.chat_message("assistant"):
            with st.spinner("Executing semantic similarity scan & generating grounded synthesis..."):
                retrieved_chunks = simple_semantic_search(
                    user_query, 
                    st.session_state.processed_chunks, 
                    top_k=top_k
                )
                
                try:
                    answer = generate_rag_response(
                        user_query, 
                        retrieved_chunks, 
                        provider, 
                        api_key, 
                        model_name
                    )
                    st.markdown(answer)
                    
                    if retrieved_chunks:
                        with st.expander(f"Verifiable Document Citations ({len(retrieved_chunks)} Sources)"):
                            for idx, src in enumerate(retrieved_chunks):
                                match = re.search(r'\[Document: (.*?) - Page (\d+)\]', src)
                                doc_label = match.group(1) if match else "Document"
                                page_label = f"Page {match.group(2)}" if match else f"Chunk #{idx+1}"
                                clean_content = re.sub(r'\[Document: .*? - Page \d+\]\n?', '', src).strip()
                                
                                st.markdown(f"""
                                <div class="citation-card">
                                    <div class="citation-header">
                                        <span class="citation-tag">
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                                <polyline points="20 6 9 17 4 12"></polyline>
                                            </svg>
                                            {doc_label}
                                        </span>
                                        <span class="citation-meta">{page_label}</span>
                                    </div>
                                    <div style="font-size: 0.86rem; color: #94A3B8;">{clean_content}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": retrieved_chunks
                    })
                except Exception as e:
                    st.error(f"Inference error encountered: {e}")
