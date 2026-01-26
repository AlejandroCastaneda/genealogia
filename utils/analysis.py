import streamlit as st
import pandas as pd

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