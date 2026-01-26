from PIL import Image
import streamlit as st

def generate_menu():
    with st.sidebar:
        logo = Image.open("media/FamilySearch.png") 
        st.image(logo)
        st.header("Menú")
        #mostramos una lista personalizada de mis páginas
        st.page_link('app.py', label='Inicio', icon='📖')
        st.page_link('pages/family_tree.py', label='Árbol genealógico', icon='🌳')
        st.page_link('pages/genealogical_footprint.py', label='Huella genealógica', icon='🧬')
        st.markdown("---")
        st.markdown("### 🌐 Recursos externos")
        st.markdown(
            '<a href="https://portafolio-alejandro-castaneda.vercel.app/" target="_blank">🔗 Portafolio Alejandro</a>',
            unsafe_allow_html=True
        )