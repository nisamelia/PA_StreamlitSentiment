from email.mime import base
import streamlit as st
from streamlit_navigation_bar import st_navbar
import pydeck as pdk
import pandas as pd

st.write("# SELAMAT DATANG!")
st.markdown(
    """
Dashboard ini menampilkan destinasi wisata Daerah Istimewa Yogyakarta yang banyak dibicarakan di X (Twitter) selama 2023. Selain itu, dashboard ini juga menampilkan sentimen dari tweets dalam kategori positif, netral, dan negatif.
"""
)


# DEKLARASI VARIABEL

# Data
data = pd.DataFrame({
        "latitude": [-7.7956, -7.7828, -7.7706],
        "longitude": [110.3695, 110.3671, 110.3773],
        "name": ["Titik Nol Jogja", "Malioboro", "Keraton Yogyakarta"]
    })

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

# FUNGSI 

# Add Map
def add_map(data, center_lat, center_lon, zoom, basemap):
    st.write("## Peta Persebaran Wisata Daerah Istimewa Yogyakarta Tahun 2023 :")
    st.markdown("Sumber : Dinas Pariwisata DIY Tahun 2023")
    # layer = pdk.Layer(
    #     "ScatterplorLayer",
    #     data,
    #     get_position=["latitude", "longitude"],
    #     get_color=[255, 0, 0,160],
    #     get_radius=100,
    #     pickable=True
    # )

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
        # layers=[layer]
    ))

add_map(data, center_lat=-7.7956, center_lon=110.3695, zoom=9, basemap=basemaps[selected_basemap])