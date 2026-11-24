import os
import re
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader

load_dotenv()

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PaperMind · Document Intelligence",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📄</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Design System ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── App shell ── */
.stApp {
    background: #0a0a0f !important;
    color: #e2e8f0 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d0d14 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* ── Sidebar brand strip ── */
.sb-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 20px 20px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 4px;
}
.sb-logo {
    width: 32px; height: 32px;
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.sb-logo svg { display: block; }
.sb-name {
    font-size: 1rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.02em;
}
.sb-tagline {
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 1px;
}

/* ── Sidebar sections ── */
.sb-section {
    padding: 12px 16px 4px;
}
.sb-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #475569;
    margin-bottom: 8px;
}

/* ── Stat row ── */
.stat-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 10px 0 0;
}
.stat-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 12px;
}
.stat-num {
    font-size: 1.25rem;
    font-weight: 700;
    color: #f1f5f9;
    font-variant-numeric: tabular-nums;
    line-height: 1.1;
}
.stat-lbl {
    font-size: 0.69rem;
    color: #64748b;
    margin-top: 2px;
}
.stat-box.wide {
    grid-column: span 2;
}

/* ── Docs badge list ── */
.doc-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 10px;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 8px;
    margin-top: 6px;
    font-size: 0.8rem;
    color: #a5b4fc;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.doc-badge svg { flex-shrink: 0; }

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stSlider > div {
    background: #12121c !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.88rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}
[data-testid="stSelectbox"] > div {
    background: #12121c !important;
    border-color: rgba(255,255,255,0.08) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.015) !important;
    border: 1.5px dashed rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    padding: 12px !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(99,102,241,0.6) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: #cbd5e1 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 7px 14px !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.18) !important;
    color: #f1f5f9 !important;
}
.stButton > button[kind="primary"] {
    background: #6366f1 !important;
    color: #fff !important;
    border-color: #6366f1 !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #5457d4 !important;
    border-color: #5457d4 !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.45) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: #94a3b8 !important;
    font-size: 0.84rem !important;
}

/* ── Main layout ── */
.main-wrap {
    max-width: 820px;
    margin: 0 auto;
    padding: 0 24px 100px;
}

/* ── Top bar ── */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 0 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 24px;
}
.top-bar-left {
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.top-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.03em;
    margin: 0;
}
.top-sub {
    font-size: 0.84rem;
    color: #64748b;
    margin: 0;
}
.engine-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    border: 1px solid;
}
.engine-pill.active {
    background: rgba(34,197,94,0.08);
    border-color: rgba(34,197,94,0.25);
    color: #4ade80;
}
.engine-pill.idle {
    background: rgba(100,116,139,0.08);
    border-color: rgba(100,116,139,0.2);
    color: #64748b;
}
.pill-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
}
.pill-dot.active { background: #4ade80; box-shadow: 0 0 6px #4ade80; animation: blink 2s infinite; }
.pill-dot.idle   { background: #64748b; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.4} }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 64px 24px;
}
.empty-icon {
    width: 72px; height: 72px;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 20px;
    color: #818cf8;
}
.empty-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}
.empty-desc {
    font-size: 0.9rem;
    color: #64748b;
    max-width: 400px;
    margin: 0 auto 32px;
    line-height: 1.6;
}
.steps-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    max-width: 640px;
    margin: 0 auto;
}
.step-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 16px;
    text-align: left;
}
.step-num {
    font-size: 0.7rem;
    font-weight: 700;
    color: #6366f1;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.step-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 5px;
}
.step-desc {
    font-size: 0.8rem;
    color: #64748b;
    line-height: 1.5;
}

/* ── Chips ── */
.chips-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #475569;
    margin-bottom: 8px;
}

/* ── Chat messages ── */
.msg-wrap {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    align-items: flex-start;
}
.msg-avatar {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 0.8rem;
    font-weight: 700;
}
.msg-avatar.user {
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.25);
    color: #818cf8;
}
.msg-avatar.assistant {
    background: rgba(139,92,246,0.12);
    border: 1px solid rgba(139,92,246,0.22);
    color: #a78bfa;
}
.msg-body { flex: 1; min-width: 0; }
.msg-role {
    font-size: 0.74rem;
    font-weight: 600;
    color: #475569;
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.msg-bubble {
    font-size: 0.93rem;
    line-height: 1.65;
    color: #e2e8f0;
}
.msg-bubble.user-bubble {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 4px 14px 14px 14px;
    padding: 12px 16px;
}
.msg-bubble.assistant-bubble {
    background: transparent;
}

/* ── Citation cards ── */
.cite-wrap { margin-top: 12px; }
.cite-header {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #475569;
    margin-bottom: 7px;
}
.cite-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 11px 14px;
    margin-bottom: 7px;
    font-size: 0.82rem;
    line-height: 1.55;
    color: #94a3b8;
}
.cite-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}
.cite-fname {
    font-weight: 600;
    color: #818cf8;
    font-size: 0.78rem;
}
.cite-page {
    font-size: 0.72rem;
    color: #475569;
    font-variant-numeric: tabular-nums;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #12121c !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5) !important;
}
[data-testid="stChatInput"] textarea {
    color: #e2e8f0 !important;
    font-size: 0.93rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #475569 !important;
}

/* ── Streamlit default overrides ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
.stMarkdown p { color: #e2e8f0; line-height: 1.65; }
.stMarkdown code {
    background: rgba(99,102,241,0.12) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 5px !important;
    color: #a5b4fc !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.84em !important;
    padding: 1px 5px !important;
}
.stMarkdown pre {
    background: #0d0d14 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}
.stAlert {
    background: rgba(99,102,241,0.07) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important;
    color: #a5b4fc !important;
}
/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def extract_pdf_text(uploaded_files):
    documents_data, combined_text, total_pages = [], "", 0
    for file in uploaded_files:
        try:
            reader = PdfReader(file)
            file_text, file_pages = "", len(reader.pages)
            total_pages += file_pages
            for pnum, page in enumerate(reader.pages):
                txt = page.extract_text()
                if txt:
                    file_text += f"\n[Document: {file.name} - Page {pnum+1}]\n" + txt
            combined_text += file_text
            documents_data.append({"filename": file.name, "pages": file_pages, "char_count": len(file_text)})
        except Exception as e:
            st.error(f"Could not read {file.name}: {e}")
    return combined_text, documents_data, total_pages


def split_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    if not text.strip():
        return []
    paragraphs = re.split(r'\n\s*\n', text)
    chunks, current_chunk = [], ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += ("\n\n" + para) if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if len(para) > chunk_size:
                words, temp_chunk = para.split(), ""
                for word in words:
                    if len(temp_chunk) + len(word) + 1 <= chunk_size:
                        temp_chunk += (" " + word) if temp_chunk else word
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
    if not chunks:
        return []
    query_tokens = set(re.findall(r'\w+', query.lower()))
    scored = []
    for chunk in chunks:
        ctoks = re.findall(r'\w+', chunk.lower())
        if not ctoks:
            continue
        score = sum(1 for t in ctoks if t in query_tokens) / (len(ctoks) ** 0.5)
        scored.append((score, chunk))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for _, c in scored[:top_k]]


@st.cache_data(ttl=300, show_spinner=False)
def fetch_available_gemini_models(api_key):
    # Modern active models in Google Gemini API
    defaults = [
        "gemini-3-flash-preview",
        "gemini-flash-latest",
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-3.1-pro-preview",
        "gemini-pro-latest"
    ]
    if not api_key:
        return defaults
    try:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            models_data = res.json().get("models", [])
            deprecated_tags = ["1.5-flash", "1.5-pro", "gemini-pro", "2.5-flash", "2.5-flash-lite"]
            live = []
            for m in models_data:
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    name = m["name"].replace("models/", "")
                    if not any(d in name.lower() for d in deprecated_tags):
                        live.append(name)
            if live:
                flash = [m for m in live if "flash" in m.lower()]
                pro   = [m for m in live if "pro" in m.lower() and m not in flash]
                rest  = [m for m in live if m not in flash and m not in pro]
                return (flash + pro + rest)[:10]
    except Exception:
        pass
    return defaults


def generate_rag_response(query, chunks, provider, api_key, model_name="gemini-3-flash-preview"):
    context_str = "\n\n---\n\n".join(chunks)
    prompt = f"""You are PaperMind, a precise document intelligence assistant.
Answer the question below using ONLY the document context provided.
If the context doesn't contain the answer, say so clearly and briefly.
Format your answer with clean markdown — use bullet points, bold headings, and short paragraphs for readability.

DOCUMENT CONTEXT:
{context_str}

QUESTION:
{query}
"""
    if provider == "Google Gemini":
        import requests

        active_fallbacks = [
            "gemini-3-flash-preview",
            "gemini-flash-latest",
            "gemini-3.8-flash",
            "gemini-3.5-flash",
            "gemini-3.6-flash",
            "gemini-3.1-pro-preview",
            "gemini-pro-latest"
        ]
        candidates = [model_name] + [f for f in active_fallbacks if f != model_name]

        last_error = None
        for cand in candidates:
            cname = cand.replace("models/", "")
            for attempt in range(2):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{cname}:generateContent?key={api_key}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    res = requests.post(url, json=payload, timeout=25)
                    if res.status_code == 200:
                        data = res.json()
                        candidates_out = data.get("candidates", [])
                        if candidates_out:
                            parts = candidates_out[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "")
                    elif res.status_code in (404, 400):
                        last_error = Exception(f"HTTP {res.status_code}: {res.text}")
                        break
                    elif res.status_code in (503, 429):
                        last_error = Exception(f"HTTP {res.status_code}: {res.text}")
                        break
                    else:
                        last_error = Exception(f"Google API error {res.status_code}: {res.text}")
                except Exception as e:
                    last_error = e
                    continue

        if last_error:
            raise last_error
        return "Failed to retrieve inference from Gemini API."

    elif provider == "OpenAI":
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            chat = ChatOpenAI(openai_api_key=api_key, model_name=model_name, temperature=0.2)
            return chat([HumanMessage(content=prompt)]).content
        except ImportError:
            import requests
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            res = requests.post(url, headers=headers, json=payload, timeout=40)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            raise Exception(f"OpenAI API error {res.status_code}: {res.text}")

    return "Provider not configured."


def render_citation(src, idx):
    match = re.search(r'\[Document: (.*?) - Page (\d+)\]', src)
    fname  = match.group(1) if match else "Document"
    page   = f"Page {match.group(2)}" if match else f"Chunk #{idx+1}"
    body   = re.sub(r'\[Document: .*? - Page \d+\]\n?', '', src).strip()
    # Truncate long body
    preview = (body[:320] + "…") if len(body) > 320 else body
    st.markdown(f"""
<div class="cite-card">
  <div class="cite-card-top">
    <span class="cite-fname">{fname}</span>
    <span class="cite-page">{page}</span>
  </div>
  <div>{preview}</div>
</div>
""", unsafe_allow_html=True)


# ─── Session state ─────────────────────────────────────────────────────────────
for key, val in [("messages", []), ("chunks", []), ("doc_stats", None), ("pending", None)]:
    if key not in st.session_state:
        st.session_state[key] = val


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
<div class="sb-brand">
  <div class="sb-logo">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
  </div>
  <div>
    <div class="sb-name">PaperMind</div>
    <div class="sb-tagline">Document Intelligence</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Provider & model
    st.markdown('<div class="sb-section"><div class="sb-label">AI Model</div></div>', unsafe_allow_html=True)
    with st.container():
        provider = st.selectbox("Provider", ["Google Gemini", "OpenAI"], label_visibility="collapsed")

        if provider == "Google Gemini":
            env_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API")
                       or (st.secrets.get("GEMINI_API_KEY","") if hasattr(st,"secrets") else ""))
            api_key = st.text_input("Gemini API Key", value=env_key or "", type="password",
                                    placeholder="AIza…", label_visibility="collapsed")
            models  = fetch_available_gemini_models(api_key)
            model_name = st.selectbox("Model", models, label_visibility="collapsed")
        else:
            env_key = (os.getenv("OPENAI_API_KEY")
                       or (st.secrets.get("OPENAI_API_KEY","") if hasattr(st,"secrets") else ""))
            api_key = st.text_input("OpenAI API Key", value=env_key or "", type="password",
                                    placeholder="sk-…", label_visibility="collapsed")
            model_name = st.selectbox("Model", ["gpt-4o-mini","gpt-4o","gpt-3.5-turbo"], label_visibility="collapsed")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:14px 0;'>", unsafe_allow_html=True)

    # Document upload
    st.markdown('<div class="sb-section"><div class="sb-label">Documents</div></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")

    if uploaded:
        if st.button("Index Documents", type="primary", use_container_width=True):
            with st.spinner("Parsing & chunking…"):
                raw, doc_info, pages = extract_pdf_text(uploaded)
                chunks = split_into_chunks(raw, 1000, 150)
                st.session_state.chunks    = chunks
                st.session_state.doc_stats = {
                    "pages": pages, "chunks": len(chunks),
                    "chars": len(raw), "files": [d["filename"] for d in doc_info]
                }
                st.session_state.messages  = []
                st.rerun()

    # Stats
    if st.session_state.doc_stats:
        s = st.session_state.doc_stats
        st.markdown(f"""
<div class="stat-row" style="padding:0 16px;">
  <div class="stat-box"><div class="stat-num">{s['pages']}</div><div class="stat-lbl">Pages</div></div>
  <div class="stat-box"><div class="stat-num">{s['chunks']}</div><div class="stat-lbl">Chunks</div></div>
  <div class="stat-box wide"><div class="stat-num">{s['chars']:,}</div><div class="stat-lbl">Characters indexed</div></div>
</div>
""", unsafe_allow_html=True)
        st.markdown('<div style="padding:4px 16px 0;">', unsafe_allow_html=True)
        for f in s["files"]:
            short = (f[:36]+"…") if len(f) > 36 else f
            st.markdown(f"""
<div class="doc-badge">
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
  {short}
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:14px 0;'>", unsafe_allow_html=True)

    # RAG settings
    with st.expander("⚙️  Retrieval Settings"):
        chunk_size    = st.slider("Chunk size", 400, 2000, 1000, step=100)
        chunk_overlap = st.slider("Chunk overlap", 50, 400, 150, step=25)
        top_k         = st.slider("Top chunks (K)", 2, 10, 4)
    if "top_k" not in locals():
        top_k = 4

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:14px 0;'>", unsafe_allow_html=True)

    # Session controls
    cc1, cc2 = st.columns(2)
    with cc1:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with cc2:
        if st.button("Reset all", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chunks   = []
            st.session_state.doc_stats = None
            st.rerun()


# ─── Main area ─────────────────────────────────────────────────────────────────
has_docs = bool(st.session_state.chunks)

st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

# Top bar
pill_class = "active" if has_docs else "idle"
dot_class  = "active" if has_docs else "idle"
pill_text  = f"{len(st.session_state.chunks)} chunks ready" if has_docs else "No document loaded"

st.markdown(f"""
<div class="top-bar">
  <div class="top-bar-left">
    <h1 class="top-title">PaperMind<span style="color:#6366f1;">.</span></h1>
    <p class="top-sub">Ask anything about your uploaded documents</p>
  </div>
  <div class="engine-pill {pill_class}">
    <div class="pill-dot {dot_class}"></div>
    {pill_text}
  </div>
</div>
""", unsafe_allow_html=True)


# ─── Empty state ───────────────────────────────────────────────────────────────
if not has_docs:
    st.markdown("""
<div class="empty-state">
  <div class="empty-icon">
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
  </div>
  <div class="empty-title">No document loaded yet</div>
  <div class="empty-desc">Upload a PDF in the sidebar, hit Index Documents, and start asking questions in plain English.</div>
  <div class="steps-row">
    <div class="step-card">
      <div class="step-num">Step 01</div>
      <div class="step-name">Upload PDF</div>
      <div class="step-desc">Drop any research paper, report, manual, or contract into the sidebar uploader.</div>
    </div>
    <div class="step-card">
      <div class="step-num">Step 02</div>
      <div class="step-name">Index</div>
      <div class="step-desc">Click Index Documents — your file is split into semantic chunks for fast retrieval.</div>
    </div>
    <div class="step-card">
      <div class="step-num">Step 03</div>
      <div class="step-name">Ask anything</div>
      <div class="step-desc">Type any question. PaperMind finds the right passages and gives a cited answer.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

else:
    # ── Quick-start chips ─────────────────────────────────────────────────────
    if not st.session_state.messages:
        st.markdown('<div class="chips-label">Quick actions</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        chips = [
            (c1, "Summarize",      "Give me a concise executive summary of this document, covering its key arguments, findings, and conclusions."),
            (c2, "Key metrics",    "Extract all important numbers, statistics, percentages, dates, and quantitative figures from the document."),
            (c3, "Action items",   "What are the main recommendations, next steps, or action items described in this document?"),
            (c4, "Risks & limits", "What limitations, risks, or caveats do the authors highlight?"),
        ]
        for col, label, full_query in chips:
            with col:
                if st.button(label, use_container_width=True):
                    st.session_state.pending = full_query
                    st.rerun()
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Chat history ──────────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        avatar  = "You" if is_user else "AI"
        av_cls  = "user" if is_user else "assistant"
        bub_cls = "user-bubble" if is_user else "assistant-bubble"
        role_lbl = "You" if is_user else "PaperMind"

        with st.chat_message(msg["role"]):
            st.markdown(f"""
<div class="msg-wrap">
  <div class="msg-avatar {av_cls}">{avatar}</div>
  <div class="msg-body">
    <div class="msg-role">{role_lbl}</div>
    <div class="msg-bubble {bub_cls}">
""", unsafe_allow_html=True)
            st.markdown(msg["content"])
            st.markdown("</div></div></div>", unsafe_allow_html=True)

            if not is_user and "sources" in msg and msg["sources"]:
                with st.expander(f"Sources · {len(msg['sources'])} passages"):
                    st.markdown('<div class="cite-header">Retrieved document passages</div>', unsafe_allow_html=True)
                    for i, src in enumerate(msg["sources"]):
                        render_citation(src, i)


# ─── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask a question about your document…")

if st.session_state.pending:
    user_input = st.session_state.pending
    st.session_state.pending = None

if user_input:
    if not api_key:
        st.warning("Add your API key in the sidebar to get answers.")
    elif not has_docs:
        st.warning("Upload and index a PDF document first.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(f"""
<div class="msg-wrap">
  <div class="msg-avatar user">You</div>
  <div class="msg-body">
    <div class="msg-role">You</div>
    <div class="msg-bubble user-bubble">{user_input}</div>
  </div>
</div>""", unsafe_allow_html=True)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                retrieved = simple_semantic_search(user_input, st.session_state.chunks, top_k=top_k)
                try:
                    answer = generate_rag_response(user_input, retrieved, provider, api_key, model_name)

                    st.markdown(f"""
<div class="msg-wrap">
  <div class="msg-avatar assistant">AI</div>
  <div class="msg-body">
    <div class="msg-role">PaperMind</div>
    <div class="msg-bubble assistant-bubble">
""", unsafe_allow_html=True)
                    st.markdown(answer)
                    st.markdown("</div></div></div>", unsafe_allow_html=True)

                    if retrieved:
                        with st.expander(f"Sources · {len(retrieved)} passages"):
                            st.markdown('<div class="cite-header">Retrieved document passages</div>', unsafe_allow_html=True)
                            for i, src in enumerate(retrieved):
                                render_citation(src, i)

                    st.session_state.messages.append({
                        "role": "assistant", "content": answer, "sources": retrieved
                    })

                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
