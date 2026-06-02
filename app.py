import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SkinCare Research · Scopus Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM CSS — DARK BLUE THEME · MEJOR LEGIBILIDAD · GLASSMORPHISM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600;14..32,700;14..32,800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── ROOT VARIABLES ── */
:root {
  --dark-bg:      #0a1628;
  --dark-card:    #0f1e3a;
  --dark-hover:   #162a4e;
  --blue-primary: #1e6fdf;
  --blue-glow:    #3b82f6;
  --blue-soft:    #60a5fa;
  --cyan-accent:  #06b6d4;
  --white-text:   #f1f5f9;
  --gray-text:    #94a3b8;
  --light-text:   #cbd5e1;
  --glass:        rgba(15, 30, 58, 0.85);
  --glass-light:  rgba(30, 58, 80, 0.55);
  --shadow-sm:    0 4px 12px rgba(0,0,0,0.3);
  --shadow-md:    0 8px 24px rgba(0,0,0,0.4);
  --shadow-lg:    0 16px 48px rgba(0,0,0,0.5);
  --shadow-glow:  0 0 20px rgba(59,130,246,0.2);
  --radius:       16px;
  --radius-sm:    10px;
}

/* ── BASE DARK THEME ── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
}

.stApp {
  background: linear-gradient(135deg, #0a1628 0%, #0d1c3a 50%, #0a1628 100%) !important;
  min-height: 100vh;
}

/* Floating glow effects */
.stApp::before {
  content: '';
  position: fixed;
  top: -200px; right: -200px;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  animation: floatSlow 20s ease-in-out infinite;
}

.stApp::after {
  content: '';
  position: fixed;
  bottom: -150px; left: -150px;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(6,182,212,0.06) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  animation: floatSlowReversed 25s ease-in-out infinite;
}

@keyframes floatSlow {
  0%,100% { transform: translate(0,0) scale(1); }
  50%      { transform: translate(-40px, 50px) scale(1.1); }
}

@keyframes floatSlowReversed {
  0%,100% { transform: translate(0,0) scale(1); }
  50%      { transform: translate(30px, -40px) scale(1.08); }
}

/* ── SIDEBAR MEJORADO ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #071228 0%, #0a1835 50%, #071228 100%) !important;
  border-right: 1px solid rgba(59,130,246,0.2);
  box-shadow: 4px 0 30px rgba(0,0,0,0.5);
}

[data-testid="stSidebar"] * { 
  color: #e2e8f0 !important; 
}

[data-testid="stSidebar"] .stSlider > div > div > div { 
  background: #3b82f6 !important; 
}

[data-testid="stSidebar"] label { 
  color: #60a5fa !important; 
  font-weight: 600 !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  margin-bottom: 0.25rem !important;
}

[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
  background: rgba(59,130,246,0.2) !important;
  border: 1px solid rgba(59,130,246,0.3) !important;
  border-radius: 20px !important;
}

/* Sidebar logo area */
.sidebar-logo {
  background: rgba(59,130,246,0.08);
  border: 1px solid rgba(59,130,246,0.25);
  border-radius: 14px;
  padding: 1.2rem;
  margin-bottom: 1.8rem;
  text-align: center;
  backdrop-filter: blur(10px);
}

.sidebar-logo .logo-icon { 
  font-size: 2.5rem; 
  margin-bottom: 0.4rem;
  filter: drop-shadow(0 0 8px rgba(59,130,246,0.4));
}

.sidebar-logo .logo-title {
  font-size: 0.9rem; 
  font-weight: 700;
  color: #f1f5f9 !important;
  letter-spacing: 0.03em;
  line-height: 1.3;
}

.sidebar-logo .logo-sub {
  font-size: 0.68rem; 
  color: #94a3b8 !important;
  margin-top: 0.25rem;
}

/* Sidebar section divider */
.sidebar-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(59,130,246,0.3), transparent);
  margin: 1rem 0;
}

/* Sidebar stat pills */
.sidebar-stat {
  background: rgba(59,130,246,0.08);
  border: 1px solid rgba(59,130,246,0.15);
  border-radius: 10px;
  padding: 0.7rem 1rem;
  margin: 0.5rem 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
}

.sidebar-stat:hover {
  background: rgba(59,130,246,0.15);
  border-color: rgba(59,130,246,0.3);
}

.sidebar-stat .s-label { 
  font-size: 0.7rem; 
  color: #94a3b8 !important; 
  font-weight: 500;
}

.sidebar-stat .s-val {   
  font-size: 0.95rem; 
  font-weight: 700; 
  color: #60a5fa !important; 
  font-family: 'JetBrains Mono', monospace;
}

/* ── HERO BANNER MEJORADO ── */
.hero-banner {
  background: linear-gradient(135deg, #0d1c3a 0%, #12244a 40%, #162e5c 80%, #1a3870 100%);
  border-radius: var(--radius);
  padding: 2rem 2.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(59,130,246,0.3);
}

.hero-banner::before {
  content: '';
  position: absolute; top: -80px; right: -80px;
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
  border-radius: 50%;
}

.hero-banner::after {
  content: '';
  position: absolute; bottom: -100px; left: -50px;
  width: 250px; height: 250px;
  background: radial-gradient(circle, rgba(6,182,212,0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.hero-banner .hero-tag {
  display: inline-block;
  background: rgba(59,130,246,0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59,130,246,0.4);
  border-radius: 999px;
  padding: 0.3rem 1rem;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #60a5fa;
  margin-bottom: 1rem;
}

.hero-banner h1 {
  font-size: 2rem; 
  font-weight: 700;
  color: white; 
  margin: 0 0 0.6rem;
  line-height: 1.2;
  text-shadow: 0 2px 10px rgba(0,0,0,0.2);
  letter-spacing: -0.02em;
}

.hero-banner p {
  font-size: 0.9rem; 
  color: #cbd5e1;
  margin: 0; 
  line-height: 1.6;
  max-width: 80%;
}

/* ── KPI CARDS MEJORADAS ── */
.kpi-card {
  background: var(--glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: var(--radius);
  padding: 1.2rem 1.5rem;
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-glow);
  border-color: rgba(59,130,246,0.4);
}

.kpi-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #06b6d4);
}

.kpi-card .kpi-icon {
  font-size: 1.8rem; 
  margin-bottom: 0.75rem;
  display: block;
  filter: drop-shadow(0 0 6px rgba(59,130,246,0.4));
}

.kpi-card .kpi-val {
  font-size: 2.2rem; 
  font-weight: 800;
  color: #f1f5f9;
  font-family: 'JetBrains Mono', monospace;
  line-height: 1;
  margin-bottom: 0.35rem;
}

.kpi-card .kpi-lbl {
  font-size: 0.7rem; 
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.kpi-card .kpi-sub {
  font-size: 0.68rem; 
  color: #60a5fa;
  margin-top: 0.5rem;
}

.kpi-card .kpi-bg-num {
  position: absolute; right: 1rem; bottom: -0.3rem;
  font-size: 4rem; 
  font-weight: 800;
  color: rgba(59,130,246,0.06);
  font-family: 'JetBrains Mono', monospace;
  pointer-events: none;
  line-height: 1;
}

/* ── SECTION HEADERS MEJORADOS ── */
.section-wrap {
  display: flex; 
  align-items: center; 
  gap: 0.75rem;
  margin: 2rem 0 1.2rem;
}

.section-icon {
  width: 42px; 
  height: 42px;
  background: linear-gradient(135deg, #1e6fdf, #06b6d4);
  border-radius: 12px;
  display: flex; 
  align-items: center; 
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 4px 12px rgba(59,130,246,0.3);
  flex-shrink: 0;
}

.section-title {
  font-size: 1.2rem; 
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.01em;
}

.section-line {
  flex: 1; 
  height: 1px;
  background: linear-gradient(90deg, rgba(59,130,246,0.3), transparent);
}

/* ── CHART CARDS MEJORADAS ── */
.chart-card {
  background: var(--glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: var(--radius);
  padding: 1.2rem 1.2rem;
  box-shadow: var(--shadow-sm);
  margin-bottom: 1rem;
  transition: all 0.3s ease;
}

.chart-card:hover { 
  box-shadow: var(--shadow-md);
  border-color: rgba(59,130,246,0.3);
}

.chart-card h4 {
  font-size: 0.8rem; 
  font-weight: 700;
  color: #60a5fa;
  text-transform: uppercase; 
  letter-spacing: 0.08em;
  margin: 0 0 1rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid rgba(59,130,246,0.2);
}

/* ── TABLE STYLING MEJORADO ── */
.stDataFrame { 
  border-radius: var(--radius-sm) !important; 
  overflow: hidden !important;
  box-shadow: var(--shadow-sm) !important;
  background: rgba(15, 30, 58, 0.9) !important;
}

.stDataFrame thead tr th {
  background: #0f1e3a !important;
  color: #60a5fa !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.75rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
}

.stDataFrame tbody td {
  color: #cbd5e1 !important;
  font-size: 0.8rem !important;
}

/* ── ANIMATED ENTRY ── */
@keyframes fadeUp {
  from { opacity:0; transform:translateY(30px); }
  to   { opacity:1; transform:translateY(0); }
}

.fade-up { 
  animation: fadeUp 0.6s cubic-bezier(0.2, 0.9, 0.4, 1.1) forwards; 
}

.fade-up-1 { animation-delay: 0.05s; opacity:0; }
.fade-up-2 { animation-delay: 0.12s; opacity:0; }
.fade-up-3 { animation-delay: 0.19s; opacity:0; }
.fade-up-4 { animation-delay: 0.26s; opacity:0; }

/* ── PULSE BADGE ── */
@keyframes pulse-ring {
  0%   { transform: scale(0.9); opacity: 0.5; }
  50%  { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(0.9); opacity: 0.5; }
}

.live-badge {
  display: inline-flex; 
  align-items: center; 
  gap: 0.5rem;
  background: rgba(59,130,246,0.15);
  border: 1px solid rgba(59,130,246,0.35);
  border-radius: 999px;
  padding: 0.3rem 0.9rem;
  font-size: 0.7rem; 
  font-weight: 600;
  color: #60a5fa;
  letter-spacing: 0.05em;
}

.live-dot {
  width: 8px; 
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  animation: pulse-ring 2s ease-in-out infinite;
  box-shadow: 0 0 6px #3b82f6;
}

/* ── FOOTER MEJORADO ── */
.footer-wrap {
  margin-top: 3rem;
  padding: 1.2rem 2rem;
  background: rgba(15, 30, 58, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: var(--radius);
  text-align: center;
}

.footer-wrap p { 
  font-size: 0.75rem; 
  color: #94a3b8; 
  margin: 0; 
}

.footer-wrap strong { 
  color: #60a5fa; 
  font-weight: 600;
}

/* ── BUTTONS & INTERACTIVE ELEMENTS ── */
.stButton > button {
  background: linear-gradient(135deg, #1e6fdf, #3b82f6) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}

.stButton > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59,130,246,0.3);
}

/* Select box styling */
.stSelectbox > div > div {
  background-color: rgba(15, 30, 58, 0.8) !important;
  border-color: rgba(59,130,246,0.3) !important;
  color: #f1f5f9 !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor":  "rgba(15,30,58,0.5)",
    "font_family":   "Inter",
    "font_color":    "#e2e8f0",
    "margin":        dict(t=48, l=16, r=16, b=16),
}

BLUE_SCALE   = ["#0f1e3a", "#1e3a5f", "#2e5a8a", "#3b82f6", "#60a5fa", "#93c5fd"]
BLUE_SCALE2  = ["#1e3a5f", "#3b82f6", "#60a5fa"]
ACCENT_COLORS = ["#3b82f6", "#06b6d4", "#1e6fdf", "#0891b2", "#2e5a8a", "#60a5fa", "#0e7490"]

def themed_layout(fig, title="", height=360):
    fig.update_layout(
        **CHART_THEME,
        title=dict(
            text=title, 
            font=dict(size=13, color="#60a5fa", family="Inter"), 
            x=0, 
            y=0.97
        ),
        height=height,
        hoverlabel=dict(
            bgcolor="#0f1e3a", 
            font_color="#f1f5f9",
            font_family="Inter", 
            font_size=12,
            bordercolor="rgba(59,130,246,0.5)",
        ),
        xaxis=dict(
            gridcolor="rgba(59,130,246,0.1)", 
            linecolor="rgba(59,130,246,0.2)", 
            tickfont=dict(size=11, color="#cbd5e1"),
            title_font=dict(size=11, color="#94a3b8")
        ),
        yaxis=dict(
            gridcolor="rgba(59,130,246,0.1)", 
            linecolor="rgba(59,130,246,0.2)", 
            tickfont=dict(size=11, color="#cbd5e1"),
            title_font=dict(size=11, color="#94a3b8")
        ),
    )
    return fig

def section(icon, title):
    st.markdown(f"""
    <div class="section-wrap">
      <div class="section-icon">{icon}</div>
      <div class="section-title">{title}</div>
      <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)

def chart_card(title_text):
    st.markdown(f'<div class="chart-card"><h4>{title_text}</h4>', unsafe_allow_html=True)

def chart_card_end():
    st.markdown('</div>', unsafe_allow_html=True)

STOPWORDS = {
    "the","and","of","in","a","to","for","is","with","was","were","are","as",
    "an","on","that","this","at","by","be","from","has","have","had","it","its",
    "not","or","also","we","our","their","these","those","been","can","may","but",
    "which","than","more","all","no","de","la","en","el","los","las","se","un",
    "una","con","del","por","al","skin","cancer","melanoma","patients","study",
    "results","used","using","between","among","however","associated","compared",
    "after","based","risk","high","low","increased","significantly","use","were",
}

def extract_keywords(series, sep=";", top_n=30):
    c = Counter()
    for cell in series.dropna():
        for kw in str(cell).split(sep):
            kw = kw.strip().lower()
            if kw and len(kw) > 2 and kw not in STOPWORDS:
                c[kw] += 1
    return c.most_common(top_n)

def tokenize_abstracts(series, top_n=30):
    c = Counter()
    for text in series.dropna():
        for w in re.findall(r'\b[a-zA-Z]{4,}\b', str(text).lower()):
            if w not in STOPWORDS:
                c[w] += 1
    return c.most_common(top_n)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════
CSV_URL = "https://raw.githubusercontent.com/juliocastrolimas16-boop/dashboard.scopus/main/Grupo4_scopus.csv"

@st.cache_data(show_spinner=False)
def load_data(url):
    try:
        df = pd.read_csv(url, encoding="utf-8", on_bad_lines="skip")
    except Exception:
        df = pd.read_csv(url, encoding="latin-1", on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    col_map = {
        "Authors":"authors","Author(s) ID":"author_ids","Title":"title",
        "Year":"year","Source title":"source","Cited by":"cited_by",
        "Abstract":"abstract","Author Keywords":"keywords",
        "Index Keywords":"index_keywords","Document Type":"doc_type",
        "Affiliations":"affiliations","Language of Original Document":"language",
        "Publisher":"publisher","ISSN":"issn","DOI":"doi","Link":"link",
    }
    df.rename(columns={k:v for k,v in col_map.items() if k in df.columns}, inplace=True)
    if "year"     in df.columns: df["year"]     = pd.to_numeric(df["year"],     errors="coerce")
    if "cited_by" in df.columns: df["cited_by"] = pd.to_numeric(df["cited_by"], errors="coerce").fillna(0).astype(int)
    return df

with st.spinner("⏳ Cargando datos desde GitHub..."):
    df_raw = load_data(CSV_URL)

if df_raw.empty:
    st.error("❌ No se pudo cargar el dataset. Verifica la URL.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <div class="logo-icon">🔬</div>
      <div class="logo-title">SkinCare Research<br>Dashboard</div>
      <div class="logo-sub">Scopus Bibliometric Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown("**⚙️ FILTROS INTERACTIVOS**")
    st.markdown("")

    if "year" in df_raw.columns:
        ymin = int(df_raw["year"].dropna().min())
        ymax = int(df_raw["year"].dropna().max())
        yr_range = st.slider("📅 Rango de Años", ymin, ymax, (ymin, ymax))
    else:
        yr_range = (0, 9999)

    if "doc_type" in df_raw.columns:
        types = sorted(df_raw["doc_type"].dropna().unique().tolist())
        sel_types = st.multiselect("📄 Tipo de Documento", types, default=types)
    else:
        sel_types = []

    if "cited_by" in df_raw.columns:
        cit_min = st.slider("📌 Mínimo de Citas", 0, int(df_raw["cited_by"].max()), 0)
    else:
        cit_min = 0

    # Apply filters
    df = df_raw.copy()
    if "year"     in df.columns: df = df[df["year"].between(yr_range[0], yr_range[1], inclusive="both")]
    if sel_types and "doc_type" in df.columns: df = df[df["doc_type"].isin(sel_types)]
    if "cited_by" in df.columns: df = df[df["cited_by"] >= cit_min]

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown("**📊 RESUMEN ACTIVO**")
    st.markdown("")

    total_articles  = len(df)
    total_citations = int(df["cited_by"].sum()) if "cited_by" in df.columns else 0
    avg_cit         = round(total_citations / max(total_articles, 1), 1)

    st.markdown(f"""
    <div class="sidebar-stat"><span class="s-label">Artículos</span><span class="s-val">{total_articles:,}</span></div>
    <div class="sidebar-stat"><span class="s-label">Citas Totales</span><span class="s-val">{total_citations:,}</span></div>
    <div class="sidebar-stat"><span class="s-label">Citas / Artículo</span><span class="s-val">{avg_cit}</span></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Botón de reset
    if st.button("🔄 Resetear Filtros", use_container_width=True):
        st.rerun()
    
    st.markdown("""
    <div style="font-size:0.65rem; color:#64748b; line-height:1.5; text-align:center; padding:0.5rem;">
      Datos: <strong style="color:#60a5fa">Scopus</strong><br>
      Tema: Prevención del cáncer<br>de piel en hombres
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO BANNER
# ══════════════════════════════════════════════════════════════════════════════
dots_html = "".join(["<span></span>"] * 20)
st.markdown(f"""
<div class="hero-banner fade-up">
  <div class="hero-tag">🧬 Análisis Bibliométrico · Scopus</div>
  <h1>Prevención del Cáncer de Piel en Hombres</h1>
  <p>Dashboard interactivo de investigación científica · Visualización avanzada de publicaciones académicas</p>
  <div style="margin-top:1rem;">
    <span class="live-badge"><span class="live-dot"></span> Datos en Vivo desde GitHub</span>
  </div>
  <div class="hero-dots">{dots_html}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
def count_unique_authors(series):
    s = set()
    for c in series.dropna():
        for a in str(c).split(";"):
            a = a.strip()
            if a: s.add(a)
    return len(s)

unique_authors = count_unique_authors(df["authors"]) if "authors" in df.columns else 0
years_range    = f"{int(df['year'].min())}–{int(df['year'].max())}" if "year" in df.columns and not df["year"].isna().all() else "N/A"
sources_count  = df["source"].nunique() if "source" in df.columns else 0

k1, k2, k3, k4 = st.columns(4)
kpi_data = [
    ("c1", "📄", f"{total_articles:,}", "Artículos", f"Período {years_range}", "01"),
    ("c2", "📌", f"{total_citations:,}", "Citas Totales", f"Promedio {avg_cit}", "02"),
    ("c3", "👥", f"{unique_authors:,}", "Autores Únicos", "En el dataset filtrado", "03"),
    ("c4", "📰", f"{sources_count:,}", "Revistas", "Fuentes académicas", "04"),
]

for col, (cls, icon, val, lbl, sub, num) in zip([k1,k2,k3,k4], kpi_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card {cls} fade-up fade-up-{num[-1]}">
          <span class="kpi-icon">{icon}</span>
          <div class="kpi-val">{val}</div>
          <div class="kpi-lbl">{lbl}</div>
          <div class="kpi-sub">{sub}</div>
          <div class="kpi-bg-num">{num}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — TENDENCIA TEMPORAL
# ══════════════════════════════════════════════════════════════════════════════
section("📅", "Tendencia Temporal de Publicaciones")

col1, col2 = st.columns([3, 2])

with col1:
    if "year" in df.columns:
        pub = df["year"].dropna().astype(int).value_counts().sort_index().reset_index()
        pub.columns = ["Año", "Publicaciones"]
        rolling_avg = pub["Publicaciones"].rolling(3, min_periods=1).mean()

        fig = go.Figure()
        fig.add_bar(
            x=pub["Año"], y=pub["Publicaciones"],
            marker=dict(
                color=pub["Publicaciones"],
                colorscale=BLUE_SCALE,
                line=dict(width=0),
            ),
            name="Publicaciones",
            hovertemplate="<b>%{x}</b><br>📄 Artículos: %{y}<extra></extra>",
        )
        fig.add_scatter(
            x=pub["Año"], y=rolling_avg,
            mode="lines+markers",
            line=dict(color="#06b6d4", width=2.5, dash="dot"),
            marker=dict(size=6, color="#06b6d4", symbol="circle"),
            name="Media Móvil (3 años)",
        )
        themed_layout(fig, height=340)
        fig.update_layout(
            legend=dict(orientation="h", y=1.08, x=0, font_size=11),
            bargap=0.3,
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if "year" in df.columns and "cited_by" in df.columns:
        cit = df.groupby("year")["cited_by"].agg(["sum","mean"]).reset_index()
        cit.columns = ["Año","Total","Promedio"]
        cit["Año"] = cit["Año"].astype(int)

        fig2 = go.Figure()
        fig2.add_scatter(
            x=cit["Año"], y=cit["Total"],
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.15)",
            line=dict(color="#3b82f6", width=2.5),
            mode="lines",
            name="Citas Totales",
            hovertemplate="<b>%{x}</b><br>📌 Citas: %{y:,}<extra></extra>",
        )
        themed_layout(fig2, "Citas por Año", height=340)
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — AUTORES
# ══════════════════════════════════════════════════════════════════════════════
section("👥", "Autores Más Destacados")

if "authors" in df.columns and "cited_by" in df.columns:
    rows = []
    for _, row in df.iterrows():
        if pd.isna(row.get("authors")): continue
        for a in str(row["authors"]).split(";"):
            a = a.strip()
            if a: rows.append({"Author": a, "cited_by": row.get("cited_by", 0)})
    adf = pd.DataFrame(rows)

    col3, col4 = st.columns(2)

    if not adf.empty:
        top_cit = adf.groupby("Author")["cited_by"].sum().sort_values(ascending=False).head(15).reset_index()
        top_cit.columns = ["Autor","Citas"]
        top_pub = adf.groupby("Author").size().sort_values(ascending=False).head(15).reset_index()
        top_pub.columns = ["Autor","Artículos"]

        with col3:
            fig3 = go.Figure(go.Bar(
                x=top_cit["Citas"], y=top_cit["Autor"],
                orientation="h",
                marker=dict(
                    color=top_cit["Citas"],
                    colorscale=BLUE_SCALE,
                    line=dict(width=0),
                ),
                hovertemplate="<b>%{y}</b><br>📌 Citas: %{x:,}<extra></extra>",
            ))
            themed_layout(fig3, "🏆 Top 15 · Autores por Citas Totales", height=440)
            fig3.update_layout(yaxis=dict(automargin=True, tickfont=dict(size=10)))
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            fig4 = go.Figure(go.Bar(
                x=top_pub["Artículos"], y=top_pub["Autor"],
                orientation="h",
                marker=dict(
                    color=top_pub["Artículos"],
                    colorscale=list(reversed(BLUE_SCALE)),
                    line=dict(width=0),
                ),
                hovertemplate="<b>%{y}</b><br>📄 Artículos: %{x}<extra></extra>",
            ))
            themed_layout(fig4, "📊 Top 15 · Autores por N° Publicaciones", height=440)
            fig4.update_layout(yaxis=dict(automargin=True, tickfont=dict(size=10)))
            st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — REVISTAS
# ══════════════════════════════════════════════════════════════════════════════
section("📰", "Revistas Científicas Más Activas")

col5, col6 = st.columns([1, 1])

if "source" in df.columns:
    top_src = df["source"].value_counts().head(12).reset_index()
    top_src.columns = ["Revista","Artículos"]

    with col5:
        fig5 = go.Figure(go.Pie(
            labels=top_src["Revista"],
            values=top_src["Artículos"],
            hole=0.55,
            marker=dict(colors=ACCENT_COLORS * 2, line=dict(color="rgba(15,30,58,0.8)", width=2.5)),
            textinfo="percent",
            textfont=dict(size=11, color="#f1f5f9"),
            hovertemplate="<b>%{label}</b><br>📄 %{value} artículos<br>📊 %{percent}<extra></extra>",
        ))
        themed_layout(fig5, "Distribución por Revista (Top 12)", height=380)
        fig5.update_layout(
            legend=dict(font_size=9, x=1.02, font_color="#cbd5e1"),
            annotations=[dict(
                text=f"<b>{top_src['Artículos'].sum()}</b><br><span style='font-size:9px'>artículos</span>",
                x=0.5, y=0.5, font_size=18, font_color="#60a5fa",
                showarrow=False,
            )],
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        if "cited_by" in df.columns:
            src_c = df.groupby("source")["cited_by"].sum().sort_values(ascending=False).head(12).reset_index()
            src_c.columns = ["Revista","Citas"]
            fig6 = go.Figure(go.Bar(
                x=src_c["Citas"], y=src_c["Revista"],
                orientation="h",
                marker=dict(
                    color=src_c["Citas"],
                    colorscale=BLUE_SCALE2,
                    line=dict(width=0),
                ),
                hovertemplate="<b>%{y}</b><br>📌 Citas: %{x:,}<extra></extra>",
            ))
            themed_layout(fig6, "📌 Citas Acumuladas por Revista", height=380)
            fig6.update_layout(yaxis=dict(automargin=True, tickfont=dict(size=10)))
            st.plotly_chart(fig6, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — PALABRAS CLAVE
# ══════════════════════════════════════════════════════════════════════════════
section("🔑", "Análisis de Palabras Clave y Abstracts")

col7, col8 = st.columns(2)

kw_col = "keywords" if "keywords" in df.columns else ("index_keywords" if "index_keywords" in df.columns else None)
if kw_col:
    kw_data = extract_keywords(df[kw_col])
    if kw_data:
        kw_df = pd.DataFrame(kw_data, columns=["KW","Frec"])
        with col7:
            fig7 = go.Figure(go.Bar(
                x=kw_df.head(20)["Frec"],
                y=kw_df.head(20)["KW"],
                orientation="h",
                marker=dict(
                    color=kw_df.head(20)["Frec"],
                    colorscale=BLUE_SCALE,
                    line=dict(width=0),
                ),
                hovertemplate="<b>%{y}</b><br>🔑 Frecuencia: %{x}<extra></extra>",
            ))
            themed_layout(fig7, "🔑 Top 20 · Palabras Clave de Autores", height=440)
            fig7.update_layout(yaxis=dict(automargin=True, tickfont=dict(size=10)))
            st.plotly_chart(fig7, use_container_width=True)

if "abstract" in df.columns:
    ab_data = tokenize_abstracts(df["abstract"])
    ab_df   = pd.DataFrame(ab_data, columns=["Term","Frec"])
    with col8:
        fig8 = go.Figure(go.Treemap(
            labels=ab_df["Term"],
            parents=[""] * len(ab_df),
            values=ab_df["Frec"],
            marker=dict(
                colors=ab_df["Frec"],
                colorscale=BLUE_SCALE,
                showscale=False,
                line=dict(width=2, color="rgba(15,30,58,0.8)"),
            ),
            textfont=dict(family="Inter", size=12, color="#f1f5f9"),
            hovertemplate="<b>%{label}</b><br>📊 Frecuencia: %{value}<extra></extra>",
        ))
        themed_layout(fig8, "🗺️ Mapa de Términos en Abstracts (Top 30)", height=440)
        st.plotly_chart(fig8, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — IMPACTO Y TIPO
# ══════════════════════════════════════════════════════════════════════════════
section("📊", "Impacto Científico y Tipo de Documento")

col9, col10 = st.columns(2)

with col9:
    if "year" in df.columns and "cited_by" in df.columns:
        sc_df = df.dropna(subset=["year","cited_by"]).copy()
        sc_df["year"] = sc_df["year"].astype(int)
        sc_df["Título"] = sc_df.get("title", pd.Series([""]*len(sc_df))).apply(
            lambda x: str(x)[:70]+"…" if len(str(x))>70 else str(x))
        sc_df["size_norm"] = np.sqrt(sc_df["cited_by"] + 1) * 4

        fig9 = go.Figure(go.Scatter(
            x=sc_df["year"], y=sc_df["cited_by"],
            mode="markers",
            marker=dict(
                size=sc_df["size_norm"].clip(4, 40),
                color=sc_df["cited_by"],
                colorscale=BLUE_SCALE,
                opacity=0.8,
                line=dict(width=1, color="rgba(255,255,255,0.3)"),
                showscale=False,
            ),
            text=sc_df["Título"],
            hovertemplate="<b>%{text}</b><br>📅 Año: %{x}<br>📌 Citas: %{y}<extra></extra>",
        ))
        themed_layout(fig9, "🎯 Impacto: Año de Publicación vs Citas", height=400)
        fig9.update_layout(
            xaxis_title="Año de Publicación",
            yaxis_title="Número de Citas",
        )
        st.plotly_chart(fig9, use_container_width=True)

with col10:
    if "doc_type" in df.columns:
        dt = df["doc_type"].value_counts().reset_index()
        dt.columns = ["Tipo","N"]
        fig10 = go.Figure(go.Pie(
            labels=dt["Tipo"], values=dt["N"],
            hole=0.5,
            marker=dict(colors=ACCENT_COLORS, line=dict(color="rgba(15,30,58,0.8)", width=2.5)),
            textinfo="percent+label",
            textfont=dict(size=11, color="#f1f5f9"),
            hovertemplate="<b>%{label}</b><br>📄 %{value} artículos (%{percent})<extra></extra>",
        ))
        themed_layout(fig10, "📄 Distribución por Tipo de Documento", height=400)
        st.plotly_chart(fig10, use_container_width=True)
    elif "cited_by" in df.columns and "year" in df.columns:
        df_box = df.dropna(subset=["year","cited_by"]).copy()
        df_box["Década"] = (df_box["year"].astype(int) // 5 * 5).astype(str) + "s"
        fig10b = px.box(
            df_box, x="Década", y="cited_by",
            color_discrete_sequence=["#3b82f6"],
            title="Distribución de Citas por Quinquenio",
            labels={"cited_by": "Citas"},
        )
        themed_layout(fig10b, height=400)
        st.plotly_chart(fig10b, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — TOP CITED TABLE
# ══════════════════════════════════════════════════════════════════════════════
section("🏆", "Artículos Más Citados")

if "cited_by" in df.columns:
    show_cols = [c for c in ["title","authors","year","source","cited_by"] if c in df.columns]
    top20 = df.sort_values("cited_by", ascending=False).head(20)[show_cols].copy()
    rename = {"title":"Título","authors":"Autores","year":"Año","source":"Revista","cited_by":"Citas"}
    top20.rename(columns={k:v for k,v in rename.items() if k in top20.columns}, inplace=True)
    if "Título"  in top20.columns: top20["Título"]  = top20["Título"].apply(lambda x: str(x)[:85]+"…" if len(str(x))>85 else str(x))
    if "Autores" in top20.columns: top20["Autores"] = top20["Autores"].apply(lambda x: str(x)[:50]+"…" if len(str(x))>50 else str(x))
    if "Año"     in top20.columns: top20["Año"]     = top20["Año"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    st.dataframe(top20.reset_index(drop=True), use_container_width=True, height=430)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — AFILIACIONES
# ══════════════════════════════════════════════════════════════════════════════
if "affiliations" in df.columns:
    section("🌍", "Afiliaciones e Instituciones")

    def extract_countries(series):
        c = Counter()
        for cell in series.dropna():
            for p in str(cell).split(";"):
                p = p.strip()
                if p:
                    country = p.split(",")[-1].strip()
                    if country and len(country) > 1: c[country] += 1
        return c

    cc = extract_countries(df["affiliations"])
    if cc:
        cc_df = pd.DataFrame(cc.most_common(20), columns=["País/Institución","Artículos"])
        fig_cc = go.Figure(go.Bar(
            x=cc_df["Artículos"], y=cc_df["País/Institución"],
            orientation="h",
            marker=dict(color=cc_df["Artículos"], colorscale=BLUE_SCALE, line=dict(width=0)),
            hovertemplate="<b>%{y}</b><br>📄 Artículos: %{x}<extra></extra>",
        ))
        themed_layout(fig_cc, "🏛️ Top 20 Países / Instituciones por Afiliación", height=480)
        fig_cc.update_layout(yaxis=dict(automargin=True, tickfont=dict(size=10)))
        st.plotly_chart(fig_cc, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# EXPORT BUTTON
# ══════════════════════════════════════════════════════════════════════════════
section("💾", "Exportar Datos")

col_export, col_placeholder = st.columns([1, 3])
with col_export:
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv_data,
        file_name="skincare_research_data.csv",
        mime="text/csv",
        use_container_width=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer-wrap">
  <p>
    🔬 <strong>SkinCare Research Dashboard</strong> &nbsp;·&nbsp;
    Análisis bibliométrico sobre prevención del cáncer de piel en hombres &nbsp;·&nbsp;
    Datos: <strong>Scopus</strong> &nbsp;·&nbsp;
    Construido con <strong>Streamlit + Plotly</strong>
  </p>
</div>
""", unsafe_allow_html=True)
