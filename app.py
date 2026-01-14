import utils
import streamlit as st

#Configuración de la página
st.set_page_config(page_title="Geanealogía",
                    page_icon="📖",
                    layout="wide")

# Carga los estilos de la página
utils.load_styles()
utils.generate_menu()

# Cargar los datos del árbol
df = utils.load_data()

utils.ages_at_death(df)
utils.places_of_deaths(df)