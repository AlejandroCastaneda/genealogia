import streamlit as st

def set_up_page(page_title,page_icon):
    st.set_page_config(page_title=page_title,
                    page_icon=page_icon,
                    layout="wide")

def load_styles():
    hide_default_menu = """
    <style>
    /* Oculta el panel de navegación multipage de Streamlit */
    [data-testid="stSidebarNav"] {display: none;}
    /* Mantiene visible tu sidebar personalizado */
    section[data-testid="stSidebar"] > div:first-child {display: block !important;}
    </style>
    """

    page_bg = """
    <style>
    /* Fondo general con tonos verdes FamilySearch */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
    }

    /* Sidebar verde oscuro */
    [data-testid="stSidebar"] {
        background: #2E7D32;
    }

    /* Texto claro para contraste */
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #F8F9FA !important;
    }

    /* Botones y enlaces */
    a, button, .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
    }

    .stButton>button:hover {
        background-color: #45A049 !important;
    }
    </style>
    """

    st.markdown(hide_default_menu, unsafe_allow_html=True)
    st.markdown(page_bg, unsafe_allow_html=True)