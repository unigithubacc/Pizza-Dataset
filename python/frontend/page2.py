import streamlit as st
import requests
import plotly.graph_objects as go

# Funktion zum Abrufen der Daten der Top-Selling Stores
def fetch_top_selling_stores():
    response = requests.get('http://localhost:8000/top-selling-stores')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

# Funktion zum Abrufen der Verkaufszahlen für ein bestimmtes Geschäft
def fetch_sales_by_store(store_id):
    response = requests.get(f'http://localhost:8000/sales-by-store/{store_id}/')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Verkaufsdaten.")
        return []

# Funktion zum Erstellen des Balkendiagramms für die Top-Selling Stores
def create_store_bar_chart(data):
    store_ids = sorted(set([item['storeID'] for item in data]))
    total_revenue = {store_id: sum(item['TotalRevenue'] for item in data if item['storeID'] == store_id) for store_id in store_ids}

    # Sortiere die Stores basierend auf ihrem Gesamtumsatz
    sorted_store_ids = sorted(total_revenue.keys(), key=lambda x: total_revenue[x], reverse=True)

    fig = go.Figure()

    for store_id in sorted_store_ids:
        fig.add_trace(go.Bar(
            x=[store_id],  
            y=[total_revenue[store_id]],  
            name=f'Store {store_id}',
            legendgroup=f'Store {store_id}',
            showlegend=True,
            marker_color='blue',
            customdata=[store_id],  # Speichere die store_id für die Callback-Funktion
            hoverinfo='x+y'
        ))

    fig.update_layout(barmode='group',
                      title='Top Selling Stores',
                      xaxis_title='Store ID',
                      yaxis_title='Total Revenue in $')

    return fig

# Funktion zum Erstellen des Liniendiagramms für die Verkaufszahlen eines bestimmten Geschäfts
def create_sales_line_chart(data, store_id):
    fig = go.Figure()

    quarters = [f"{item['year']}-{item['quarter']}" for item in data]
    number_of_sales = [item['number_of_sales'] for item in data]

    fig.add_trace(go.Scatter(
        x=quarters,
        y=number_of_sales,
        mode='lines+markers',
        name=f'Store {store_id}'
    ))

    fig.update_layout(title=f'Number of Sales for Store {store_id}',
                      xaxis_title='Year-Quarter',
                      yaxis_title='Number of Sales')

    return fig

import streamlit as st

def main():
    st.title("Top Selling Stores")

    stores_data = fetch_top_selling_stores()
    if stores_data:
        fig = create_store_bar_chart(stores_data)
        st.plotly_chart(fig)
        
        # Extract unique store IDs and calculate total revenue for each store
        store_ids = set([item['storeID'] for item in stores_data])
        total_revenue = {store_id: sum(item['TotalRevenue'] for item in stores_data if item['storeID'] == store_id) for store_id in store_ids}

        # Sort store IDs based on their total revenue
        sorted_store_ids = sorted(total_revenue.keys(), key=lambda x: total_revenue[x], reverse=True)

        fig = create_store_bar_chart(stores_data)
        # Use session state to store the selected store ID
        if 'selected_store_id' not in st.session_state:
            st.session_state.selected_store_id = None
        selected_store_id = st.selectbox(
            "Select a Store",
            options=[{'id': store_id, 'label': f'Store {store_id}'} for store_id in sorted_store_ids],
            index=None,
            format_func=lambda x: f'Store {x["id"]}'
        )
        if selected_store_id:
            st.session_state.selected_store_id = selected_store_id['id']
        
        if st.session_state.selected_store_id:
            store_id = st.session_state.selected_store_id
            sales_data = fetch_sales_by_store(store_id)
            if sales_data:
                sales_fig = create_sales_line_chart(sales_data, store_id)
                st.plotly_chart(sales_fig)
