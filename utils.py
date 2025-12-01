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
    # Parseo de fechas con formato más robusto
    df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"], errors="coerce")

    # Convertir "No aplica" a NaT
    df["fecha_muerte"] = df["fecha_muerte"].replace("No aplica", pd.NA)
    df["fecha_muerte"] = pd.to_datetime(df["fecha_muerte"], errors="coerce")

    # Calcular edad solo si fecha_muerte existe
    df["edad_al_morir"] = (
        df["fecha_muerte"] - df["fecha_nacimiento"]
    ).dt.days // 365

    # Personas que sí tienen edad de muerte válida
    df_valid = df[df["edad_al_morir"].notna()]

    # Cálculo del promedio
    promedio = df_valid["edad_al_morir"].mean()

    st.subheader(f"Edades al morir - Promedio {promedio:.0f}")

    # Gráfico
    st.bar_chart(
        df_valid["edad_al_morir"].value_counts().sort_index(),
        color="#e8f5e9"
    )

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
    for _, row in df.iterrows():
        if row["hijo_id"] != 'No aplica':
            net.add_edge(row["id"], row["hijo_id"]) 

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

def missing_data_table(df):
    st.subheader("Personas con datos faltantes")

    # Columnas que quieres revisar
    columnas_revisar = [
        "apellido_1", "apellido_2",
        "fecha_nacimiento", "pais_nacimiento",
        "fecha_muerte", "pais_muerte"
    ]

    # Copia para evitar warnings
    df2 = df.copy()

    # Convertir strings vacíos a NaN
    df2.replace("", pd.NA, inplace=True)

    # Filtrar filas donde haya al menos un dato vacío
    mask_nan = df2[columnas_revisar].isna().any(axis=1)
    faltantes = df2[mask_nan].sort_values(by="generacion")

    st.write(f"Total: **{len(faltantes)} personas** con al menos un dato vacío")

    st.dataframe(faltantes)

    return faltantes
