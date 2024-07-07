import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import requests
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

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

def display_store_location(storeid):
    store_details = fetch_store_details(storeid)
    if store_details:
        fig = go.Figure(go.Scattermapbox(
            lat=[store_details['latitude']],
            lon=[store_details['longitude']],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14
            ),
            text=f"{store_details['city']}, {store_details['state']}"
        ))

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(
                center=go.layout.mapbox.Center(
                    lat=store_details['latitude'],
                    lon=store_details['longitude']
                ),
                zoom=10
            ),
            margin={"r":0,"t":0,"l":0,"b":0}
        )

        st.plotly_chart(fig)
    else:
        st.error("Unable to fetch store details")

def main():
    min_order_count = st.sidebar.number_input("Minimum number of repeat orders:", min_value=0, value=1)
    data = fetch_data(min_order_count)

    if data:
        fig = generate_heatmap(data)
        if fig:
            selected_points = plotly_events(fig, click_event=True)
            if selected_points:
                selected_storeid = selected_points[0]['x']
                display_store_location(selected_storeid)
        else:
            st.warning("No data to display for the selected criteria.")

if __name__ == "__main__":
    main()
