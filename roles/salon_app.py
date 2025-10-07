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
        col1, col2, col3 = st.columns([1, 1, 0.5])
        inicio = col1.date_input("Desde", datetime.today().replace(day=1))
        fin = col2.date_input("Hasta", datetime.today())

        aplicar = col3.button("📤 Aplicar rango", type="primary")

        if aplicar:
            if fin < inicio:
                st.error("⚠️ La fecha final no puede ser menor que la inicial.")
                st.stop()

            inicio_dt = datetime.combine(inicio, datetime.min.time())
            fin_dt = datetime.combine(fin, datetime.min.time())

            # --- Cargar datos del rango ---
            df, path = cargar_datos(nombre_salon, inicio_dt, fin_dt)

            # Agregamos columna DNI si no existe
            columnas_obligatorias = ["DNI", "NOMBRE Y APELLIDO", "ÁREA"]
            for col in columnas_obligatorias:
                if col not in df.columns:
                    df[col] = ""

            # --- Mostrar tabla editable ---
            st.markdown("#### 🧾 Cuadro de horarios del personal")
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "DNI": st.column_config.TextColumn("DNI"),
                    "NOMBRE Y APELLIDO": st.column_config.TextColumn("NOMBRE Y APELLIDO"),
                    "ÁREA": st.column_config.TextColumn("ÁREA"),
                },
            )

            # --- Guardar cambios ---
            if st.button("💾 Guardar cambios", type="primary"):
                guardar_csv_seguro(path, edited_df)
                st.success("✅ Cambios guardados correctamente.")
                st.caption(f"Archivo guardado en: `{path}`")

        else:
            st.warning("Selecciona un rango y haz clic en **📤 Aplicar rango** para mostrar los datos.")

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