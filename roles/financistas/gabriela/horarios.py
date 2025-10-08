import streamlit as st
import os
import pandas as pd

def run_horarios():
    st.title("📅 Malla Horaria de los Salones Asignados")
    st.info("Visualiza los horarios cargados por tus salones (de data/uploads/).")

    salones = {
        "FM_BELLAVISTA": "data/uploads/fm_bellavista",
        "FM_BARRANCO": "data/uploads/fm_barranco",
        "FM_JAVIER_PRADO": "data/uploads/fm_javier_prado",
        "TRUJILLO_MALL": "data/uploads/trujillo_mall"
    }

    for nombre, ruta in salones.items():
        st.subheader(f"🏢 {nombre}")

        if not os.path.exists(ruta):
            st.warning(f"⚠️ No se encontró carpeta de datos para {nombre}")
            continue

        archivos = sorted([f for f in os.listdir(ruta) if f.endswith(".csv")], reverse=True)
        if not archivos:
            st.warning(f"⚠️ No hay horarios guardados en {nombre}")
            continue

        archivo = archivos[0]
        ruta_archivo = os.path.join(ruta, archivo)

        try:
            df = pd.read_csv(ruta_archivo)
            st.dataframe(df, use_container_width=True)
            st.success(f"📂 Mostrando archivo: {archivo}")
        except Exception as e:
            st.error(f"❌ Error al cargar archivo de {nombre}: {e}")
