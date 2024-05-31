import streamlit as st
import plotly.graph_objects as go
import requests
from collections import defaultdict

def fetch_top_pizzas():
    response = requests.get('http://localhost:8000/top-selling-products')
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

def create_stacked_barchart(data):
    # Berechne die Summe der Verkäufe für jede Pizza
    pizza_sales = defaultdict(int)
    for item in data:
        pizza_sales[item['name']] += item['TotalSold']

    # Sortiere die Pizzen nach der Summe der Verkäufe
    sorted_pizzas = sorted(pizza_sales.items(), key=lambda x: x[1], reverse=True)
    sorted_pizza_names = [pizza[0] for pizza in sorted_pizzas]

    sizes = sorted(set([item['size'] for item in data]))
    sales_by_size = {size: [0] * len(sorted_pizza_names) for size in sizes}

    # Ordne die Verkäufe den sortierten Pizzen zu
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

