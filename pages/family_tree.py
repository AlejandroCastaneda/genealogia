from utils.analysis import missing_data_table
from utils.data_loader import load_data
from utils.genealogy import generation_sizes
from utils.navigation import generate_menu
from utils.styles import set_up_page, load_styles
from utils.visualization import draw_family_tree_interactive

#Configuración de la página
set_up_page("Árbol genealógico", "🌳")

# Carga los estilos de la página
load_styles()
generate_menu()

# Cargar los datos del árbol
df = load_data()

draw_family_tree_interactive(df)
generation_sizes(df)
missing_data_table(df)