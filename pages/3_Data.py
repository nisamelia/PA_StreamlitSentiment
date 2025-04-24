import streamlit as st
import pandas as pd

st.title("Data Hasil Sentimen Analisis Menggunakan VADER Lexicon-Based")

SA_data = pd.read_csv(r".\data\sa_vader.csv")
SA_data = SA_data.drop(['image_url', 'location'], axis=1)
st.write(SA_data)