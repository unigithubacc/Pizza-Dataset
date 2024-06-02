import streamlit as st
import plotly.graph_objects as go
import requests
from collections import defaultdict


def fetch_sales_distribution(year=None, quarter=None):
    try:
        url = 'http://localhost:8000/sales-distribution'
        params = {}
        if year and year != "All":
            params['year'] = year
        if quarter and quarter != "All":
            params['quarter'] = quarter
        
        response = requests.get(url, params=params)  
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []

def create_pie_chart(data):
    categories = [item['category'] for item in data]
    total_sales = [item['total_sold'] for item in data]

    # Define consistent color mapping for each category
    color_map = {
        "Vegetarian": "#636EFA",
        "Specialty": "#EF553B",
        "Classic": "#00CC96",
        # Add any other categories that you have
    }
    
    # Apply color mapping
    colors = [color_map.get(category, "#FFFFFF") for category in categories]  # Default to white if category not in map

    fig = go.Figure(data=[go.Pie(labels=categories, values=total_sales, hole=.3, marker=dict(colors=colors))])
    fig.update_layout(title_text='Sales Distribution by Product Category')
    
    return fig

def main():
    st.title("Sales Distribution by Product Category")
    
    # Dropdown menu for selecting years including "All"
    selected_year = st.selectbox("Select year", ["All", 2020, 2021, 2022], index=0)
    
    # Dropdown menu for selecting quarters including "All"
    selected_quarter = st.selectbox("Select quarter", ["All", "Q1", "Q2", "Q3", "Q4"], index=0)

    sales_data = fetch_sales_distribution(selected_year, selected_quarter)
    if sales_data:
        fig = create_pie_chart(sales_data)
        st.plotly_chart(fig)
        
        # Display the list of categories and their sales figures
        st.subheader("List of categories and their sales figures:")
        st.table(sales_data)