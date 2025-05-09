import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go

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

# Distribusi PM2.5
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

# Arah Angin Dominan
st.subheader("5 Arah Angin Dominan")
wind_counts = df_filtered["wd"].value_counts().nlargest(5)
fig2 = px.pie(
    values=wind_counts.values, names=wind_counts.index,
    title="Distribusi Arah Angin Dominan", hole=0.4
)
st.plotly_chart(fig2, use_container_width=True)

# Pola Harian PM2.5
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
st.write(
    """Dari tren harian, kita dapat melihat bahwa pada pagi hari jam 6-7 pagi merupakan waktu dengan nilai PM2.5 
    terendah yaitu ~74 µg/m³ hal ini dikarenakan aktivitas masih rendah dan angin pagi. PM2.5 mencapai nilai 
    tertinggi pada jam 10-11 malam yaitu ~88-89 µg/m³ yang dikarenakan akumulasi emisi sepanjang hari dan penurunan 
    kecepatan angin."""
)

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

# Komparasi Tren Dua Stasiun
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

# Tambah kolom 'season' ke df
def get_season(month):
    if month in [3, 4, 5]:
        return 'Semi'
    elif month in [6, 7, 8]:
        return 'Panas'
    elif month in [9, 10, 11]:
        return 'Gugur'
    else:
        return 'Dingin'

df["season"] = df["datetime"].dt.month.map(get_season)
df_clean = df.dropna(subset=["PM2.5", "season"])

# Hitung ringkasan statistik PM2.5 per musim
df_season = (
    df_clean
      .groupby('season')['PM2.5']
      .agg(['mean','median','std','count'])
      .reindex(['Semi','Panas','Gugur','Dingin'])
      .rename(columns={'mean':'Rata2','median':'Median','std':'StdDev','count':'N'})
)

# Bar Chart Interaktif rata-rata PM2.5 per musim
st.header("📊 Perbedaan Rata-Rata Konsentrasi PM2.5 Antar Musim")
fig_bar = px.bar(df_season, x=df_season.index, y='Rata2',
                 labels={'x': 'Musim', 'Rata2': 'PM2.5 (µg/m³)'},
                 title="Rata-Rata PM2.5 per Musim (Beijing, 2013–2017)")
st.plotly_chart(fig_bar, use_container_width=True)

# Boxplot Interaktif distribusi PM2.5 per musim
data = [df_clean[df_clean['season'] == s]['PM2.5'] for s in df_season.index]
fig_box = go.Figure()
for season, values in zip(df_season.index, data):
    fig_box.add_trace(go.Box(y=values, name=season, boxmean=True))
fig_box.update_layout(title="Distribusi PM2.5 per Musim",
                      yaxis_title='PM2.5 (µg/m³)',
                      xaxis_title='Musim')
st.plotly_chart(fig_box, use_container_width=True)

st.write(
    """Dari grafik tersebut, kita dapat melihat bahwa musim dingin mencatat rata-rata PM2.5 tertinggi (~95.7 µg/m³), 
    jauh di atas musim lain. Sepanjang musim dingin (Nov–Feb), pembakaran batubara dan biomassa untuk pemanas rumah 
    tangga di Beijing meningkat pesat, menyebabkan lonjakan emisi PM2.5. Musim panas menunjukkan rata-rata terendah 
    (~64.7 µg/m³). Musim panas (Jun–Aug) didominasi oleh angin muson dan intensitas hujan yang lebih besar, memfasilitasi 
    proses “wet deposition” sehingga PM2.5 tersapu dari atmosfer. Variabilitas (StdDev) terbesar juga terjadi pada musim 
    dingin (107.7), menandakan fluktuasi ekstrem yang tinggi. Musim Semi dan Gugur berada di tengah.."""
)

# Function to categorize pollution levels
def categorize_pollution(pm25):
    if pm25 > 90:
        return 'Tinggi'
    elif pm25 > 70:
        return 'Sedang'
    else:
        return 'Rendah'

# Kategori polusi tiap stasiun (Interaktif)
st.header("📊 Level Polusi Tiap Stasiun")
pm25_avg = df.groupby('station')['PM2.5'].mean().reset_index()
pm25_avg['kategori'] = pm25_avg['PM2.5'].apply(categorize_pollution)

# Interaktif Bar Plot
fig_cat = px.bar(pm25_avg, x='station', y='PM2.5', color='kategori',
                 title='Kategori Tingkat Polusi Udara per Stasiun',
                 labels={'PM2.5': 'Rata-Rata PM2.5 (µg/m³)', 'station': 'Stasiun'},
                 color_discrete_sequence=px.colors.sequential.Viridis)
fig_cat.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_cat, use_container_width=True)

# Kesimpulan
st.subheader("Kesimpulan")
st.write(
    """
Berdasarkan analisis yang dilakukan, beberapa kesimpulan penting dapat diambil:

1. **Konsentrasi PM2.5 di wilayah perkotaan** cenderung lebih tinggi dibandingkan wilayah suburban.
2. **Secara musiman**, konsentrasi rata-rata PM2.5 tertinggi terjadi pada musim **dingin** (Desember–Februari), 
   dengan nilai sekitar **95.7 µg/m³**. Rata-rata terendah tercatat pada musim **panas** (Juni–Agustus), yaitu **64.7 µg/m³**. 
   Hal ini menunjukkan bahwa musim dingin merupakan periode paling kritis terhadap paparan polusi udara, kemungkinan besar 
   disebabkan oleh:
   - 🔥 Peningkatan pembakaran bahan bakar fosil untuk pemanasan.
   - 🌬️ Penurunan kecepatan angin yang membuat polutan terjebak di atmosfer.
   - 🌡️ Fenomena *temperature inversion* yang menahan polutan di lapisan bawah udara.

3. **Dalam skala bulanan**:
   - Bulan dengan rata-rata PM2.5 tertinggi adalah **Desember** (104.58 µg/m³).
   - Bulan dengan rata-rata terendah adalah **Agustus** (53.47 µg/m³).

Pola ini memperkuat indikasi bahwa faktor meteorologis sangat mempengaruhi tingkat pencemaran udara.
"""
)