import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import re
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard · Prevención del Cáncer de Piel en Hombres",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* General */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Main background */
    .stApp { background-color: #f7f9fc; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #0f3460 0%, #16213e 100%);
        color: white;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label { color: #a8d8ea !important; font-weight: 600; }

    /* Header banner */
    .hero-banner {
        background: linear-gradient(135deg, #0f3460 0%, #533483 50%, #e94560 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        color: white;
    }
    .hero-banner h1 { font-size: 1.9rem; font-weight: 700; margin: 0; }
    .hero-banner p  { font-size: 0.95rem; opacity: 0.85; margin: 0.4rem 0 0; }

    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border-left: 5px solid #533483;
        margin-bottom: 0.5rem;
    }
    .kpi-card .kpi-val  { font-size: 2.2rem; font-weight: 700; color: #0f3460; }
    .kpi-card .kpi-lbl  { font-size: 0.8rem; color: #6c757d; text-transform: uppercase; letter-spacing: .05em; margin-top: 2px; }
    .kpi-card.accent1   { border-left-color: #e94560; }
    .kpi-card.accent2   { border-left-color: #0f9b8e; }
    .kpi-card.accent3   { border-left-color: #f5a623; }

    /* Section headers */
    .section-header {
        font-size: 1.15rem; font-weight: 700; color: #0f3460;
        border-bottom: 3px solid #e94560;
        padding-bottom: 0.35rem; margin: 1.5rem 0 1rem;
        display: inline-block;
    }

    /* Chart cards */
    .chart-card {
        background: white;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-bottom: 1.2rem;
    }

    /* DataFrame */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ──────────────────────────────────────────────────────────────
CSV_URL = "https://raw.githubusercontent.com/juliocastrolimas16-boop/dashboard.scopus/main/Grupo4_scopus.csv"

@st.cache_data(show_spinner=False)
def load_data(url: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(url, encoding="utf-8", on_bad_lines="skip")
    except Exception:
        df = pd.read_csv(url, encoding="latin-1", on_bad_lines="skip")

    # Normalise column names
    df.columns = [c.strip() for c in df.columns]

    # Map Scopus standard export column names → internal keys
    col_map = {
        "Authors":            "authors",
        "Author(s) ID":       "author_ids",
        "Title":              "title",
        "Year":               "year",
        "Source title":       "source",
        "Cited by":           "cited_by",
        "Abstract":           "abstract",
        "Author Keywords":    "keywords",
        "Index Keywords":     "index_keywords",
        "Document Type":      "doc_type",
        "Affiliations":       "affiliations",
        "Language of Original Document": "language",
        "Publisher":          "publisher",
        "ISSN":               "issn",
        "DOI":                "doi",
        "Link":               "link",
    }
    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)

    # Coerce types
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
    if "cited_by" in df.columns:
        df["cited_by"] = pd.to_numeric(df["cited_by"], errors="coerce").fillna(0).astype(int)

    return df

with st.spinner("Cargando datos desde GitHub…"):
    df_raw = load_data(CSV_URL)

if df_raw.empty:
    st.error("No se pudo cargar el dataset. Verifica la URL o el archivo CSV.")
    st.stop()

# ── SIDEBAR FILTERS ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 Filtros")
    st.markdown("---")

    # Year filter
    if "year" in df_raw.columns:
        ymin = int(df_raw["year"].dropna().min())
        ymax = int(df_raw["year"].dropna().max())
        yr_range = st.slider("Rango de Años", ymin, ymax, (ymin, ymax))
    else:
        yr_range = (0, 9999)

    # Document type filter
    if "doc_type" in df_raw.columns:
        types = sorted(df_raw["doc_type"].dropna().unique().tolist())
        sel_types = st.multiselect("Tipo de Documento", types, default=types)
    else:
        sel_types = []

    # Citation minimum
    if "cited_by" in df_raw.columns:
        cit_min = st.slider("Mínimo de Citas", 0, int(df_raw["cited_by"].max()), 0)
    else:
        cit_min = 0

    st.markdown("---")
    st.markdown("**Fuente del Datos**")
    st.markdown("Scopus — Artículos sobre\nprevención del cáncer de piel en hombres")

# ── APPLY FILTERS ──────────────────────────────────────────────────────────────
df = df_raw.copy()
if "year" in df.columns:
    df = df[df["year"].between(yr_range[0], yr_range[1], inclusive="both")]
if sel_types and "doc_type" in df.columns:
    df = df[df["doc_type"].isin(sel_types)]
if "cited_by" in df.columns:
    df = df[df["cited_by"] >= cit_min]

# ── HERO BANNER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <h1>🔬 Prevención del Cáncer de Piel en Hombres</h1>
  <p>Análisis bibliométrico · Fuente: Scopus · Dashboard interactivo de investigación científica</p>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

total_articles = len(df)
total_citations = int(df["cited_by"].sum()) if "cited_by" in df.columns else 0
years_covered = f"{int(df['year'].min())} – {int(df['year'].max())}" if "year" in df.columns else "N/A"

# unique authors
def count_unique_authors(series):
    authors = set()
    for cell in series.dropna():
        for a in str(cell).split(";"):
            a = a.strip()
            if a:
                authors.add(a)
    return len(authors)

unique_authors = count_unique_authors(df["authors"]) if "authors" in df.columns else 0

with k1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-val">{total_articles:,}</div>
        <div class="kpi-lbl">📄 Artículos</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div class="kpi-card accent1">
        <div class="kpi-val">{total_citations:,}</div>
        <div class="kpi-lbl">📌 Citas Totales</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class="kpi-card accent2">
        <div class="kpi-val">{unique_authors:,}</div>
        <div class="kpi-lbl">👥 Autores Únicos</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class="kpi-card accent3">
        <div class="kpi-val">{years_covered}</div>
        <div class="kpi-lbl">📅 Años Cubiertos</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# SECTION 1 — TEMPORAL ANALYSIS
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-header">📅 Tendencia Temporal de Publicaciones</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    if "year" in df.columns:
        pub_by_year = df["year"].dropna().astype(int).value_counts().sort_index().reset_index()
        pub_by_year.columns = ["Año", "Publicaciones"]

        fig_yr = px.bar(
            pub_by_year, x="Año", y="Publicaciones",
            color="Publicaciones",
            color_continuous_scale=["#a8d8ea", "#533483", "#e94560"],
            title="Distribución de Publicaciones por Año",
            labels={"Publicaciones": "N° Artículos"},
        )
        fig_yr.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            showlegend=False, coloraxis_showscale=False,
            margin=dict(t=50, l=20, r=20, b=20),
            xaxis=dict(tickmode="linear", dtick=1),
        )
        # Add trend line
        fig_yr.add_scatter(
            x=pub_by_year["Año"], y=pub_by_year["Publicaciones"].rolling(3, min_periods=1).mean(),
            mode="lines", line=dict(color="#e94560", width=2.5, dash="dot"),
            name="Tendencia (3-año)",
        )
        st.plotly_chart(fig_yr, use_container_width=True)

with col2:
    if "year" in df.columns and "cited_by" in df.columns:
        cit_by_year = df.groupby("year")["cited_by"].sum().reset_index()
        cit_by_year.columns = ["Año", "Citas"]
        cit_by_year["Año"] = cit_by_year["Año"].astype(int)

        fig_cit = px.area(
            cit_by_year, x="Año", y="Citas",
            title="Citas Acumuladas por Año",
            color_discrete_sequence=["#533483"],
        )
        fig_cit.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=50, l=20, r=20, b=20),
            xaxis=dict(tickmode="linear", dtick=2),
        )
        fig_cit.update_traces(fillcolor="rgba(83,52,131,0.18)")
        st.plotly_chart(fig_cit, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# SECTION 2 — AUTHORS & CITATIONS
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-header">👥 Autores con Más Citas</div>', unsafe_allow_html=True)

col3, col4 = st.columns([1, 1])

if "authors" in df.columns and "cited_by" in df.columns:
    author_rows = []
    for _, row in df.iterrows():
        cits = row.get("cited_by", 0)
        if pd.isna(row.get("authors")):
            continue
        for auth in str(row["authors"]).split(";"):
            auth = auth.strip()
            if auth:
                author_rows.append({"Author": auth, "cited_by": cits})

    auth_df = pd.DataFrame(author_rows)
    if not auth_df.empty:
        top_auth_cit = (
            auth_df.groupby("Author")["cited_by"].sum()
            .sort_values(ascending=False).head(15).reset_index()
        )
        top_auth_cit.columns = ["Autor", "Citas"]

        with col3:
            fig_auth = px.bar(
                top_auth_cit.sort_values("Citas"), x="Citas", y="Autor",
                orientation="h",
                color="Citas",
                color_continuous_scale=["#a8d8ea", "#e94560"],
                title="Top 15 Autores — Citas Totales",
            )
            fig_auth.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                coloraxis_showscale=False,
                margin=dict(t=50, l=20, r=20, b=20),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_auth, use_container_width=True)

        with col4:
            top_auth_count = (
                auth_df.groupby("Author").size()
                .sort_values(ascending=False).head(15).reset_index()
            )
            top_auth_count.columns = ["Autor", "Artículos"]
            fig_auth2 = px.bar(
                top_auth_count.sort_values("Artículos"), x="Artículos", y="Autor",
                orientation="h",
                color="Artículos",
                color_continuous_scale=["#a8d8ea", "#533483"],
                title="Top 15 Autores — N° de Publicaciones",
            )
            fig_auth2.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                coloraxis_showscale=False,
                margin=dict(t=50, l=20, r=20, b=20),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_auth2, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# SECTION 3 — SOURCES / JOURNALS
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-header">📰 Revistas Científicas más Activas</div>', unsafe_allow_html=True)

col5, col6 = st.columns([1, 1])

if "source" in df.columns:
    top_sources = df["source"].value_counts().head(12).reset_index()
    top_sources.columns = ["Revista", "Artículos"]

    with col5:
        fig_src = px.pie(
            top_sources, names="Revista", values="Artículos",
            hole=0.45, title="Distribución por Revista (Top 12)",
            color_discrete_sequence=px.colors.sequential.Purp_r,
        )
        fig_src.update_layout(margin=dict(t=50, l=10, r=10, b=10))
        fig_src.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_src, use_container_width=True)

    with col6:
        if "cited_by" in df.columns:
            src_cit = df.groupby("source")["cited_by"].sum().sort_values(ascending=False).head(12).reset_index()
            src_cit.columns = ["Revista", "Citas"]
            fig_src2 = px.bar(
                src_cit.sort_values("Citas"), x="Citas", y="Revista",
                orientation="h", color="Citas",
                color_continuous_scale=["#a8d8ea", "#0f3460"],
                title="Citas por Revista (Top 12)",
            )
            fig_src2.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                coloraxis_showscale=False,
                margin=dict(t=50, l=20, r=20, b=20),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_src2, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# SECTION 4 — KEYWORD / ABSTRACT ANALYSIS
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-header">🔑 Análisis de Palabras Clave</div>', unsafe_allow_html=True)

STOPWORDS = {
    "the", "and", "of", "in", "a", "to", "for", "is", "with", "was",
    "were", "are", "as", "an", "on", "that", "this", "at", "by", "be",
    "from", "has", "have", "had", "it", "its", "not", "or", "also",
    "we", "our", "their", "these", "those", "been", "can", "may",
    "but", "which", "than", "more", "all", "no", "de", "la", "en",
    "el", "los", "las", "se", "un", "una", "con", "del", "por", "al",
    "skin", "cancer", "melanoma",  # domain-specific high-freq terms
}

def extract_keywords(series, sep=";", stopwords=STOPWORDS, top_n=40):
    counter = Counter()
    for cell in series.dropna():
        for kw in str(cell).split(sep):
            kw = kw.strip().lower()
            if kw and len(kw) > 2 and kw not in stopwords:
                counter[kw] += 1
    return counter.most_common(top_n)

col7, col8 = st.columns([1, 1])

# Author keywords bar chart
kw_col = "keywords" if "keywords" in df.columns else ("index_keywords" if "index_keywords" in df.columns else None)
if kw_col:
    kw_counts = extract_keywords(df[kw_col])
    if kw_counts:
        kw_df = pd.DataFrame(kw_counts, columns=["Palabra Clave", "Frecuencia"])
        with col7:
            fig_kw = px.bar(
                kw_df.head(20).sort_values("Frecuencia"), x="Frecuencia", y="Palabra Clave",
                orientation="h", color="Frecuencia",
                color_continuous_scale=["#a8d8ea", "#e94560"],
                title="Top 20 Palabras Clave de Autores",
            )
            fig_kw.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                coloraxis_showscale=False,
                margin=dict(t=50, l=10, r=10, b=10),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_kw, use_container_width=True)

# Abstract word frequency
if "abstract" in df.columns:
    def tokenize_abstracts(series):
        counter = Counter()
        for text in series.dropna():
            words = re.findall(r'\b[a-zA-Z]{4,}\b', str(text).lower())
            for w in words:
                if w not in STOPWORDS:
                    counter[w] += 1
        return counter

    ab_counts = tokenize_abstracts(df["abstract"])
    ab_df = pd.DataFrame(ab_counts.most_common(25), columns=["Término", "Frecuencia"])

    with col8:
        fig_ab = px.treemap(
            ab_df, path=["Término"], values="Frecuencia",
            title="Términos más Frecuentes en Abstracts (Top 25)",
            color="Frecuencia",
            color_continuous_scale=["#a8d8ea", "#0f3460"],
        )
        fig_ab.update_layout(margin=dict(t=50, l=10, r=10, b=10))
        fig_ab.update_coloraxes(showscale=False)
        st.plotly_chart(fig_ab, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# SECTION 5 — DOCUMENT TYPE & CITATIONS SCATTER
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-header">📊 Análisis de Impacto y Tipo de Documento</div>', unsafe_allow_html=True)

col9, col10 = st.columns([1, 1])

with col9:
    if "doc_type" in df.columns:
        dtype_counts = df["doc_type"].value_counts().reset_index()
        dtype_counts.columns = ["Tipo", "Artículos"]
        fig_dt = px.pie(
            dtype_counts, names="Tipo", values="Artículos", hole=0.4,
            title="Distribución por Tipo de Documento",
            color_discrete_sequence=["#533483", "#e94560", "#0f9b8e", "#f5a623", "#0f3460"],
        )
        fig_dt.update_layout(margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig_dt, use_container_width=True)

with col10:
    if "year" in df.columns and "cited_by" in df.columns:
        scatter_df = df.dropna(subset=["year", "cited_by"]).copy()
        scatter_df["year"] = scatter_df["year"].astype(int)
        scatter_df["title_short"] = scatter_df.get("title", pd.Series([""] * len(scatter_df))).apply(
            lambda x: str(x)[:60] + "…" if len(str(x)) > 60 else str(x)
        )
        fig_sc = px.scatter(
            scatter_df, x="year", y="cited_by",
            size="cited_by", color="cited_by",
            hover_name="title_short" if "title" in scatter_df.columns else None,
            color_continuous_scale=["#a8d8ea", "#533483", "#e94560"],
            title="Impacto de Artículos: Año vs Citas",
            labels={"year": "Año de Publicación", "cited_by": "Número de Citas"},
            size_max=40,
        )
        fig_sc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False,
            margin=dict(t=50, l=20, r=20, b=20),
        )
        st.plotly_chart(fig_sc, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# SECTION 6 — TOP CITED ARTICLES TABLE
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="section-header">🏆 Artículos Más Citados</div>', unsafe_allow_html=True)

if "cited_by" in df.columns:
    show_cols = [c for c in ["title", "authors", "year", "source", "cited_by"] if c in df.columns]
    top_cited = df.sort_values("cited_by", ascending=False).head(20)[show_cols].copy()
    rename_map = {
        "title": "Título", "authors": "Autores", "year": "Año",
        "source": "Revista", "cited_by": "Citas",
    }
    top_cited.rename(columns={k: v for k, v in rename_map.items() if k in top_cited.columns}, inplace=True)
    if "Título" in top_cited.columns:
        top_cited["Título"] = top_cited["Título"].apply(lambda x: str(x)[:80] + "…" if len(str(x)) > 80 else str(x))
    if "Autores" in top_cited.columns:
        top_cited["Autores"] = top_cited["Autores"].apply(lambda x: str(x)[:60] + "…" if len(str(x)) > 60 else str(x))

    st.dataframe(
        top_cited.reset_index(drop=True),
        use_container_width=True,
        height=420,
    )

# ═══════════════════════════════════════════════════════════
# SECTION 7 — AFFILIATIONS / COUNTRIES (if present)
# ═══════════════════════════════════════════════════════════
if "affiliations" in df.columns:
    st.markdown('<div class="section-header">🌍 Afiliaciones Institucionales</div>', unsafe_allow_html=True)

    def extract_countries(series):
        counter = Counter()
        for cell in series.dropna():
            parts = str(cell).split(";")
            for p in parts:
                p = p.strip()
                if p:
                    # last token usually is the country
                    country = p.split(",")[-1].strip()
                    if country and len(country) > 1:
                        counter[country] += 1
        return counter

    country_counts = extract_countries(df["affiliations"])
    if country_counts:
        cc_df = pd.DataFrame(country_counts.most_common(20), columns=["País/Institución", "Artículos"])
        fig_cc = px.bar(
            cc_df.sort_values("Artículos"), x="Artículos", y="País/Institución",
            orientation="h", color="Artículos",
            color_continuous_scale=["#a8d8ea", "#0f3460"],
            title="Top 20 Países / Instituciones por Afiliación",
        )
        fig_cc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False,
            margin=dict(t=50, l=10, r=10, b=10),
            yaxis=dict(automargin=True),
        )
        st.plotly_chart(fig_cc, use_container_width=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#aaa; font-size:0.8rem;'>"
    "Dashboard desarrollado con Streamlit · Datos: Scopus | Prevención del Cáncer de Piel en Hombres"
    "</div>",
    unsafe_allow_html=True,
)
