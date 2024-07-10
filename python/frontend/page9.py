import streamlit as st
import requests
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Fetch dashboard overview data
@st.cache_data
def fetch_dashboard_overview():
    try:
        url = 'http://localhost:8000/dashboard-overview'  # Adjust the URL to match your actual endpoint
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return {}

# Create card component
def create_card(title, value, icon):
    card_html = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; 
                background-color: #f9f9f9; padding: 5px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="flex-grow: 1;">
            <h5 style="margin: 0; font-size: 1,0em;">{title}</h5>
            <p style="font-size: 1.2em; font-weight: bold; margin: 0;">{value}</p>
        </div>
        <div style="font-size: 1.5em; color: #007BFF;">
            {icon}
        </div>
    </div>
    """
    return card_html

def main():
    # Set background image (optional)
    background_image = """
    <style>
    .stApp {
        background: url('DallEPizzaLogo.png');
        background-size: cover;
    }
    </style>
    """
    st.markdown(background_image, unsafe_allow_html=True)

    # Define columns for layout
    col1, col2 = st.columns([8, 1])  # Adjust column ratios as needed

    # Column 1: Logo
    with col2:
        st.header(" ")
        st.image("static/DallEPizzaLogo.png", width=200)  # Adjust width as needed

    # Column 2: Title and dashboard overview
    with col1:
        #st.title("Welcome to the Data Analysis Dashboard")
        st.header("Welcome to WESTERN PIZZA's Shop Analytics ")

        # Fetch the data
        data = fetch_dashboard_overview()
        
        # Check if the keys exist in the data
        total_revenue = data.get('TotalRevenue', 0)
        total_orders = data.get('TotalOrders', 0)
        total_customers = data.get('TotalCustomers', 0)
        total_stores = data.get('TotalStores', 0)
        pizzas_sold = data.get('PizzasSold', 0)
        number_of_products = data.get('NumberOfProducts', 0)
        most_popular_product = data.get('MostPopularProduct', "N/A")
        average_order_value = data.get('AverageOrderValue', 0)
        
        # Icons
        dollar_icon = "💵"
        list_icon = "📋"
        person_icon = "👤"
        store_icon = "🏪"
        pizza_icon = "🍕"
        product_icon = "📦"
        popular_icon = "⭐"
        avg_order_icon = "📊"

        # Create cards
        st.markdown(create_card("Total Revenue", f"${total_revenue:,.2f}", dollar_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Orders", total_orders, list_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Customers", total_customers, person_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Stores", total_stores, store_icon), unsafe_allow_html=True)
        st.markdown(create_card("Pizzas Sold", pizzas_sold, pizza_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Products", number_of_products, product_icon), unsafe_allow_html=True)
        st.markdown(create_card("Most Popular Product", most_popular_product, popular_icon), unsafe_allow_html=True)
        st.markdown(create_card("Average Order Value", f"${average_order_value:,.2f}", avg_order_icon), unsafe_allow_html=True)

