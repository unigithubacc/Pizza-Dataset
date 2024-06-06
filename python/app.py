import streamlit as st
from frontend.page1 import main as page1_main
from frontend.page2 import main as page2_main
from frontend.page3 import main as page3_main
from frontend.page4 import main as page4_main
from frontend.page5 import main as page5_main
from frontend.page6 import main as page6_main

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
    "Seite 5": page5_main,
    "page 6": page6_main
}

# CSS-Datei laden
load_css("frontend/style.css")

# URL-Parameter auslesen
page_param = st.query_params.get('page', 'Products')

# Sidebar Navigation
st.sidebar.title("Navigation")
# Überprüfen, ob der gesuchte Schlüssel im Wörterbuch vorhanden ist
if page_param in PAGES.keys():
    selection = st.sidebar.selectbox("Select page", list(PAGES.keys()), index=list(PAGES.keys()).index(page_param))
else:
    # Wenn der Schlüssel nicht gefunden wird, wählen wir einen Standardwert
    selection = st.sidebar.selectbox("Select page", list(PAGES.keys()))

# Setze URL-Parameter basierend auf der Auswahl in der Sidebar
st.query_params.page = selection

# Ausgewählte Seite anzeigen
page = PAGES[selection]
page()
