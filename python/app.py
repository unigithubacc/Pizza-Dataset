import streamlit as st
from frontend.page1 import main as page1_main
from frontend.page2 import main as page2_main
from frontend.page3 import main as page3_main
from frontend.page4 import main as page4_main
from frontend.page5 import main as page5_main
from frontend.page6 import main as page6_main
from frontend.page7 import main as page7_main
from frontend.page8 import main as page8_main
from navigation import render_navbar, close_navbar

st.set_page_config(page_title="Shop Analytics", page_icon=":material/local_pizza:", layout="wide")   # Setzen Sie hier das Layout auf "wide"

# Lade die CSS-Datei
def load_css():
    css = """
    <style>
    .sidebar .sidebar-content {
        padding: 0;
    }
    .sidebar .sidebar-content .block-container {
        padding: 0;
    }
    .sidebar .element-container {
        margin: 0 !important;
    }
    .nav-button {
        width: 100%;
        height: 50px;
        text-align: left;
        padding: 10px;
        margin: 0;
        border: none;
        background: #f0f2f6;
        font-size: 16px;
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    .nav-button:hover {
        background: #e0e2e6;
    }
    .nav-icon {
        width: 20px;
        margin-right: 10px;
    }
    .subpage-button {
        width: 100%;
        height: 40px;
        text-align: left;
        padding: 8px 20px;
        margin: 0;
        border: none;
        background: #f7f8fa;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    .subpage-button:hover {
        background: #e9ecef;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Dictionary, das die Seiten-Funktionen speichert
PAGES = {
    "Products": page1_main,
    "Store Overview": page2_main,
    "Store/Multiple": page6_main,
    "Store/Single": page7_main,
    "Store/Repeat Customer": page8_main,
    "Customers": page3_main,
    "Dynamische Datenfilterung": page4_main,
    "Seite 5": page5_main,
}

# Icons für die Seiten
ICONS = {
    "Products": "🛒",
    "Store Overview": "🏪",
    "Store/Multiple": "",
    "Store/Single": "",
    "Store/Repeat Customer": "",
    "Customers": "👥",
    "Dynamische Datenfilterung": "📊",
    "Seite 5": "📄"
}

# CSS laden
load_css()

# URL-Parameter auslesen
page_param = st.query_params.get('page', 'Store/Multiple')

# Sidebar Navigation
#st.sidebar.title("Navigation")

# Füge Buttons für jede Seite hinzu und speichere die Auswahl
selection = None

# Hauptseiten
main_pages = [ "Store Overview", "Products", "Customers", "Dynamische Datenfilterung", "Seite 5"]
for page in main_pages:
    if page == "Store Overview":
        store_expanded = st.sidebar.expander("🏪 Store Overview", expanded=page_param.startswith("Store Overview"))
        with store_expanded:
            if st.button("Multiple", key="Store/Multiple", help="Store/Multiple", use_container_width=True):
                selection = "Store/Multiple"
            if st.button("Single", key="Store/Single", help="Store/Single", use_container_width=True):
                selection = "Store/Single"
            if st.button("Repeat Customer", key="Store/Repeat Customer", help="Store/Repeat Customer", use_container_width=True):
                selection = "Store/Repeat Customer"
    else:
        if st.sidebar.button(f"{ICONS[page]} {page}", key=page, help=page, use_container_width=True):
            selection = page

# Wenn keine Seite ausgewählt wurde, wähle die Standardseite
if not selection:
    selection = page_param if page_param in PAGES else 'Store/Multiple'

# Setze URL-Parameter basierend auf der Auswahl in der Sidebar
st.query_params.page = selection

# Navigation rendern und Auswahl speichern
# render_navbar("Pizza shop analysis tool", list(PAGES.keys()), selection)

# Ausgewählte Seite anzeigen
page = PAGES[selection]
page()

close_navbar()
