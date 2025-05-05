import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="PM2.5 Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Data
@st.cache_data
def load_data():
    # URL raw file GitHub
    url = "https://raw.githubusercontent.com/107rasyid/belajar-analisis-data-dengan-python/main/dashboard/main_data.csv"
    # Membaca CSV dari URL
    df = pd.read_csv(url, parse_dates=["datetime"])
    return df

# DataFrame utama
df = load_data()

# Sidebar Profil dan Filter
st.sidebar.title("Profil Saya")
st.sidebar.markdown("**Nama:** Rasyid Alfiansyah")
st.sidebar.markdown("**Email:** rasyidalfiansyh@gmail.com")
st.sidebar.markdown("**GitHub:** [107rasyid](https://github.com/107rasyid)")
st.sidebar.markdown("**LinkedIn:** [Rasyid Alfiansyah](https://www.linkedin.com/in/rasyid-alfiansyah/)")
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

# ============================================
# Visualisasi
# ============================================

# 1. Distribusi PM2.5
st.subheader("Distribusi PM2.5 di Semua Stasiun")
pm25_stats = df_filtered["PM2.5"].describe().round(2)
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
fig3 = px.line(
    x=hourly_avg.index, y=hourly_avg.values,
    markers=True, title="Rata-Rata PM2.5 per Jam"
)
fig3.update_layout(xaxis_title="Jam", yaxis_title="PM2.5 (µg/m³)")
st.plotly_chart(fig3, use_container_width=True)

# ============================================
# Insight dan Analisis Lanjutan
# ============================================

# Filter data for stations
df_tren = df[df['station'].isin(['Aotizhongxin', 'Huairou'])].copy()
df_tren['station'] = df_tren['station'].astype(str)

# Calculate monthly average PM2.5
monthly_pm25 = df_tren.groupby(
    ['station', pd.Grouper(key='datetime', freq='ME')],
    observed=True
)['PM2.5'].mean().reset_index()

# Plotting the trend
# Pilih stasiun dan tahun
st.sidebar.subheader("Filter Data")
station_filter = st.sidebar.selectbox("Pilih Stasiun", monthly_pm25['station'].unique())
year_filter = st.sidebar.selectbox("Pilih Tahun", sorted(monthly_pm25['datetime'].dt.year.unique()))

# Filter data sesuai pilihan
filtered_data = monthly_pm25[
    (monthly_pm25['station'] == station_filter) &
    (monthly_pm25['datetime'].dt.year == year_filter)
]

# Plot interaktif berdasarkan filter
st.subheader(f"Tren PM2.5 Bulanan di {station_filter} - Tahun {year_filter}")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=filtered_data, x='datetime', y='PM2.5', marker='o', ax=ax)
ax.set_title(f"PM2.5 Bulanan di {station_filter} ({year_filter})")
ax.set_xlabel("Bulan")
ax.set_ylabel("PM2.5 (µg/m³)")
st.pyplot(fig)

# Insight Tren PM2.5 Bulanan
df_filtered['month'] = df_filtered['datetime'].dt.month
monthly_avg_pm25 = df_filtered.groupby('month')['PM2.5'].mean().round(2)
st.subheader("Rata-Rata PM2.5 Bulanan")
fig4 = px.line(
    x=monthly_avg_pm25.index, y=monthly_avg_pm25.values,
    markers=True, title="Tren Rata-Rata PM2.5 per Bulan"
)
fig4.update_layout(xaxis_title="Bulan", yaxis_title="PM2.5 (µg/m³)")
st.plotly_chart(fig4, use_container_width=True)

st.write(
    """Dari tren bulanan, kita dapat melihat bahwa pada beberapa bulan, seperti bulan Desember dan Januari, 
    tingkat PM2.5 cenderung lebih tinggi, kemungkinan besar akibat pembakaran bahan bakar yang lebih intensif 
    selama musim dingin."""
)

# Function to categorize pollution levels
def categorize_pollution(pm25):
    if pm25 > 90:
        return 'Tinggi'
    elif pm25 > 70:
        return 'Sedang'
    else:
        return 'Rendah'

# Categorize pollution levels for each station
pm25_avg = df.groupby('station')['PM2.5'].mean().reset_index()
pm25_avg['kategori'] = pm25_avg['PM2.5'].apply(categorize_pollution)

# Plotting the pollution categories
st.subheader("Kategori Tingkat Polusi Udara per Stasiun")
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.barplot(data=pm25_avg, x='station', y='PM2.5', hue='kategori', palette='viridis', dodge=False, ax=ax3)
ax3.set_title('Kategori Tingkat Polusi Udara per Stasiun', fontsize=14)
ax3.set_xlabel('Stasiun', fontsize=12)
ax3.set_ylabel('Rata-Rata PM2.5 (µg/m³)', fontsize=12)
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45)
ax3.legend(title='Kategori')
st.pyplot(fig3)

# Kesimpulan
st.subheader("Kesimpulan")
st.write(
    """Berdasarkan analisis yang dilakukan, kita dapat menarik beberapa kesimpulan penting:
    1. PM2.5 di wilayah perkotaan (Aotizhongxin) cenderung lebih tinggi daripada di wilayah suburban (Huairou).
    2. 
    
    Analisis ini dapat menjadi referensi dalam pembuatan kebijakan untuk meningkatkan kualitas udara di perkotaan.
    """
)

# Halaman Komparasi Tren Dua Stasiun
st.header("📊 Komparasi Tren PM2.5 Bulanan Antar Stasiun")

# Pilih dua stasiun
station_options = df["station"].unique().tolist()
col1, col2 = st.columns(2)
with col1:
    stasiun_1 = st.selectbox("Pilih Stasiun 1", station_options, index=station_options.index("Aotizhongxin"))
with col2:
    stasiun_2 = st.selectbox("Pilih Stasiun 2", station_options, index=station_options.index("Huairou"))

# Pilih tahun
available_years = sorted(df["datetime"].dt.year.unique())
selected_year = st.selectbox("Pilih Tahun", available_years, index=available_years.index(2014))

# Filter data dua stasiun & tahun
df_dua_stasiun = df[
    (df["station"].isin([stasiun_1, stasiun_2])) &
    (df["datetime"].dt.year == selected_year)
].copy()

# Hitung rata-rata bulanan
monthly_comparison = df_dua_stasiun.groupby(
    ['station', pd.Grouper(key='datetime', freq='M')]
)['PM2.5'].mean().reset_index()

# Plotting
st.subheader(f"Perbandingan Tren PM2.5 Bulanan: {stasiun_1} vs {stasiun_2} - Tahun {selected_year}")
fig5 = px.line(
    monthly_comparison,
    x='datetime', y='PM2.5',
    color='station', markers=True,
    title=f'Tren Bulanan PM2.5 di {stasiun_1} vs {stasiun_2} ({selected_year})'
)
fig5.update_layout(xaxis_title='Bulan', yaxis_title='PM2.5 (µg/m³)')
st.plotly_chart(fig5, use_container_width=True)

st.caption("Gunakan grafik ini untuk membandingkan dinamika polusi udara antara dua stasiun di tahun yang sama.")