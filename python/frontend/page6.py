import streamlit as st
import plotly.express as px
import requests

# Funktion zum Abrufen der wiederkehrenden Kundenberichte
def fetch_repeat_customers_report():
    url = "http://localhost:8000/repeat-customers-report/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []

def main():
    st.write("Welcome to the Products page!")
    st.write("Here you can find information about our products.")

    # Daten abrufen
    report_data = fetch_repeat_customers_report()

    # Überprüfen, ob Daten erfolgreich abgerufen wurden
    if report_data:
        # Diagramm erstellen
        fig = px.bar(report_data, x="storeid", y=["total_customers", "repeat_customers"], labels={"value": "Count"},
                     title='Repeat Customers Report', barmode='group')
        
        # Diagramm anzeigen
        st.plotly_chart(fig)
