# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="PM2.5 EDA Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Data
@st.cache_data
def load_data():
    # Sesuaikan path jika perlu
    df = pd.read_csv("dashboard/main_data.csv", parse_dates=["datetime"])
    return df

# DataFrame utama
df = load_data()

# Sidebar Profil dan Filter
st.sidebar.title("Profil Saya")
st.sidebar.markdown("**Nama:** Rasyid Alfiansyah")
st.sidebar.markdown("**Email:** rasyidalfiansyh@gmail.com")
st.sidebar.markdown("**GitHub:** [107rasyid](https://github.com/107rasyid)")
st.sidebar.markdown("**LinkedIn:** [Rasyid Alfiansyah](https://www.linkedin.com/in/rasyid-alfiansyah-b61770217/)")
st.sidebar.markdown("---")

# Filter Stasiun
stations = df["station"].unique().tolist()
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun:", stations, default=stations
)

# Filter Tanggal
min_date = df["datetime"].min().date()
max_date = df["datetime"].max().date()
start_date, end_date = st.sidebar.date_input(
    "Rentang Tanggal:", [min_date, max_date],
    min_value=min_date, max_value=max_date
)
st.sidebar.markdown("---")

# Section About
st.sidebar.title("About")
st.sidebar.info(
    "Dashboard ini menampilkan analisis data PM2.5 berdasarkan dataset historis."
)
st.sidebar.caption("April 2025")

# Filtered DataFrame
df_filtered = df[
    (df["station"].isin(selected_stations)) &
    (df["datetime"].dt.date.between(start_date, end_date))
]

# Main Title
st.title("🛰️ Dashboard Analisis PM2.5")

# Navigation
page = st.radio(
    "Pilih Halaman:", ["EDA", "Insight", "Tren Bulanan"],
    horizontal=True
)

# ============================================
# Halaman: EDA
# ============================================
if page == "EDA":
    st.header("Exploratory Data Analysis (EDA)")

    # 1. Distribusi PM2.5
    st.subheader("Distribusi PM2.5 di Semua Stasiun")
    pm25_stats = df_filtered["PM2.5"].describe().round(2)
    st.write(pm25_stats)
    fig1 = px.histogram(
        df_filtered, x="PM2.5", nbins=50,
        title="Distribusi PM2.5", marginal="box"
    )
    fig1.add_vline(
        x=pm25_stats["50%"], line_dash="dash",
        annotation_text=f"Median: {pm25_stats['50%']:.1f}"    
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Arah Angin Dominan
    st.subheader("5 Arah Angin Dominan")
    wind_counts = df_filtered["wd"].value_counts().nlargest(5)
    st.write(wind_counts)
    fig2 = px.pie(
        values=wind_counts.values, names=wind_counts.index,
        title="Distribusi Arah Angin Dominan", hole=0.4
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 3. Pola Harian PM2.5
    st.subheader("Rata-Rata PM2.5 per Jam")
    hourly_avg = df_filtered.groupby(
        df_filtered["datetime"].dt.hour
    )["PM2.5"].mean().round(2)
    st.write(hourly_avg)
    fig3 = px.line(
        x=hourly_avg.index, y=hourly_avg.values,
        markers=True, title="Rata-Rata PM2.5 per Jam"
    )
    fig3.update_layout(xaxis_title="Jam", yaxis_title="PM2.5 (µg/m³)")
    st.plotly_chart(fig3, use_container_width=True)

# ============================================
# Halaman: Insight
# ============================================
elif page == "Insight":
    st.header("Insight Data PM2.5")
    st.markdown(f"""
    - **Rata-rata PM2.5**: {pm25_stats['mean']} µg/m³ (Batas WHO: 25 µg/m³).
    - **Median PM2.5**: {pm25_stats['50%']} µg/m³.
    - **Nilai Maksimum**: {pm25_stats['max']} µg/m³.
    - **Arah Angin Dominan**: {', '.join(wind_counts.index.tolist())}.
    - **Pola Harian**: terendah jam {hourly_avg.idxmin()} ({hourly_avg.min()} µg/m³), tertinggi jam {hourly_avg.idxmax()} ({hourly_avg.max()} µg/m³).
    """
    )

# ============================================
# Halaman: Tren Bulanan
# ============================================
elif page == "Tren Bulanan":
    st.header("Tren Bulanan: Aotizhongxin vs Huairou")
    # Filter stasiun urban vs suburban
    df_tren = df_filtered[df_filtered["station"].isin(['Aotizhongxin','Huairou'])].copy()
    df_tren['month'] = df_tren['datetime'].dt.to_period('M').dt.to_timestamp()
    monthly_pm25 = df_tren.groupby(['month','station'])['PM2.5'].mean().reset_index()
    # Tampilkan pivot table
    pivot = monthly_pm25.pivot(index='month', columns='station', values='PM2.5').round(1)
    st.dataframe(pivot)
    # Plot tren
    fig4 = px.line(
        monthly_pm25, x='month', y='PM2.5', color='station', markers=True,
        title='Tren Bulanan PM2.5 (2013-2017)'
    )
    st.plotly_chart(fig4, use_container_width=True)
