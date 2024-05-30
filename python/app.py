import streamlit as st
from frontend.page1 import main as page1_main
from frontend.page2 import main as page2_main
from frontend.page3 import main as page3_main
from frontend.page4 import main as page4_main

# Lade die CSS-Datei
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Dictionary, das die Seiten-Funktionen speichert
PAGES = {
    "Seite 1": page1_main,
    "Seite 2": page2_main,
    "Seite 3": page3_main,
    "Seite 4": page4_main
}

# CSS-Datei laden
load_css("frontend\\style.css")

# Navbar mit einem Dropdown-Menü
st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Seite auswählen", list(PAGES.keys()))

# Ausgewählte Seite anzeigen
page = PAGES[selection]
page()
