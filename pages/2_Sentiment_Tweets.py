import folium
import streamlit as st
import pydeck as pdk
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import HeatMap, Fullscreen
from streamlit_folium import folium_static
from wordcloud import STOPWORDS, WordCloud
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")
sentiment_df = pd.read_csv(r"C:\PA_Streamlit\data\sa_vader.csv")
sentiment_df.rename(columns={"bujur": "longitude", "lintang": "latitude"}, inplace=True)
grouped_df = sentiment_df.groupby(["latitude", "longitude", "klasifikasi_vader", "stopwords", "stemmed", "matched_keyword"]).size().reset_index(name="count")

# Sidebar untuk memilih sentimen
btn_sentiment = grouped_df["klasifikasi_vader"].unique()
chosen_sentiment = st.sidebar.selectbox("Pilih Sentimen :", btn_sentiment)
filtered_df = grouped_df[grouped_df["klasifikasi_vader"] == chosen_sentiment].copy()

def generateSentimentMap(default_location=[-7.949695, 110.492840], default_zoom_start=9.25):
    base_map = folium.Map(location=default_location, zoom_start=default_zoom_start, control_scale=True)
    return base_map

# Buat Peta Dasar
basemapSentiment = generateSentimentMap()
# FullScreen
Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(basemapSentiment)

HeatMap(filtered_df[['latitude','longitude']],zoom=100,radius=15).add_to(basemapSentiment)
folium.LayerControl(position="topright").add_to(basemapSentiment)
st.write("### Data Sentiment")
folium_static(basemapSentiment)

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

text_wordcloud = filtered_df["stemmed"].str.cat(sep=" ")
custom_stopwords = set(STOPWORDS)
custom_stopwords.update(["jogja"])
if text_wordcloud:
    w = WordCloud(background_color="white", colormap="OrRd", stopwords=custom_stopwords).generate(text_wordcloud)
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.imshow(w, interpolation="bilinear")
    plt.axis("off")
    st.sidebar.write("### WORD CLOUD")
    st.sidebar.pyplot(fig)