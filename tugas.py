import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ========================================
# KONFIGURASI HALAMAN
# ========================================
st.set_page_config(
    page_title="COVID-19 Vaccination Statistics Dashboard",
    page_icon="💉",
    layout="wide"
)

# ========================================
# LOAD DATASET
# ========================================
@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "country_vaccinations.csv"
    if not data_path.exists():
        st.error("❌ File country_vaccinations.csv tidak ditemukan")
        st.stop()
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# ========================================
# HEADER
# ========================================
st.markdown(
    "<h1 style='text-align:center;color:#2E86C1;'>💉 Dashboard Statistik Vaksinasi COVID-19</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "Visualisasi dan **statistik deskriptif lengkap** data vaksinasi COVID-19 "
    "sebagai bagian dari **SDG 3 – Good Health and Well-Being**"
)
st.markdown("---")

# ========================================
# SIDEBAR FILTER
# ========================================
st.sidebar.header("🔍 Filter Data")

countries = st.sidebar.multiselect(
    "Pilih Negara (minimal 3 agar grafik jelas)",
    options=sorted(df["country"].unique()),
    default=df["country"].unique()[:5]
)

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    [df["date"].min(), df["date"].max()]
)

# ========================================
# FILTER DATA
# ========================================
filtered_df = df[
    (df["country"].isin(countries)) &
    (df["date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

if filtered_df.empty:
    st.warning("⚠️ Data kosong, silakan ubah filter")
    st.stop()

# Data numerik bersih (penting agar grafik muncul)
num_cols = [
    "total_vaccinations",
    "people_vaccinated",
    "people_fully_vaccinated",
    "daily_vaccinations"
]
clean_df = filtered_df[num_cols].dropna()

# Data terakhir per negara
latest = (
    filtered_df.sort_values("date")
    .groupby("country")
    .last()
    .reset_index()
)

# ========================================
# KPI
# ========================================
st.header("📊 Ringkasan Angka Utama")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Jumlah Negara", filtered_df["country"].nunique())
c2.metric("Total Vaksinasi", int(latest["total_vaccinations"].sum()))
c3.metric("Sudah Vaksin", int(latest["people_vaccinated"].sum()))
c4.metric("Vaksin Lengkap", int(latest["people_fully_vaccinated"].sum()))

st.markdown("---")

# ========================================
# TAB
# ========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Tren Waktu",
    "🌍 Diagram Batang",
    "📊 Statistik Deskriptif",
    "📦 Boxplot",
    "🟠 Scatter",
    "🥧 Pie Chart"
])

# ========================================
# TAB 1 – LINE CHART (GARIS + TITIK)
# ========================================
with tab1:
    st.subheader("📈 Tren Vaksinasi Harian")

    fig = px.line(
        filtered_df,
        x="date",
        y="daily_vaccinations",
        color="country",
        markers=True,
        title="Grafik Garis Vaksinasi Harian"
    )
    st.plotly_chart(fig, use_container_width=True)

# ========================================
# TAB 2 – BAR CHART
# ========================================
with tab2:
    st.subheader("🌍 Total Vaksinasi per Negara")

    fig = px.bar(
        latest,
        x="country",
        y="total_vaccinations",
        title="Diagram Batang Total Vaksinasi"
    )
    st.plotly_chart(fig, use_container_width=True)

# ========================================
# TAB 3 – STATISTIK DESKRIPTIF (TABEL + ANGKA)
# ========================================
with tab3:
    st.subheader("📊 Statistik Deskriptif")

    st.dataframe(
        clean_df.describe().round(2),
        use_container_width=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean Harian", int(clean_df["daily_vaccinations"].mean()))
    c2.metric("Median Harian", int(clean_df["daily_vaccinations"].median()))
    c3.metric("Maksimum Harian", int(clean_df["daily_vaccinations"].max()))
    c4.metric("Minimum Harian", int(clean_df["daily_vaccinations"].min()))

# ========================================
# TAB 4 – BOXPLOT (PETAK-PETAK)
# ========================================
with tab4:
    st.subheader("📦 Boxplot Vaksinasi Harian")

    fig = px.box(
        clean_df,
        y="daily_vaccinations",
        points="all",
        title="Boxplot Sebaran Vaksinasi Harian"
    )
    st.plotly_chart(fig, use_container_width=True)

# ========================================
# TAB 5 – SCATTER (TITIK / LINGKARAN)
# ========================================
with tab5:
    st.subheader("🟠 Scatter Plot")

    fig = px.scatter(
        clean_df,
        x="people_vaccinated",
        y="people_fully_vaccinated",
        size="daily_vaccinations",
        color="daily_vaccinations",
        title="Hubungan Vaksinasi Sebagian vs Lengkap",
        hover_data=["daily_vaccinations"]
    )
    st.plotly_chart(fig, use_container_width=True)

# ========================================
# TAB 6 – PIE CHART (LINGKARAN)
# ========================================
with tab6:
    st.subheader("🥧 Pie Chart Proporsi Vaksinasi Lengkap")

    pie_df = latest[["country", "people_fully_vaccinated"]].dropna()

    fig = px.pie(
        pie_df,
        names="country",
        values="people_fully_vaccinated",
        title="Proporsi Vaksinasi Lengkap per Negara"
    )
    st.plotly_chart(fig, use_container_width=True)

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown(
    "<center>📘 Dashboard Statistik Vaksinasi COVID-19 | Streamlit</center>",
    unsafe_allow_html=True
)
