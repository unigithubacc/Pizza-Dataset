import streamlit as st

def main():

# Titel der Streamlit-Seite
    st.title("Meine erste Streamlit-App")

# Begrüßungstext
    st.write("Willkommen zu meiner einfachen Streamlit-Seite!")

# Eingabefeld für eine Zahl
    number = st.number_input("Gib eine Zahl ein", min_value=0)

# Berechnung des Quadrats der eingegebenen Zahl
    squared_number = number ** 2

# Ausgabe des Ergebnisses
    st.write(f"Das Quadrat der eingegebenen Zahl ist: {squared_number}")