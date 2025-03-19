import streamlit as st
import pydeck as pdk
import pandas as pd

tweet_df = pd.read_csv(r"C:\PA_Streamlit\data\crawl_all_SA.csv")

view = pdk.data_utils.computer_view(tweet_df["bujur", "lintang"])

def show_map_sentimen(tweet_df):
    map_type = st.selectbox("Pilih ")