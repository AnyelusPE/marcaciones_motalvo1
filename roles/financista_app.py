import streamlit as st
import pandas as pd
from datetime import datetime
from core.db import cargar_datos, guardar_csv_seguro


def run_financista_app(usuario):
    nombre_financista = usuario["usuario"]
    st.sidebar.markdown(f"### 💼 {nombre_financista}")
    st.sidebar.markdown("(financista)")

    menu = st.sidebar.radio("Navegación", ["Cruce de horarios", "Historial", "Configuración"])

    if menu == "Cruce de horarios":
        st.title(f"📊 Panel de Financista - {nombre_financista}")
        st.info("Selecciona una sede y un rango de fechas para revisar o editar los cruces de horarios.")

        # --- Selección de sede ---
        sedes = ["FM_BARRANCO", "FM_BELLAVISTA", "FM_JAVIER_PRADO", "TRUJILLO_MALL"]
        sede = st.selectbox("🏢 Selecciona la sede:", sedes)

        # --- Selección de fechas ---
        col1, col2 = st.columns(2)
        inicio = col1.date_input("Desde", datetime.today().replace(day=1))
        fin = col2.date_input("Hasta", datetime.today())

        if fin < inicio:
            st.error("⚠️ La fecha final no puede ser menor que la inicial.")
            st.stop()

        inicio_dt = datetime.combine(inicio, datetime.min.time())
        fin_dt = datetime.combine(fin, datetime.min.time())

        # --- Cargar datos del rango ---
        df, path = cargar_datos(nombre_financista, inicio_dt, fin_dt, sede)

        # --- Mostrar tabla editable ---
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "NOMBRE Y APELLIDO": st.column_config.TextColumn("NOMBRE Y APELLIDO"),
                "ÁREA": st.column_config.TextColumn("ÁREA"),
            },
        )

        # --- Guardar cambios ---
        if st.button("💾 Guardar cambios"):
            guardar_csv_seguro(path, edited_df)
            st.success("✅ Cambios guardados correctamente.")
            st.caption(f"Archivo guardado en: `{path}`")

    elif menu == "Historial":
        st.title("📚 Historial de cruces guardados")
        st.info("Aquí podrás revisar los archivos generados por rangos de fechas.")

        base_path = f"data/uploads/{nombre_financista}"
        if not os.path.exists(base_path):
            st.warning("No hay archivos guardados todavía.")
        else:
            archivos = os.listdir(base_path)
            seleccion = st.selectbox("Selecciona un archivo para revisar:", archivos)
            if seleccion:
                df = pd.read_csv(f"{base_path}/{seleccion}")
                st.dataframe(df, use_container_width=True)

    elif menu == "Configuración":
        st.title("⚙️ Configuración del módulo Financista")
        st.warning("Módulo en desarrollo...")

    # --- Cerrar sesión ---
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.rerun()