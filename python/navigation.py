import streamlit as st

def render_navbar(title, options, default_option):
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1><hr style='border:1px solid #333; width: 100%;'>", unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        .navbar {
            overflow: hidden;
            background-color: #333;
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 1000;
        }

        .navbar a {
            float: left;
            display: block;
            color: #f2f2f2;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none;
        }

        .navbar a:hover {
            background-color: #ddd;
            color: black;
        }

        .navbar a.active {
            background-color: #04AA6D;
            color: white;
        }

        .content {
            padding: 16px;
            margin-top: 60px;
        }
        </style>
        <div class="navbar">
        """ +
        "".join([f"<a href='?page={opt}' class='{ 'active' if opt == default_option else '' }'>{opt}</a>" for opt in options]) +
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='content'>", unsafe_allow_html=True)

def close_navbar():
    st.markdown("</div>", unsafe_allow_html=True)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
