import streamlit as st
import pandas as pd
from datetime import datetime
from core.db import cargar_datos, guardar_csv_seguro


def run_salon_app(usuario):
    """
    Panel principal del rol 'salón'.
    Permite seleccionar rango de fechas, editar horarios y guardarlos en su carpeta correspondiente.
    """
    nombre_salon = usuario["usuario"]

    # --- Sidebar ---
    st.sidebar.markdown(f"### 💇 {nombre_salon}")
    st.sidebar.markdown("(salón)")
    menu = st.sidebar.radio("Navegación", ["Inicio", "Configuración"])

    # ==========================
    # SECCIÓN PRINCIPAL: INICIO
    # ==========================
    if menu == "Inicio":
        st.title(f"📅 Panel del salón - {nombre_salon}")
        st.info("📝 Puedes editar los datos directamente en la tabla. Los cambios se pueden guardar.")

        # --- Selección de rango de fechas ---
        st.markdown("#### 📆 Selecciona el rango de fechas:")
        col1, col2 = st.columns(2)
        inicio = col1.date_input("Desde", datetime.today().replace(day=1))
        fin = col2.date_input("Hasta", datetime.today())

        if fin < inicio:
            st.error("⚠️ La fecha final no puede ser menor que la inicial.")
            st.stop()

        inicio_dt = datetime.combine(inicio, datetime.min.time())
        fin_dt = datetime.combine(fin, datetime.min.time())

        # --- Cargar datos del rango ---
        df, path = cargar_datos(nombre_salon, inicio_dt, fin_dt)

        # --- Mostrar tabla editable ---
        st.markdown("#### 🧾 Cuadro de horarios del personal")
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "NOMBRE Y APELLIDO": st.column_config.TextColumn("NOMBRE Y APELLIDO"),
                "ÁREA": st.column_config.TextColumn("ÁREA"),
            },
        )

        # --- Botón de guardar cambios ---
        if st.button("💾 Guardar cambios", type="primary"):
            guardar_csv_seguro(path, edited_df)
            st.success("✅ Cambios guardados correctamente.")
            st.caption(f"Archivo guardado en: `{path}`")

    # ==========================
    # SECCIÓN: CONFIGURACIÓN
    # ==========================
    elif menu == "Configuración":
        st.title("⚙️ Configuración del salón")
        st.write("Aquí podrás configurar parámetros futuros (como límites de personal o formatos de horario).")
        st.warning("Módulo en desarrollo...")

    # --- Cerrar sesión ---
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.rerun()