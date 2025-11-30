import streamlit as st
import pandas as pd
from PIL import Image
from pyvis.network import Network

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

#Función para la barra lateral sidebar
def generate_menu():
    with st.sidebar:
        logo = Image.open("media/FamilySearch.png") 
        st.image(logo)
        st.header("Menú")
        #mostramos una lista personalizada de mis páginas
        st.page_link('app.py', label='Inicio', icon='📖')
        st.page_link('pages/arbol.py', label='Árbol', icon='🌳')
        st.markdown("---")
        st.markdown("### 🌐 Recursos externos")
        st.markdown(
            '<a href="https://portafolio-alejandro-castaneda.vercel.app/" target="_blank">🔗 Portafolio Alejandro</a>',
            unsafe_allow_html=True
        )

def load_data():
    df = pd.read_csv("data/arbol.csv")

    # Convertir fechas a datetime cuando posible
    df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"], errors="coerce")
    df["fecha_muerte"] = pd.to_datetime(df["fecha_muerte"], errors="coerce")

    return df

def birth_cities(df):
    st.subheader("Ciudades de nacimiento")
    conteo_ciudades = df["ciudad_nacimiento"].value_counts()
    st.bar_chart(conteo_ciudades, sort=False, color="#e8f5e9")

def birth_countries(df):
    st.subheader("Países de nacimiento")
    conteo_paises = df["pais_nacimiento"].value_counts()
    st.bar_chart(conteo_paises, sort=False, color="#e8f5e9")

def most_common_surnames(df):
    st.subheader("Apellidos más repetidos")

    # Tomamos los apellidos de las dos columnas
    ap1 = df["apellido_1"].dropna().astype(str)
    ap2 = df["apellido_2"].dropna().astype(str)

    # Unimos todo en una sola serie
    todos_apellidos = pd.concat([ap1, ap2])

    # Contamos
    conteo = todos_apellidos.value_counts()

    # Gráfica
    st.bar_chart(conteo, sort=False, color="#e8f5e9")

def ages_at_death(df):
    st.subheader("Edades al morir")

    df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"], errors="coerce")
    df["fecha_muerte"] = pd.to_datetime(df["fecha_muerte"], errors="coerce")
    df["edad_al_morir"] = (df["fecha_muerte"] - df["fecha_nacimiento"]).dt.days // 365

    df_valid = df[df["edad_al_morir"].notna()]

    st.bar_chart(df_valid["edad_al_morir"].value_counts().sort_index(), color="#e8f5e9")

def draw_family_tree_interactive(df):
    st.title("Árbol genealógico")
    df = df.dropna(subset=["id"])

    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#e8f5e9",
        font_color="black"
    )

    # 🔥 Activar layout jerárquico para usar "level"
    net.set_options("""
    {
        "layout": {
            "hierarchical": {
                "enabled": true,
                "levelSeparation": 150,
                "nodeSpacing": 300,
                "treeSpacing": 300,
                "direction": "DU",
                "sortMethod": "directed"
            }
        },
        "physics": {
            "enabled": false
        },
        "interaction": {
            "dragNodes": false,
            "dragView": true,
            "zoomView": true
        }
    }
    """)


    # Nodos con color simple
    for _, row in df.iterrows():
        nombre = " ".join(
            str(x) for x in [
                row.get("nombre_1", ""),
                row.get("nombre_2", ""),
                row.get("apellido_1", ""),
                row.get("apellido_2", "")
            ]
            if pd.notna(x)
        )

        color = "#8ab4f8" if row['sexo'] == "Hombre" else "#ff9ecb"

        try:
            nivel = int(row.get("generacion", 0))
        except:
            nivel = 0

        net.add_node(
            row["id"],
            label=nombre,
            color=color,
            level=nivel,
            title=f"<a href='https://www.familysearch.org/tree/person/details/{row['id']}' target='_blank'>Abrir ficha</a>"
        )


    # Conexiones
    ids_existentes = set(df["id"])

    for _, row in df.iterrows():
        child = row["id"]

        if pd.notna(row["padre_id"]) and row["padre_id"] in ids_existentes:
            net.add_edge(row["padre_id"], child)

        if pd.notna(row["madre_id"]) and row["madre_id"] in ids_existentes:
            net.add_edge(row["madre_id"], child)

    html = net.generate_html()
    st.components.v1.html(html, height=800, scrolling=True)

def generation_sizes(df):
    st.subheader("Tamaño de cada generación")

    # Contar cuántas personas hay por generación
    conteo = df["generacion"].value_counts().sort_index()

    # Calcular el esperado: 2^n
    esperado = {gen: 2**gen for gen in conteo.index}

    # Unir todo en un DataFrame
    resumen = pd.DataFrame({
        "generación": conteo.index,
        "personas_reales": conteo.values,
        "personas_esperadas": [esperado[g] for g in conteo.index],
    })

    resumen["faltantes"] = resumen["personas_esperadas"] - resumen["personas_reales"]

    # Mostrar resumen en texto
    for _, row in resumen.iterrows():
        if row["faltantes"] > 0:
            st.write(f"Generación {int(row['generación'])} → Faltan {int(row['faltantes'])} personas")
        else:
            st.write(f"Generación {int(row['generación'])} → Completa ({int(row['personas_reales'])} personas)")
