import streamlit as st
import pandas as pd

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

def surname_distribution(df):
    # Eliminar IDs duplicados (conserva el primero)
    df = df.drop_duplicates(subset=["id"], keep="first").copy()

    # Generación más alta encontrada
    highest_generation = int(df["generacion"].max())

    # Total teórico de apellidos
    total_surnames = 2 * (2 ** (highest_generation + 1) - 1)

    # Diccionario acumulador
    surname_weights = {}

    # --- Generación 0 (ambos apellidos pesan igual) ---
    gen0 = df[df["generacion"] == 0]

    for _, row in gen0.iterrows():
        for col in ["apellido_1", "apellido_2"]:
            apellido = row[col]
            if pd.notna(apellido) and apellido != "":
                surname_weights[apellido] = (
                    surname_weights.get(apellido, 0)
                    + (highest_generation + 1)
                )

    # --- Resto de generaciones (solo apellido_2) ---
    for g in range(1, highest_generation + 1):
        subset = df[df["generacion"] == g]

        weight = (highest_generation - g) + 1

        for apellido in subset["apellido_2"].dropna():
            if apellido != "":
                surname_weights[apellido] = (
                    surname_weights.get(apellido, 0) + weight
                )

    # Imprimir porcentajes
    for apellido, weight in sorted(
        surname_weights.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        porcentaje = (weight / total_surnames) * 100
        st.write(f"{porcentaje:.1f}% {apellido}")