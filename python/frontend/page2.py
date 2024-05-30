import streamlit as st
import requests
import matplotlib.pyplot as plt

def fetch_top_pizzas():
    response = requests.get('http://localhost:8000/top-selling-products')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Fehler beim Abrufen der Daten.")
        return []

def create_barchart(data):
    fig, ax = plt.subplots()
    pizza_names = []
    total_sales = []
    
    for item in data:
        pizza_names.append(item['name'])
        total_sales.append(item['totalsold'])
    
    ax.bar(pizza_names, total_sales)
    ax.set_xlabel('Pizza Name')
    ax.set_ylabel('Total Sold')
    ax.set_title('Verkaufszahlen verschiedener Pizzas')
    
    return fig

def main():
    st.title("Top Verkaufte Pizzen")
    pizzas_data = fetch_top_pizzas()
    if pizzas_data:
        st.write(pizzas_data)
        
        # Erstellen und Anzeigen des Balkendiagramms
        fig = create_barchart(pizzas_data)
        st.pyplot(fig)

if __name__ == "__main__":
    main()
