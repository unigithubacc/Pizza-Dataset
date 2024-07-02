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

@st.cache_data
def fetch_products_size(store_id, start_date, end_date):
    response = requests.get(f'http://localhost:8000/store-products-size-revenue?storeid={store_id}&start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

@st.cache_data
def fetch_products_category(store_id, start_date, end_date):
    response = requests.get(f'http://localhost:8000/store-products-category-revenue?storeid={store_id}&start_date={start_date}&end_date={end_date}')
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

# Function to create pie chart for product categories
def create_product_category_pie_chart(data):
    category_names = [category['category'] for category in data]
    category_revenues = [category['product_revenue'] for category in data]

    fig = go.Figure(data=[go.Pie(labels=category_names, values=category_revenues, hole=0.3)])

    fig.update_layout(
        title='Product Revenue by Category'
    )

    return fig

# Function to create pie chart for product sizes
def create_product_size_pie_chart(data):
    size_names = [size['size'] for size in data]
    size_revenues = [size['product_revenue'] for size in data]

    fig = go.Figure(data=[go.Pie(labels=size_names, values=size_revenues, hole=0.3)])

    fig.update_layout(
        title='Product Revenue by Size'
    )

    return fig

def main():
    # Initialisierung von session_state
    if 'selected_store_id' not in st.session_state:
        st.session_state.selected_store_id = None

    start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date(2023, 1, 1))
    
    divide_by_size = st.sidebar.checkbox("Divide Pizzas by Size", value=False)

    col1, col2 = st.columns([4, 5])

    with col1:
        stores_data = fetch_top_selling_stores(start_date, end_date)
        if stores_data:
            fig2 = create_store_bar_chart2(stores_data)
            selected_points = plotly_events(fig2, click_event=True)

            if selected_points:
                st.session_state.selected_store_id = selected_points[0]['x']

    with col2:
        if st.session_state.selected_store_id is not None:
            selected_store_id = st.session_state.selected_store_id
            store_product_data = fetch_store_product_revenue(selected_store_id, start_date, end_date, divide_by_size)
            if store_product_data:
                fig = create_product_revenue_bar_chart(store_product_data, divide_by_size)
                st.plotly_chart(fig)
            
            # Fetch and display product category pie chart
            store_category_data = fetch_products_category(selected_store_id, start_date, end_date)
            store_size_data = fetch_products_size(selected_store_id, start_date, end_date)
            
            if store_category_data and store_size_data:
                col3, col4 = st.columns(2)
                with col3:
                    pie_chart_category = create_product_category_pie_chart(store_category_data)
                    st.plotly_chart(pie_chart_category)
                
                with col4:
                    pie_chart_size = create_product_size_pie_chart(store_size_data)
                    st.plotly_chart(pie_chart_size)
        else: 
            st.sidebar.warning("Select a Store to see more information")
