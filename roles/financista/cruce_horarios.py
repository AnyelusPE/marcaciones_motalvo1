import streamlit as st
import pandas as pd
import os
from roles.financista.utils import listar_salones

def run_cruce_horarios(usuario):
    st.title("🔍 Cruce de Horarios y Marcaciones")
    st.info("Sube el archivo del biométrico, selecciona uno o varios salones y la quincena que deseas cruzar.")

    # --- Subida del biométrico ---
    st.subheader("📤 Subir archivo del biométrico (Excel o CSV)")
    archivo_bio = st.file_uploader("Arrastra o selecciona el archivo del biométrico", type=["csv", "xlsx"])

    # --- Selección de salones ---
    st.subheader("🏢 Selecciona los salones para el cruce")

    salones = listar_salones()
    if not salones:
        st.warning("⚠️ No hay carpetas de salones en 'data/uploads/'.")
        return

    seleccionados = []
    cols = st.columns(2)
    for i, salon in enumerate(salones):
        if cols[i % 2].checkbox(salon, key=f"salon_{salon}"):
            seleccionados.append(salon)

    if not seleccionados:
        st.info("Selecciona al menos un salón para continuar.")
        return

    # --- Selección de quincena ---
    st.subheader("📅 Selecciona la quincena")
    quincena = st.radio("Periodo", ["Q1 (1-15)", "Q2 (16-fin)"], horizontal=True)
    q_code = "Q1" if "Q1" in quincena else "Q2"

    # --- Botón para procesar ---
    if st.button("🔄 Realizar Cruce"):
        if archivo_bio is None:
            st.error("Por favor, sube primero el archivo del biométrico.")
            return

        # Procesar biométrico
        bio_df = cargar_biometrico(archivo_bio)

        resultados = []
        for salon in seleccionados:
            archivo_salon = buscar_csv_salon(salon, q_code)
            if not archivo_salon:
                st.warning(f"⚠️ No se encontró archivo CSV para {salon} ({q_code}).")
                continue

            salon_df = pd.read_csv(archivo_salon)
            cruce_df = cruzar_datos(salon_df, bio_df, salon)
            resultados.append((salon, cruce_df))

        if not resultados:
            st.warning("No se generaron cruces.")
            return

        st.success("✅ Cruce realizado con éxito.")
        for salon, df in resultados:
            st.markdown(f"### 📋 Resultados para {salon}")
            st.dataframe(df, use_container_width=True)

            # Descargar CSV
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label=f"⬇️ Descargar resultado {salon}",
                data=csv,
                file_name=f"{salon}_cruce_{q_code}.csv",
                mime="text/csv"
            )


# --------------------------
# Funciones auxiliares
# --------------------------

def cargar_biometrico(file):
    """Lee CSV o Excel del biométrico."""
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error al leer biométrico: {e}")
        return pd.DataFrame()


def buscar_csv_salon(nombre_salon, q_code):
    """Busca el CSV del salón correspondiente a la quincena."""
    carpeta = os.path.join("data", "uploads", nombre_salon)
    if not os.path.exists(carpeta):
        return None
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".csv") and q_code in archivo:
            return os.path.join(carpeta, archivo)
    return None


def cruzar_datos(horario_df, bio_df, nombre_salon):
    """Ejemplo de cruce básico."""
    try:
        if "DNI" not in horario_df.columns or "DNI" not in bio_df.columns:
            st.warning(f"El formato de columnas no coincide para {nombre_salon}.")
            return pd.DataFrame()

        merged = pd.merge(horario_df, bio_df, on="DNI", how="left", suffixes=("_horario", "_biometrico"))
        merged["RESULTADO"] = merged.apply(
            lambda x: "TARDANZA" if str(x.get("entrada_biometrico", "")) > str(x.get("entrada_horario", "")) else "OK",
            axis=1
        )
        return merged
    except Exception as e:
        st.error(f"Error al cruzar datos para {nombre_salon}: {e}")
        return pd.DataFrame()