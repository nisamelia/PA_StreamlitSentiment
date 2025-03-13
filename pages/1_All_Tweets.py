import streamlit as st
import pydeck as pdk

st.set_page_config(layout="wide")

# Define map styles (or layers)
left_map = pdk.Deck(
    map_style="mapbox://styles/mapbox/satellite-streets-v11",
    initial_view_state=pdk.ViewState(latitude=0, longitude=0, zoom=3),
)

right_map = pdk.Deck(
    map_style="mapbox://styles/mapbox/outdoors-v11",
    initial_view_state=pdk.ViewState(latitude=0, longitude=0, zoom=3),
)

st.write("# PERBANDINGAN DATA DINAS PARIWISATA DAN DATA TWEETS WISATA")
# Create two columns for the split map
col1, col2 = st.columns(2)

with col1:
    st.write("### Dinas Pariwisata DIY 2023")
    st.pydeck_chart(left_map)

with col2:
    st.write("### Data Tweets Wisata DIY 2023")
    st.pydeck_chart(right_map)
