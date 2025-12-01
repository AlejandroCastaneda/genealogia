import utils
import streamlit as st

#Configuración de la página
st.set_page_config(page_title="Árbol genealógico",
                    page_icon="🌳",
                    layout="wide")

# Carga los estilos de la página
utils.load_styles()
utils.generate_menu()

# Cargar los datos del árbol
df = utils.load_data()

utils.draw_family_tree_interactive(df)
utils.generation_sizes(df)
utils.missing_data_table(df)