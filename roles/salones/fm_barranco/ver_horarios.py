import os
import pandas as pd
import streamlit as st

def run_ver_horarios():
    st.title("🗂️ Historial de horarios guardados")

    carpeta = os.path.join("data", "uploads", "fm_barranco")
    os.makedirs(carpeta, exist_ok=True)

    archivos = sorted([f for f in os.listdir(carpeta) if f.endswith(".csv")])

    if not archivos:
        st.warning("📭 No se encontraron horarios guardados aún.")
        return

    archivo = st.selectbox("Selecciona un archivo guardado:", archivos)
    ruta = os.path.join(carpeta, archivo)

    df = pd.read_csv(ruta, dtype=str)
    st.dataframe(df, use_container_width=True)
    st.success(f"📄 Mostrando archivo: {archivo}")
