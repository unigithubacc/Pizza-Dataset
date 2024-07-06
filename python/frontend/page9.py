import streamlit as st
import requests

# Fetch dashboard overview data
def fetch_dashboard_overview():
    try:
        url = 'http://localhost:8501/dashboard-overview'  # Adjust the URL to match your actual endpoint
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

# Main application logic
def main():
    st.title("Data analysis dashboard")

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

if __name__ == "__main__":
    main()
