import pandas as pd
import streamlit as st
import plotly.express as px
import requests

# Funktion zum Abrufen der Daten vom API-Endpunkt
def fetch_data():
    url = "http://localhost:8000/repeat-customers-report/"  # Passen Sie die URL entsprechend Ihrer API-Konfiguration an
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Fehler beim Abrufen der Daten")
        return []

# Hauptfunktion
def main():
    st.write("Willkommen zur Kundenreport-Seite!")
    st.write("Hier finden Sie Informationen über unsere wiederkehrenden Kunden.")

    # Daten abrufen
    data = fetch_data()
    
    if data:
        # Daten für die Heatmap vorbereiten
        df = pd.DataFrame(data)
        
        # Heatmap erstellen
        fig = px.density_heatmap(df, x="storeid", y="total_customers", z="repeat_rate", color_continuous_scale="Viridis", 
                                labels={"total_customers": "Total Customers", "repeat_rate": "% Repeat Rate", "storeid": "Store ID"})
        
        # Die Heatmap im Streamlit-Bericht anzeigen
        st.plotly_chart(fig)

