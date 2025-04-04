
from textwrap import fill
from turtle import color
import jenkspy
import streamlit as st
import pandas as pd
import plotly.express as px
import folium as folium
from folium import IFrame
from folium.plugins import HeatMap, Fullscreen
from streamlit_folium import folium_static
from wordcloud import STOPWORDS, WordCloud
import matplotlib.pyplot as plt
import altair as alt
import branca.colormap as cm
import numpy as np
import geopandas as gdp
import plotly.graph_objects as go


## DEFINE DATA
dinpar_df = pd.read_csv(r"C:\PA_Streamlit\data\dtw_jumlah_dinpar.csv")
crawled_df = pd.read_csv(r"C:\PA_Streamlit\data\sa_vader.csv")

# Convert Date Time
def load_data():
    crawled_df["created_at"] = pd.to_datetime(crawled_df["created_at"], format="%a %b %d %H:%M:%S %z %Y")
    crawled_df["month"] = crawled_df["created_at"].dt.month
    return crawled_df

crawled_df = load_data()

# Declare Date to Filtering
dt_start = st.sidebar.date_input("Pilih Tanggal Awal", crawled_df["created_at"].min().date())
dt_end = st.sidebar.date_input("Pilih Tanggal Akhir", crawled_df["created_at"].max().date())

df_filtered = crawled_df[(crawled_df["created_at"].dt.date >= dt_start) & (crawled_df["created_at"].dt.date <= dt_end)]

# Count Tweets Per Day
df_grouped = df_filtered.groupby(df_filtered["created_at"].dt.date).size().reset_index(name="count")

# Define legend HTML
legend_html = '''
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 180px; height: 100px; 
    background-color: white; border-radius: 5px;
    padding: 10px; border: 2px solid grey; z-index:9999; font-size:14px;
    ">
    <b>Heatmap Intensity</b><br>
    <span style="background:#00FF00; width:20px; height:10px; display:inline-block;"></span> Low <br>
    <span style="background:#FFFF00; width:20px; height:10px; display:inline-block;"></span> Medium <br>
    <span style="background:#FF0000; width:20px; height:10px; display:inline-block;"></span> High <br>
</div>
'''

basemapLayer = ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"]

st.write("# PERBANDINGAN DATA DINAS PARIWISATA DAN DATA TWEETS WISATA")

# Dictionary nama bulan
list_month = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember", 13: "Semua Bulan"
}

col1, col2 = st.columns(2)

admin_diy = gdp.read_file(r"C:\PA_Streamlit\data\admin_diy\DIY_Prov.shp")
if admin_diy.crs != "EPSG:4326":
    admin_diy = admin_diy.to_crs("EPSG:4326")

with col1:
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

    st.subheader(f"Heatmap Wisata - {selected_month_name}")
    folium_static(basemapWisata)

with col2:
    num_month = sorted(crawled_df['month'].unique())

    dict_month = {"Semua Bulan": None}
    dict_month.update({list_month[i]: i for i in num_month})

    selected_month_name = st.selectbox("Pilih Bulan", list(dict_month.keys()))
    selected_month = dict_month[selected_month_name]

    # Menampilkan pilihan bulan yang dipilih
    st.write(f"Anda memilih: {selected_month_name}")

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

    def style_function(feature):
        return {
            "color": "black",          # Outline color (change to red, green, etc.)
            "weight": 1,              # Border thickness
            "fillColor": "black",      # Fill color (change as needed)
            "fillOpacity": 0,       # Fill opacity (0 = transparent, 1 = solid)
            "opacity": 0.5            # Border opacity
            }
    batas_admin_layer = folium.FeatureGroup(name="Batas Administrasi", control=True)
    folium.GeoJson(admin_diy, name="Batas Administrasi", style_function=style_function).add_to(batas_admin_layer)
    batas_admin_layer.add_to(basemapTweet)

    # # Tambahkan Fullscreen Button
    # Fullscreen(
    #     position="topright",
    #     title="Expand me",
    #     title_cancel="Exit me",
    #     force_separate_button=True,
    # ).add_to(basemapTweet)

    if not monthly_tweets.empty:
        # Heatmap
        tweet_heatmap = folium.FeatureGroup(name="Heatmap Tweet")
        HeatMap(monthly_tweets[['lintang', 'bujur']].values, zoom=100, radius=15).add_to(tweet_heatmap)
        tweet_heatmap.add_to(basemapTweet)

        # Circle Map
        tweet_count = pd.read_csv(r".\data\tweet_count.csv")

        # Natural Breaks
        tweet_jenks = tweet_count["frekuensi"].values
        tweet_breaks = jenkspy.jenks_breaks(tweet_jenks, n_classes=5)
        colors = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]

        if selected_month is None:
            tweet_circlemap = folium.FeatureGroup(name="Circle Map")
            # tweet_color = np.linspace(tweet_count["frekuensi"].min(), tweet_count["frekuensi"].max(), 6)
            # colors = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]
            # tweet_color = cm.linear.YlOrRd_09.scale(tweet_count["frekuensi"].min(), tweet_count["frekuensi"].max())
            # tweet_color.caption = "Jumlah Tweet"

            for _, row in tweet_count.iterrows():
                for i in range(5):
                    if tweet_breaks[i] <= row["frekuensi"] < tweet_breaks[i+1]:
                        color = colors[i]
                        break
                    else:
                        color = colors

                folium.CircleMarker(
                    location=[row["lintang"], row["bujur"]],
                    radius=3,
                    color = color,
                    # color=tweet_color(row["frekuensi"]),
                    fill=True,
                    # fill_color=tweet_color(row["frekuensi"]),
                    fill_color = color,
                    fill_opacity=0.8,
                    popup=folium.Popup(f"<b>{row['frasa']}</b><br>Jumlah: {row['frekuensi']}", max_width=200)
                ).add_to(tweet_circlemap)
            tweet_circlemap.add_to(basemapTweet)
    else:
        st.warning("Tidak ada data tweet untuk bulan yang dipilih.")

        # Tambahkan Fullscreen Button
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

    st.write("### Data Tweets Wisata DIY 2023")

    #     # **Legenda Manual**
    # legend_html = f"""
    # <!DOCTYPE html>
    # <html>
    # <head>
    # <style>
    #     table {{
    #         border-collapse: collapse;
    #         width: 100%;
    #         font-size: 12px;
    #     }}
    #     th, td {{
    #         border: 1px solid black;
    #         padding: 5px;
    #         text-align: left;
    #     }}
    #     .color-box {{
    #         width: 15px;
    #         height: 15px;
    #         display: inline-block;
    #         margin-right: 5px;
    #     }}
    # </style>
    # </head>
    # <body>
    #     <b>Klasifikasi Pengunjung</b>
    #     <table>
    #         <tr><th>Warna</th><th>Frekuensi</th></tr>
    #         <tr><td><span class="color-box" style="background:{colors[0]};"></span></td><td>{tweet_breaks[0]} - {tweet_breaks[1]}</td></tr>
    #         <tr><td><span class="color-box" style="background:{colors[1]};"></span></td><td>{tweet_breaks[1]} - {tweet_breaks[2]}</td></tr>
    #         <tr><td><span class="color-box" style="background:{colors[2]};"></span></td><td>{tweet_breaks[2]} - {tweet_breaks[3]}</td></tr>
    #         <tr><td><span class="color-box" style="background:{colors[3]};"></span></td><td>{tweet_breaks[3]} - {tweet_breaks[4]}</td></tr>
    #         <tr><td><span class="color-box" style="background:{colors[4]};"></span></td><td>{tweet_breaks[4]} - {tweet_breaks[5]}</td></tr>
    #     </table>
    # </body>
    # </html>
    # """
    # # Konversi HTML ke IFrame untuk popup
    # iframe = IFrame(legend_html, width=250, height=200)
    # popup = folium.Popup(iframe, max_width=300)

    # # Tambahkan Marker dengan popup legenda ke peta
    # legend_marker = folium.Marker(
    #     location=[-7.7956, 110.3695],  # Koordinat tengah Yogyakarta
    #     popup=popup,
    #     icon=folium.Icon(icon="info-sign", color="blue"),
    # )

    # # Tambahkan ke peta
    # legend_marker.add_to(basemapTweet)

    folium_static(basemapTweet)


text_wordcloud = crawled_df["stemmed"].str.cat(sep=" ")
# custom_stopwords = set(STOPWORDS)
# custom_stopwords.update([
#     "jogja"
# ])
if text_wordcloud:
    w = WordCloud(background_color="white", colormap="OrRd").generate(text_wordcloud)
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.imshow(w, interpolation="bilinear")
    plt.axis("off")
    st.sidebar.write("### WORD CLOUD")
    st.sidebar.pyplot(fig)

st.write("### TWEET")
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
crawled_graph = pd.read_csv(r".\data\sa_vader_month.csv")

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

chart_data = pd.read_csv(r".\data\scatter.csv")
scatter_chart = alt.Chart(chart_data).mark_circle(size=100).encode(
    x=alt.X('frekuensi', title='Jumlah Tweet'),
    y=alt.Y('total', title='Jumlah Pengunjung'),
    color=alt.Color('dtw', scale=alt.Scale(range=['#FF0000', '#0000FF'])),
    tooltip=['frekuensi', 'total', 'dtw']
)
st.altair_chart(scatter_chart, use_container_width=True)