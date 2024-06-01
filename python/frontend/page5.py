import streamlit as st
import plotly.graph_objects as go
import requests
from collections import defaultdict


def fetch_sales_distribution(year=None):
    try:
        url = 'http://localhost:8000/sales-distribution'
        if year and year != "All":
            url += f'?year={year}'
        response = requests.get(url)  
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
    }
    
    # Apply color mapping
    colors = [color_map.get(category, "#000000") for category in categories]  # Default to black if category not in map

    fig = go.Figure(data=[go.Pie(labels=categories, values=total_sales, hole=.3, marker=dict(colors=colors))])
    fig.update_layout(title_text='Sales Distribution by Product Category')
    
    return fig

def main():
    st.title("Sales Distribution by Product Category")
    
    # Dropdown menu for selecting years including "All"
    selected_year = st.selectbox("Select year", ["All", 2020, 2021, 2022])

    sales_data = fetch_sales_distribution(selected_year)
    if sales_data:
        fig = create_pie_chart(sales_data)
        st.plotly_chart(fig)
        
        # Display the list of categories and their sales figures
        st.subheader("List of categories and their sales figures:")
        st.table(sales_data)