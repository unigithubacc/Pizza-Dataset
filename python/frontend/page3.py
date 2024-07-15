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
import pandas as pd
import plotly.express as px
import requests

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

@st.cache_data
def fetch_average_per_hour(storeid):
    url = f"http://localhost:8000/sales/average_per_hour/?storeid={storeid}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching store details")
        return None
    
@st.cache_data
def fetch_avg_orders_per_day(storeid):
    url = f"http://localhost:8000/sales/avg_orders_per_day/?storeid={storeid}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching average orders per day: {e}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"Response content: {e.response.text}")
        else:
            st.error("No response content available")
        return None

@st.experimental_fragment
def generate_heatmap(data, selected_storeid=None):
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
        
        fig.update_layout(height=430)

        # Highlight the selected store
        if selected_storeid is not None:
            for i, store in enumerate(df['storeid'].unique()):
                if store == selected_storeid:
                    fig.add_shape(
                        type="rect",
                        x0=i - 0.5, y0=-0.5,
                        x1=i + 0.5, y1=len(labels) - 0.5,
                        line=dict(color="red", width=3),
                    )
                    break
        return fig
    else:
        return None

def create_geo_chart(customer_data, store_data, selected_storeid=None):
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
        icon_color = 'red' if store['storeid'] == selected_storeid else 'blue'
        folium.Marker(
            location=[store['latitude'], store['longitude']],
            popup=store_popup,
            icon=folium.Icon(color=icon_color, icon='store', prefix='fa')
        ).add_to(m)

    return m

def display_store_location_and_customers(selected_storeid, min_orders):
    store_details = fetch_store_details(selected_storeid)
    customer_data = fetch_customer_locations(selected_storeid, min_orders)
  
    if store_details:
        store_data = [store_details]  # Put the store details in a list to use with the create_geo_chart function
        geo_map = create_geo_chart(customer_data, store_data, selected_storeid=selected_storeid)
        st_folium(geo_map, width=900, height=320)
    else:
        st.error("Unable to fetch store details")
        
def display_line_chart(selected_storeid=None):
    if selected_storeid:
        data = fetch_average_per_hour(selected_storeid)
        if data:
            # Erstellen eines DataFrames aus den API-Daten
            df = pd.DataFrame(data)
            df['hour'] = pd.to_datetime(df['hour'], unit='h').dt.hour
            
            # Vervollständigen der Daten für fehlende Stunden
            all_hours = list(range(24))
            df = df.set_index('hour').reindex(all_hours, fill_value=0).reset_index()
            
            # Erstellen des Liniendiagramms mit Plotly Express
            fig = px.line(df, x='hour', y='avg_sales_per_hour', title='Average Sales per Hour')
            
            # Anpassen der Achsenbeschriftungen und der sichtbaren x-Werte
            fig.update_layout(
                xaxis_title='Time in hour',  # X-Achse
                yaxis_title='Average Sales per Hour',
                width=800,  # Setzen der Breite des Diagramms
                height=395,  # Setzen der Höhe des Diagramms
                xaxis=dict(
                    tickmode='array',
                    tickvals=[hour for hour in all_hours if df.loc[df['hour'] == hour, 'avg_sales_per_hour'].sum() > 0]
                )
            )
            
            st.plotly_chart(fig)
        else:
            st.write("Keine Daten verfügbar.")
def display_bar_chart(selected_storeid=None):
    if selected_storeid:
        data = fetch_avg_orders_per_day(selected_storeid)
        if data:
            df = pd.DataFrame(data)
            
            # Create the bar chart with Plotly Express
            fig = px.bar(df, x='day_of_week', y='avg_orders', 
                         title='Average Number of Orders per Day of Week')
            
            # Customize the layout
            fig.update_layout(
                xaxis_title='Day of Week',
                yaxis_title='Average Number of Orders',
                width=800,  # Set the width of the chart
                height=395  # Set the height of the chart
            )
            
            st.plotly_chart(fig)
        else:
            st.write("No data available for average number of orders per day.")



def main():
    
    col1, col2, col3 = st.columns([1, 20, 8])
    
    with col2:
        # Extract query parameters from the URL
        query_params = st.query_params
        store_id_from_url = query_params.get("storeid", None)

        min_order_count = st.sidebar.number_input("Minimum number of repeat orders:", min_value=1, value=1)
        data = fetch_data(min_order_count)
        
                    
        if data:
            with st.container():
                    # Ensure the selected_storeid is initialized in session state
                if "selected_storeid" not in st.session_state:
                    st.session_state.selected_storeid = store_id_from_url
                    
                fig = generate_heatmap(data, selected_storeid=st.session_state.selected_storeid)
                st.sidebar.info("Select a store from the heatmap to see store and customer locations.")
                
                if fig:
                    selected_points = plotly_events(fig, click_event=True)
                    if selected_points:
                        selected_storeid = selected_points[0]['x']
                        st.session_state.selected_storeid = selected_storeid
                        st.query_params.update(storeid=selected_storeid)
                        display_store_location_and_customers(selected_storeid, min_order_count)
                        st.rerun()
                    elif st.session_state.selected_storeid:
                        display_store_location_and_customers(st.session_state.selected_storeid, min_order_count)
                else:
                    st.warning("No data to display for the selected criteria.")
        else:
            st.warning("No data available.")


    with col3:
        if "selected_storeid" in st.session_state:
            display_line_chart(st.session_state.selected_storeid)
            display_bar_chart(st.session_state.selected_storeid)
            