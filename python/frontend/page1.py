import streamlit as st
import plotly.graph_objects as go
import requests
from collections import defaultdict
from datetime import datetime

def fetch_top_pizzas():
    response = requests.get('http://localhost:8000/products/top-selling-products')
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching data.")
        return []

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

def fetch_revenue_over_time():
    response = requests.get('http://localhost:8000/products/revenue-over-time')
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching data.")
        return []

def fetch_revenue_by_size(year=None, quarter=None, month=None):
    try:
        url = 'http://localhost:8000/products/revenue-by-size'
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

def create_stacked_barchart(data):
    pizza_sales = defaultdict(int)
    for item in data:
        pizza_sales[item['name']] += item['TotalSold']

    sorted_pizzas = sorted(pizza_sales.items(), key=lambda x: x[1], reverse=True)
    sorted_pizza_names = [pizza[0] for pizza in sorted_pizzas]

    sizes = sorted(set([item['size'] for item in data]))
    sales_by_size = {size: [0] * len(sorted_pizza_names) for size in sizes}

    for item in data:
        index = sorted_pizza_names.index(item['name'])
        sales_by_size[item['size']][index] = item['TotalSold']

    fig = go.Figure()

    for size in sizes:
        fig.add_trace(go.Bar(
            x=sorted_pizza_names,
            y=sales_by_size[size],
            name=size,
            legendgroup=size,
            showlegend=True
        ))

    fig.update_layout(barmode='stack',
                      title='Sales figures for various pizzas by size',
                      xaxis_tickangle=-45,
                      xaxis_title='Pizza Name',
                      yaxis_title='Total Sold',
                      width=800,
                      height=400
                     )

    return fig

def create_pie_chart(data):
    categories = [item['category'] for item in data]
    total_sales = [item['total_sold'] for item in data]

    color_map = {
        "Vegetarian": "#636EFA",
        "Specialty": "#EF553B",
        "Classic": "#00CC96",
    }
    
    colors = [color_map.get(category, "#FFFFFF") for category in categories]

    fig = go.Figure(data=[go.Pie(labels=categories, values=total_sales, hole=.3, marker=dict(colors=colors))])
    fig.update_layout(title_text='Sales Distribution by Product Category',
                      width=800,
                      height=400
                      )
    
    return fig

def create_line_chart(data):
    fig = go.Figure()
    product_groups = defaultdict(list)
    
    for item in data:
        product_groups[item['name']].append((item['month'], item['revenue']))
    
    for product, values in product_groups.items():
        values.sort()
        months = [v[0] for v in values]
        revenues = [v[1] for v in values]
        fig.add_trace(go.Scatter(x=months, y=revenues, mode='lines', name=product))
    
    fig.update_layout(title='Revenue Over Time by Product',
                      xaxis_title='Month',
                      yaxis_title='Revenue',
                      width=800,
                      height=400)
    
    return fig

def create_size_pie_chart(data):
    sizes = [item['size'] for item in data]
    revenues = [item['revenue'] for item in data]

    fig = go.Figure(data=[go.Pie(labels=sizes, values=revenues, hole=.3)])
    fig.update_layout(title_text='Most Popular Size by Revenue',
                      width=800,
                      height=400
                      )
    
    return fig

def convert_month_slider_value(month_slider_value):
    base_year = 2020
    year = base_year + (month_slider_value - 1) // 12
    month = (month - 1) % 12 + 1
    month_name = datetime(year, month, 1).strftime('%b')
    return f"{month_name}. {year}", year, month

def main():
    st.sidebar.title("Filters")
    
    filter_mode = st.sidebar.radio("Select filter mode", ["Year and Quarter", "Month"])
    
    if filter_mode == "Year and Quarter":
        selected_year = st.sidebar.selectbox("Select year", ["All", 2020, 2021, 2022], index=0)
        selected_quarter = st.sidebar.selectbox("Select quarter", ["All", "Q1", "Q2", "Q3", "Q4"], index=0)
        st.write(f"Fetching data for year: {selected_year} and quarter: {selected_quarter}")
        sales_data = fetch_sales_distribution(year=selected_year, quarter=selected_quarter)
        size_data = fetch_revenue_by_size(year=selected_year, quarter=selected_quarter)
    
    else:
        selected_month = st.sidebar.slider("Select month (1 = Jan 2020, 36 = Dec 2022)", min_value=1, max_value=36, value=1)
        readable_month, year, month = convert_month_slider_value(selected_month)
        st.write(f"Fetching data for {readable_month}")
        sales_data = fetch_sales_distribution(month=selected_month)
        size_data = fetch_revenue_by_size(month=selected_month)

    pizzas_data = fetch_top_pizzas()
    revenue_data = fetch_revenue_over_time()

    if pizzas_data and sales_data and revenue_data and size_data:
        col1, col2 = st.columns(2)

        with col1:
            bar_chart = create_stacked_barchart(pizzas_data)
            st.plotly_chart(bar_chart)

            pie_chart = create_pie_chart(sales_data)
            st.plotly_chart(pie_chart)

        with col2:
            line_chart = create_line_chart(revenue_data)
            st.plotly_chart(line_chart)

            size_pie_chart = create_size_pie_chart(size_data)
            st.plotly_chart(size_pie_chart)

if __name__ == "__main__":
    main()
