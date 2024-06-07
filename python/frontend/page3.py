import streamlit as st
import folium
import requests
from streamlit_folium import folium_static
from folium.plugins import HeatMap, MarkerCluster

def fetch_customer_info(min_orders=None):
    try:
        url = 'http://localhost:8000/customer-locations'
        if min_orders:
            url += f'?min_orders={min_orders}'
        response = requests.get(url)  
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []
    
def fetch_store_locations():
    try:
        response = requests.get('http://localhost:8000/store-locations')  
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching store data: {e}")
        return []

def create_geo_chart(customer_data, store_data):
    if customer_data:
        avg_lat = sum([item['latitude'] for item in customer_data]) / len(customer_data)
        avg_lon = sum([item['longitude'] for item in customer_data]) / len(customer_data)
    else:
        avg_lat, avg_lon = 0, 0

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

    # Add marker cluster for customers
    customer_cluster = MarkerCluster(name="Customers").add_to(m)

    # Add heatmap for customers
    heat_data = [[item['latitude'], item['longitude']] for item in customer_data]
    HeatMap(heat_data).add_to(m)

    # Add customer markers
    for item in customer_data:
        folium.Marker(
            location=[item['latitude'], item['longitude']],
            popup=f"Lat: {item['latitude']}, Long: {item['longitude']}",
        ).add_to(customer_cluster)
    

    # Add store markers
    for store in store_data:
        store_popup = f"Store ID: {store['storeID']}<br>City: {store['city']}<br>State: {store['state']}"
        folium.Marker(
            location=[store['latitude'], store['longitude']],
            popup=store_popup,
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(m)

    return m

def main():
    st.title("Customer and Store Distribution by Location")

    # Initialize session state for storing fetched data
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = fetch_customer_info()
    if 'store_data' not in st.session_state:
        st.session_state.store_data = fetch_store_locations()

    # Input for minimum number of orders
    min_orders = st.number_input("Enter minimum number of orders:", min_value=0, step=1, value=0)

    # Fetch filtered customer data based on user input
    if min_orders > 0:
        st.session_state.customer_data = fetch_customer_info(min_orders)
    else:
        st.session_state.customer_data = fetch_customer_info()

    # Create and display the map
    geo_chart = create_geo_chart(st.session_state.customer_data, st.session_state.store_data)
    folium_static(geo_chart)