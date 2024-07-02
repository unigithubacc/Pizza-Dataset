import streamlit as st
import requests
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
from datetime import date

# Funktion zum Abrufen der Top-Selling-Stores-Daten
@st.cache_data
def fetch_top_selling_stores(start_date, end_date):
    response = requests.get(f'http://localhost:8000/top-selling-stores?start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

@st.cache_data
def fetch_store_product_revenue(store_id, start_date, end_date, divide_by_size):
    response = requests.get(f'http://localhost:8000/store-products-revenue?storeid={store_id}&start_date={start_date}&end_date={end_date}&divide_by_size={divide_by_size}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

# Function to create bar chart for top-selling stores
def create_store_bar_chart2(data):
    store_ids = sorted(set([item['storeid'] for item in data]))
    total_revenue = {store_id: sum(item['TotalRevenue'] for item in data if item['storeid'] == store_id) for store_id in store_ids}

    sorted_store_ids = sorted(total_revenue.keys(), key=lambda x: total_revenue[x], reverse=True)

    fig2 = go.Figure()

    for store_id in sorted_store_ids:
        fig2.add_trace(go.Bar(
            x=[store_id],
            y=[total_revenue[store_id]],
            name=f'Store {store_id}',
            legendgroup=f'Store {store_id}',
            showlegend=False,
            marker_color='lightskyblue',
            customdata=[store_id],
            hoverinfo='x+y'
        ))

    fig2.update_layout(barmode='group',
                      title='Top Selling Stores',
                      xaxis_title='Store ID',
                      yaxis_title='Total Revenue in $',
                      clickmode='event+select',
                      )

    return fig2

# Function to create bar chart for store product revenue
def create_product_revenue_bar_chart(data, divide_by_size):
    product_names = [product['name'] for product in data]
    product_revenues = [product['product_revenue'] for product in data]

    if divide_by_size:
        product_sizes = [product['size'] for product in data]
        labels = [f"{name} ({size})" for name, size in zip(product_names, product_sizes)]
    else:
        labels = product_names

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels,
        x=product_revenues,
        marker_color='lightskyblue',
        hoverinfo='y+x',
        orientation='h',  # Set horizontal orientation
        name='Product Revenue'
    ))

    fig.update_layout(
        title='Store Product Revenue',
        yaxis_title='Product Name' + (' (Size)' if divide_by_size else ''),
        xaxis_title='Product Revenue in $',
        height=500,
        barmode='relative'
    )

    return fig

def main():
    start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date(2023, 1, 1))
    
    divide_by_size = st.sidebar.checkbox("Divide Pizzas by Size", value=False)

    col1, col2 = st.columns([4, 5])

    with col1:
        stores_data = fetch_top_selling_stores(start_date, end_date)
        if stores_data:
            fig2 = create_store_bar_chart2(stores_data)
            selected_points = plotly_events(fig2, click_event=True)

    with col2:
        if selected_points:
            selected_store_id = selected_points[0]['x']
            store_product_data = fetch_store_product_revenue(selected_store_id, start_date, end_date, divide_by_size)
            if store_product_data:
                fig = create_product_revenue_bar_chart(store_product_data, divide_by_size)
                st.plotly_chart(fig)  # Hier wird das zweite Diagramm angezeigt
        else: 
            st.sidebar.warning("Select a Store to see more information")

