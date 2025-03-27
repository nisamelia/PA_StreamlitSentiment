from email.mime import base
from os import name
import streamlit as st
import pydeck as pdk
import pandas as pd
import plotly.express as px
import folium as folium
from folium.plugins import HeatMap, Fullscreen
from streamlit_folium import st_folium, folium_static

## DEFINE DATA
dinpar_df = pd.read_csv(r"C:\PA_Streamlit\data\dtw_jumlah_dinpar.csv")

# Convert Date Time
def load_data():
    crawled_df = pd.read_csv(r"C:\PA_Streamlit\data\crawl_all_SA.csv")
    crawled_df["created_at"] = pd.to_datetime(crawled_df["created_at"], format="%a %b %d %H:%M:%S %z %Y")
    return crawled_df

crawled_df = load_data()

# Declare Date to Filtering
dt_start = st.sidebar.date_input("Pilih Tanggal Awal", crawled_df["created_at"].min().date())
dt_end = st.sidebar.date_input("Pilih Tanggal Akhir", crawled_df["created_at"].max().date())

df_filtered = crawled_df[(crawled_df["created_at"].dt.date >= dt_start) & (crawled_df["created_at"].dt.date <= dt_end)]

# Count Tweets Per Day
df_grouped = df_filtered.groupby(df_filtered["created_at"].dt.date).size().reset_index(name="count")

view = pdk.data_utils.compute_view(dinpar_df[["bujur", "lintang"]])
view_zoom = 3

def show_map_dinpar(dinpar_df):
    map_type = st.selectbox("Pilih Tipe Peta", ["Heat Map", "Hexagon"], key="map_dinpar")
    dinpar = None
    if map_type == "Heat Map":
        dinpar = pdk.Layer(
            "HeatmapLayer",
            data = dinpar_df,
            get_position = ["bujur", "lintang"],
            # threshold = 0.2,
            get_weight = "total",
            pickable = True,
            )
    elif map_type == "Hexagon":
        dinpar = pdk.Layer(
            "HexagonLayer",
            data = dinpar_df,
            get_position = ["bujur", "lintang"],
            auto_highlight = True,
            get_weight="total",
            extruded = True,
            coverage = 1,
            # radius = 200,
            elevation_range=[0, 1000],
            elevation_scale = 20,
            pickable = True,
            )
    return pdk.Deck(
        layers=[dinpar],
        map_style="mapbox://styles/mapbox/navigation-night-v1",
        initial_view_state=view,
    )


basemapLayer = ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"]
# HeatMap Tweets
def generateTweetMap(default_location=[-7.949695, 110.492840], default_zoom_start=9.25):
    base_map = folium.Map(location=default_location, zoom_start=default_zoom_start)
        # Add multiple basemap layers
    for i in basemapLayer:
        folium.TileLayer(i).add_to(base_map)

    return base_map
basemapTweet=generateTweetMap()
Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(basemapTweet)
HeatMap(crawled_df[['lintang','bujur']],zoom=100,radius=15).add_to(basemapTweet)
folium.LayerControl(position="topright").add_to(basemapTweet)

# HeatMap Tweets using plotly express
def generateCrawledMap(crawled_df):
    # config = {'scrollZoom': True}
    fig_tweets = px.density_mapbox(crawled_df, lat='lintang', lon='bujur', radius=10,
                                center=dict(lat=crawled_df.lintang.mean(), lon=crawled_df.bujur.mean()),
                                zoom=4, mapbox_style='open-street-map', height=900)

    fig_tweets.update_layout(
    )

    # fig_tweets.show(config=config)

    return fig_tweets

# HeatMap Dinas Pariwisata
def generateWisataMap(default_location=[-7.949695, 110.492840], default_zoom_start=9.25):
    base_map = folium.Map(location=default_location, zoom_start=default_zoom_start)
    for i in basemapLayer:
        folium.TileLayer(i).add_to(base_map)
    return base_map
basemapWisata=generateWisataMap()

Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(basemapWisata)
HeatMap(dinpar_df[['lintang','bujur','total']],radius=15).add_to(basemapWisata)
folium.LayerControl(position="topright").add_to(basemapWisata)


st.write("# PERBANDINGAN DATA DINAS PARIWISATA DAN DATA TWEETS WISATA")
# Create two columns for the split map
col1, col2 = st.columns(2)

with col1:
    st.write("### Dinas Pariwisata DIY 2023")

with col2:
    config = {'scrollZoom': True}
    st.write("### Data Tweets Wisata DIY 2023")
    fig = generateCrawledMap(crawled_df)  # Call function and store the result
    st.plotly_chart(fig, use_container_width=True, config=config)  # Display map in Streamlit

st.write("### TWEET")
fig = px.line(
    df_grouped,
    x = "created_at",
    y = "count",
    markers=True,
    title="Tweet Trends",
    labels={"created_at" : "Date", "count": "Number of Tweets"}
)

# Show the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)