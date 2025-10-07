import streamlit as st
import pandas as pd
import os


def run_cruce_horarios(usuario):
    st.title("🔍 Cruce de Horarios y Marcaciones")
    st.info("Sube el archivo del biométrico y selecciona el horario del salón para cruzar los datos automáticamente.")

    # Subida del biométrico
    archivo_bio = st.file_uploader("📤 Subir archivo del biométrico (Excel o CSV)", type=["csv", "xlsx"])

    # Selección del horario
    base_path = "data/uploads"
    if not os.path.exists(base_path):
        st.warning("No hay salones registrados.")
        return

    salones = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    salon_sel = st.selectbox("🏢 Selecciona la sede para el cruce:", salones)

    archivos_salon = os.listdir(os.path.join(base_path, salon_sel))
    csvs = [f for f in archivos_salon if f.endswith(".csv")]

    archivo_sel = st.selectbox("🗂️ Selecciona el archivo de horario del salón:", csvs if csvs else ["(No hay archivos disponibles)"])

    if archivo_bio and archivo_sel != "(No hay archivos disponibles)":
        df_horario = pd.read_csv(os.path.join(base_path, salon_sel, archivo_sel), dtype=str).fillna("")
        if archivo_bio.name.endswith(".xlsx"):
            df_bio = pd.read_excel(archivo_bio, dtype=str).fillna("")
        else:
            df_bio = pd.read_csv(archivo_bio, dtype=str).fillna("")

        st.success("✅ Archivos cargados correctamente.")

        # Simulación simple del cruce (puedes mejorar luego)
        st.markdown("### 📊 Resultado del cruce:")
        resultado = df_horario.merge(df_bio, on="DNI", how="left", suffixes=("_horario", "_bio"))
        st.dataframe(resultado, use_container_width=True)

        if st.button("💾 Exportar resultado a Excel"):
            ruta_salida = os.path.join("data", "uploads", salon_sel, f"CRUCE_{archivo_sel}")
            resultado.to_excel(ruta_salida, index=False)
            st.success(f"Archivo guardado en `{ruta_salida}`")
