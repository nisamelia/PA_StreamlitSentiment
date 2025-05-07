import streamlit as st
import pandas as pd
import plotly.express as px
import folium as folium
from folium.plugins import HeatMap, Fullscreen
from streamlit_folium import folium_static
from wordcloud import STOPWORDS, WordCloud
import matplotlib.pyplot as plt
import altair as alt
import branca.colormap as cm
import numpy as np
import geopandas as gdp
import plotly.graph_objects as go

st.set_page_config(layout="wide")
## DEFINE DATA
dinpar_df = pd.read_csv(r"./data/dtw_jumlah_dinpar.csv")
crawled_df = pd.read_csv(r"./data/sa_vader.csv")

# Convert Date Time
def load_data():
    crawled_df["created_at"] = pd.to_datetime(crawled_df["created_at"], format="%a %b %d %H:%M:%S %z %Y")
    crawled_df["month"] = crawled_df["created_at"].dt.month
    return crawled_df

crawled_df = load_data()

basemapLayer = ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"]


# Dictionary nama bulan
list_month = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember", 13: "Semua Bulan"
}

title = st.columns((6,2), gap='medium')
# select1, select2 = st.columns(2)
# title = st.columns((1.5, 3.5, 3.5), gap='medium')
col = st.columns((3, 3, 2), gap='small')
# col1, col2 = st.columns(2)

def dinparMap():
    # Konversi nama kolom dalam dataset menjadi lowercase
    dinpar_df.columns = dinpar_df.columns.str.lower()

    # **Menampilkan Select Box dengan Nama Bulan**
    selected_month_name = st.selectbox("Pilih Bulan", list(list_month.values()))

    # **Mendapatkan angka bulan dari nama bulan yang dipilih**
    selected_month = {v: k for k, v in list_month.items()}[selected_month_name]

    # **Filtering Data**
    if selected_month == 13:
        month_columns = [str(i) for i in range(1, 13)]
        dinpar_df["count"] = dinpar_df[month_columns].sum(axis=1)
    else:
        month_col = str(selected_month)
        if month_col in dinpar_df.columns:
            dinpar_df["count"] = dinpar_df[month_col]
        else:
            st.warning(f"Data untuk bulan {selected_month_name} tidak tersedia.")
            dinpar_df["count"] = 0

    dinpar_df_filtered = dinpar_df[["dtw", "count", "lintang", "bujur"]].copy()
    dinpar_df_filtered.dropna(subset=["lintang", "bujur"], inplace=True)
    dinpar_df_filtered = dinpar_df_filtered[dinpar_df_filtered["count"] > 0]

    def generateWisataMap():
        return folium.Map(location=[-7.949695, 110.492840], zoom_start=9.25, control_scale=True)

    basemapWisata = generateWisataMap()
    Fullscreen(position="topright", title="Expand", title_cancel="Exit", force_separate_button=True).add_to(basemapWisata)

    if not dinpar_df_filtered.empty:
        max_count = dinpar_df_filtered["count"].max() if dinpar_df_filtered["count"].max() > 0 else 1
        dinpar_df_filtered["normalized_count"] = dinpar_df_filtered["count"] / max_count
        HeatMap(dinpar_df_filtered[["lintang", "bujur", "normalized_count"]].values.tolist(), radius=15, blur=10).add_to(basemapWisata)
    else:
        st.warning("Tidak ada data lokasi untuk bulan yang dipilih.")

    # Tambahkan Layer Control
    folium.TileLayer('CartoDB Positron', name="CartoDB Positron").add_to(basemapWisata)
    folium.TileLayer('CartoDB Voyager', name="CartoDB Voyager").add_to(basemapWisata)
    folium.TileLayer('CartoDB DarkMatter', name="CartoDB DarkMatter").add_to(basemapWisata)
    folium.TileLayer('OpenStreetMap', name="OpenStreetMap").add_to(basemapWisata)
    folium.LayerControl(position="topright").add_to(basemapWisata)

    st.subheader(f"Heatmap Wisata DIY 2023- {selected_month_name}")
    folium_static(basemapWisata)

def tweetMap():
    num_month = sorted(crawled_df['month'].unique())

    dict_month = {"Semua Bulan": None}
    dict_month.update({list_month[i]: i for i in num_month})

    selected_month_name = st.selectbox("Pilih Bulan", list(dict_month.keys()))
    selected_month = dict_month[selected_month_name]

    # Filter data tweets berdasarkan bulan
    if selected_month is None:
        monthly_tweets = crawled_df
    else:
        monthly_tweets = crawled_df[crawled_df["month"] == selected_month]

    # Fungsi untuk membuat peta dasar
    def generateTweetMap():
        return folium.Map(location=[-7.949695, 110.492840], zoom_start=9.25, control_scale=True)

    # Buat peta dasar
    basemapTweet = generateTweetMap()

    if not monthly_tweets.empty:
        # Heatmap
        tweet_heatmap = folium.FeatureGroup(name="Heatmap Tweet")
        HeatMap(monthly_tweets[['lintang', 'bujur']].values, zoom=100, radius=15).add_to(tweet_heatmap)
        tweet_heatmap.add_to(basemapTweet)

    Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(basemapTweet)

    # Tambahkan Layer Control
    folium.TileLayer('CartoDB Positron', name="CartoDB Positron").add_to(basemapTweet)
    folium.TileLayer('CartoDB Voyager', name="CartoDB Voyager").add_to(basemapTweet)
    folium.TileLayer('CartoDB DarkMatter', name="CartoDB DarkMatter").add_to(basemapTweet)
    folium.TileLayer('OpenStreetMap', name="OpenStreetMap").add_to(basemapTweet)
    folium.LayerControl(position="topright").add_to(basemapTweet)

    st.write(f"### Heatmap Tweets Wisata DIY 2023 - {selected_month_name}")

    folium_static(basemapTweet)

def totalTweet():
    # Tambahkan FontAwesome
    st.markdown('<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">', unsafe_allow_html=True)
    # st.markdown("""
    #     <style>
    #     .card {
    #         width: 100%;
    #         padding: 20px;
    #         border-radius: 15px;
    #         color: white;
    #         font-size: 32px;
    #         margin-top: 0px; 
    #         display: flex;
    #         justify-content: center;
    #         align-items: center;
    #         text-align: center;
    #     }
    #     .card-red { background-color: #e74c3c; }
    #     </style>
    #     """, unsafe_allow_html=True)

    #     # Tampilkan kartu-kartu
    # st.markdown("""
    #     <div class="card card-red">
    #         <i class="fas fa-building"></i> <b>TWEET</b><br>
    #         <small>2.685</small>
    #     </div>
    #     """, unsafe_allow_html=True)
            # st.metric(label='Total Tweet', value='2.685')
    st.markdown("""
        <style>
        .card {
            width: 100%;
            padding: 20px;
            color: white;
            font-size: 32px;
            margin-top: 0px; 
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        .card-red { background-color: #262730; }
        .card-title {
            font-size: 24px;
            font-weight: normal;
            margin: 0;
        }
        .card-value {
            font-size: 32px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # Isi kartu
    st.markdown("""
        <div class="card card-red">
            <div class="card-title">Tweet</div>
            <div class="card-value">2.685</div>
        </div>
    """, unsafe_allow_html=True)
def wordCloudTweet():
    text_wordcloud = crawled_df["stemmed"].str.cat(sep=" ")
    if text_wordcloud:
        w = WordCloud(background_color="#262730", colormap="OrRd").generate(text_wordcloud)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='black')
        plt.imshow(w, interpolation="bilinear")
        plt.axis("off")
        st.write("<h4 style='text-align: center; color: white; margin-top: 16px;'>WORD CLOUD</h4>", unsafe_allow_html=True)
        st.pyplot(fig)

with title[0]:
    st.write("# PERBANDINGAN DATA DINAS PARIWISATA DAN DATA TWEETS WISATA")

with col[0]:
    dinparMap()

with col[1]:
    tweetMap()

with col[2]:
    totalTweet()
    wordCloudTweet()



st.write("### TWEET")

# Declare Date to Filtering
dt_start = st.date_input("Pilih Tanggal Awal", crawled_df["created_at"].min().date())
dt_end = st.date_input("Pilih Tanggal Akhir", crawled_df["created_at"].max().date())

df_filtered = crawled_df[(crawled_df["created_at"].dt.date >= dt_start) & (crawled_df["created_at"].dt.date <= dt_end)]

# Count Tweets Per Day
df_grouped = df_filtered.groupby(df_filtered["created_at"].dt.date).size().reset_index(name="count")

fig_daily = px.area(
    df_grouped,
    x = "created_at",
    y = "count",
    # markers=True,
    title="Tweet Trends",
    labels={"created_at" : "Date", "count": "Number of Tweets"}
)

# Show the plot in Streamlit
st.plotly_chart(fig_daily, use_container_width=True)

# Load data
crawled_graph = pd.read_csv(r"./data/sa_vader_month.csv")

# Ubah 'created_at' menjadi format datetime
crawled_graph["created_at"] = pd.to_datetime(crawled_graph["created_at"], format="%a %b %d %H:%M:%S %z %Y")

# Ambil nama bulan dari 'created_at'
crawled_graph["month"] = crawled_graph["created_at"].dt.strftime('%B')

# Urutan bulan dalam setahun
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

# Hitung jumlah tweet per bulan
crawled_month = crawled_graph.groupby("month").size().reset_index(name="count")

# Atur kategori bulan agar berurutan
crawled_month["month"] = pd.Categorical(crawled_month["month"], categories=month_order, ordered=True)
crawled_month = crawled_month.sort_values("month")

# Buat grafik batang dengan Plotly
fig_monthly = go.Figure(go.Bar(
    x=crawled_month["month"],
    y=crawled_month["count"],
    marker=dict(color="royalblue"),
    name="Jumlah Tweet Per Bulan",
    text=crawled_month["count"]
))

# Atur layout grafik
fig_monthly.update_layout(
    title="Jumlah Tweet per Bulan",
    xaxis_title="Bulan",
    yaxis_title="Jumlah Tweet",
    xaxis=dict(tickangle=-45),
    template="plotly_dark",
)

# Tampilkan grafik di Streamlit
st.plotly_chart(fig_monthly, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    # Top 10 Data
    dinpar_10 = dinpar_df[['dtw', '13']].sort_values(by='13', ascending=False).head(10)
    dinpar_10.columns = ['dtw', '13']
    dinpar_10_fig = px.bar(dinpar_10,
                    x='dtw',
                    y='13',
                    labels={'dtw': 'Lokasi Wisata', '13': 'Jumlah Pengunjung'},
                    text_auto=True)
    st.plotly_chart(dinpar_10_fig)

with col2:
    # Hitung jumlah penyebutan keyword (matched_keyword)
    jumlah_counts = crawled_df['matched_keyword'].value_counts().reset_index()
    jumlah_counts.columns = ['matched_keyword', 'jumlah']
    # Gabungkan jumlah dengan crawled_df menggunakan merge untuk menghindari duplikasi
    crawled_df = crawled_df.drop_duplicates(subset=['matched_keyword'])  # Hindari duplikasi
    crawled_df = crawled_df.merge(jumlah_counts, on='matched_keyword', how='left')
    
    # Ambil 10 besar
    crawled_cols = crawled_df[['matched_keyword', 'jumlah', 'sumber']].sort_values(by='jumlah', ascending=False).head(10)
    # Buat grafik batang
    crawled_10_fig = px.bar(
        crawled_cols,
        x='matched_keyword',
        y='jumlah',
        labels={'matched_keyword': 'Lokasi Wisata', 'jumlah': 'Jumlah Tweets', 'sumber': 'Sumber'},
        text=crawled_cols['sumber'],
        text_auto=True
        )
    # Tampilkan grafik
    st.plotly_chart(crawled_10_fig)