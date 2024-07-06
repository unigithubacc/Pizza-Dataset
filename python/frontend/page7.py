import streamlit as st
import requests
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
from datetime import date

@st.cache_data
def fetch_product_frequency(store_id, start_date, end_date):
    response = requests.get(f'http://localhost:8000/products/frequency', params={
        'storeid': store_id,
        'start_date': start_date,
        'end_date': end_date
    })
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

@st.cache_data
def fetch_top_selling_stores(start_date, end_date):
    response = requests.get(f'http://localhost:8000/top-selling-stores?start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

@st.cache_data
def fetch_store_product_revenue(store_id, start_date, end_date, divide_by_size):
    response = requests.get(f'http://localhost:8000/store-products-revenue?storeid={store_id}&start_date={start_date}&end_date={end_date}&divide_by_size={divide_by_size}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

@st.cache_data
def fetch_products_size(store_id, start_date, end_date):
    response = requests.get(f'http://localhost:8000/store-products-size-revenue?storeid={store_id}&start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

@st.cache_data
def fetch_products_category(store_id, start_date, end_date):
    response = requests.get(f'http://localhost:8000/store-products-category-revenue?storeid={store_id}&start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

def create_store_bar_chart2(data):
    store_ids = sorted(set([item['storeid'] for item in data]))
    total_revenue = {store_id: sum(item['TotalRevenue'] for item in data if item['storeid'] == store_id) for store_id in store_ids}

    sorted_store_ids = sorted(total_revenue.keys(), key=lambda x: total_revenue[x], reverse=True)

    fig2 = go.Figure()

    for store_id in sorted_store_ids:
        fig2.add_trace(go.Bar(
            x=[store_id],
            y=[total_revenue[store_id]],
            name=f'Store {store_id}',
            legendgroup=f'Store {store_id}',
            showlegend=False,
            marker_color='lightskyblue',
            customdata=[store_id],
            hoverinfo='x+y'
        ))

    fig2.update_layout(barmode='group',
                      title='Top Selling Stores',
                      xaxis_title='Store ID',
                      yaxis_title='Total Revenue in $',
                      clickmode='event+select',
                      height=445,
                      width=640
                      )

    return fig2

def create_product_revenue_bar_chart(data, divide_by_size, size_color_map, metric, chart_type):
    product_names = [product['name'] for product in data]
    product_metrics = [product[metric] for product in data]

    # Define the color mapping for each category
    category_color_map = {
        'Classic': '#66a61e',
        'Vegetarian': '#e6ab02',
        'Specialty': '#a6761d'
    }
    
    # Map each pizza to its corresponding category color
    product_color_map = {
        'Margherita Pizza': category_color_map['Classic'],
        'Pepperoni Pizza': category_color_map['Classic'],
        'Hawaiian Pizza': category_color_map['Classic'],
        'Meat Lover\'s Pizza': category_color_map['Classic'],
        'Veggie Pizza': category_color_map['Vegetarian'],
        'Sicilian Pizza': category_color_map['Vegetarian'],
        'BBQ Chicken Pizza': category_color_map['Specialty'],
        'Buffalo Chicken Pizza': category_color_map['Specialty'],
        'Oxtail Pizza': category_color_map['Specialty']
    }

    if divide_by_size:
        product_sizes = [product['size'] for product in data]
        labels = [f"{name} ({size})" for name, size in zip(product_names, product_sizes)]
        colors = [size_color_map[size] for size in product_sizes]
    else:
        labels = product_names
        colors = [product_color_map.get(name, 'lightskyblue') for name in product_names]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels,
        x=product_metrics,
        marker_color=colors,
        hoverinfo='y+x',
        orientation='h',  # Set horizontal orientation
        name='Product Revenue' if chart_type == 'Revenue' else f'Product Number of Sales'
    ))

    fig.update_layout(
        title=f'Store Product Revenue' if chart_type == 'Revenue' else f'Store Product Number of Sales',
        yaxis_title='Pizza Name' + (' (Size)' if divide_by_size else ''),
        xaxis_title=f'Revenue in $' if chart_type == 'Revenue' else f'Number of Sales',
        height=500,
        barmode='relative'
    )

    return fig

def create_product_size_pie_chart(data, size_color_map, metric, chart_type):
    size_names = [size['size'] for size in data]
    size_metrics = [size[metric] for size in data]
    colors = [size_color_map[size] for size in size_names]

    fig = go.Figure(data=[go.Pie(
        labels=size_names, 
        values=size_metrics, 
        hole=0.3,
        marker=dict(colors=colors)
    )])

    fig.update_layout(
        title=f'Product Revenue by Size' if chart_type == 'Revenue' else f'Number of Sales by Size',
    )

    return fig

def create_product_category_pie_chart(data, metric, chart_type):
    category_names = [category['category'] for category in data]
    category_metrics = [category[metric] for category in data]

    category_color_map = {
        'Classic': '#66a61e',
        'Vegetarian': '#e6ab02',
        'Specialty': '#a6761d'
    }

    colors = [category_color_map.get(category, 'lightskyblue') for category in category_names]

    fig = go.Figure(data=[go.Pie(
        labels=category_names, 
        values=category_metrics, 
        hole=0.3,
        marker=dict(colors=colors)
    )])

    fig.update_layout(
        title=f'Product Revenue by Category' if chart_type == 'Revenue' else f'Number of Sales by Category',
    )

    return fig

def create_heatmap(data):
    product1_names = [item['product1'] for item in data]
    product2_names = [item['product2'] for item in data]
    frequency = [item['avgfrequencyperorder'] for item in data]

    unique_products = sorted(set(product1_names + product2_names))
    product_index = {product: idx for idx, product in enumerate(unique_products)}

    heatmap_data = {
        'x': [product_index[p1] for p1 in product1_names],
        'y': [product_index[p2] for p2 in product2_names],
        'z': frequency,
        'type': 'heatmap',
        'colorscale': 'reds',
        'showscale': True,
    }

    layout = {  
        'title': 'Analysis of Product Pairings: Product1 Frequency vs. Combined Purchases',
        'xaxis': {
            'tickvals': list(product_index.values()),
            'ticktext': list(product_index.keys()),
            'title': 'Product 1'
        },
        'yaxis': {
            'tickvals': list(product_index.values()),
            'ticktext': list(product_index.keys()),
            'title': 'Product 2'
        }
    }

    fig = go.Figure(data=[heatmap_data], layout=layout)
    return fig

def main():
    query_params = st.query_params
    store_id_from_url = query_params.get("storeid", None)

    if 'selected_store_id' not in st.session_state:
        st.session_state.selected_store_id = store_id_from_url

    if store_id_from_url and store_id_from_url != st.session_state.selected_store_id:
        st.session_state.selected_store_id = store_id_from_url

    start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date(2023, 1, 1))
    
    divide_by_size = st.sidebar.checkbox("Divide Pizzas by Size", value=False)
    
    # Sidebar option to select between 'Revenue' and 'Total Sales'
    chart_type = st.sidebar.radio("Select Chart Type", ("Revenue", "Total Sales"))
    metric = 'product_revenue' if chart_type == 'Revenue' else 'number_of_orders'

    col1, col2, col3 = st.columns([2, 2 ,1])

    size_color_map = {
        'Small': '#1b9e77',
        'Medium': '#d95f02',
        'Large': '#7570b3',
        'Extra Large': '#e7298a'
    }

    with col1:
        stores_data = fetch_top_selling_stores(start_date, end_date)
        if stores_data:
            fig2 = create_store_bar_chart2(stores_data)
            selected_points = plotly_events(fig2, click_event=True)
            
            if selected_points:
                st.session_state.selected_store_id = selected_points[0]['x']
                st.query_params.update(storeid=st.session_state.selected_store_id)
      
        st.divider()
        
        col4, col5 = st.columns([1, 5])
        with col5:        
            st.subheader(f"Selected Store ID: {st.session_state.selected_store_id}")
            if st.session_state.selected_store_id is None:
                st.warning("Select a bar to see more information for this Store.") 

    with col2:
        if st.session_state.selected_store_id is not None:
            selected_store_id = st.session_state.selected_store_id
            store_product_data = fetch_store_product_revenue(selected_store_id, start_date, end_date, divide_by_size)
            if store_product_data:
                fig = create_product_revenue_bar_chart(store_product_data, divide_by_size, size_color_map, metric, chart_type)
                st.plotly_chart(fig)

            product_frequency_data = fetch_product_frequency(selected_store_id, start_date, end_date)
            if product_frequency_data:
                fig_heatmap = create_heatmap(product_frequency_data)
                st.plotly_chart(fig_heatmap)
                
            
    with col3:
        if st.session_state.selected_store_id is not None:
            store_category_data = fetch_products_category(selected_store_id, start_date, end_date)
            store_size_data = fetch_products_size(selected_store_id, start_date, end_date)
            
            if store_category_data and store_size_data:
                pie_chart_category = create_product_category_pie_chart(store_category_data, metric, chart_type)
                st.plotly_chart(pie_chart_category)                
                
                pie_chart_size = create_product_size_pie_chart(store_size_data, size_color_map, metric, chart_type)
                st.plotly_chart(pie_chart_size)
