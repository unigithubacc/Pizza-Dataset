import streamlit as st
from frontend.page1 import main as page1_main
from frontend.page2 import main as page2_main
from frontend.page3 import main as page3_main
from frontend.page5 import main as page5_main
from frontend.page6 import main as page6_main
from frontend.page7 import main as page7_main
from frontend.page8 import main as page8_main
from frontend.page9 import main as page9_main
from navigation import render_navbar, close_navbar

st.set_page_config(page_title="Shop Analytics", page_icon=":material/local_pizza:", layout="wide")

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
    "Homepage": page9_main,
    "Products": page1_main,
    "Store Overview": page2_main,
    "Store/Multiple": page6_main,
    "Store/Single": page7_main,
    "Customers": page3_main,
}

# Icons für die Seiten
ICONS = {
    "Homepage": "🏛️",
    "Products": "🛒",
    "Store Overview": "🏪",
    "Store/Multiple": "",
    "Store/Single": "",
    "Customers": "👥",
}

# CSS laden
load_css()

# URL-Parameter auslesen und initialisieren
query_params = st.query_params
page_param = query_params.get('page', 'Homepage')
storeid_param = query_params.get('storeid', '')

if 'page' not in st.session_state:
    st.session_state.page = page_param

if 'storeid' not in st.session_state:
    st.session_state.storeid = storeid_param

# Sidebar Navigation
selection = None

# Hauptseiten
main_pages = ["Homepage", "Store Overview", "Customers", "Products"]
for page in main_pages:
    if page == "Store Overview":
        store_expanded = st.sidebar.expander("🏪 Store Overview", expanded=st.session_state.page.startswith("Store Overview"))
        with store_expanded:
            if st.button("Multiple", key="Store/Multiple", help="Store/Multiple", use_container_width=True):
                st.session_state.page = "Store/Multiple"
                selection = "Store/Multiple"
            if st.button("Single", key="Store/Single", help="Store/Single", use_container_width=True):
                st.session_state.page = "Store/Single"
                selection = "Store/Single"
    else:
        if st.sidebar.button(f"{ICONS[page]} {page}", key=page, help=page, use_container_width=True):
            st.session_state.page = page
            selection = page

# Wenn keine Seite ausgewählt wurde, wähle die Standardseite
if not selection:
    selection = st.session_state.page if st.session_state.page in PAGES else 'Homepage'

# Store ID eingeben (falls auf "Store/Single", "Store/Repeat Customer" oder "Store/Multiple" Seite)
if selection in ["Store/Single","Customers"]:
    #st.session_state.storeid = st.sidebar.text_input("Enter Store ID", st.session_state.storeid)
    if st.session_state.storeid:
        st.query_params.update({'page': selection, 'storeid': st.session_state.storeid})
    else:
        st.query_params.update({'page': selection})
else:
    st.query_params.update({'page': selection})

# Ausgewählte Seite anzeigen
page = PAGES[selection]
page()

close_navbar()
