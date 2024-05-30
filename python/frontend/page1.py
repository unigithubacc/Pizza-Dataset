import streamlit as st
import plotly.graph_objects as go
import requests

def fetch_top_pizzas():
    response = requests.get('http://localhost:8000/top-selling-products')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

def create_stacked_barchart(data):
    sizes = sorted(set([item['size'] for item in data]))
    pizza_names = sorted(set([item['name'] for item in data]))

    sales_by_size = {size: [] for size in sizes}
    for item in data:
        sales_by_size[item['size']].append(item['TotalSold'])

    fig = go.Figure()

    for size in sizes:
        fig.add_trace(go.Bar(
            x=pizza_names,
            y=sales_by_size[size],
            name=size,
            legendgroup=size,
            showlegend=True
        ))

    fig.update_layout(barmode='stack',
                      title='Sales figures for various pizzas by size',
                      xaxis_tickangle=-45,
                      xaxis_title='Pizza Name',
                      yaxis_title='Total Sold')

    return fig

def main():
    st.title("Top selling pizzas")
    pizzas_data = fetch_top_pizzas()
    if pizzas_data:
        fig = create_stacked_barchart(pizzas_data)
        st.plotly_chart(fig)
        
        # Anzeigen der Liste der Pizzen und ihrer Verkaufszahlen
        st.subheader("List of pizzas and their sales figures:")
        st.table(pizzas_data)
