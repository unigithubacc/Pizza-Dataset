import streamlit as st
import requests
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# Function to fetch sales data for all stores
def fetch_sales_data():
    response = requests.get(f'http://127.0.0.1:8000/sales-report/')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Verkaufsdaten.")
        return []

# Function to create bar chart for top-selling stores
def create_store_bar_chart(data, selected_store_ids, selected_store_colors, default_color):
    store_ids = sorted(set([item['storeid'] for item in data]))
    total_revenue = {store_id: sum(item['number_of_sales'] for item in data if item['storeid'] == store_id) for store_id in store_ids}

    sorted_store_ids = sorted(total_revenue.keys(), key=lambda x: total_revenue[x], reverse=True)

    fig = go.Figure()

    for store_id in sorted_store_ids:
        marker_color = selected_store_colors[selected_store_ids.index(store_id)] if store_id in selected_store_ids else default_color
        fig.add_trace(go.Bar(
            x=[store_id],
            y=[total_revenue[store_id]],
            name=f'Store {store_id}',
            legendgroup=f'Store {store_id}',
            showlegend=True,
            marker_color=marker_color,
            customdata=[store_id],
            hoverinfo='x+y'
        ))

    fig.update_layout(barmode='group',
                      title='Top Selling Stores',
                      xaxis_title='Store ID',
                      yaxis_title='Total Sales',
                      clickmode='event+select',
                      width=800,  # Setzt die Breite auf 800px
                      height=400)  # Setzt die Höhe auf 400px

    return fig

# Function to create line chart for sales data of multiple stores
def create_sales_line_chart(data, store_ids, store_colors):
    fig = go.Figure()

    for i, store_id in enumerate(store_ids):
        store_data = [item for item in data if item['storeid'] == store_id]
        if store_data:
            quarters = [f"{item['year']}-{item['quarter']}" for item in store_data]
            number_of_sales = [item['number_of_sales'] for item in store_data]

            fig.add_trace(go.Scatter(
                x=quarters,
                y=number_of_sales,
                mode='lines+markers',
                name=f'Store {store_id}',
                line=dict(color=store_colors[i])
            ))

    fig.update_layout(title='Number of Sales for Selected Stores',
                      xaxis_title='Year-Quarter',
                      yaxis_title='Number of Sales',
                      width=800,  # Setzt die Breite des Diagramms auf 800 Pixel
                      height=400  # Setzt die Höhe des Diagramms auf 400 Pixel
    )

    return fig

# Function to create an empty line chart
def create_empty_line_chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines+markers', name='No data'))
    fig.update_layout(title='Number of Sales for Store',
                      xaxis_title='Year-Quarter',
                      yaxis_title='Number of Sales',
                      width=800,  # Setzt die Breite des Diagramms auf 800 Pixel
                      height=400  # Setzt die Höhe des Diagramms auf 400 Pixel
    )
    return fig

def main():

    # Check if sales data is already in session_state
    if 'sales_data' not in st.session_state:
        st.session_state.sales_data = fetch_sales_data()

    sales_data = st.session_state.sales_data
    if sales_data:
        if 'selected_store_ids' not in st.session_state:
            st.session_state.selected_store_ids = []
            st.session_state.selected_store_colors = []

        # Define color palette
        color_palette = ['#f781bf', '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628']
        default_color = 'blue'

        fig = create_store_bar_chart(sales_data, st.session_state.selected_store_ids, st.session_state.selected_store_colors, default_color)
        selected_points = plotly_events(fig, click_event=True)
        
        if selected_points:
            # Extract the store_id from the x-coordinate
            new_store_id = selected_points[0]['x']
            if new_store_id in st.session_state.selected_store_ids:
                index = st.session_state.selected_store_ids.index(new_store_id)
                st.session_state.selected_store_ids.pop(index)
                st.session_state.selected_store_colors.pop(index)
            else:
                st.session_state.selected_store_ids.append(new_store_id)
                st.session_state.selected_store_colors.append(color_palette[len(st.session_state.selected_store_ids) % len(color_palette)])
            st.rerun()

        # Update the bar chart with new colors
        fig = create_store_bar_chart(sales_data, st.session_state.selected_store_ids, st.session_state.selected_store_colors, default_color)

        if st.session_state.selected_store_ids:
            st.write(f"Selected Store IDs: {st.session_state.selected_store_ids}")  # Debugging Line
            sales_fig = create_sales_line_chart(sales_data, st.session_state.selected_store_ids, st.session_state.selected_store_colors)
        else:
            sales_fig = create_empty_line_chart()
            st.warning("Select store IDs to see the number of sales for those stores")
            
        st.plotly_chart(sales_fig, use_container_width=False)
    else:
        st.error("No sales data available.")

