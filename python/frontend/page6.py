import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import requests

def fetch_data():
    url = "http://localhost:8000/repeat-customers-report/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Fehler beim Abrufen der Daten")
        return []

def main():
    st.write("Willkommen zur Kundenreport-Seite!")
    st.write("Hier finden Sie Informationen über unsere wiederkehrenden Kunden.")

    data = fetch_data()

    if data:
        df = pd.DataFrame(data)

        bins = [0, 400, 600, 800, 1000, 1200, 1400]
        labels = ['0-400', '400-600', '600-800', '800-1000', '1000-1200', '1200-1400']
        df['customer_range'] = pd.cut(df['total_customers'], bins=bins, labels=labels)

        # Ensure all possible values are handled
        all_possible_labels = set(labels)
        existing_labels = set(df['customer_range'])
        missing_labels = all_possible_labels - existing_labels
        if missing_labels:
            for label in missing_labels:
                # Create a temporary DataFrame with the missing label
                temp_df = pd.DataFrame({'customer_range': [label], 'total_customers': [0], 'storeid': [None]})
                # Concatenate the original DataFrame with the temporary DataFrame
                df = pd.concat([df, temp_df], ignore_index=True)

        # Reverse the order of labels for the y-axis
        labels_reversed = labels[::-1]

        z_values = np.full((len(labels), len(df['storeid'].unique())), np.nan)

        range_index_map = {label: idx for idx, label in enumerate(labels_reversed)}

        for i, store in enumerate(df['storeid'].unique()):
            store_data = df[df['storeid'] == store]
            for _, row in store_data.iterrows():
                # Handle missing or nan values
                if pd.isna(row['customer_range']):
                    continue  # Skip rows with missing customer_range
                range_index = range_index_map.get(row['customer_range'], None)
                if range_index is None:
                    st.warning(f"Unexpected customer_range value: {row['customer_range']}")
                    continue
                z_values[range_index, i] = row['repeat_rate']

        fig = px.imshow(z_values,
                        labels=dict(x="Store ID", y="Total Customers", color="% Repeat Rate"),
                        x=df['storeid'].unique(),
                        y=labels_reversed,
                        color_continuous_scale="Viridis")

        st.plotly_chart(fig)
