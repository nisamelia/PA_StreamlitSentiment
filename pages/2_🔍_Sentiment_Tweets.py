import folium
import streamlit as st
import pandas as pd
from folium.plugins import HeatMap, Fullscreen, MarkerCluster
from streamlit_folium import folium_static
from wordcloud import STOPWORDS, WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide")
sentiment_df = pd.read_csv(r"./data/sa_vader.csv")
sentiment_df.rename(columns={"bujur": "longitude", "lintang": "latitude"}, inplace=True)
grouped_df = sentiment_df.groupby(["latitude", "longitude", "klasifikasi_vader", "stopwords", "stemmed", "matched_keyword", "created_at"]).size().reset_index(name="count")

st.markdown("""
# <span style='color:orange; font-weight:bold; font-size:48px;'>ANALISIS SENTIMEN</span> PENGGUNA SOSIAL MEDIA X TERHADAP WISATA DIY 2023
""", unsafe_allow_html=True)
with st.expander(':orange[**TENTANG**]', expanded=True):
        st.write(
            '''
    Halaman ini menampilkan sebaran sentimen masyarakat terhadap destinasi wisata di Daerah Istimewa Yogyakarta berdasarkan data dari media sosial X (Twitter) selama tahun 2023.

🔍 Analisis ini mengelompokkan tweet ke dalam tiga kategori sentimen: positif, netral, dan negatif, untuk memberikan gambaran umum tentang persepsi publik terhadap berbagai lokasi wisata di DIY.


            '''
        )

st.subheader(f"Peta Sentimen Wisata DIY 2023")

# def generateSentimentMap(default_location=[-7.949695, 110.492840], default_zoom_start=9.25):
#     base_map = folium.Map(location=default_location, zoom_start=default_zoom_start, control_scale=True)
#     return base_map

# Sidebar untuk memilih sentimen
btn_sentiment = grouped_df["klasifikasi_vader"].unique()
chosen_sentiment = st.selectbox("Pilih Sentimen :", btn_sentiment)
filtered_df = grouped_df[grouped_df["klasifikasi_vader"] == chosen_sentiment].copy()


# def heatmapSentiment():
#     map_type = st.selectbox("Pilih Jenis Peta:", ["Heatmap", "Dotmap"])
#     jumlah_counts = filtered_df['matched_keyword'].value_counts().reset_index()
#     jumlah_counts.columns = ['matched_keyword', 'jumlah']
#     crawled_count = filtered_df.drop_duplicates(subset=['matched_keyword'])
#     crawled_count = crawled_count.merge(jumlah_counts, on='matched_keyword', how='left')

#     m = generateSentimentMap()

#     Fullscreen(
#         position="topright",
#         title="Expand me",
#         title_cancel="Exit me",
#         force_separate_button=True,
#     ).add_to(m)

#     if map_type == "Dotmap":
#         st.write("### Dotmap Sentiment Tweets")

#         marker_cluster = MarkerCluster().add_to(m)

#         for idx, row in crawled_count.iterrows():
#             popup_text = f"""
#             <b>Lokasi Wisata:</b> {row['matched_keyword']}<br>
#             <b>Jumlah Tweet:</b> {row['jumlah']}
#             """
#             folium.CircleMarker(
#                 location=[row['latitude'], row['longitude']],
#                 radius=5 + row['jumlah'] * 0.5,
#                 color='blue',
#                 fill=True,
#                 fill_opacity=0.7,
#                 popup=folium.Popup(popup_text, max_width=250)
#             ).add_to(marker_cluster)

#     else:
#         st.write("### Heatmap Sentiment Tweets")
#         HeatMap(filtered_df[['latitude', 'longitude']], zoom=100, radius=15).add_to(m)
#         # Ambil titik koordinat
#         lat = -7.601157772174116
#         lon = 110.96561597343998

#         # Encode gambar ke base64
#         base_path = os.path.dirname(os.path.abspath(__file__))
#         image_path = os.path.join(base_path, "..", "data", "legenda_2.png")
#         encoded = base64.b64encode(open(image_path, 'rb').read()).decode()

#         # Buat elemen HTML langsung untuk ditampilkan di peta
#         html = f'''
#         <div style="border:2px solid #666; background:white; padding:5px;">
#             <img src="data:image/png;base64,{encoded}" width="200" height="175">
#         </div>
#         '''

#         # Tambahkan sebagai Marker dengan DivIcon
#         folium.Marker(
#             location=[lat, lon],
#             icon=folium.DivIcon(html=html)
#         ).add_to(m)

#     folium.LayerControl(position="topright").add_to(m)
#     folium_static(m)

def heatmapSentiment():
    map_type = st.selectbox(
        "Pilih Jenis Peta (Tweet)",
        ["Heatmap", "Proportional Symbol Map", "3D Column Map"],
        key="sentiment_map_type"
    )

    # Hitung jumlah tweet per lokasi
    agg = filtered_df.groupby(["matched_keyword", "latitude", "longitude"]).size().reset_index(name="count")
    agg["normalized"] = np.log1p(agg["count"]) / np.log1p(agg["count"].max())

    if map_type == "Heatmap":
        fig = px.density_mapbox(
            agg,
            lat="latitude",
            lon="longitude",
            z="normalized",
            radius=40,
            center={"lat": -7.949695, "lon": 110.492840},
            zoom=8.25,
            mapbox_style="carto-positron",
            hover_name="matched_keyword",
            hover_data={"count": True, "normalized": False},
            color_continuous_scale="RdYlGn_r",
            opacity=0.7
        )

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                title=dict(text="Jumlah Tweet", font=dict(color="black", size=12)),
                orientation="h",
                yanchor="bottom",
                y=0,
                xanchor="center",
                x=0.5,
                thickness=15,
                len=0.7,
                tickvals=[0.0, 0.5, 1.0],
                ticktext=["Rendah", "Sedang", "Tinggi"],
                tickfont=dict(color="black")
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    elif map_type == "Proportional Symbol Map":
        fig = px.scatter_mapbox(
            agg,
            lat="latitude",
            lon="longitude",
            size="count",
            color="count",
            size_max=35,
            zoom=8.5,
            center={"lat": -7.949695, "lon": 110.492840},
            mapbox_style="carto-positron",
            color_continuous_scale="Viridis",
            hover_name="matched_keyword",
            hover_data={"count": True}
        )

        min_val = agg["count"].min()
        max_val = agg["count"].max()
        mid_val = (min_val + max_val) / 2

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                title=dict(text="Jumlah Tweet", font=dict(color="black", size=12)),
                orientation="h",
                yanchor="bottom",
                y=0,
                xanchor="center",
                x=0.5,
                thickness=15,
                len=0.7,
                tickvals=[min_val, mid_val, max_val],
                ticktext=["Rendah", "Sedang", "Tinggi"],
                tickfont=dict(color="black")
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    else:  # 3D COLUMN MAP
        norm = mcolors.Normalize(vmin=agg["count"].min(), vmax=agg["count"].max())
        colormap = cm.get_cmap("OrRd")

        agg["color"] = agg["count"].apply(lambda x: [int(c * 255) for c in colormap(norm(x))[:3]] + [200])

        layer = pdk.Layer(
            "ColumnLayer",
            data=agg,
            get_position='[longitude, latitude]',
            get_elevation="count",
            elevation_scale=150,
            radius=400,
            get_fill_color="color",
            pickable=True,
            auto_highlight=True,
            extruded=True
        )

        view_state = pdk.ViewState(
            latitude=-7.949695,
            longitude=110.492840,
            zoom=8.5,
            pitch=60,
            bearing=0
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{matched_keyword}\nJumlah Tweet: {count}"},
            map_style=None  # atau "mapbox://styles/mapbox/light-v10"
        )

        st.pydeck_chart(deck)


def topSentiment():
    jumlah_counts = filtered_df['matched_keyword'].value_counts().reset_index()
    jumlah_counts.columns = ['matched_keyword', 'jumlah']

    crawled_count = filtered_df.drop_duplicates(subset=['matched_keyword'])
    crawled_count = crawled_count.merge(jumlah_counts, on='matched_keyword', how='left')

    crawled_cols = crawled_count[['matched_keyword', 'jumlah', 'klasifikasi_vader']].sort_values(by='jumlah', ascending=False).head(10)
    crawled_10_fig = px.bar(
        crawled_cols,
        x='matched_keyword',
        y='jumlah',
        labels={'matched_keyword': 'Lokasi Wisata', 'jumlah': 'Jumlah Tweets', 'klasifikasi_vader': 'Sentimen'},
        # text=crawled_cols['sumber'],
        title=f"Top 10 Wisata Sentimen {chosen_sentiment}",
        text_auto=True
    )
    # Tampilkan grafik
    st.plotly_chart(crawled_10_fig)

# Grafik Sentimen per Bulan
# Urutan bulan per tahun
def monthSentiment():
    filtered_df["created_at"] = pd.to_datetime(filtered_df["created_at"], format="%a %b %d %H:%M:%S %z %Y")

    # Ambil bulan
    filtered_df["month"] = filtered_df["created_at"].dt.strftime('%B')

    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December']

    # Perhitungan sentimen per bulan
    sentiment_month = filtered_df.groupby("month").size().reset_index(name="count")

    # Kategori bulan berurutan
    sentiment_month["month"] = pd.Categorical(sentiment_month["month"], categories=month_order, ordered=True)
    sentiment_month = sentiment_month.sort_values("month")

    # Buat grafik sentimen per bulan
    fig_st_monthly = go.Figure(go.Bar(
        x=sentiment_month["month"],
        y=sentiment_month["count"],
        marker=dict(color="royalblue"),
        text=sentiment_month["count"]
    ))

    # Atur layout
    fig_st_monthly.update_layout(
        title=f"Jumlah Sentimen {chosen_sentiment} Per Bulan",
        xaxis_title="Bulan",
        yaxis_title="Jumlah Tweet",
        xaxis=dict(tickangle=-45),
        template="plotly_dark",
    )

    # Tampilkan grafik di Streamlit
    st.plotly_chart(fig_st_monthly, use_container_width=True)

def wordCloudSentiment():
    text_wordcloud = filtered_df["stemmed"].str.cat(sep=" ")
    custom_stopwords = set(STOPWORDS)
    custom_stopwords.update(["jogja"])
    if text_wordcloud:
        w = WordCloud(background_color="white", colormap="OrRd", stopwords=custom_stopwords).generate(text_wordcloud)
        fig, ax = plt.subplots(figsize=(10, 5))
        plt.imshow(w, interpolation="bilinear")
        plt.axis("off")
        st.subheader("Sentiment Word Cloud")
        st.pyplot(fig)

def diagramSentiment(sentiment_df):
    if 'klasifikasi_vader' in sentiment_df.columns:
        sentiment_counts = sentiment_df['klasifikasi_vader'].value_counts()
        labels = sentiment_counts.index
        sizes = sentiment_counts.values

        # Warna sesuai dengan contoh (positif-hijau, negatif-merah, netral-kuning)
        color_map = {
            'positif': '#2ECC71',
            'negatif': '#E74C3C',
            'netral': '#F1C40F'
        }
        colors = [color_map.get(label, '#cccccc') for label in labels]

        fig, ax = plt.subplots()
        wedges, texts= ax.pie(
            sizes,
            labels=labels,
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.4)  # Membuat pie menjadi donut
        )
        ax.axis('equal')  # Biar bentuknya bulat

        # Tambahkan teks di tengah donut
        ax.text(0, 0, "Sentiment", ha='center', va='center', fontsize=12)
        st.subheader("Sentiment Tweet")
        st.pyplot(fig)

        # Tampilkan informasi persentase di bawah chart
        total = sum(sizes)
        col1, col2, col3 = st.columns(3)
        for label, size in zip(labels, sizes):
            percent = round(size / total * 100)
            icon = '👍' if label == 'positif' else ('👎' if label == 'negatif' else '👌')
            col = col1 if label == 'positif' else (col2 if label == 'negatif' else col3)
            with col:
                st.markdown(f"{icon} **{percent}%**<br><span style='color:gray'>{label}</span>", unsafe_allow_html=True)

col = st.columns((7,  4), gap='medium')

with col[0]:
    heatmapSentiment()

with col[1]:
    wordCloudSentiment()
    diagramSentiment(sentiment_df)

col2 = st.columns((3, 3, 3), gap='medium')

with col2[0]:
    topSentiment()
with col2[1]:
    monthSentiment()
with col2[2]:
    with st.expander('Tentang', expanded=True):
        st.write(
            '''
            - Metode Analisis Sentimen: [VADER LEXICON-BASED](https://github.com/cjhutto/vaderSentiment).
            - :orange[**Akurasi**]: 80%
            - :orange[**Total Data Analisis**]: 2.685
            - :orange[**Sumber Data**]: Crawling Data Sosial Media X menggunakan library [tweet-harvest](https://github.com/helmisatria/tweet-harvest) (1 Januari 2023 - 31 Desember 2023)
            '''
        )

