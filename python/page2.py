import streamlit as st
import requests

def fetch_top_pizzas():
    response = requests.get('http://localhost:8000/top-selling-products')
    # Überprüfen Sie, ob die Antwort erfolgreich war
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

def main():
    st.title("Top Verkaufte Pizzen")

    pizzas_data = fetch_top_pizzas()
    if pizzas_data:
        st.write(pizzas_data)
        # Erstellen eines Balkendiagramms
        st.bar_chart([item["TotalSold"] for item in pizzas_data])  # Korrigierte Schlüsselbezeichnung