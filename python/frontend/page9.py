import streamlit as st
import requests
import plotly.express as px
from datetime import datetime, timedelta

# Fetch dashboard overview data
def fetch_dashboard_overview():
    try:
        url = 'http://localhost:8000/dashboard-overview'  # Adjust the URL to match your actual endpoint
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return {}
    
    # Fetch product launch dates
def fetch_product_launch_dates():
    try:
        url = 'http://localhost:8000/product-launch-dates'  # Adjust the URL to match your endpoint
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching product launch dates: {e}")
        return []

# Create card component
def create_card(title, value, icon):
    card_html = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; 
                background-color: #f9f9f9; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <div style="flex-grow: 1;">
            <h4 style="margin: 0;">{title}</h4>
            <p style="font-size: 1.5em; font-weight: bold; margin: 0;">{value}</p>
        </div>
        <div style="font-size: 2em; color: #007BFF;">
            {icon}
        </div>
    </div>
    """
    return card_html

def main():
    # Define columns for layout
    col1, col2 = st.columns([10, 1])  # Adjust column ratios as needed

    # Column 1: Logo
    with col2:
        st.image("PizzaCompanyLogo.jpg", width=200)  # Adjust width as needed

    # Column 2: Title and dashboard overview
    with col1:
        st.title("Welcome to the Data Analysis Dashboard")
        st.header("General Overview")

        # Fetch the data
        data = fetch_dashboard_overview()
        
        # Check if the keys exist in the data
        total_revenue = data.get('TotalRevenue', 0)
        total_orders = data.get('TotalOrders', 0)
        total_customers = data.get('TotalCustomers', 0)
        total_stores = data.get('TotalStores', 0)
        
        # Icons
        dollar_icon = "💵"
        list_icon = "📋"
        person_icon = "👤"
        store_icon = "🏪"

        # Create cards
        st.markdown(create_card("Total Revenue", f"${total_revenue:,.2f}", dollar_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Orders", total_orders, list_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Customers", total_customers, person_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Stores", total_stores, store_icon), unsafe_allow_html=True)

                # Fetch product launch dates
        launch_dates = fetch_product_launch_dates()

        if launch_dates:
            # Prepare data for time beam chart
            launch_dates.sort(key=lambda x: x['Launch'])  # Sort by launch date

            product_names = [entry['Name'] for entry in launch_dates]
            launch_dates_str = [entry['Launch'] for entry in launch_dates]
            launch_dates_dt = [datetime.fromisoformat(date_str) for date_str in launch_dates_str]

            # Create DataFrame for Plotly timeline chart
            df = {
                "Task": product_names,
                "Start": launch_dates_dt,
                "Finish": [dt + timedelta(days=1) for dt in launch_dates_dt]  # Add 1 day to visualize as points
            }

            # Create time beam chart using Plotly
            fig = px.timeline(df, x_start='Start', x_end='Finish', y='Task')

            st.header("Product Launch Timeline")
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
