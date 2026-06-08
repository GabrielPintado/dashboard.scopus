import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter
import re
import numpy as np

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="IA en Detección de Cáncer de Piel",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — dark clinical theme
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Dark background */
.stApp {
    background: #0d1117;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] .css-1d391kg { background: #161b22; }

/* Hero header */
.hero-header {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 40%, #0d1117 100%);
    border: 1px solid #1f6feb;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(31,111,235,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2rem;
    font-weight: 700;
    color: #58a6ff;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 1rem;
    color: #8b949e;
    margin: 0;
    font-weight: 300;
}
.hero-question {
    font-size: 0.95rem;
    color: #e6edf3;
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    background: rgba(31,111,235,0.1);
    border-left: 3px solid #1f6feb;
    border-radius: 0 8px 8px 0;
    font-style: italic;
}

/* KPI Cards */
.kpi-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.4rem 1.5rem;
    text-align: center;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #58a6ff; }
.kpi-number {
    font-size: 2.4rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    color: #58a6ff;
    line-height: 1;
}
.kpi-label {
    font-size: 0.78rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.4rem;
}
.kpi-sub {
    font-size: 0.85rem;
    color: #3fb950;
    margin-top: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Section headings */
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e6edf3;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #21262d;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Chart containers */
.chart-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.2rem;
}

/* Tags */
.ai-tag {
    display: inline-block;
    background: rgba(31,111,235,0.15);
    color: #58a6ff;
    border: 1px solid rgba(31,111,235,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.75rem;
    margin: 0.15rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Divider */
hr { border-color: #21262d; }

/* Streamlit widgets */
.stSelectbox label, .stMultiSelect label, .stSlider label {
    color: #8b949e !important;
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PLOTLY DARK THEME
# ──────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#0d1117",
    font=dict(family="Space Grotesk", color="#8b949e", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d"),
)
COLOR_SEQ = ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#ffa657", "#79c0ff", "#56d364"]

# ──────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/juliocastrolimas16-boop/dashboard.scopus/main/Grupo4_scopus.csv"
    df = pd.read_csv(url)
    df["Cited by"] = pd.to_numeric(df["Cited by"], errors="coerce").fillna(0).astype(int)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    return df

df = load_data()

# ──────────────────────────────────────────────
# SIDEBAR — FILTERS
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔬 Filtros")
    st.markdown("---")

    all_years = sorted(df["Year"].unique())
    year_range = st.slider(
        "Rango de años",
        min_value=int(min(all_years)),
        max_value=int(max(all_years)),
        value=(int(min(all_years)), int(max(all_years))),
    )

    doc_types = ["Todos"] + sorted(df["Document Type"].dropna().unique().tolist())
    selected_doc = st.selectbox("Tipo de documento", doc_types)

    min_cites = st.slider("Mínimo de citas", 0, int(df["Cited by"].max()), 0)

    st.markdown("---")
    st.markdown("**Pregunta de investigación:**")
    st.caption(
        "¿Cuál es la eficacia de los modelos predictivos de IA para la detección temprana del cáncer de piel en hombres?"
    )
    st.markdown("---")
    st.caption("Datos: Scopus · UPCH · Grupo 4")

# ──────────────────────────────────────────────
# FILTER DATA
# ──────────────────────────────────────────────
fdf = df[
    (df["Year"] >= year_range[0])
    & (df["Year"] <= year_range[1])
    & (df["Cited by"] >= min_cites)
]
if selected_doc != "Todos":
    fdf = fdf[fdf["Document Type"] == selected_doc]

# ──────────────────────────────────────────────
# HERO HEADER
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <div class="hero-title">🔬 IA & Detección Temprana de Cáncer de Piel</div>
  <div class="hero-subtitle">Análisis Bibliométrico · Scopus · Prevención en Hombres</div>
  <div class="hero-question">
    ❝ ¿Cuál es la eficacia de los modelos predictivos de IA para la detección temprana del cáncer de piel en hombres? ❞
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# KPI CARDS
# ──────────────────────────────────────────────
total_articles = len(fdf)
total_citations = int(fdf["Cited by"].sum())
avg_citations = round(fdf["Cited by"].mean(), 1) if total_articles > 0 else 0
top_cited = int(fdf["Cited by"].max()) if total_articles > 0 else 0
years_span = year_range[1] - year_range[0] + 1

k1, k2, k3, k4, k5 = st.columns(5)
for col, num, label, sub in [
    (k1, total_articles, "Artículos", f"{years_span} años"),
    (k2, total_citations, "Citas Totales", "impacto acumulado"),
    (k3, avg_citations, "Citas Promedio", "por artículo"),
    (k4, top_cited, "Máx. Citas", "artículo más citado"),
    (k5, fdf["Source title"].nunique(), "Revistas", "fuentes únicas"),
]:
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-number">{num}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# ROW 1: Publicaciones por año + Tipo de documento
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">📅 Tendencia Temporal & Tipología</div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])

with c1:
    year_counts = fdf.groupby("Year").agg(
        Artículos=("Title", "count"),
        Citas=("Cited by", "sum"),
    ).reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=year_counts["Year"], y=year_counts["Artículos"],
               name="Artículos", marker_color="#1f6feb", opacity=0.8),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=year_counts["Year"], y=year_counts["Citas"],
                   name="Citas totales", mode="lines+markers",
                   line=dict(color="#58a6ff", width=2),
                   marker=dict(size=7, color="#58a6ff")),
        secondary_y=True,
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="Publicaciones y Citas por Año", font=dict(color="#e6edf3", size=13)),
        legend=dict(bgcolor="#161b22", bordercolor="#30363d", font=dict(color="#8b949e")),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="N° Artículos", secondary_y=False,
                     gridcolor="#21262d", color="#8b949e")
    fig.update_yaxes(title_text="Citas Totales", secondary_y=True,
                     gridcolor="#21262d", color="#58a6ff")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    doc_counts = fdf["Document Type"].value_counts().reset_index()
    doc_counts.columns = ["Tipo", "Cantidad"]
    fig2 = px.pie(
        doc_counts, values="Cantidad", names="Tipo",
        color_discrete_sequence=COLOR_SEQ,
        hole=0.45,
    )
    fig2.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="Tipo de Documento", font=dict(color="#e6edf3", size=13)),
        legend=dict(bgcolor="#161b22", bordercolor="#30363d", font=dict(color="#8b949e")),
        showlegend=True,
    )
    fig2.update_traces(textfont_color="white", hovertemplate="%{label}: %{value} (%{percent})")
    st.plotly_chart(fig2, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 2: Top artículos más citados (horizontal bar)
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">⭐ Artículos Más Citados (Eficacia de Modelos IA)</div>', unsafe_allow_html=True)

top_n = st.slider("Mostrar top N artículos", 5, min(20, total_articles), 10, key="top_n")
top_articles = fdf.nlargest(top_n, "Cited by")[["Title", "Year", "Cited by", "Authors", "Source title"]].copy()
top_articles["Título Corto"] = top_articles["Title"].str[:70] + "…"

fig3 = px.bar(
    top_articles.sort_values("Cited by"),
    x="Cited by", y="Título Corto",
    orientation="h",
    color="Cited by",
    color_continuous_scale=[[0, "#1f3a5f"], [0.5, "#1f6feb"], [1, "#58a6ff"]],
    hover_data={"Authors": True, "Year": True, "Source title": True, "Título Corto": False},
)
fig3.update_layout(
    **PLOT_LAYOUT,
    height=max(350, top_n * 36),
    title=dict(text=f"Top {top_n} Artículos por Número de Citas", font=dict(color="#e6edf3", size=13)),
    coloraxis_showscale=False,
    yaxis=dict(gridcolor="#21262d", color="#e6edf3"),
    xaxis=dict(gridcolor="#21262d", color="#8b949e", title="Número de citas"),
)
st.plotly_chart(fig3, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 3: Autores más citados + Revistas
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">👥 Autores & Fuentes de Publicación</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    author_cite = {}
    for _, row in fdf.iterrows():
        if pd.notna(row["Authors"]):
            for a in str(row["Authors"]).split(";"):
                a = a.strip()
                if a:
                    author_cite[a] = author_cite.get(a, 0) + int(row["Cited by"])
    top_authors_df = (
        pd.DataFrame(list(author_cite.items()), columns=["Autor", "Citas"])
        .sort_values("Citas", ascending=False)
        .head(12)
    )
    fig4 = px.bar(
        top_authors_df.sort_values("Citas"),
        x="Citas", y="Autor", orientation="h",
        color="Citas",
        color_continuous_scale=[[0, "#1a2f1a"], [0.5, "#238636"], [1, "#3fb950"]],
    )
    fig4.update_layout(
        **PLOT_LAYOUT,
        height=420,
        title=dict(text="Top 12 Autores por Citas Acumuladas", font=dict(color="#e6edf3", size=13)),
        coloraxis_showscale=False,
        yaxis=dict(color="#e6edf3"),
        xaxis=dict(gridcolor="#21262d", color="#8b949e"),
    )
    st.plotly_chart(fig4, use_container_width=True)

with c4:
    journal_stats = (
        fdf.groupby("Source title")
        .agg(Artículos=("Title", "count"), Citas=("Cited by", "sum"))
        .reset_index()
        .sort_values("Citas", ascending=False)
        .head(12)
    )
    fig5 = px.scatter(
        journal_stats, x="Artículos", y="Citas",
        size="Citas", color="Citas",
        color_continuous_scale=[[0, "#3a1f5c"], [0.5, "#8957e5"], [1, "#d2a8ff"]],
        hover_name="Source title",
        text="Source title",
    )
    fig5.update_traces(textposition="top center", textfont=dict(size=9, color="#8b949e"))
    fig5.update_layout(
        **PLOT_LAYOUT,
        height=420,
        title=dict(text="Revistas: Artículos vs Citas", font=dict(color="#e6edf3", size=13)),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig5, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 4: Análisis de palabras clave en abstracts
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">🧠 Tecnologías IA Identificadas en Abstracts</div>', unsafe_allow_html=True)

# Curated AI/ML keyword groups relevant to the research question
AI_KEYWORDS = {
    "Deep Learning": ["deep learning", "convolutional neural", "cnn", "resnet", "vgg", "efficientnet", "neural network"],
    "Machine Learning": ["machine learning", "random forest", "svm", "support vector", "xgboost", "gradient boosting", "lightgbm"],
    "Computer Vision": ["image classification", "dermoscop", "total body photography", "segmentation", "detection", "image analysis"],
    "Diagnóstico Temprano": ["early detection", "early diagnosis", "screening", "early melanoma", "detection temprana"],
    "Rendimiento Modelo": ["sensitivity", "specificity", "accuracy", "auc", "roc", "precision", "recall", "f1", "kappa"],
    "Melanoma": ["melanoma", "skin lesion", "skin cancer", "pigmented", "naev"],
    "Interpretabilidad": ["explainab", "interpretab", "xai", "shap", "grad-cam", "transparent"],
}

keyword_counts = {}
for group, terms in AI_KEYWORDS.items():
    count = 0
    for _, row in fdf.iterrows():
        text = (str(row.get("Abstract", "")) + " " + str(row.get("Title", ""))).lower()
        if any(t in text for t in terms):
            count += 1
    keyword_counts[group] = count

kw_df = pd.DataFrame(list(keyword_counts.items()), columns=["Categoría", "N° Artículos"])
kw_df = kw_df.sort_values("N° Artículos", ascending=False)

fig6 = px.bar(
    kw_df, x="Categoría", y="N° Artículos",
    color="N° Artículos",
    color_continuous_scale=[[0, "#1a2940"], [0.5, "#1f6feb"], [1, "#79c0ff"]],
    text="N° Artículos",
)
fig6.update_layout(
    **PLOT_LAYOUT,
    title=dict(text="Frecuencia de Categorías IA/ML en el Corpus (Responde a la Pregunta de Investigación)",
               font=dict(color="#e6edf3", size=13)),
    coloraxis_showscale=False,
    xaxis=dict(tickangle=-20),
)
fig6.update_traces(textposition="outside", textfont=dict(color="#58a6ff", size=12))
st.plotly_chart(fig6, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 5: Métricas de rendimiento extraídas
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Métricas de Eficacia Reportadas en Artículos Clave</div>', unsafe_allow_html=True)

# Extract performance metrics from abstracts using regex
perf_data = []
patterns = {
    "Accuracy": r"(\d{2,3}(?:\.\d{1,2})?)\s*%?\s*(?:classification\s+)?accuracy",
    "Sensitivity": r"sensitivity\s+(?:of\s+)?(\d{2,3}(?:\.\d{1,2})?)\s*%",
    "Specificity": r"specificity\s+(?:of\s+)?(\d{2,3}(?:\.\d{1,2})?)\s*%",
    "AUC": r"(?:auc|area under)[^=\d]*?(\d\.\d{2,3})",
}

for _, row in fdf.iterrows():
    text = str(row.get("Abstract", "")).lower()
    entry = {"Título": str(row["Title"])[:60] + "…", "Año": row["Year"], "Citas": row["Cited by"]}
    found = False
    for metric, pat in patterns.items():
        m = re.search(pat, text)
        if m:
            val = float(m.group(1))
            if metric == "AUC" and val <= 1.0:
                entry[metric] = val * 100
            elif val <= 100:
                entry[metric] = val
            found = True
    if found and len(entry) > 3:
        perf_data.append(entry)

if perf_data:
    perf_df = pd.DataFrame(perf_data).fillna(0)
    metrics_cols = [c for c in ["Accuracy", "Sensitivity", "Specificity", "AUC"] if c in perf_df.columns]

    # Melt for grouped bar
    melted = perf_df.melt(
        id_vars=["Título", "Año", "Citas"],
        value_vars=metrics_cols,
        var_name="Métrica", value_name="Valor (%)"
    )
    melted = melted[melted["Valor (%)"] > 0]

    fig7 = px.strip(
        melted, x="Métrica", y="Valor (%)",
        color="Métrica",
        color_discrete_sequence=COLOR_SEQ,
        hover_data=["Título", "Año", "Citas"],
        stripmode="overlay",
    )
    fig7.add_hline(y=90, line_dash="dot", line_color="#f78166",
                   annotation_text="Umbral clínico 90%",
                   annotation_font_color="#f78166")
    fig7.update_layout(
        **PLOT_LAYOUT,
        height=400,
        title=dict(text="Distribución de Métricas de Rendimiento (cada punto = un artículo)",
                   font=dict(color="#e6edf3", size=13)),
        yaxis=dict(range=[50, 105], title="Valor (%)"),
        showlegend=False,
    )
    st.plotly_chart(fig7, use_container_width=True)

    # Summary table
    summary_stats = melted.groupby("Métrica")["Valor (%)"].agg(["mean", "max", "min", "count"]).round(1)
    summary_stats.columns = ["Promedio (%)", "Máx (%)", "Mín (%)", "N° Artículos"]
    st.dataframe(
        summary_stats.style
        .format("{:.1f}")
        .background_gradient(subset=["Promedio (%)"], cmap="Blues"),
        use_container_width=True,
    )
else:
    st.info("No se encontraron métricas numéricas explícitas en los abstracts con el rango de filtros actual.")

# ──────────────────────────────────────────────
# ROW 6: Top words in titles (mini word analysis)
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">🏷️ Términos Frecuentes en Títulos</div>', unsafe_allow_html=True)

STOPWORDS = {
    "of", "the", "and", "in", "a", "for", "with", "using", "based", "on",
    "an", "by", "from", "to", "is", "are", "at", "as", "or", "de", "la",
    "en", "y", "el", "un", "una", "for", "into", "through", "via", "its",
}
all_words = []
for title in fdf["Title"].dropna():
    words = re.findall(r"\b[a-zA-Z]{4,}\b", title.lower())
    all_words.extend([w for w in words if w not in STOPWORDS])

word_freq = Counter(all_words).most_common(30)
wf_df = pd.DataFrame(word_freq, columns=["Término", "Frecuencia"])

fig8 = px.treemap(
    wf_df, path=["Término"], values="Frecuencia",
    color="Frecuencia",
    color_continuous_scale=[[0, "#0f3460"], [0.5, "#1f6feb"], [1, "#79c0ff"]],
)
fig8.update_layout(
    **PLOT_LAYOUT,
    height=320,
    title=dict(text="Términos más frecuentes en títulos (tamaño = frecuencia)",
               font=dict(color="#e6edf3", size=13)),
    margin=dict(l=10, r=10, t=40, b=10),
)
fig8.update_traces(textfont=dict(color="white", size=14))
st.plotly_chart(fig8, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 7: Data table
# ──────────────────────────────────────────────
with st.expander("📋 Ver tabla completa de artículos filtrados"):
    display_cols = ["Year", "Title", "Authors", "Source title", "Cited by", "Document Type"]
    st.dataframe(
        fdf[display_cols].sort_values("Cited by", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=400,
    )

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#484f58; font-size:0.8rem; padding:1rem 0;">
    Dashboard Bibliométrico · Grupo 4 · UPCH · Datos: Scopus · 2026
    <br>Pregunta: <em>¿Cuál es la eficacia de los modelos predictivos de IA para la detección temprana del cáncer de piel en hombres?</em>
</div>
""", unsafe_allow_html=True)
