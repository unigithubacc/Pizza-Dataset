import streamlit as st
import requests
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
from datetime import date

# Funktion zum Abrufen der Top-Selling-Stores-Daten
@st.cache_data
def fetch_top_selling_stores(start_date, end_date):
    response = requests.get(f'http://localhost:8000/top-selling-stores?start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

# Funktion zum Abrufen der Revenue-Daten für ausgewählte Stores
@st.cache_data
def fetch_revenue_data(store_ids, period, end_date):
    store_id_query = "&".join([f"storeid={store_id}" for store_id in store_ids])
    url = f'http://localhost:8000/revenue-by-store/?{store_id_query}&period={period}&end_date={end_date}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Revenue-Daten.")
        return []

# Funktion zum Abrufen der Verkaufsdaten (Total Sales)
@st.cache_data
def fetch_sales_data(period, end_date):
    response = requests.get(f'http://localhost:8000/sales-report-time-interval/?period={period}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Verkaufsdaten.")
        return []

# Funktion zum Erstellen eines Balkendiagramms
def create_store_bar_chart(data, selected_store_ids, selected_store_colors, default_color):
    store_ids = sorted(set([item['storeid'] for item in data]))
    total_revenue = {store_id: next(item['TotalRevenue'] for item in data if item['storeid'] == store_id) for store_id in store_ids}

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
            hoverinfo='x+y',
            selectedpoints=None  # Ensure no selection highlighting
        ))

    fig.update_layout(barmode='group',
                      title='Top Selling Stores',
                      xaxis_title='Store ID',
                      yaxis_title='Revenue in $',
                      clickmode='event',
                      width=800,
                      height=400)

    return fig

# Funktion zum Erstellen eines Liniendiagramms für Revenue
def create_revenue_line_chart(data, store_ids, store_colors, period):
    fig = go.Figure()

    for i, store_id in enumerate(store_ids):
        store_data = [item for item in data if item['storeid'] == store_id]
        if store_data:
            x_values = [item['period'] for item in store_data]
            total_revenue = [item['total_revenue'] for item in store_data]

            fig.add_trace(go.Scatter(
                x=x_values,
                y=total_revenue,
                mode='lines+markers',
                name=f'Store {store_id}',
                line=dict(color=store_colors[i])
            ))

    fig.update_layout(title='Revenue for Selected Stores',
                      xaxis_title=f'{period}',
                      yaxis_title='Total Revenue',
                      width=800,
                      height=400)

    return fig

# Funktion zum Erstellen eines Liniendiagramms für Total Sales
def create_sales_line_chart(data, store_ids, store_colors, period):
    fig = go.Figure()

    for i, store_id in enumerate(store_ids):
        store_data = [item for item in data if item['storeid'] == store_id]
        if store_data:
            x_values = [item['period'] for item in store_data]
            total_sales = [item['total_sales'] for item in store_data]

            fig.add_trace(go.Scatter(
                x=x_values,
                y=total_sales,
                mode='lines+markers',
                name=f'Store {store_id}',
                line=dict(color=store_colors[i])
            ))

    fig.update_layout(title='Number of Sales for Selected Stores',
                      xaxis_title=f'{period}',
                      yaxis_title='Total Sales',
                      width=800,
                      height=400)

    return fig

# Funktion zum Erstellen eines leeren Liniendiagramms
def create_empty_line_chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines+markers', name='No data'))
    fig.update_layout(title='Number of Sales for Store',
                      xaxis_title='Period',
                      yaxis_title='Number of Sales',
                      width=800,
                      height=400)
    return fig

def main():
    # Datumseingabe
    start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date(2023, 1, 1))

    # Periodenauswahl
    period = st.sidebar.selectbox("Select Period", ["Day", "Month", "Quarter", "Year"], index=3)

    # API-Aufrufe nur bei Änderungen von end_date oder period
    if 'top_selling_stores' not in st.session_state or st.session_state.start_date != start_date or st.session_state.end_date != end_date:
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.top_selling_stores = fetch_top_selling_stores(start_date, end_date)

    top_selling_stores = st.session_state.top_selling_stores

    if top_selling_stores:
        if 'selected_store_ids' not in st.session_state:
            st.session_state.selected_store_ids = []
            st.session_state.selected_store_colors = []

        # Farbpalette definieren
        color_palette = ['#f781bf', '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628']
        default_color = 'lightskyblue'

        fig = create_store_bar_chart(top_selling_stores, st.session_state.selected_store_ids, st.session_state.selected_store_colors, default_color)
        selected_points = plotly_events(fig, click_event=True)

        if selected_points:
            # Store ID aus den ausgewählten Punkten extrahieren
            new_store_id = selected_points[0]['x']
            if new_store_id in st.session_state.selected_store_ids:
                index = st.session_state.selected_store_ids.index(new_store_id)
                st.session_state.selected_store_ids.pop(index)
                st.session_state.selected_store_colors.pop(index)
            else:
                st.session_state.selected_store_ids.append(new_store_id)
                st.session_state.selected_store_colors.append(color_palette[len(st.session_state.selected_store_ids) % len(color_palette)])

        # Aktualisiere das Balkendiagramm mit neuen Farben
        fig = create_store_bar_chart(top_selling_stores, st.session_state.selected_store_ids, st.session_state.selected_store_colors, default_color)

        # Erstelle und zeige das Revenue-Liniendiagramm unter dem Balkendiagramm
        if st.session_state.selected_store_ids:
            revenue_data = fetch_revenue_data(st.session_state.selected_store_ids, period, end_date)
            revenue_fig = create_revenue_line_chart(revenue_data, st.session_state.selected_store_ids, st.session_state.selected_store_colors, period)
            st.plotly_chart(revenue_fig, use_container_width=False)

            # Erstelle und zeige das Total Sales-Liniendiagramm
            sales_data = fetch_sales_data(period, end_date)
            sales_fig = create_sales_line_chart(sales_data, st.session_state.selected_store_ids, st.session_state.selected_store_colors, period)
            st.plotly_chart(sales_fig, use_container_width=False)
        else:
            empty_fig = create_empty_line_chart()
            st.plotly_chart(empty_fig, use_container_width=False)
            st.sidebar.warning("Select store IDs to see the number of sales for those stores")

    else:
        st.error("No top selling stores data available.")
