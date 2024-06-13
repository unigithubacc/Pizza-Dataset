import streamlit as st
import requests
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# Function to fetch top-selling stores data
def fetch_top_selling_stores():
    response = requests.get('http://localhost:8000/top-selling-stores')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

# Function to fetch sales data for a specific store
def fetch_sales_by_store(store_id):
    response = requests.get(f'http://localhost:8000/sales-by-store/?storeid={store_id}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Verkaufsdaten.")
        return []

# Function to create bar chart for top-selling stores
def create_store_bar_chart(data):
    store_ids = sorted(set([item['storeID'] for item in data]))
    total_revenue = {store_id: sum(item['TotalRevenue'] for item in data if item['storeID'] == store_id) for store_id in store_ids}

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
            customdata=[store_id],
            hoverinfo='x+y'
        ))

    fig.update_layout(barmode='group',
                      title='Top Selling Stores',
                      xaxis_title='Store ID',
                      yaxis_title='Total Revenue in $',
                      clickmode='event+select')

    return fig

# Function to create line chart for sales data of a specific store
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

def main():
    st.title("Top Selling Stores")

    stores_data = fetch_top_selling_stores()
    if stores_data:
        fig = create_store_bar_chart(stores_data)
        selected_points = plotly_events(fig, click_event=True)

        if selected_points:
            # Extrahieren Sie den store_id aus der x-Koordinate
            selected_store_id = selected_points[0]['x']
            st.write(f"Selected Store ID: {selected_store_id}")  # Debugging Line
            sales_data = fetch_sales_by_store(selected_store_id)
            if sales_data:
                sales_fig = create_sales_line_chart(sales_data, selected_store_id)
                st.plotly_chart(sales_fig, use_container_width=True)
        else:
            st.warning("select a store ID to see the number of sales for that store")