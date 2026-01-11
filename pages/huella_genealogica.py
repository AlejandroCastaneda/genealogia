import utils
import streamlit as st

#Configuración de la página
st.set_page_config(page_title="Huella genealógica",
                    page_icon="🧬",
                    layout="wide")

# Carga los estilos de la página
utils.load_styles()
utils.generate_menu()

# Cargar los datos del árbol
df = utils.load_data()

st.subheader("🧬 Huella genealógica")

col1, col2 = st.columns([1, 2]) 

with col1:
    utils.apellidos_distribution(df)

with col2:
    utils.pie_countries(df)
