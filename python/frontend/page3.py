import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import requests
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium

@st.cache_data
def fetch_data(min_order_count):
    url = f"http://localhost:8000/repeat-customers-report/?min_order_count={min_order_count}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching data")
        return []

@st.cache_data
def fetch_store_details(storeid):
    url = f"http://localhost:8000/store-details/?storeid={storeid}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching store details")
        return None

@st.cache_data
def fetch_customer_locations(storeid, min_orders):
    url = f"http://localhost:8000/customer_locations/{storeid}?min_orders={min_orders}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching customer locations")
        return []

def generate_heatmap(data):
    if data:
        df = pd.DataFrame(data)
        bins = [0, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1500]
        labels = ['0-500', '500-600', '600-700', '700-800', '800-900', '900-1000', '1000-1200', '1200-1400', '1400-1500']
        df['customer_range'] = pd.cut(df['total_customers'], bins=bins, labels=labels)

        # Ensure all possible values are handled
        all_possible_labels = set(labels)
        existing_labels = set(df['customer_range'])
        missing_labels = all_possible_labels - existing_labels
        if missing_labels:
            for label in missing_labels:
                temp_df = pd.DataFrame({'customer_range': [label], 'total_customers': [0], 'storeid': [None]})
                df = pd.concat([df, temp_df], ignore_index=True)

        labels_reversed = labels[::-1]
        z_values = np.full((len(labels), len(df['storeid'].unique())), np.nan)
        range_index_map = {label: idx for idx, label in enumerate(labels_reversed)}

        for i, store in enumerate(df['storeid'].unique()):
            store_data = df[df['storeid'] == store]
            for _, row in store_data.iterrows():
                if pd.isna(row['customer_range']):
                    continue
                range_index = range_index_map.get(row['customer_range'], None)
                if range_index is None:
                    st.warning(f"Unexpected customer_range value: {row['customer_range']}")
                    continue
                z_values[range_index, i] = row['repeat_rate']

        fig = px.imshow(z_values,
                        labels=dict(x="Store ID", y="Total Customers", color="% Repeat Rate"),
                        x=df['storeid'].unique(),
                        y=labels_reversed,
                        title='Returning Customer Heatmap',
                        color_continuous_scale="Viridis")

        return fig
    else:
        return None

def create_geo_chart(customer_data, store_data):
    if customer_data:
        avg_lat = sum([item['latitude'] for item in customer_data]) / len(customer_data)
        avg_lon = sum([item['longitude'] for item in customer_data]) / len(customer_data)
    else:
        avg_lat, avg_lon = 0, 0

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10)

    # Add marker cluster for customers
    customer_cluster = MarkerCluster(name="Customers").add_to(m)



    # Add customer markers
    for item in customer_data:
        folium.Marker(
            location=[item['latitude'], item['longitude']],
            popup=f"Lat: {item['latitude']}, Long: {item['longitude']}",
        ).add_to(customer_cluster)

    # Add store markers
    for store in store_data:
        store_popup = f"Store ID: {store.get('storeid', 'N/A')}<br>City: {store.get('city', 'N/A')}<br>State: {store.get('state', 'N/A')}"
        folium.Marker(
            location=[store['latitude'], store['longitude']],
            popup=store_popup,
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(m)

    return m

def display_store_location_and_customers(selected_storeid, min_orders):
    store_details = fetch_store_details(selected_storeid)
    customer_data = fetch_customer_locations(selected_storeid, min_orders)
  
    if store_details:
        store_data = [store_details]  # Put the store details in a list to use with the create_geo_chart function
        geo_map = create_geo_chart(customer_data, store_data)
        st_folium(geo_map, width=1400, height=370)
    else:
        st.error("Unable to fetch store details")

def main():
    # Extract query parameters from the URL
    query_params = st.query_params
    store_id_from_url = query_params.get("storeid", None)

    min_order_count = st.sidebar.number_input("Minimum number of repeat orders:", min_value=1, value=1)
    data = fetch_data(min_order_count)
                
    if data:
        with st.container():
            fig = generate_heatmap(data)
            st.sidebar.info("Select a store from the heatmap to see store and customer locations.")
            if fig:
                selected_points = plotly_events(fig, click_event=True)
                if selected_points:
                    selected_storeid = selected_points[0]['x']
                    st.query_params.update(storeid=selected_storeid)
                    display_store_location_and_customers(selected_storeid, min_order_count)
                elif store_id_from_url:
                    display_store_location_and_customers(store_id_from_url, min_order_count)
            else:
                st.warning("No data to display for the selected criteria.")
    else:
        st.warning("No data available.")