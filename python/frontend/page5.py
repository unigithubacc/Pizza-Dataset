import streamlit as st
import plotly.graph_objects as go
import requests
from datetime import datetime

# Fetch sales distribution
def fetch_sales_distribution(year=None, quarter=None, month=None):
    try:
        url = 'http://localhost:8000/sales-distribution'
        params = {}
        if year and year != "All":
            params['year'] = year
        if quarter and quarter != "All":
            params['quarter'] = quarter
        if month:
            params['month'] = month
        
        response = requests.get(url, params=params)  
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []

# Create pie chart
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

def convert_month_slider_value(month_slider_value):
    # Calculate the year and month based on the slider value
    base_year = 2020
    year = base_year + (month_slider_value - 1) // 12
    month = (month_slider_value - 1) % 12 + 1
    # Format month name and year
    month_name = datetime(year, month, 1).strftime('%b')
    return f"{month_name}. {year}", year, month

def main():
    st.title("Sales Distribution by Product Category")
    
    # Radio button to select filter mode
    filter_mode = st.radio("Select filter mode", ["Year and Quarter", "Month"])
    
    if filter_mode == "Year and Quarter":
        # Dropdown menu for selecting years including "All"
        selected_year = st.selectbox("Select year", ["All", 2020, 2021, 2022], index=0)
        
        # Dropdown menu for selecting quarters including "All"
        selected_quarter = st.selectbox("Select quarter", ["All", "Q1", "Q2", "Q3", "Q4"], index=0)
        
        # Fetch filtered sales data based on the selected year and quarter
        st.write(f"Fetching data for year: {selected_year} and quarter: {selected_quarter}")
        sales_data = fetch_sales_distribution(year=selected_year, quarter=selected_quarter)
    
    else:
        # Slider for selecting month
        selected_month = st.slider("Select month (1 = Jan 2020, 36 = Dec 2022)", min_value=1, max_value=36, value=1)
        readable_month, year, month = convert_month_slider_value(selected_month)
        
        # Fetch filtered sales data based on the selected month
        st.write(f"Fetching data for {readable_month}")
        sales_data = fetch_sales_distribution(month=selected_month)
    
    if sales_data:
        fig = create_pie_chart(sales_data)
        st.plotly_chart(fig)
        
        # Display the list of categories and their sales figures
        st.subheader("List of categories and their sales figures:")
        st.table(sales_data)

if __name__ == "__main__":
    main()
