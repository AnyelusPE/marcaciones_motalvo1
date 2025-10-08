import streamlit as st
import pandas as pd
import os
from datetime import datetime

def run_reportes():
    st.title("📊 Reportes de Asistencia")
    st.caption("Consulta los cruces consolidados generados en la sección anterior.")
    st.markdown("---")

    base_path = "data/cruces"
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    archivos = [f for f in os.listdir(base_path) if f.startswith("CRUCE_GENERAL") and f.endswith(".xlsx")]

    if not archivos:
        st.warning("⚠️ No se han generado cruces aún. Realiza un cruce consolidado primero.")
        st.stop()

    # === Filtros ===
    st.subheader("🗓️ Filtros de búsqueda")

    años = sorted({f.split("_")[2].split("-")[0] for f in archivos}, reverse=True)
    año_sel = st.selectbox("Año", años, index=0)

    meses = {
        "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
        "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }
    mes_sel = st.selectbox("Mes", list(meses.keys()), format_func=lambda x: meses[x])
    quincena_sel = st.radio("Quincena", ["Q1 (1–15)", "Q2 (16–fin)"], horizontal=True)

    # === Filtrar ===
    archivos_filtrados = [
        f for f in archivos if año_sel in f and f"-{mes_sel}-" in f and quincena_sel.split()[0] in f
    ]

    st.markdown("---")
    if not archivos_filtrados:
        st.warning("⚠️ No se encontró ningún cruce con los filtros seleccionados.")
        st.stop()

    archivo_sel = st.selectbox("Selecciona un cruce generado:", archivos_filtrados)
    ruta_sel = os.path.join(base_path, archivo_sel)

    # === Mostrar resultado ===
    try:
        df = pd.read_excel(ruta_sel)
        st.success(f"✅ Mostrando cruce: {archivo_sel}")
        st.dataframe(df, use_container_width=True)

        with open(ruta_sel, "rb") as f:
            st.download_button("📥 Descargar Cruce Consolidado", f, file_name=archivo_sel)

    except Exception as e:
        st.error(f"🚫 Error al leer el archivo: {e}")
