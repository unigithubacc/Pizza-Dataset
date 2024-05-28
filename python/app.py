import streamlit as st
from frontend.page1 import main as page1_main
from frontend.page2 import main as page2_main

# Dictionary, das die Seiten-Funktionen speichert
PAGES = {
    "Seite 1": page1_main,
    "Seite 2": page2_main
}

# Sidebar Navigation
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Gehe zu", list(PAGES.keys()))

# Aufrufen der entsprechenden Seite basierend auf der Auswahl
if selection in PAGES:
    page = PAGES[selection]
    page()
else:
    st.error("Ungültige Seiteauswahl. Bitte wähle eine gültige Option.")