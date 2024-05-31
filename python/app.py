import streamlit as st
from frontend.page1 import main as page1_main
from frontend.page2 import main as page2_main
from frontend.page3 import main as page3_main
from frontend.page4 import main as page4_main
from frontend.page5 import main as page5_main

# Lade die CSS-Datei
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Dictionary, das die Seiten-Funktionen speichert
PAGES = {
    "Products": page1_main,
    "Store": page2_main,
    "Customers": page3_main,
    "Dynamische Datenfilterung": page4_main,
    "Seite 5": page5_main
}

# CSS-Datei laden
load_css("frontend\\style.css")

# Navbar mit einem Dropdown-Menü
st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Select page", list(PAGES.keys()))

# Ausgewählte Seite anzeigen
page = PAGES[selection]
page()
