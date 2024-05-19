import streamlit as st
import requests

st.title('My Full-Stack App')
response = requests.get('http://127.0.0.1:8000/')
if response:
    st.json(response.json())
else:
    st.error('Failed to retrieve data')