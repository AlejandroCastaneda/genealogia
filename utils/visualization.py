import streamlit as st
import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import re

def draw_family_tree_interactive(df):
    st.title("Árbol genealógico")
    df = df.dropna(subset=["id"])
    df = df.drop_duplicates(subset=["id", "hijo_id"], keep="first")

    # Crear contador por id
    contador = df.groupby("id").cumcount()

    # Modificar solo los duplicados
    df["id"] = df["id"] + (contador + 1).astype(str).where(contador > 0, "")

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

        def familysearch_id(id_modificado):
            match = re.match(r"^([A-Z0-9]{4}-[A-Z0-9]{3})", id_modificado)
            return match.group(1) if match else id_modificado

        fs_id = familysearch_id(row["id"])

        net.add_node(
            row["id"],
            label=nombre,
            color=color,
            level=nivel,
            title=f"<a href='https://www.familysearch.org/tree/person/details/{fs_id}' target='_blank'>Abrir ficha</a>"
        )


    # Conexiones
    for _, row in df.iterrows():
        if row["hijo_id"] != 'No aplica':
            net.add_edge(row["id"], row["hijo_id"]) 

    html = net.generate_html()
    st.components.v1.html(html, height=800, scrolling=True)

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
        options= places
    )

    # Aplicar filtro
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