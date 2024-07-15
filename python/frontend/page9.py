import pandas as pd
import streamlit as st
import requests
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Fetch dashboard overview data
@st.cache_data
def fetch_dashboard_overview():
    try:
        url = 'http://localhost:8000/dashboard-overview'  # Adjust the URL to match your actual endpoint
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return {}
    
@st.cache_data
def fetch_revenue_ranking():
    try:
        url = 'http://localhost:8000/revenue-ranking/'  # Adjust the URL to match your actual endpoint
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return {}    

@st.cache_data
def fetch_pizzerankings():
    try:
        url = 'http://localhost:8000/pizzerankings/'  # Adjust the URL to match your actual endpoint
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
                background-color: #f9f9f9; padding: 5px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="flex-grow: 1;">
            <h5 style="margin: 0; font-size: 1,0em;">{title}</h5>
            <p style="font-size: 1.2em; font-weight: bold; margin: 0;">{value}</p>
        </div>
        <div style="font-size: 1.5em; color: #007BFF;">
            {icon}
        </div>
    </div>
    """
    return card_html

def create_revenue_ranking_chart(data):
    # Convert data to a DataFrame
    df = pd.DataFrame(data)
    df['total_revenue'] = df['total_revenue'].astype(float)

    # Group by storeid and find the last known x-value (year and quarter)
    last_known_period = df.groupby('storeid').last().reset_index()

    # Sort the legend by rank for the last known x-value
    sorted_legend = last_known_period.sort_values(by='rank')['storeid'].tolist()

    # Create the line chart with plotly.graph_objects
    fig = go.Figure()

    # Group by storeid and create a trace for each store in sorted order
    for storeid in sorted_legend:
        # Use .loc to avoid warning
        store_data = df.loc[df['storeid'] == storeid].copy()
        # Combine year and quarter as new index for x-axis
        store_data.loc[:, 'period'] = store_data['year'].astype(str) + ' ' + store_data['quarter']
        fig.add_trace(go.Scatter(x=store_data['period'],
                                 y=store_data['rank'],
                                 mode='lines+markers',
                                 name=f'Store {storeid}'))

    # Layout adjustments
    fig.update_layout(title='Ranking of stores by Revenue',
                      xaxis=dict(tickangle=-45, tickmode='linear', dtick=1),
                      yaxis=dict(title='Rank', side='left', autorange='reversed'),
                      yaxis2=dict(title='Rank', overlaying='y', side='right',
                                  tickvals=df['rank'].unique().tolist(),
                                  ticktext=df['rank'].astype(str).unique().tolist()),
                                                        autosize=False,
                      width=900,
                      height=410)

    return fig

def create_pizza_ranking_chart(data):
    # Define the colors in the specified order
    colors = [
        '#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
        '#ff7f00', '#ffff33', '#a65628', '#f781bf',
        '#999999', '#a6cee3', '#1f78b4', '#b2df8a',
    ]

    # Convert data to a DataFrame
    df = pd.DataFrame(data)
    
    # Add a new column combining year and quarter
    df['year_quarter'] = df.apply(lambda row: f"{row['year']} Q{row['quarter']}", axis=1)
    
    # Sort data by year and quarter
    df_sorted = df.sort_values(by=['year_quarter'])
    
    # Get the last known period and sort legend by rank
    last_known_period = df.groupby('name').last().reset_index()    
    sorted_legend = last_known_period.sort_values(by='rank')['name'].tolist()    
    
    # Create the chart with Plotly
    fig = go.Figure()
    
    # Add a line for each pizza, sorted by sorted_legend
    for i, pizza_name in enumerate(sorted_legend):
        filtered_df = df[df['name'] == pizza_name]
        fig.add_trace(go.Scatter(
            x=filtered_df['year_quarter'],
            y=filtered_df['rank'],
            mode='lines+markers',
            name=pizza_name,
            line=dict(color=colors[i % len(colors)])  # Use colors cyclically
        ))
    
    # Layout adjustments
    fig.update_layout(
        title='Ranking of pizzas by Total Sales',
        yaxis=dict(title='Rank', side='left', autorange='reversed'),
        xaxis={'tickangle': -45},
        width=1200,
        height=380
    )
    
    return fig


def main():
    # Set background image (optional)
    background_image = """
    <style>
    .stApp {
        background: url('DallEPizzaLogo.png');
        background-size: cover;
    }
    </style>
    """
    st.markdown(background_image, unsafe_allow_html=True)

    # Define columns for layout
    col1, col2 = st.columns([4, 5])  # Adjust column ratios as needed

    # Column 1: Logo
    with col2:

        st.sidebar.image("static/DallEPizzaLogo.png", width=200)  # Adjust width as needed
        
        ranking_data = fetch_revenue_ranking()

        # Erstelle und zeige das Diagramm
        chart = create_revenue_ranking_chart(ranking_data)
        st.plotly_chart(chart)
        
        # Datenabruf
        pizzerankings_data = fetch_pizzerankings()
        
        # Erstelle und zeige das Diagramm
        chart = create_pizza_ranking_chart(pizzerankings_data)
        st.plotly_chart(chart)

    # Column 2: Title and dashboard overview
    with col1:
        #st.title("Welcome to the Data Analysis Dashboard")
        st.header("Welcome to WESTERN PIZZA's Shop Analytics ")

        # Fetch the data
        data = fetch_dashboard_overview()
        
        # Check if the keys exist in the data
        total_revenue = data.get('TotalRevenue', 0)
        total_orders = data.get('TotalOrders', 0)
        total_customers = data.get('TotalCustomers', 0)
        total_stores = data.get('TotalStores', 0)
        pizzas_sold = data.get('PizzasSold', 0)
        number_of_products = data.get('NumberOfProducts', 0)
        most_popular_product = data.get('MostPopularProduct', "N/A")
        average_order_value = data.get('AverageOrderValue', 0)
        
        # Icons
        dollar_icon = "💵"
        list_icon = "📋"
        person_icon = "👤"
        store_icon = "🏪"
        pizza_icon = "🍕"
        product_icon = "📦"
        popular_icon = "⭐"
        avg_order_icon = "📊"

        # Create cards
        st.markdown(create_card("Total Revenue", f"${total_revenue:,.2f}", dollar_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Orders", total_orders, list_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Customers", total_customers, person_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Stores", total_stores, store_icon), unsafe_allow_html=True)
        st.markdown(create_card("Pizzas Sold", pizzas_sold, pizza_icon), unsafe_allow_html=True)
        st.markdown(create_card("Number of Products", number_of_products, product_icon), unsafe_allow_html=True)
        st.markdown(create_card("Most Popular Product", most_popular_product, popular_icon), unsafe_allow_html=True)
        st.markdown(create_card("Average Order Value", f"${average_order_value:,.2f}", avg_order_icon), unsafe_allow_html=True)

