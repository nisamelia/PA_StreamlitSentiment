import streamlit as st
import pydeck as pdk
import pandas as pd
from streamlit_folium import st_folium

# Set konfigurasi halaman Streamlit
st.set_page_config(layout="wide")

# Load data dari CSV
sentiment_df = pd.read_csv(r"C:\PA_Streamlit\data\sa_vader.csv")

# Pastikan nama kolom sesuai dengan data
sentiment_df.rename(columns={"bujur": "longitude", "lintang": "latitude"}, inplace=True)

# Menghitung jumlah tweet per koordinat dan sentimen
grouped_df = sentiment_df.groupby(["latitude", "longitude", "klasifikasi_vader"]).size().reset_index(name="count")

# Mapping warna berdasarkan sentimen
COLOR_MAP = {
    "netral": [253, 250, 246],   # Putih
    "positif": [0, 255, 0],      # Hijau
    "negatif": [0, 0, 255]       # Biru
}

# Sidebar untuk memilih sentimen
btn_sentiment = grouped_df["klasifikasi_vader"].unique()
chosen_sentiment = st.sidebar.selectbox("Pilih Sentimen :", btn_sentiment)

# Filter data berdasarkan sentimen yang dipilih
filtered_df = grouped_df[grouped_df["klasifikasi_vader"] == chosen_sentiment].copy()
filtered_df["color"] = filtered_df["klasifikasi_vader"].map(COLOR_MAP)

# Hitung initial view state berdasarkan data yang ada
view = pdk.data_utils.compute_view(filtered_df[["longitude", "latitude"]])

# Fungsi untuk menampilkan peta
def show_map_sentimen(data):
    map_type = st.selectbox("Pilih Tipe Peta", ["Heat Map", "Hexagon", "Scatter Plot"], key="map_sentiment")
    
    sentiment_layer = None
    
    if map_type == "Heat Map":
        sentiment_layer = pdk.Layer(
            "HeatmapLayer",
            data=filtered_df,
            get_position=["longitude", "latitude"],
            # threshold=0.2,
            pickable=True,
            get_weight = "count"
        )
    
    elif map_type == "Hexagon":
        sentiment_layer = pdk.Layer(
            "HexagonLayer",
            data=filtered_df,
            get_position=["longitude", "latitude"],
            auto_highlight=True,
            extruded=True,
            coverage=1,
            elevation_range=[0, 1000],
            elevation_scale=20,
            pickable=True,
        )
    
    elif map_type == "Scatter Plot":
        sentiment_layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=6,
            radius_min_pixels=2,
            radius_max_pixels=300,  # Diperbaiki dari radius_max_pixel
            line_width_min_pixels=1,
            get_position=["longitude", "latitude"],
            get_radius="count",
            get_fill_color="color",
        )
    
    return pdk.Deck(
        layers=[sentiment_layer],
        map_style="mapbox://styles/mapbox/navigation-night-v1",
        initial_view_state=view,
        tooltip={"text": "Sentimen: {klasifikasi_vader}\nJumlah: {count}"},
    )

# Tampilkan peta di Streamlit
st.title("Visualisasi Sentimen Tweet")
st.pydeck_chart(show_map_sentimen(sentiment_df))