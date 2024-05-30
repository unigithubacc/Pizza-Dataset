import streamlit as st
import requests
import plotly.graph_objects as go

def fetch_top_selling_stores():
    response = requests.get('http://localhost:8000/top-selling-stores')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

def create_store_bar_chart(data):
    store_ids = sorted(set([item['storeID'] for item in data]))
    total_revenue = {store_id: sum(item['TotalRevenue'] for item in data if item['storeID'] == store_id) for store_id in store_ids}

    # Sortiere die Stores basierend auf ihrem Gesamtumsatz
    sorted_store_ids = sorted(total_revenue.keys(), key=lambda x: total_revenue[x], reverse=True)

    fig = go.Figure()

    for store_id in sorted_store_ids:
        fig.add_trace(go.Bar(
            x=[store_id],  # Da nur eine Kategorie pro Bar vorhanden ist
            y=[total_revenue[store_id]],  # Passen Sie dies an, falls Sie mehrere Balken für jede Kategorie haben möchten
            name=f'Store {store_id}',
            legendgroup=f'Store {store_id}',
            showlegend=True
        ))

    fig.update_layout(barmode='group',  # Änderung von 'bar' zu 'group'
                      title='Top Selling Stores',
                      xaxis_title='Store ID',
                      yaxis_title='Total Revenue in $')

    return fig

def main():
    st.title("Top Selling Stores")

    stores_data = fetch_top_selling_stores()
    if stores_data:
        fig = create_store_bar_chart(stores_data)
        st.plotly_chart(fig)

        # Anzeigen der Liste der Stores und ihrer Umsatzzahlen
        st.subheader("List of Stores and their revenue figures:")
        st.table(stores_data)

