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
# CUSTOM CSS — DARK CLINICAL THEME MEJORADO
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600;14..32,700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark background mejorado */
.stApp {
    background: linear-gradient(135deg, #0a0e17 0%, #0d1117 100%);
    color: #e2e8f0;
}

/* Sidebar moderno */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1117 0%, #161b22 100%) !important;
    border-right: 1px solid rgba(31,111,235,0.2);
    backdrop-filter: blur(10px);
}

/* Hero header con efecto glassmorphism */
.hero-header {
    background: linear-gradient(135deg, rgba(15,52,96,0.95) 0%, rgba(22,33,62,0.95) 40%, rgba(13,17,23,0.95) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(31,111,235,0.3);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(31,111,235,0.2) 0%, transparent 70%);
    border-radius: 50%;
    animation: pulse 8s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
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
    background: rgba(31,111,235,0.15);
    border-left: 3px solid #1f6feb;
    border-radius: 0 12px 12px 0;
    font-style: italic;
    backdrop-filter: blur(5px);
}

/* KPI Cards mejoradas */
.kpi-card {
    background: linear-gradient(135deg, #161b22 0%, #1a1f2e 100%);
    border: 1px solid rgba(31,111,235,0.2);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.kpi-card:hover {
    transform: translateY(-4px);
    border-color: #58a6ff;
    box-shadow: 0 8px 24px rgba(31,111,235,0.2);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #1f6feb, #58a6ff);
    transform: scaleX(0);
    transition: transform 0.3s;
}
.kpi-card:hover::before {
    transform: scaleX(1);
}
.kpi-number {
    font-size: 2.6rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.kpi-label {
    font-size: 0.78rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 0.4rem;
}
.kpi-sub {
    font-size: 0.85rem;
    color: #3fb950;
    margin-top: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Section headings con iconos */
.section-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #e6edf3;
    margin: 2rem 0 1.2rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(31,111,235,0.3);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Chart containers con efecto glass */
.chart-card {
    background: rgba(22,27,34,0.6);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(48,54,61,0.5);
    border-radius: 16px;
    padding: 1.2rem;
    transition: all 0.3s;
}
.chart-card:hover {
    border-color: rgba(31,111,235,0.5);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* Badges y tags mejorados */
.ai-tag {
    display: inline-block;
    background: linear-gradient(135deg, rgba(31,111,235,0.2), rgba(88,166,255,0.1));
    color: #58a6ff;
    border: 1px solid rgba(31,111,235,0.3);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.75rem;
    margin: 0.2rem;
    font-family: 'JetBrains Mono', monospace;
    transition: all 0.2s;
}
.ai-tag:hover {
    transform: scale(1.05);
    background: rgba(31,111,235,0.3);
}

/* Botones personalizados */
.stButton > button {
    background: linear-gradient(135deg, #1f6feb, #58a6ff);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: all 0.3s;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(31,111,235,0.4);
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PLOTLY DARK THEME - CORREGIDO (sin xaxis/yaxis)
# ──────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(22,27,34,0)",
    plot_bgcolor="rgba(13,17,23,0.6)",
    font=dict(family="Inter", color="#8b949e", size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(bgcolor="#161b22", font_size=12, font_family="Inter"),
    legend=dict(bgcolor="rgba(22,27,34,0.8)", bordercolor="#30363d", borderwidth=1),
)
COLOR_SEQ = ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#ffa657", "#79c0ff", "#56d364"]

# ──────────────────────────────────────────────
# DATA LOADING CON CACHÉ MEJORADO
# ──────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    url = "https://raw.githubusercontent.com/juliocastrolimas16-boop/dashboard.scopus/main/Grupo4_scopus.csv"
    df = pd.read_csv(url)
    
    # Limpieza robusta de datos
    df["Cited by"] = pd.to_numeric(df["Cited by"], errors="coerce").fillna(0).astype(int)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    
    # Limpiar autores (manejar múltiples separadores)
    df["Authors_clean"] = df["Authors"].fillna("").apply(
        lambda x: [a.strip() for a in re.split(r'[;,]+', str(x)) if a.strip()]
    )
    
    # Limpiar abstracts
    df["Abstract_clean"] = df["Abstract"].fillna("").astype(str)
    df["Title_clean"] = df["Title"].fillna("").astype(str)
    
    return df

df = load_data()

# ──────────────────────────────────────────────
# SIDEBAR — FILTROS MEJORADOS
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔬 Panel de Control")
    st.markdown("---")
    
    # Filtros principales
    all_years = sorted(df["Year"].unique())
    year_range = st.slider(
        "📅 Rango de años",
        min_value=int(min(all_years)),
        max_value=int(max(all_years)),
        value=(int(min(all_years)), int(max(all_years))),
        help="Selecciona el período de publicación"
    )
    
    doc_types = ["Todos"] + sorted(df["Document Type"].dropna().unique().tolist())
    selected_doc = st.selectbox("📄 Tipo de documento", doc_types)
    
    min_cites = st.slider(
        "⭐ Mínimo de citas", 
        0, 
        int(df["Cited by"].max()), 
        0,
        help="Filtrar por impacto mínimo"
    )
    
    # Nuevo filtro de búsqueda en título
    search_term = st.text_input("🔍 Buscar en títulos", placeholder="ej: melanoma, deep learning...")
    
    st.markdown("---")
    
    # Sección de información
    with st.expander("ℹ️ Sobre el Dashboard"):
        st.markdown("""
        **Pregunta de investigación:**
        > ¿Cuál es la eficacia de los modelos predictivos de IA para la detección temprana del cáncer de piel en hombres?
        
        **Métricas clave:**
        - Sensibilidad / Especificidad
        - Accuracy (exactitud)
        - AUC-ROC
        - Comparativa género
        
        **Fuente:** Scopus (2015-2025)
        """)
    
    st.markdown("---")
    st.caption("🔬 Datos: Scopus · UPCH · Grupo 4")

# ──────────────────────────────────────────────
# FILTER DATA MEJORADO
# ──────────────────────────────────────────────
def apply_filters(df, year_range, selected_doc, min_cites, search_term):
    fdf = df[
        (df["Year"] >= year_range[0]) &
        (df["Year"] <= year_range[1]) &
        (df["Cited by"] >= min_cites)
    ].copy()
    
    if selected_doc != "Todos":
        fdf = fdf[fdf["Document Type"] == selected_doc]
    
    if search_term:
        mask = fdf["Title_clean"].str.contains(search_term, case=False, na=False) | \
               fdf["Abstract_clean"].str.contains(search_term, case=False, na=False)
        fdf = fdf[mask]
    
    return fdf

fdf = apply_filters(df, year_range, selected_doc, min_cites, search_term)

# ──────────────────────────────────────────────
# HERO HEADER
# ──────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
  <div class="hero-title">🔬 IA & Detección Temprana de Cáncer de Piel</div>
  <div class="hero-subtitle">Análisis Bibliométrico Avanzado · Scopus 2015-2025 · Enfoque en Prevención Masculina</div>
  <div class="hero-question">
    ❝ ¿Cuál es la eficacia de los modelos predictivos de IA para la detección temprana del cáncer de piel en hombres? ❞
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# KPI CARDS MEJORADAS
# ──────────────────────────────────────────────
total_articles = len(fdf)
total_citations = int(fdf["Cited by"].sum())
avg_citations = round(fdf["Cited by"].mean(), 1) if total_articles > 0 else 0
top_cited = int(fdf["Cited by"].max()) if total_articles > 0 else 0
years_span = year_range[1] - year_range[0] + 1

# Calcular métricas de eficacia
articles_with_metrics = 0
avg_accuracy = 0
if len(fdf) > 0:
    metric_pattern = re.compile(r'(accuracy|sensitivity|specificity|auc)[^0-9]*(\d{2,3}(?:\.\d{1,2})?)', re.I)
    metrics_found = []
    for abstract in fdf["Abstract_clean"]:
        matches = metric_pattern.findall(abstract)
        if matches:
            metrics_found.extend(matches)
    articles_with_metrics = len(set([m[0] for m in metrics_found])) if metrics_found else 0
    if metrics_found:
        numeric_vals = [float(m[1]) for m in metrics_found if m[1].replace('.', '').isdigit()]
        avg_accuracy = round(np.mean(numeric_vals), 1) if numeric_vals else 0

k1, k2, k3, k4, k5, k6 = st.columns(6)
metrics_data = [
    (k1, total_articles, "Artículos", f"{years_span} años", "📊"),
    (k2, total_citations, "Citas Totales", "impacto acumulado", "📈"),
    (k3, avg_citations, "Citas Promedio", "por artículo", "⭐"),
    (k4, top_cited, "Máx. Citas", "artículo más citado", "🏆"),
    (k5, fdf["Source title"].nunique(), "Revistas", "fuentes únicas", "📚"),
    (k6, f"{avg_accuracy}%" if avg_accuracy > 0 else "N/A", "Accuracy Promedio", "de modelos IA", "🎯"),
]

for col, num, label, sub, icon in metrics_data:
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-number">{icon} {num}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# RESULTADO DE FILTROS
# ──────────────────────────────────────────────
if total_articles == 0:
    st.warning("⚠️ No se encontraron artículos con los filtros seleccionados. Por favor, ajusta los criterios.")
    st.stop()

# ──────────────────────────────────────────────
# ROW 1: TENDENCIA TEMPORAL + RESUMEN EJECUTIVO
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Análisis Temporal & Insights Clave</div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])

with c1:
    year_counts = fdf.groupby("Year").agg(
        Artículos=("Title", "count"),
        Citas=("Cited by", "sum"),
    ).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=year_counts["Year"], y=year_counts["Artículos"],
               name="Artículos", marker_color="#1f6feb", opacity=0.8,
               hovertemplate="Año: %{x}<br>Artículos: %{y}<extra></extra>"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=year_counts["Year"], y=year_counts["Citas"],
                   name="Citas totales", mode="lines+markers",
                   line=dict(color="#58a6ff", width=2),
                   marker=dict(size=8, color="#58a6ff", symbol="diamond"),
                   hovertemplate="Año: %{x}<br>Citas: %{y:,}<extra></extra>"),
        secondary_y=True,
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="📊 Evolución de Publicaciones e Impacto", font=dict(color="#e6edf3", size=14)),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    # Aplicar configuraciones de ejes con update_xaxes/update_yaxes
    fig.update_xaxes(gridcolor="#21262d", showgrid=True, gridwidth=0.5)
    fig.update_yaxes(title_text="📄 N° Artículos", secondary_y=False, gridcolor="#21262d", showgrid=True)
    fig.update_yaxes(title_text="📊 Citas Totales", secondary_y=True, gridcolor="#21262d", showgrid=True)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    # Resumen ejecutivo en tarjeta
    growth_rate = 0
    if len(year_counts) > 1:
        first_year = year_counts.iloc[0]["Artículos"]
        last_year = year_counts.iloc[-1]["Artículos"]
        if first_year > 0:
            growth_rate = ((last_year - first_year) / first_year) * 100
    
    st.markdown(f"""
    <div class="chart-card" style="padding:1.5rem;">
        <h4 style="color:#58a6ff; margin-bottom:1rem;">🎯 Resumen Ejecutivo</h4>
        <p style="font-size:0.9rem; line-height:1.6;">
        <strong style="color:#3fb950;">📈 Tasa de crecimiento:</strong> {growth_rate:.1f}%<br>
        <strong style="color:#58a6ff;">🔬 Artículos con métricas IA:</strong> {articles_with_metrics}/{total_articles}<br>
        <strong style="color:#d2a8ff;">🏥 Revistas líderes:</strong> {fdf['Source title'].value_counts().head(3).index.tolist()}<br>
        <strong style="color:#f78166;">⭐ Factor de impacto:</strong> {avg_citations} citas/artículo
        </p>
        <hr style="margin:1rem 0;">
        <p style="font-size:0.85rem; color:#8b949e;">
        <strong>Insight clave:</strong> La investigación en IA para cáncer de piel ha crecido significativamente, con un enfoque creciente en modelos de deep learning para diagnóstico temprano.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# ROW 2: TOP ARTÍCULOS + TIPOS DE DOCUMENTO
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">⭐ Artículos Más Relevantes & Tipología</div>', unsafe_allow_html=True)
c3, c4 = st.columns([2, 1])

with c3:
    top_n = st.slider("📌 Mostrar top N artículos", 5, min(20, total_articles), 10, key="top_n")
    top_articles = fdf.nlargest(top_n, "Cited by")[["Title", "Year", "Cited by", "Authors", "Source title"]].copy()
    top_articles["Título Corto"] = top_articles["Title"].str[:80] + "…" if any(len(t) > 80 for t in top_articles["Title"]) else top_articles["Title"]
    
    fig3 = px.bar(
        top_articles.sort_values("Cited by"),
        x="Cited by", y="Título Corto",
        orientation="h",
        color="Cited by",
        color_continuous_scale=[[0, "#1f3a5f"], [0.5, "#1f6feb"], [1, "#58a6ff"]],
        hover_data={"Authors": True, "Year": True, "Source title": True},
        labels={"Cited by": "Número de citas", "Título Corto": "Artículo"}
    )
    fig3.update_layout(
        **PLOT_LAYOUT,
        height=max(400, top_n * 38),
        title=dict(text=f"🏆 Top {top_n} Artículos Más Citados", font=dict(color="#e6edf3", size=14)),
        coloraxis_showscale=False,
    )
    fig3.update_xaxes(gridcolor="#21262d", title="Número de citas", showgrid=True)
    fig3.update_yaxes(gridcolor="#21262d", color="#e6edf3", automargin=True, showgrid=False)
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    doc_counts = fdf["Document Type"].value_counts().reset_index()
    doc_counts.columns = ["Tipo", "Cantidad"]
    fig2 = px.pie(
        doc_counts, values="Cantidad", names="Tipo",
        color_discrete_sequence=COLOR_SEQ,
        hole=0.45,
        hover_data={"Cantidad": True}
    )
    fig2.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="📋 Distribución por Tipo", font=dict(color="#e6edf3", size=14)),
        legend=dict(bgcolor="rgba(22,27,34,0.8)", bordercolor="#30363d"),
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label", textfont_color="white")
    st.plotly_chart(fig2, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 3: AUTORES + REVISTAS (MEJORADO)
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">👥 Líderes Académicos & Fuentes</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    # Mejorado el procesamiento de autores
    author_cite = {}
    for _, row in fdf.iterrows():
        if row["Authors_clean"]:
            for a in row["Authors_clean"]:
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
        labels={"Citas": "Citas acumuladas", "Autor": ""}
    )
    fig4.update_layout(
        **PLOT_LAYOUT,
        height=450,
        title=dict(text="🏅 Top 12 Autores por Impacto", font=dict(color="#e6edf3", size=14)),
        coloraxis_showscale=False,
    )
    fig4.update_xaxes(gridcolor="#21262d", title="Citas acumuladas", showgrid=True)
    fig4.update_yaxes(gridcolor="#21262d", color="#e6edf3", automargin=True, showgrid=False)
    st.plotly_chart(fig4, use_container_width=True)

with c6:
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
        labels={"Artículos": "Número de artículos", "Citas": "Citas totales"}
    )
    fig5.update_traces(textposition="top center", textfont=dict(size=9, color="#8b949e"))
    fig5.update_layout(
        **PLOT_LAYOUT,
        height=450,
        title=dict(text="📚 Revistas: Productividad vs Impacto", font=dict(color="#e6edf3", size=14)),
        coloraxis_showscale=False,
    )
    fig5.update_xaxes(gridcolor="#21262d", showgrid=True)
    fig5.update_yaxes(gridcolor="#21262d", showgrid=True)
    st.plotly_chart(fig5, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 4: ANÁLISIS DE TECNOLOGÍAS IA (MEJORADO)
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">🧠 Tecnologías de IA Identificadas</div>', unsafe_allow_html=True)

AI_KEYWORDS = {
    "Deep Learning": ["deep learning", "convolutional neural network", "cnn", "resnet", "vgg", "efficientnet", "densenet"],
    "Machine Learning": ["machine learning", "random forest", "svm", "support vector machine", "xgboost", "gradient boosting"],
    "Computer Vision": ["image classification", "dermoscopy", "total body photography", "segmentation", "object detection"],
    "Diagnóstico Temprano": ["early detection", "early diagnosis", "screening", "prevention", "risk assessment"],
    "Métricas de Rendimiento": ["sensitivity", "specificity", "accuracy", "auc", "roc curve", "precision", "recall", "f1 score"],
    "Interpretabilidad": ["explainable ai", "interpretability", "xai", "shap", "grad cam", "attention mechanism"]
}

# Optimizado el conteo con sets
keyword_counts = {}
for group, terms in AI_KEYWORDS.items():
    mask = pd.Series([False] * len(fdf))
    for term in terms:
        mask |= fdf["Abstract_clean"].str.contains(term, case=False, na=False) | \
                fdf["Title_clean"].str.contains(term, case=False, na=False)
    keyword_counts[group] = mask.sum()

kw_df = pd.DataFrame(list(keyword_counts.items()), columns=["Categoría", "N° Artículos"])
kw_df = kw_df.sort_values("N° Artículos", ascending=False)

fig6 = px.bar(
    kw_df, x="Categoría", y="N° Artículos",
    color="N° Artículos",
    color_continuous_scale=[[0, "#1a2940"], [0.5, "#1f6feb"], [1, "#79c0ff"]],
    text="N° Artículos",
    labels={"N° Artículos": "Artículos que mencionan la tecnología"}
)
fig6.update_layout(
    **PLOT_LAYOUT,
    title=dict(text="🤖 Frecuencia de Tecnologías IA en la Literatura", font=dict(color="#e6edf3", size=14)),
    coloraxis_showscale=False,
)
fig6.update_xaxes(tickangle=-15, tickfont=dict(size=11), gridcolor="#21262d")
fig6.update_yaxes(gridcolor="#21262d", showgrid=True)
fig6.update_traces(textposition="outside", textfont=dict(color="#58a6ff", size=11))
st.plotly_chart(fig6, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 5: MÉTRICAS DE RENDIMIENTO (MEJORADO)
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Métricas de Eficacia de Modelos IA</div>', unsafe_allow_html=True)

# Extracción mejorada de métricas
perf_data = []
patterns = {
    "Accuracy": r"accuracy\s*(?:of\s*)?(?:is\s*)?(\d{2,3}(?:\.\d{1,2})?)\s*%",
    "Sensitivity": r"sensitivity\s*(?:of\s*)?(?:is\s*)?(\d{2,3}(?:\.\d{1,2})?)\s*%",
    "Specificity": r"specificity\s*(?:of\s*)?(?:is\s*)?(\d{2,3}(?:\.\d{1,2})?)\s*%",
    "AUC": r"(?:auc|area under the curve)\s*(?:of\s*)?(?:is\s*)?0?\.?(\d{2,3})",
}

for idx, row in fdf.iterrows():
    text = (str(row["Abstract_clean"]) + " " + str(row["Title_clean"])).lower()
    entry = {"Título": str(row["Title"])[:70] + "…", "Año": row["Year"], "Citas": row["Cited by"]}
    metrics_found = False
    
    for metric, pat in patterns.items():
        matches = re.findall(pat, text)
        if matches:
            val = float(matches[0])
            if metric == "AUC":
                val = val / 100 if val > 1 else val * 100
            elif val > 100:
                val = val / 10 if val <= 1000 else val
            if 0 <= val <= 100:
                entry[metric] = val
                metrics_found = True
    
    if metrics_found and len(entry) > 3:
        perf_data.append(entry)

if perf_data:
    perf_df = pd.DataFrame(perf_data)
    metrics_cols = [c for c in ["Accuracy", "Sensitivity", "Specificity", "AUC"] if c in perf_df.columns]
    
    # Gráfico de violín para mejor visualización
    melted = perf_df.melt(
        id_vars=["Título", "Año", "Citas"],
        value_vars=metrics_cols,
        var_name="Métrica", value_name="Valor (%)"
    )
    melted = melted[melted["Valor (%)"] > 0]
    
    fig7 = go.Figure()
    for metric in metrics_cols:
        metric_data = melted[melted["Métrica"] == metric]["Valor (%)"]
        fig7.add_trace(go.Violin(
            y=metric_data,
            x=[metric] * len(metric_data),
            name=metric,
            box_visible=True,
            meanline_visible=True,
            fillcolor=COLOR_SEQ[metrics_cols.index(metric) % len(COLOR_SEQ)],
            line_color="white",
            opacity=0.7,
            points="all",
            pointpos=-1.5,
            jitter=0.3
        ))
    
    fig7.add_hline(y=90, line_dash="dot", line_color="#f78166",
                   annotation_text="Umbral clínico deseable (90%)",
                   annotation_font_color="#f78166")
    fig7.update_layout(
        **PLOT_LAYOUT,
        height=450,
        title=dict(text="📈 Distribución de Métricas de Rendimiento", font=dict(color="#e6edf3", size=14)),
        showlegend=False,
    )
    fig7.update_xaxes(title="Métrica", gridcolor="#21262d")
    fig7.update_yaxes(title="Valor (%)", range=[40, 105], gridcolor="#21262d", showgrid=True)
    st.plotly_chart(fig7, use_container_width=True)
    
    # Tabla resumen mejorada
    col1, col2 = st.columns([2, 1])
    with col1:
        summary_stats = melted.groupby("Métrica")["Valor (%)"].agg(["mean", "median", "max", "min", "count"]).round(1)
        summary_stats.columns = ["Promedio (%)", "Mediana (%)", "Máx (%)", "Mín (%)", "N° Artículos"]
        st.dataframe(
            summary_stats.style
            .format("{:.1f}")
            .background_gradient(subset=["Promedio (%)"], cmap="RdYlGn", vmin=70, vmax=95),
            use_container_width=True,
            height=250,
        )
    
    with col2:
        # Insights adicionales
        best_accuracy = perf_df.loc[perf_df["Accuracy"].idxmax()] if "Accuracy" in perf_df.columns else None
        if best_accuracy is not None:
            st.info(f"🎯 **Mejor desempeño:**\n\n{best_accuracy['Título'][:60]}...\n\n**Accuracy:** {best_accuracy['Accuracy']:.1f}%")
else:
    st.info("ℹ️ No se encontraron métricas de rendimiento explícitas en los abstracts con los filtros actuales. Sugerimos ampliar el rango de búsqueda.")

# ──────────────────────────────────────────────
# ROW 6: ANÁLISIS DE GÉNERO (NUEVO)
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">👨 Enfoque en Población Masculina</div>', unsafe_allow_html=True)

# Palabras clave relacionadas con hombres/población masculina
male_keywords = ["men", "male", "masculine", "gender", "sex", "male population", "men's health"]
female_keywords = ["women", "female", "feminine", "women's health"]

male_articles = 0
female_articles = 0
gender_comparison = 0

for _, row in fdf.iterrows():
    text = (row["Title_clean"] + " " + row["Abstract_clean"]).lower()
    if any(kw in text for kw in male_keywords):
        male_articles += 1
    if any(kw in text for kw in female_keywords):
        female_articles += 1
    if any(kw in text for kw in male_keywords) and any(kw in text for kw in female_keywords):
        gender_comparison += 1

col_g1, col_g2, col_g3 = st.columns(3)

with col_g1:
    st.markdown(f"""
    <div class="chart-card" style="text-align:center;">
        <div class="kpi-number">👨 {male_articles}</div>
        <div class="kpi-label">Artículos con enfoque masculino</div>
        <div class="kpi-sub">{male_articles/total_articles*100:.1f}% del total</div>
    </div>
    """, unsafe_allow_html=True)

with col_g2:
    st.markdown(f"""
    <div class="chart-card" style="text-align:center;">
        <div class="kpi-number">👩 {female_articles}</div>
        <div class="kpi-label">Artículos con enfoque femenino</div>
        <div class="kpi-sub">{female_articles/total_articles*100:.1f}% del total</div>
    </div>
    """, unsafe_allow_html=True)

with col_g3:
    st.markdown(f"""
    <div class="chart-card" style="text-align:center;">
        <div class="kpi-number">⚖️ {gender_comparison}</div>
        <div class="kpi-label">Comparativa por género</div>
        <div class="kpi-sub">Análisis diferenciado</div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# ROW 7: WORD CLOUD EN TÍTULOS (MEJORADO)
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">🏷️ Nube de Términos Clave</div>', unsafe_allow_html=True)

STOPWORDS = {
    "of", "the", "and", "in", "a", "for", "with", "using", "based", "on",
    "an", "by", "from", "to", "is", "are", "at", "as", "or", "de", "la",
    "en", "y", "el", "un", "una", "into", "through", "via", "its", "their",
    "this", "that", "these", "those", "be", "been", "was", "were", "has",
    "have", "having", "do", "does", "did", "doing", "but", "so", "not", "no"
}

all_words = []
for title in fdf["Title_clean"].dropna():
    words = re.findall(r"\b[a-zA-Z]{4,}\b", title.lower())
    all_words.extend([w for w in words if w not in STOPWORDS])

word_freq = Counter(all_words).most_common(40)
wf_df = pd.DataFrame(word_freq, columns=["Término", "Frecuencia"])

fig8 = px.treemap(
    wf_df, path=["Término"], values="Frecuencia",
    color="Frecuencia",
    color_continuous_scale=[[0, "#0f3460"], [0.5, "#1f6feb"], [1, "#79c0ff"]],
    hover_data={"Frecuencia": True}
)
fig8.update_layout(
    **PLOT_LAYOUT,
    height=400,
    title=dict(text="🔤 Términos más frecuentes en títulos (tamaño = frecuencia)", font=dict(color="#e6edf3", size=14)),
    margin=dict(l=10, r=10, t=50, b=10),
)
fig8.update_traces(textfont=dict(color="white", size=12), textinfo="label+value")
st.plotly_chart(fig8, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 8: TABLA DE DATOS + EXPORTACIÓN
# ──────────────────────────────────────────────
with st.expander("📋 Ver tabla completa de artículos filtrados", expanded=False):
    col_export1, col_export2 = st.columns([3, 1])
    
    with col_export2:
        # Botón de exportación a CSV
        csv_data = fdf[["Year", "Title", "Authors", "Source title", "Cited by", "Document Type"]].to_csv(index=False)
        st.download_button(
            label="📥 Exportar a CSV",
            data=csv_data,
            file_name=f"scopus_ia_piel_{year_range[0]}_{year_range[1]}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_export1:
        st.markdown(f"**Total de registros:** {len(fdf)} artículos")
    
    display_cols = ["Year", "Title", "Authors", "Source title", "Cited by", "Document Type"]
    st.dataframe(
        fdf[display_cols].sort_values("Cited by", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=400,
        column_config={
            "Year": st.column_config.NumberColumn("Año", format="%d"),
            "Cited by": st.column_config.NumberColumn("Citas", format="%d"),
            "Title": st.column_config.TextColumn("Título", width="large"),
            "Authors": st.column_config.TextColumn("Autores", width="medium"),
        }
    )

# ──────────────────────────────────────────────
# FOOTER MEJORADO
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#484f58; font-size:0.8rem; padding:1.5rem 0;">
    <strong>Dashboard Bibliométrico Avanzado</strong><br>
    Grupo 4 · UPCH · Datos: Scopus (2015-2025)<br>
    <span style="color:#58a6ff;">🎯 Pregunta de investigación:</span> ¿Cuál es la eficacia de los modelos predictivos de IA para la detección temprana del cáncer de piel en hombres?<br>
    <span style="font-size:0.7rem;">🔬 Herramientas: Streamlit · Plotly · Pandas · Scopus API</span>
</div>
""", unsafe_allow_html=True)

# Mensaje de éxito
st.success("✅ Dashboard actualizado correctamente - Análisis en tiempo real con filtros dinámicos", icon="🎉")
