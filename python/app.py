import streamlit as st
import requests
import pandas as pd

st.title("Dynamische Datenfilterung")

filter_text = st.text_input("Filter", "")

@st.cache_data(ttl=60)
def fetch_data(filter: str):
    response = requests.get("http://localhost:8000/stores/", params={"filter": filter})
    if response.status_code == 200:
        return response.json()
    else:
        return []

data = fetch_data(filter_text)

if data:
    df = pd.DataFrame(data)
    st.dataframe(df)
else:
    st.write("Keine Daten gefunden.")
