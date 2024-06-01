import streamlit as st
import plotly.graph_objects as go
import requests
from collections import defaultdict

def fetch_sales_distribution():
    try:
        response = requests.get('http://localhost:8000/sales-distribution')  # Replace with your actual API URL
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []

def create_pie_chart(data):
    categories = [item['category'] for item in data]
    total_sales = [item['total_sold'] for item in data]

    fig = go.Figure(data=[go.Pie(labels=categories, values=total_sales, hole=.3)])
    fig.update_layout(title_text='Sales Distribution by Product Category')
    
    return fig

def main():
    st.title("Sales Distribution by Product Category")
    sales_data = fetch_sales_distribution()
    if sales_data:
        fig = create_pie_chart(sales_data)
        st.plotly_chart(fig)
        
        # Display the list of categories and their sales figures
        st.subheader("List of categories and their sales figures:")
        st.table(sales_data)