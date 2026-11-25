import os
import re
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader

load_dotenv()

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PaperMind · Document Intelligence",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none'><path d='M12 2V6' stroke='%23FB923C' stroke-width='2.6' stroke-linecap='round'/><path d='M12 18V22' stroke='%23EA580C' stroke-width='2.6' stroke-linecap='round'/><path d='M4.93 4.93L7.76 7.76' stroke='%2338BDF8' stroke-width='2.6' stroke-linecap='round'/><path d='M16.24 16.24L19.07 19.07' stroke='%23F97316' stroke-width='2.6' stroke-linecap='round'/><path d='M2 12H6' stroke='%230284C7' stroke-width='2.6' stroke-linecap='round'/><path d='M18 12H22' stroke='%23F97316' stroke-width='2.6' stroke-linecap='round'/><path d='M4.93 19.07L7.76 16.24' stroke='%230369A1' stroke-width='2.6' stroke-linecap='round'/><path d='M16.24 7.76L19.07 4.93' stroke='%23FDBA74' stroke-width='2.6' stroke-linecap='round'/></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Theme Mode Selection ──────────────────────────────────────────────────────
if "dark_mode_toggle" not in st.session_state:
    st.session_state.dark_mode_toggle = False

is_dark = st.session_state.dark_mode_toggle

if is_dark:
    theme_vars = """
    --app-bg: #0C0D12;
    --app-aurora: radial-gradient(ellipse 720px 480px at 50% 210px, rgba(56, 189, 248, 0.16) 0%, rgba(249, 115, 22, 0.13) 42%, rgba(12, 13, 18, 0) 72%),
                 radial-gradient(circle at 10% 120px, rgba(254, 215, 170, 0.08) 0%, rgba(12, 13, 18, 0) 48%),
                 radial-gradient(circle at 90% 280px, rgba(56, 189, 248, 0.08) 0%, rgba(12, 13, 18, 0) 48%);
    --text-primary: #F3F4F6;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --sidebar-bg: #121319;
    --sidebar-border: rgba(255, 255, 255, 0.08);
    --card-bg: #181920;
    --card-border: rgba(255, 255, 255, 0.08);
    --card-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    --user-bubble-bg: #1F212A;
    --user-bubble-text: #FFFFFF;
    --user-bubble-border: rgba(255, 255, 255, 0.1);
    --assistant-bubble-bg: #181920;
    --assistant-bubble-border: rgba(255, 255, 255, 0.08);
    --chat-input-bg: #181920;
    --chat-input-border: rgba(255, 255, 255, 0.12);
    --chat-input-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.6);
    --medallion-bg: #181920;
    --medallion-border: rgba(255, 255, 255, 0.12);
    --medallion-shadow: 0 16px 36px -4px rgba(249, 115, 22, 0.25);
    --chip-bg: rgba(24, 25, 32, 0.9);
    --chip-border: rgba(251, 146, 60, 0.35);
    --stat-box-bg: #181920;
    --doc-badge-bg: #181920;
    --doc-badge-border: rgba(249, 115, 22, 0.3);
    """
else:
    theme_vars = """
    --app-bg: #F8F6F1;
    --app-aurora: radial-gradient(ellipse 720px 480px at 50% 210px, rgba(56, 189, 248, 0.25) 0%, rgba(251, 146, 60, 0.18) 42%, rgba(248, 246, 241, 0) 72%),
                 radial-gradient(circle at 10% 120px, rgba(254, 215, 170, 0.32) 0%, rgba(248, 246, 241, 0) 48%),
                 radial-gradient(circle at 90% 280px, rgba(186, 230, 253, 0.28) 0%, rgba(248, 246, 241, 0) 48%);
    --text-primary: #18191B;
    --text-secondary: #52525B;
    --text-muted: #71717A;
    --sidebar-bg: #EFECE5;
    --sidebar-border: rgba(0, 0, 0, 0.07);
    --card-bg: #FFFFFF;
    --card-border: rgba(0, 0, 0, 0.06);
    --card-shadow: 0 4px 18px -2px rgba(0, 0, 0, 0.03);
    --user-bubble-bg: #18191B;
    --user-bubble-text: #FFFFFF;
    --user-bubble-border: transparent;
    --assistant-bubble-bg: #FFFFFF;
    --assistant-bubble-border: rgba(0, 0, 0, 0.06);
    --chat-input-bg: #FFFFFF;
    --chat-input-border: rgba(0, 0, 0, 0.1);
    --chat-input-shadow: 0 16px 40px -10px rgba(249, 115, 22, 0.14), 0 2px 10px rgba(0, 0, 0, 0.04);
    --medallion-bg: #FFFFFF;
    --medallion-border: rgba(255, 255, 255, 0.95);
    --medallion-shadow: 0 16px 36px -4px rgba(249, 115, 22, 0.22), 0 4px 14px rgba(0,0,0,0.05);
    --chip-bg: rgba(255, 255, 255, 0.9);
    --chip-border: rgba(251, 146, 60, 0.35);
    --stat-box-bg: #FFFFFF;
    --doc-badge-bg: #FFFFFF;
    --doc-badge-border: rgba(249, 115, 22, 0.22);
    """

# ─── Design System ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    {theme_vars}
}}

/* ── Reset & Typography base ── */
*, *::before, *::after {{ box-sizing: border-box; }}

html, body {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: var(--text-primary);
}}

p, h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stButton, input, textarea {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}}

/* Never override icon fonts so Streamlit Material Symbols render properly */
[class*="material-symbols"],
[class*="material-icons"],
[data-testid="stIcon"],
[data-testid="stIconMaterial"],
i {{
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
}}

/* ── Browser surface refinements (Impeccable craft) ── */
::selection {{
    background: rgba(251, 146, 60, 0.28) !important;
    color: #C2410C !important;
}}
caret-color: #EA580C;

::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: #52525B;
    border-radius: 9999px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: #71717A;
}}

/* ── App Shell & Ethereal Aurora Atmosphere ── */
.stApp {{
    background-color: var(--app-bg) !important;
    background-image: var(--app-aurora) !important;
    background-attachment: fixed !important;
    color: var(--text-primary) !important;
}}

.main, [data-testid="stMain"] {{
    background: transparent !important;
}}

/* Align main content and bottom chat container to identical centered measure */
[data-testid="stMainBlockContainer"],
.block-container {{
    width: 100% !important;
    max-width: 860px !important;
    padding: 0.75rem 1.5rem 1.5rem !important;
    margin: 0 auto !important;
}}

[data-testid="stBottomBlockContainer"] {{
    width: 100% !important;
    max-width: 860px !important;
    padding: 0.5rem 1.5rem 1.25rem !important;
    margin: 0 auto !important;
}}

/* ── Header & Sidebar Expand Button Fixes ── */
/* Keep header and toolbar visible (transparent) so stExpandSidebarButton stays clickable */
header[data-testid="stHeader"] {{
    background: transparent !important;
    background-color: transparent !important;
    visibility: visible !important;
    pointer-events: none !important;
    z-index: 99999 !important;
}}

[data-testid="stToolbar"] {{
    visibility: visible !important;
    display: flex !important;
    background: transparent !important;
    pointer-events: none !important;
}}

/* Hide only Streamlit menu / deploy clutter, NEVER hide stToolbar or stExpandSidebarButton */
#MainMenu,
[data-testid="stMainMenu"],
[data-testid="stAppDeployButton"],
[data-testid="stToolbarActions"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
footer {{
    display: none !important;
    visibility: hidden !important;
}}

/* Prominent expand-sidebar chevron button (Streamlit 1.40+ & legacy testids) */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stHeader"] button[aria-label="Expand sidebar"] {{
    visibility: visible !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    pointer-events: auto !important;
    opacity: 1 !important;
    z-index: 100000 !important;
    background: var(--card-bg) !important;
    border: 1.5px solid var(--card-border) !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.16) !important;
    color: var(--text-primary) !important;
    min-width: 36px !important;
    min-height: 36px !important;
    padding: 6px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="stHeader"] button[aria-label="Expand sidebar"]:hover {{
    border-color: #FB923C !important;
    box-shadow: 0 6px 18px rgba(251, 146, 60, 0.28) !important;
    transform: scale(1.05) !important;
}}
[data-testid="stExpandSidebarButton"] span,
[data-testid="stExpandSidebarButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg {{
    color: var(--text-primary) !important;
    fill: var(--text-primary) !important;
    stroke: var(--text-primary) !important;
}}

/* Sidebar collapse button (inside sidebar) */
[data-testid="stSidebarCollapseButton"] {{
    color: var(--text-primary) !important;
    opacity: 0.75 !important;
    transition: opacity 0.2s ease !important;
}}
[data-testid="stSidebarCollapseButton"]:hover {{
    opacity: 1 !important;
}}
[data-testid="stSidebarCollapseButton"] button {{
    color: var(--text-primary) !important;
}}
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapseButton"] svg {{
    color: var(--text-primary) !important;
    fill: var(--text-primary) !important;
}}

/* ── Opaque Bottom Masking Zone (hides scrolled content behind/below typing bar) ── */
[data-testid="stBottom"] {{
    position: sticky !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100% !important;
    z-index: 999 !important;
    background: transparent !important;
}}
[data-testid="stBottom"] > div {{
    background: linear-gradient(
        to bottom,
        rgba(0, 0, 0, 0) 0%,
        var(--app-bg) 24px,
        var(--app-bg) 100%
    ) !important;
    padding-top: 16px !important;
    border: none !important;
    box-shadow: none !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-border) !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    background-color: var(--sidebar-bg) !important;
}}
[data-testid="stSidebar"] label {{
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    letter-spacing: -0.01em;
}}

/* ── Sidebar brand strip ── */
.sb-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 22px 20px 14px;
    border-bottom: 1px solid var(--sidebar-border);
    margin-bottom: 6px;
}}
.sb-logo {{
    width: 38px; height: 38px;
    background: var(--card-bg);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 14px -2px rgba(249, 115, 22, 0.18), 0 1px 3px rgba(0,0,0,0.04);
    border: 1px solid var(--card-border);
}}
.sb-title-row {{
    display: flex;
    align-items: center;
    gap: 8px;
}}
.sb-name {{
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
}}
.sb-badge {{
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    background: rgba(249, 115, 22, 0.12);
    color: #EA580C;
    padding: 2px 7px;
    border-radius: 9999px;
}}
.sb-tagline {{
    font-size: 0.74rem;
    color: var(--text-muted);
    margin-top: 2px;
    font-weight: 500;
}}

/* ── Sidebar sections ── */
.sb-section {{
    padding: 10px 18px 4px;
}}
.sb-label {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 8px;
}}
.sb-divider {{
    border: none;
    border-top: 1px solid var(--sidebar-border);
    margin: 14px 0;
}}

/* ── Stat row ── */
.stat-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 10px 0 0;
}}
.stat-box {{
    background: var(--stat-box-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 10px 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}}
.stat-num {{
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
    line-height: 1.1;
}}
.stat-lbl {{
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--text-muted);
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.stat-box.wide {{
    grid-column: span 2;
}}

/* ── Docs badge list ── */
.doc-badge {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 11px;
    background: var(--doc-badge-bg);
    border: 1px solid var(--doc-badge-border);
    border-radius: 10px;
    margin-top: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #EA580C;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.doc-badge svg {{ flex-shrink: 0; }}

/* ── Unified Polished Dark Sidebar Inputs (API Key, Selectbox, Password) ── */
[data-testid="stSidebar"] [data-testid="stTextInput"],
[data-testid="stSidebar"] [data-testid="stTextInput"] > div,
[data-testid="stSidebar"] [data-testid="stTextInput"] > div > div,
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="base-input"] {{
    background-color: #16171D !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25) !important;
}}

[data-testid="stSidebar"] [data-testid="stTextInput"] input {{
    background-color: #16171D !important;
    border: none !important;
    color: #FFFFFF !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
}}

[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {{
    color: #94A3B8 !important;
    opacity: 1 !important;
}}

[data-testid="stSidebar"] [data-baseweb="input"]:focus-within {{
    border-color: #FB923C !important;
    box-shadow: 0 0 0 3px rgba(251, 146, 60, 0.22) !important;
}}

[data-testid="stSidebar"] [data-baseweb="input"] button {{
    background-color: #16171D !important;
    color: #94A3B8 !important;
    border: none !important;
}}
[data-testid="stSidebar"] [data-baseweb="input"] button:hover {{
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] [data-baseweb="input"] svg {{
    fill: #94A3B8 !important;
}}

/* BaseWeb Select dropdowns in sidebar */
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background-color: #16171D !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25) !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span {{
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] svg {{
    fill: #94A3B8 !important;
}}

/* Dropdown popover menu styling */
div[data-baseweb="popover"], div[data-baseweb="menu"] {{
    background-color: #16171D !important;
    border-radius: 12px !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
}}
li[role="option"] {{
    color: #FFFFFF !important;
    background-color: #16171D !important;
}}
li[role="option"]:hover, li[aria-selected="true"] {{
    background-color: #24252E !important;
    color: #FB923C !important;
}}

/* Secure badge */
.secure-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #064E3B;
    border: 1px solid #059669;
    color: #6EE7B7;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
    margin: 4px 0 8px;
}}
.secure-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #34D399;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: var(--card-bg) !important;
    border: 1.5px dashed rgba(249, 115, 22, 0.45) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02) !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: #EA580C !important;
    box-shadow: 0 4px 14px rgba(249, 115, 22, 0.12) !important;
}}
[data-testid="stFileUploader"] section {{
    background: transparent !important;
    border: none !important;
}}
[data-testid="stFileUploader"] span, 
[data-testid="stFileUploader"] small {{
    color: var(--text-secondary) !important;
}}
[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] button *,
[data-testid="stFileUploader"] button span {{
    background: #16171D !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}}
[data-testid="stFileUploader"] button * {{
    background: transparent !important;
    border: none !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: var(--card-bg) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}
.stButton > button:hover {{
    background: rgba(249, 115, 22, 0.08) !important;
    border-color: rgba(249, 115, 22, 0.3) !important;
    color: var(--text-primary) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #0284C7 0%, #FB923C 55%, #EA580C 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 24px -4px rgba(249, 115, 22, 0.38) !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: linear-gradient(135deg, #0369A1 0%, #EA580C 55%, #C2410C 100%) !important;
    box-shadow: 0 12px 28px -4px rgba(249, 115, 22, 0.52) !important;
    transform: translateY(-1px) !important;
}}

/* ── Theme Button (High Contrast & Visible in Light/Dark) ── */
.theme-btn > button {{
    background: var(--card-bg) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--card-border) !important;
    border-radius: 12px !important;
    font-size: 0.84rem !important;
    font-weight: 700 !important;
    padding: 8px 14px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
}}
.theme-btn > button:hover {{
    border-color: #FB923C !important;
    color: #EA580C !important;
    box-shadow: 0 4px 14px rgba(251, 146, 60, 0.2) !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02) !important;
    overflow: hidden !important;
}}
[data-testid="stExpander"] summary {{
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    background: var(--card-bg) !important;
}}
[data-testid="stExpander"] summary:hover {{
    color: var(--text-primary) !important;
}}

/* ── Sliders ── */
[data-testid="stSlider"] div[role="slider"] {{
    background-color: #EA580C !important;
    border: 2px solid #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(234, 88, 12, 0.45) !important;
}}

/* ── Top bar ── */
.top-bar {{
    padding: 0 0 8px;
    margin-bottom: 0;
}}
.top-title-row {{
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}}
.top-title {{
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.035em;
    margin: 0;
}}
.top-sparkle {{
    color: #EA580C;
    font-size: 1.05rem;
}}
.top-sub {{
    font-size: 0.84rem;
    color: var(--text-secondary);
    margin: 2px 0 0;
}}
.engine-pill {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}}
.engine-pill.active {{
    background: #064E3B;
    border: 1px solid #059669;
    color: #6EE7B7;
}}
.engine-pill.idle {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    color: var(--text-muted);
}}
.pill-dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
}}
.pill-dot.active {{
    background: #34D399;
    box-shadow: 0 0 6px #34D399;
    animation: blink 2s infinite;
}}
.pill-dot.idle {{
    background: #71717A;
}}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:.4}} }}

/* ── Empty state (Refined Ethereal Centerpiece, sized to stay cleanly above typing bar) ── */
.empty-state {{
    text-align: center;
    padding: 4px 8px 16px;
    max-width: 780px;
    margin: 0 auto;
}}
.hero-chip {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    background: var(--chip-bg);
    border: 1px solid var(--chip-border);
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #EA580C;
    box-shadow: 0 4px 14px -2px rgba(251, 146, 60, 0.15);
    margin-bottom: 12px;
}}
.hero-orb {{
    position: relative;
    width: 60px; height: 60px;
    margin: 0 auto 10px;
    display: flex; align-items: center; justify-content: center;
}}
.hero-medallion {{
    width: 54px; height: 54px;
    background: var(--medallion-bg);
    border: 1px solid var(--medallion-border);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    box-shadow: var(--medallion-shadow);
    position: relative;
    z-index: 2;
}}
.empty-title {{
    font-size: clamp(1.45rem, 2.5vw, 1.9rem);
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.035em;
    line-height: 1.2;
    margin-bottom: 8px;
}}
.empty-desc {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    max-width: 520px;
    margin: 0 auto 18px;
    line-height: 1.5;
}}
.steps-row {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    max-width: 780px;
    margin: 0 auto;
}}
@media (max-width: 640px) {{
    .steps-row {{
        grid-template-columns: 1fr;
    }}
}}
.step-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 14px 14px;
    text-align: left;
    box-shadow: var(--card-shadow);
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}}
.step-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px -2px rgba(249, 115, 22, 0.15);
    border-color: rgba(249, 115, 22, 0.3);
}}
.step-num {{
    font-size: 0.66rem;
    font-weight: 700;
    color: #EA580C;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 5px;
}}
.step-name {{
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
    letter-spacing: -0.01em;
}}
.step-desc {{
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.42;
}}

/* ── Chips ── */
.chips-label {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 10px;
}}

/* ── Chat messages ── */
.msg-wrap {{
    display: flex;
    gap: 14px;
    margin-bottom: 24px;
    align-items: flex-start;
}}
.msg-avatar {{
    width: 36px; height: 36px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 0.8rem;
    font-weight: 700;
}}
.msg-avatar.user {{
    background: #18191B;
    color: #FFFFFF;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    border: 1px solid rgba(255,255,255,0.1);
}}
.msg-avatar.assistant {{
    background: var(--card-bg);
    border: 1px solid rgba(251, 146, 60, 0.3);
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.15);
}}
.msg-body {{ flex: 1; min-width: 0; }}
.msg-role {{
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--text-muted);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
.msg-bubble {{
    font-size: 0.95rem;
    line-height: 1.7;
}}
.msg-bubble.user-bubble {{
    background: var(--user-bubble-bg);
    color: var(--user-bubble-text);
    border-radius: 20px 20px 4px 20px;
    padding: 14px 18px;
    box-shadow: 0 4px 16px -2px rgba(0,0,0,0.15);
    border: 1px solid var(--user-bubble-border);
    display: inline-block;
}}
.msg-bubble.assistant-bubble {{
    background: var(--assistant-bubble-bg);
    border: 1px solid var(--assistant-bubble-border);
    border-radius: 4px 20px 20px 20px;
    padding: 20px 24px;
    box-shadow: var(--card-shadow);
    color: var(--text-primary);
}}

/* ── Citation cards ── */
.cite-wrap {{ margin-top: 12px; }}
.cite-header {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 8px;
}}
.cite-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.84rem;
    line-height: 1.6;
    color: var(--text-secondary);
}}
.cite-card-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}}
.cite-fname {{
    font-weight: 700;
    color: #38BDF8;
    font-size: 0.8rem;
}}
.cite-page {{
    background: rgba(249, 115, 22, 0.15);
    color: #EA580C;
    font-weight: 600;
    font-size: 0.72rem;
    padding: 2px 8px;
    border-radius: 9999px;
    font-variant-numeric: tabular-nums;
}}
.cite-body {{
    color: var(--text-secondary);
}}

/* ── Floating Chat Input Box ── */
[data-testid="stChatInput"] {{
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    background: var(--chat-input-bg) !important;
    background-color: var(--chat-input-bg) !important;
    border: 1px solid var(--chat-input-border) !important;
    border-radius: 28px !important;
    box-shadow: var(--chat-input-shadow) !important;
    padding: 4px 8px !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: #FB923C !important;
    box-shadow: 0 20px 48px -8px rgba(249, 115, 22, 0.24), 0 0 0 3px rgba(251, 146, 60, 0.2) !important;
}}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] > div > div {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
}}
[data-testid="stChatInput"] textarea {{
    background: transparent !important;
    background-color: transparent !important;
    color: var(--text-primary) !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    border: none !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: var(--text-muted) !important;
    font-weight: 400 !important;
}}
[data-testid="stChatInput"] button {{
    background: linear-gradient(135deg, #38BDF8 0%, #FB923C 60%, #EA580C 100%) !important;
    border-radius: 50% !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3) !important;
}}

/* ── Streamlit default overrides ── */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}
[data-testid="stChatMessageAvatar"] {{
    display: none !important;
}}
.stMarkdown p {{ color: var(--text-primary); line-height: 1.7; }}
.stMarkdown code {{
    background: rgba(249, 115, 22, 0.1) !important;
    border: 1px solid rgba(249, 115, 22, 0.25) !important;
    border-radius: 6px !important;
    color: #FB923C !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85em !important;
    padding: 2px 6px !important;
}}
.stMarkdown pre {{
    background: #121319 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: #F3F4F6 !important;
}}
.stMarkdown pre code {{
    background: transparent !important;
    border: none !important;
    color: #F3F4F6 !important;
}}
.stAlert {{
    background: rgba(249, 115, 22, 0.08) !important;
    border: 1px solid rgba(249, 115, 22, 0.25) !important;
    border-radius: 12px !important;
    color: #FB923C !important;
}}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def get_secret(key_name, default=""):
    try:
        if key_name in st.secrets:
            return str(st.secrets[key_name]).strip()
    except Exception:
        pass
    return default


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
    preview = (body[:320] + "…") if len(body) > 320 else body
    st.markdown(f"""
<div class="cite-card">
  <div class="cite-card-top">
    <span class="cite-fname">{fname}</span>
    <span class="cite-page">{page}</span>
  </div>
  <div class="cite-body">{preview}</div>
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
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <path d="M12 2V6" stroke="#FB923C" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M12 18V22" stroke="#EA580C" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M4.93 4.93L7.76 7.76" stroke="#38BDF8" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M16.24 16.24L19.07 19.07" stroke="#F97316" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M2 12H6" stroke="#0284C7" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M18 12H22" stroke="#F97316" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M4.93 19.07L7.76 16.24" stroke="#0369A1" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M16.24 7.76L19.07 4.93" stroke="#FDBA74" stroke-width="2.6" stroke-linecap="round"/>
    </svg>
  </div>
  <div>
    <div class="sb-title-row">
      <span class="sb-name">PaperMind</span>
      <span class="sb-badge">STUDIO</span>
    </div>
    <div class="sb-tagline">Document Intelligence Engine</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Theme Toggle Button (Clear, prominent, impossible to miss)
    st.markdown('<div class="theme-btn" style="padding: 4px 18px 10px;">', unsafe_allow_html=True)
    sb_theme_label = "☀️ Switch to Light Mode" if is_dark else "🌙 Switch to Dark Mode"
    if st.button(sb_theme_label, use_container_width=True, key="sidebar_theme_btn"):
        st.session_state.dark_mode_toggle = not is_dark
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # Provider & model
    st.markdown('<div class="sb-section"><div class="sb-label">AI Model & Engine</div></div>', unsafe_allow_html=True)
    with st.container():
        provider = st.selectbox("Provider", ["Google Gemini", "OpenAI"], label_visibility="collapsed")

        if provider == "Google Gemini":
            env_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API") or get_secret("GEMINI_API_KEY"))
            user_key_input = st.text_input("Gemini API Key", value="", type="password",
                                    placeholder="●●●●●●●● (Configured securely)" if env_key else "Paste Gemini API Key (AIza…)", label_visibility="collapsed")
            api_key = user_key_input.strip() if user_key_input.strip() else env_key
            if env_key and not user_key_input:
                st.markdown("""
<div class="secure-badge">
  <span class="secure-dot"></span>
  <span>Active via secure environment</span>
</div>
""", unsafe_allow_html=True)
            models  = fetch_available_gemini_models(api_key)
            model_name = st.selectbox("Model", models, label_visibility="collapsed")
        else:
            env_key = (os.getenv("OPENAI_API_KEY") or get_secret("OPENAI_API_KEY"))
            user_key_input = st.text_input("OpenAI API Key", value="", type="password",
                                    placeholder="●●●●●●●● (Configured securely)" if env_key else "Paste OpenAI Key (sk-…)", label_visibility="collapsed")
            api_key = user_key_input.strip() if user_key_input.strip() else env_key
            if env_key and not user_key_input:
                st.markdown("""
<div class="secure-badge">
  <span class="secure-dot"></span>
  <span>Active via secure environment</span>
</div>
""", unsafe_allow_html=True)
            model_name = st.selectbox("Model", ["gpt-4o-mini","gpt-4o","gpt-3.5-turbo"], label_visibility="collapsed")

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # Document upload
    st.markdown('<div class="sb-section"><div class="sb-label">Documents</div></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")

    if uploaded:
        if st.button("Index Documents", type="primary", use_container_width=True):
            with st.spinner("Parsing & semantic chunking…"):
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
            short = (f[:34]+"…") if len(f) > 34 else f
            st.markdown(f"""
<div class="doc-badge">
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
  <span>{short}</span>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # RAG settings
    with st.expander("⚙️  Retrieval Settings"):
        chunk_size    = st.slider("Chunk size", 400, 2000, 1000, step=100)
        chunk_overlap = st.slider("Chunk overlap", 50, 400, 150, step=25)
        top_k         = st.slider("Top chunks (K)", 2, 10, 4)
    if "top_k" not in locals():
        top_k = 4

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

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

# ─── Top Bar with Title & Status ────────────────────────────────────────────────
pill_class = "active" if has_docs else "idle"
dot_class  = "active" if has_docs else "idle"
pill_text  = f"{len(st.session_state.chunks)} chunks ready" if has_docs else "No document loaded"
sub_text   = "Ask complex questions across your documents with cited evidence" if has_docs else "Document Intelligence Studio"

st.markdown(f"""
<div class="top-bar" style="display:flex; align-items:center; justify-content:space-between; gap:12px; border-bottom:1px solid var(--sidebar-border); padding:0 0 12px; margin-bottom:14px;">
  <div>
    <div class="top-title-row">
      <h1 class="top-title">PaperMind</h1>
      <span class="top-sparkle">✦</span>
    </div>
    <p class="top-sub">{sub_text}</p>
  </div>
  <div class="engine-pill {pill_class}"><span class="pill-dot {dot_class}"></span><span>{pill_text}</span></div>
</div>
""", unsafe_allow_html=True)


# ─── Empty state ───────────────────────────────────────────────────────────────
if not has_docs:
    st.markdown("""
<div class="empty-state">
  <div class="hero-chip">
    <span>✨</span>
    <span>Precision Document Intelligence</span>
  </div>
  <div class="hero-orb">
    <div class="hero-medallion">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
        <path d="M12 2V6" stroke="#FB923C" stroke-width="2.6" stroke-linecap="round"/>
        <path d="M12 18V22" stroke="#EA580C" stroke-width="2.6" stroke-linecap="round"/>
        <path d="M4.93 4.93L7.76 7.76" stroke="#38BDF8" stroke-width="2.6" stroke-linecap="round"/>
        <path d="M16.24 16.24L19.07 19.07" stroke="#F97316" stroke-width="2.6" stroke-linecap="round"/>
        <path d="M2 12H6" stroke="#0284C7" stroke-width="2.6" stroke-linecap="round"/>
        <path d="M18 12H22" stroke="#F97316" stroke-width="2.6" stroke-linecap="round"/>
        <path d="M4.93 19.07L7.76 16.24" stroke="#0369A1" stroke-width="2.6" stroke-linecap="round"/>
        <path d="M16.24 7.76L19.07 4.93" stroke="#FDBA74" stroke-width="2.6" stroke-linecap="round"/>
      </svg>
    </div>
  </div>
  <h2 class="empty-title">How can PaperMind help you explore your documents?</h2>
  <p class="empty-desc">Upload research papers, quarterly reports, legal contracts, or manuals in the sidebar. Ask complex questions and receive cited, grounded answers instantly.</p>
  
  <div class="steps-row">
    <div class="step-card">
      <div class="step-num">01 · INGEST</div>
      <div class="step-name">Upload Any PDF</div>
      <div class="step-desc">Drop documents into the sidebar uploader with fast multi-file batch parsing.</div>
    </div>
    <div class="step-card">
      <div class="step-num">02 · INDEX</div>
      <div class="step-name">Semantic Chunking</div>
      <div class="step-desc">Text is chunked with smart overlap for maximum retrieval precision.</div>
    </div>
    <div class="step-card">
      <div class="step-num">03 · SYNTHESIZE</div>
      <div class="step-name">Cited Answers</div>
      <div class="step-desc">Ask queries in plain English with grounded answers citing exact pages.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

else:
    # ── Quick-start chips ─────────────────────────────────────────────────────
    if not st.session_state.messages:
        st.markdown('<div class="chips-label">SUGGESTED EXPLORATIONS</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        chips = [
            (c1, "✨ Summarize",      "Give me a concise executive summary of this document, covering its key arguments, findings, and conclusions."),
            (c2, "📊 Key metrics",    "Extract all important numbers, statistics, percentages, dates, and quantitative figures from the document."),
            (c3, "🎯 Action items",   "What are the main recommendations, next steps, or action items described in this document?"),
            (c4, "⚡ Risks & limits", "What limitations, risks, or caveats do the authors highlight?"),
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

        with st.chat_message(msg["role"]):
            if is_user:
                st.markdown(f"""
<div class="msg-wrap">
  <div class="msg-avatar user">You</div>
  <div class="msg-body">
    <div class="msg-role">You</div>
    <div class="msg-bubble user-bubble">{msg['content']}</div>
  </div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div class="msg-wrap">
  <div class="msg-avatar assistant">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M12 2V6" stroke="#FB923C" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M12 18V22" stroke="#EA580C" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M4.93 4.93L7.76 7.76" stroke="#38BDF8" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M16.24 16.24L19.07 19.07" stroke="#F97316" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M2 12H6" stroke="#0284C7" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M18 12H22" stroke="#F97316" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M4.93 19.07L7.76 16.24" stroke="#0369A1" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M16.24 7.76L19.07 4.93" stroke="#FDBA74" stroke-width="2.6" stroke-linecap="round"/>
    </svg>
  </div>
  <div class="msg-body">
    <div class="msg-role">PaperMind AI</div>
    <div class="msg-bubble assistant-bubble">
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
  <div class="msg-avatar assistant">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M12 2V6" stroke="#FB923C" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M12 18V22" stroke="#EA580C" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M4.93 4.93L7.76 7.76" stroke="#38BDF8" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M16.24 16.24L19.07 19.07" stroke="#F97316" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M2 12H6" stroke="#0284C7" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M18 12H22" stroke="#F97316" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M4.93 19.07L7.76 16.24" stroke="#0369A1" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M16.24 7.76L19.07 4.93" stroke="#FDBA74" stroke-width="2.6" stroke-linecap="round"/>
    </svg>
  </div>
  <div class="msg-body">
    <div class="msg-role">PaperMind AI</div>
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
