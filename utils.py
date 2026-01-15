import streamlit as st
import pandas as pd
from PIL import Image
from pyvis.network import Network
import matplotlib.pyplot as plt

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

def generate_menu():
    with st.sidebar:
        logo = Image.open("media/FamilySearch.png") 
        st.image(logo)
        st.header("Menú")
        #mostramos una lista personalizada de mis páginas
        st.page_link('app.py', label='Inicio', icon='📖')
        st.page_link('pages/arbol.py', label='Árbol genealógico', icon='🌳')
        st.page_link('pages/huella_genealogica.py', label='Huella genealógica', icon='🧬')
        st.markdown("---")
        st.markdown("### 🌐 Recursos externos")
        st.markdown(
            '<a href="https://portafolio-alejandro-castaneda.vercel.app/" target="_blank">🔗 Portafolio Alejandro</a>',
            unsafe_allow_html=True
        )

def load_data():
    df = pd.read_csv("data/arbol.csv")
    return df

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
    df = df.drop_duplicates(subset=["id", "hijo_id"], keep="first")

    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#e8f5e9",
        font_color="black"
    )

    # Activar layout jerárquico para usar "level"
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

        color = "#6D4C41" if row['sexo'] == "Hombre" else "#66BB6A"

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

    # Asegurar que fecha_nacimiento es datetime
    df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"], errors="coerce")

    # Extraer año
    df["anio_nacimiento"] = df["fecha_nacimiento"].dt.year

    # Conteo por generación
    conteo = df["generacion"].value_counts().sort_index()

    # Esperado 2^n
    esperado = {gen: 2**gen for gen in conteo.index}

    # Promedio de año por generación
    promedio_anio = (
        df.groupby("generacion")["anio_nacimiento"]
        .mean()
        .round(0)
    )

    # Construir resumen
    resumen = pd.DataFrame({
        "generacion": conteo.index,
        "personas_reales": conteo.values,
        "personas_esperadas": [esperado[g] for g in conteo.index],
        "anio_promedio": [promedio_anio.get(g) for g in conteo.index]
    })

    resumen["faltantes"] = resumen["personas_esperadas"] - resumen["personas_reales"]

    # Mostrar resultados
    for _, row in resumen.iterrows():
        gen = int(row["generacion"])
        reales = int(row["personas_reales"])
        esperadas = int(row["personas_esperadas"])
        faltan = int(row["faltantes"])
        anio = row["anio_promedio"]

        if pd.isna(anio):
            anio_txt = "sin datos"
        else:
            anio_txt = f"~{int(anio)}"

        if faltan > 0:
            st.write(
                f"Generación {gen} → "
                f"Faltan {faltan} | Año promedio: {anio_txt}"
            )
        else:
            st.write(
                f"Generación {gen} → Completa ({reales}) | Año promedio: {anio_txt}"
            )

def missing_data_table(df):
    st.subheader("Personas con datos faltantes")

    columnas_revisar = [
        "apellido_1", "apellido_2",
        "fecha_nacimiento", "pais_nacimiento",
        "fecha_muerte", "pais_muerte"
    ]

    df2 = df.copy()
    df2.replace("", pd.NA, inplace=True)

    # Filas con al menos un dato faltante
    mask_nan = df2[columnas_revisar].isna().any(axis=1)
    faltantes = df2.loc[mask_nan].copy()

    # Selector de generación
    generaciones = sorted(faltantes["generacion"].dropna().unique())
    gen_seleccionada = st.selectbox(
        "Filtrar por generación",
        options=["Todas"] + generaciones
    )

    # Aplicar filtro
    if gen_seleccionada != "Todas":
        faltantes = faltantes[faltantes["generacion"] == gen_seleccionada]

    faltantes["fecha_nacimiento"] = pd.to_datetime(
    faltantes["fecha_nacimiento"], errors="coerce"
    ).dt.strftime("%d/%m/%Y")

    faltantes["fecha_muerte"] = pd.to_datetime(
        faltantes["fecha_muerte"], errors="coerce"
    ).dt.strftime("%d/%m/%Y")


    # ---- Construir columnas amigables ----
    faltantes["Nombre"] = (
        faltantes["nombre_1"].fillna("") + " " +
        faltantes["nombre_2"].fillna("") + " " +
        faltantes["apellido_1"].fillna("") + " " +
        faltantes["apellido_2"].fillna("")
    ).str.replace(" +", " ", regex=True).str.strip()

    faltantes["Lugar nacimiento"] = (
        faltantes["ciudad_nacimiento"].fillna("") + ", " +
        faltantes["pais_nacimiento"].fillna("")
    ).str.replace(", $", "", regex=True)

    faltantes["Lugar defunción"] = (
        faltantes["ciudad_muerte"].fillna("") + ", " +
        faltantes["pais_muerte"].fillna("")
    ).str.replace(", $", "", regex=True)

    # Seleccionar y renombrar columnas finales
    salida = faltantes[[
        "Nombre",
        "fecha_nacimiento",
        "Lugar nacimiento",
        "fecha_muerte",
        "Lugar defunción",
        "id"
    ]].rename(columns={
        "fecha_nacimiento": "Fecha nacimiento",
        "fecha_muerte": "Fecha defunción",
        "id": "ID"
    })

    st.write(f"Total: **{len(faltantes)} personas** con al menos un dato vacío")
    st.dataframe(salida, width="stretch", hide_index=True)

def apellidos_distribution(df):
    df = df.drop_duplicates(subset=["id"], keep="first")


    # Tomar ambos apellidos
    ap1 = df["apellido_1"]
    ap2 = df["apellido_2"]

    # Unir en una sola serie
    apellidos = pd.concat([ap1, ap2])

    # Limpiar: quitar NaN, vacíos y normalizar
    apellidos = (
        apellidos
        .dropna()
        .astype(str)
        .str.strip()
        .str.title()
    )

    total = len(apellidos)

    conteo = apellidos.value_counts()

    for apellido, cantidad in conteo.items():
        porcentaje = (cantidad / total) * 100
        st.write(f"**{porcentaje:.1f}%** {apellido}")

def countries_of_birth(df):
    df = df.drop_duplicates(subset=["id"], keep="first")

    # Copia segura
    df2 = df.copy()

    # Limpiar datos
    df2 = df2[df2["pais_nacimiento"].notna() & (df2["pais_nacimiento"] != "")]

    # Conteo
    conteo = df2["pais_nacimiento"].value_counts()

    # Colores personalizados
    colores = []
    for pais in conteo.index:
        if pais == "Colombia":
            colores.append("#FCD116")   # amarillo Colombia
        else:
            colores.append("#B0BEC5")   # gris

    # Gráfico
    fig, ax = plt.subplots()
    # Fondo del gráfico
    fig.patch.set_facecolor("#e8f5e9")
    ax.set_facecolor("#e8f5e9")
    ax.pie(
        conteo.values,
        labels=conteo.index,
        autopct="%1.0f%%",
        startangle=90,
        colors=colores
    )
    ax.axis("equal")

    st.pyplot(fig)

def birth_cities(df):
    df = df.drop_duplicates(subset=["id"], keep="first")
    
    # Copia segura
    df2 = df.copy()

    # Limpiar datos
    df2 = df2[df2["ciudad_nacimiento"].notna() & (df2["ciudad_nacimiento"] != "")]

    # Conteo
    conteo = df2["ciudad_nacimiento"].value_counts()

    # Gráfico
    fig, ax = plt.subplots()
    # Fondo del gráfico
    fig.patch.set_facecolor("#e8f5e9")
    ax.set_facecolor("#e8f5e9")
    ax.pie(
        conteo.values,
        labels=conteo.index,
        autopct="%1.0f%%",
        startangle=90,
    )
    ax.axis("equal")

    st.pyplot(fig)

def places_of_deaths(df):
    st.subheader("Lugares de defunción")

    df2 = df.copy()
    df2.replace("", pd.NA, inplace=True)

    # Eliminar registros donde ciudad_muerte sea "No aplica"
    df2 = df2[df2["ciudad_muerte"].str.strip().ne("No aplica")]

    # Selector de generación
    places = sorted(df2["ciudad_muerte"].dropna().unique())
    place_selec = st.selectbox(
        "Filtrar por ciudad",
        options=["Todas"] + places
    )

    # Aplicar filtro
    if place_selec != "Todas":
        df2 = df2[df2["ciudad_muerte"] == place_selec]

    df2["fecha_muerte"] = pd.to_datetime(
        df2["fecha_muerte"], errors="coerce"
    ).dt.strftime("%d/%m/%Y")


    # ---- Construir columnas amigables ----
    df2["Nombre"] = (
        df2["nombre_1"].fillna("") + " " +
        df2["nombre_2"].fillna("") + " " +
        df2["apellido_1"].fillna("") + " " +
        df2["apellido_2"].fillna("")
    ).str.replace(" +", " ", regex=True).str.strip()

    # Seleccionar y renombrar columnas finales
    salida = df2[[
        "Nombre",
        "fecha_muerte",
        "id"
    ]].rename(columns={
        "fecha_muerte": "Fecha defunción",
        "id": "ID"
    })

    st.dataframe(salida, width="stretch", hide_index=True)