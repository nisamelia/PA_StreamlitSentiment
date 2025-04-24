import streamlit as st
import pydeck as pdk
import pandas as pd
import plotly.express as px

st.write("# SELAMAT DATANG!")
st.markdown(
    """
Dashboard ini menampilkan destinasi wisata Daerah Istimewa Yogyakarta yang banyak dibicarakan di X (Twitter) selama 2023. Selain itu, dashboard ini juga menampilkan sentimen dari tweets dalam kategori positif, netral, dan negatif.
"""
)


# DEKLARASI VARIABEL

# Data
data = pd.read_csv(r'C:\PA_Streamlit\data\dtw_koordinat_all.csv', delimiter=',')

data_wisata = pd.DataFrame({
    "tahun": [2020, 2021, 2022, 2023],
    "jumlah" : [1848548, 4294725, 6474115, 7740689]
})

data_wisata_prov = pd.read_excel(r'C:\PA_Streamlit\data\wisatawan_prov_2023.xlsx', engine='openpyxl')

# Basemap
basemaps = {
        "Dark":"mapbox://styles/mapbox/dark-v11",
    "Streets":"mapbox://styles/mapbox/streets-v12",
    "Outdoors":"mapbox://styles/mapbox/outdoors-v12",
    "Light":"mapbox://styles/mapbox/light-v11",
    "Sattelite":"mapbox://styles/mapbox/satellite-v9",
    "Sattelite Streets":"mapbox://styles/mapbox/satellite-streets-v12",
    "Naigation Day":"mapbox://styles/mapbox/navigation-day-v1",
    "Navigation Night":"mapbox://styles/mapbox/navigation-night-v1"
}

# Pilih Basemap
selected_basemap = st.sidebar.selectbox("Pilih Basemap:", list(basemaps.keys()), index=0)

# Add Map PyDeck
def add_map(data, center_lat, center_lon, zoom, basemap):
    st.write("## Peta Persebaran Wisata Daerah Istimewa Yogyakarta Tahun 2023 :")
    st.markdown("Sumber : Dinas Pariwisata DIY Tahun 2023")
    tooltip = {
        "html": "{Name}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
            }
    }
    layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position=["Longitude", "Latitude"],
        get_color=[255, 0, 0,160],
        get_radius=400,
        pickable=True
    )

    # Pengaturan Tampilan Peta
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=0
    )

    # Menampilkan peta di Streamlit
    st.pydeck_chart(pdk.Deck(
        map_style=basemap,
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip
    ))

add_map(data, center_lat=-7.7956, center_lon=110.3695, zoom=9, basemap=basemaps[selected_basemap])

graph1, graph2 = st.columns([1,1])

col1, col2 = st.columns([1, 1])

# Graphs

def show_charts(data_wisata):
    chart_type = st.selectbox("Pilih Jenis Grafik", ["Line Chart", "Bar Chart", "Scatter Plot"])
    if chart_type == "Line Chart":
        fig = px.line(data_wisata, x="tahun", y="jumlah", title="Line Chart", markers=True)
    elif chart_type == "Bar Chart":
        fig = px.bar(data_wisata, x="tahun", y="jumlah", title="Bar Chart")
    elif chart_type == "Scatter Plot":
        fig = px.scatter(data_wisata, x="tahun", y="jumlah", title="Scatter Plot")
    fig.update_layout(
        width=500
    )
    st.plotly_chart(fig)
with graph1:
    st.write("### Grafik Wisatawan DIY 2023")
with col1:
    show_charts(data_wisata)

def show_graph_year(data_wisata_prov):
    chart_type = st.selectbox("Pilih Jenis Grafik", ["Bar Chart", "Line Chart"])
    if chart_type == "Bar Chart":
        fig = px.bar(data_wisata_prov, x="prov", y="jumlah", title="Bar Chart")
    elif chart_type == "Line Chart":
        fig = px.line(data_wisata_prov, x="prov", y="jumlah", title="Line Chart", markers=True)
    st.plotly_chart(fig)
with graph2:
    st.write("### Grafik 10 Provinsi dengan Jumlah Wisatawan Domestik Terbanyak")
with col2:
    show_graph_year(data_wisata_prov)