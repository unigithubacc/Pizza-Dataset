import logging
import streamlit as st
import requests
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import folium
from streamlit_folium import folium_static
from datetime import date
import webbrowser

logging.basicConfig(level=logging.DEBUG)

@st.cache_data
def fetch_store_locations():
    response = requests.get('http://localhost:8000/store-locations')
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Fehler beim Abrufen der Store-Standorte.")
        return []

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
def fetch_revenue_data(period, end_date):
    response = requests.get(f'http://localhost:8000/revenue-by-store/?period={period}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Revenue-Daten.")
        return []

# Funktion zum Abrufen der Kundenanzahl-Daten für Stores
@st.cache_data
def fetch_customers_count(start_date, end_date):
    response = requests.get(f'http://localhost:8000/stores/customers-count?start_date={start_date}&end_date={end_date}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Kundenanzahl-Daten.")
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

def prepare_data_for_chart(data, store_ids, period):
    prepared_data = []
    for store_id in store_ids:
        filtered_data = [entry for entry in data if entry['storeid'] == store_id]
        if filtered_data:
            # Entscheidung, ob der erste Eintrag ignoriert werden soll, basierend auf dem Period
            ignore_first_entry = False
            if period in ["Day", "Month"]:
                ignore_first_entry = True
            
            if ignore_first_entry:
                # Ignorieren des ersten Eintrags für jede storeID
                filtered_data = filtered_data[1:]  # Starte bei Index 1, um den ersten Eintrag zu ignorieren
            prepared_data.extend(filtered_data)
    return prepared_data

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

# Funktion zum Erstellen eines Kreisdiagramms
def create_customers_pie_chart(data, selected_store_ids, selected_store_colors):
    selected_data = [item for item in data if item['storeid'] in selected_store_ids]
    
    labels = [f"Store {item['storeid']}" for item in selected_data]
    values = [item['totalcustomers'] for item in selected_data]
    colors = [selected_store_colors[selected_store_ids.index(item['storeid'])] for item in selected_data]


    customdata = [item['storeid'] for item in selected_data]  # Store-IDs in customdata hinzufügen
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3, marker=dict(colors=colors), customdata=customdata)])
    fig.update_layout(title_text="Customers per Store")

    fig.update_traces(customdata=[item['storeid'] for item in selected_data], 
                      hoverinfo='value+label+percent', 
                      textinfo='value+percent', 
                      textposition='inside',
                      textfont_size=15)

    return fig

def create_store_map(selected_store_ids, width='100%', height=500):
    stores = fetch_store_locations()
    selected_stores = [store for store in stores if store['storeID'] in selected_store_ids]

    # Geografische Zentren von Kalifornien, Nevada und Arizona
    center_coords = [(37.7749, -122.4194), (39.8283, -119.8173), (36.1699, -111.8901)]  # Kalifornien, Nevada, Arizona
    # Wählen Sie das erste Koordinatensystem aus, wenn keine ausgewählten Stores vorhanden sind
    if not selected_stores:
        avg_lat, avg_lon = center_coords[0]

    if selected_stores:
        avg_lat = sum([store['latitude'] for store in selected_stores]) / len(selected_stores)
        avg_lon = sum([store['longitude'] for store in selected_stores]) / len(selected_stores)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

    for store in selected_stores:
        store_popup = f"Store ID: {store['storeID']}<br>City: {store['city']}<br>State: {store['state']}"
        folium.Marker(
            location=[store['latitude'], store['longitude']],
            popup=store_popup,
            icon=folium.Icon(color='red', icon='store', prefix='fa')
        ).add_to(m)

    return m

# Hauptfunktion
def main():
    # Datumseingabe
    start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date(2023, 1, 1))

    # Periodenauswahl
    period = st.sidebar.selectbox("Select Linechart View", ["Day", "Month", "Quarter", "Year"], index=2)

    col1, col2 = st.columns([1, 1])
    
    with col1:
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
            logging.debug(f"Selected points: {selected_points}")
            
            if selected_points:
                # Store ID aus den ausgewählten Punkten extrahieren
                new_store_id = selected_points[0]['x']
                if new_store_id in st.session_state.selected_store_ids:
                    index = st.session_state.selected_store_ids.index(new_store_id)
                    st.session_state.selected_store_ids.pop(index)
                    st.session_state.selected_store_colors.pop(index)
                    st.rerun()
                else:
                    st.session_state.selected_store_ids.append(new_store_id)
                    st.session_state.selected_store_colors.append(color_palette[len(st.session_state.selected_store_ids) % len(color_palette)])
                    st.rerun()

            # Aktualisiere das Balkendiagramm mit neuen Farben
            fig = create_store_bar_chart(top_selling_stores, st.session_state.selected_store_ids, st.session_state.selected_store_colors, default_color)
            logging.debug(f"Updated colors: {st.session_state.selected_store_colors}")

            store_map = create_store_map(st.session_state.selected_store_ids, width='100%', height=500)
            folium_static(store_map, width=700, height=300)

    with col2:
        if st.session_state.selected_store_ids:
            chart_type = st.sidebar.radio("Select Chart Type", ("Revenue", "Total Sales"))

            if chart_type == "Revenue":
                revenue_data = fetch_revenue_data(period, end_date)
                prepared_revenue_data = prepare_data_for_chart(revenue_data, st.session_state.selected_store_ids, period)
                revenue_fig = create_revenue_line_chart(prepared_revenue_data, st.session_state.selected_store_ids, st.session_state.selected_store_colors, period)
                st.plotly_chart(revenue_fig, use_container_width=False)
                
                chart_type == "Customers"
                customers_count_data = fetch_customers_count(start_date, end_date)
                customers_pie_fig = create_customers_pie_chart(customers_count_data, st.session_state.selected_store_ids, st.session_state.selected_store_colors)
                selected_points = plotly_events(customers_pie_fig, click_event=True)  # Hinzugefügt zum Erfassen von Klicks
                if selected_points:
                    print(selected_points)
                    point_index = selected_points[0]['pointNumber'] 
                    store_id = customers_pie_fig.data[0].customdata[point_index] 
                    url = f"http://localhost:8501/?page=Store%2FSingle&storeid={store_id}"
                    webbrowser.open_new_tab(url)

                
            elif chart_type == "Total Sales":
                sales_data = fetch_sales_data(period, end_date)
                prepared_sales_data = prepare_data_for_chart(sales_data, st.session_state.selected_store_ids, period)
                sales_fig = create_sales_line_chart(prepared_sales_data, st.session_state.selected_store_ids, st.session_state.selected_store_colors, period)
                st.plotly_chart(sales_fig, use_container_width=False)

                chart_type == "Customers"
                customers_count_data = fetch_customers_count(start_date, end_date)
                customers_pie_fig = create_customers_pie_chart(customers_count_data, st.session_state.selected_store_ids, st.session_state.selected_store_colors)
                selected_points = plotly_events(customers_pie_fig, click_event=True)  # Hinzugefügt zum Erfassen von Klicks
                if selected_points:
                    print(selected_points)
                    point_index = selected_points[0]['pointNumber'] 
                    store_id = customers_pie_fig.data[0].customdata[point_index] 
                    url = f"http://localhost:8501/?page=Store%2FSingle&storeid={store_id}"
                    webbrowser.open_new_tab(url)
        else:
            empty_fig = create_empty_line_chart()
            st.plotly_chart(empty_fig, use_container_width=False)
            st.sidebar.warning("Select store IDs to see the number of sales for those stores")

        if not top_selling_stores:
            st.error("No top selling stores data available.")
