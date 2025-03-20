from os import name
import streamlit as st
import pydeck as pdk
import pandas as pd
import plotly.express as px

## DEFINE DATA
dinpar_df = pd.read_csv(r"C:\PA_Streamlit\data\dtw_jumlah_dinpar.csv")

# Convert Date Time
def load_data():
    crawled_df = pd.read_csv(r"C:\PA_Streamlit\data\crawl_all_SA.csv")
    crawled_df["created_at"] = pd.to_datetime(crawled_df["created_at"], format="%a %b %d %H:%M:%S %z %Y")
    return crawled_df

crawled_df = load_data()

# COLOR_BREWER_BLUE_SCALE = [
#     [240, 249, 232],
#     [204, 235, 197],
#     [168, 221, 181],
#     [123, 204, 196],
#     [67, 162, 202],
#     [8, 104, 172],
# ]

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
            threshold = 0.2,
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

def show_map_tweet(crawled_df):
    map_type = st.selectbox("Pilih Tipe Peta", ["Heat Map", "Hexagon"], key="map_tweet")
    tweet = None
    if map_type == "Heat Map":
        tweet = pdk.Layer(
            "HeatmapLayer",
            data = crawled_df,
            # opacity = 0.9,
            get_position = ["bujur", "lintang"],
            threshold = 0.2,
            # get_weight = "total",
            pickable = True,
            )
    elif map_type == "Hexagon":
        tweet = pdk.Layer(
            "HexagonLayer",
            data = crawled_df,
            get_position = ["bujur", "lintang"],
            auto_highlight = True,
            # get_weight="total",
            extruded = True,
            coverage = 1,
            # radius = 200,
            elevation_range=[0, 1000],
            elevation_scale = 20,
            pickable = True,
            )
    return pdk.Deck(
        layers=[tweet],
        map_style="mapbox://styles/mapbox/navigation-night-v1",
        initial_view_state=view,
    ) 

# st.set_page_config(layout="wide")

st.write("# PERBANDINGAN DATA DINAS PARIWISATA DAN DATA TWEETS WISATA")
# Create two columns for the split map
col1, col2 = st.columns(2)

with col1:
    st.write("### Dinas Pariwisata DIY 2023")
    st.pydeck_chart(show_map_dinpar(dinpar_df))

with col2:
    st.write("### Data Tweets Wisata DIY 2023")
    st.pydeck_chart(show_map_tweet(crawled_df))

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