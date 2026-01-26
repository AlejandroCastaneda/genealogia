from utils.data_loader import load_data
from utils.genealogy import surname_distribution
from utils.navigation import generate_menu
from utils.styles import set_up_page, load_styles
from utils.visualization import countries_of_birth, birth_cities
import streamlit as st

#Configuración de la página
set_up_page("Huella genealógica", "🧬")

# Carga los estilos de la página
load_styles()
generate_menu()

# Cargar los datos del árbol
df = load_data()

st.subheader("🧬 Huella genealógica")

col1, col2 = st.columns([1, 2]) 

with col1:
    surname_distribution(df)

with col2:
    countries_of_birth(df)
    birth_cities(df)
