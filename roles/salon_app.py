import streamlit as st
import pandas as pd
from datetime import datetime
from core.db import cargar_datos, guardar_csv_seguro
import calendar
import os


def obtener_quincena(fecha):
    """Determina si una fecha pertenece a la 1ra o 2da quincena del mes."""
    if fecha.day <= 15:
        inicio = fecha.replace(day=1)
        fin = fecha.replace(day=15)
        return "Q1", inicio, fin
    else:
        ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
        inicio = fecha.replace(day=16)
        fin = fecha.replace(day=ultimo_dia)
        return "Q2", inicio, fin


def run_salon_app(usuario):
    """
    Panel del salón con control de quincenas y columna de DNI antes de nombre.
    """
    nombre_salon = usuario["usuario"]

    # --- Sidebar ---
    st.sidebar.markdown(f"### 💇 {nombre_salon}")
    st.sidebar.markdown("(salón)")
    menu = st.sidebar.radio("Navegación", ["Inicio", "Configuración"])

    if menu == "Inicio":
        st.title(f"📅 Panel del salón - {nombre_salon}")
        st.info("📝 Puedes editar los datos directamente en la tabla. Los cambios se pueden guardar.")

        # --- Selección de fechas ---
        st.markdown("#### 📆 Selecciona el rango de fechas:")
        col1, col2, col3 = st.columns([1, 1, 0.6])
        inicio = col1.date_input("Desde", datetime.today().replace(day=1))
        fin = col2.date_input("Hasta", datetime.today())
        aplicar = col3.button("📤 Aplicar rango", type="primary")

        if aplicar:
            if fin < inicio:
                st.error("⚠️ La fecha final no puede ser menor que la inicial.")
                st.stop()

            # Detectar quincena a partir de la fecha inicial
            _, inicio_q, fin_q = obtener_quincena(inicio)
            _, _, fin_q_fin = obtener_quincena(fin)

            # Si el rango cruza dos quincenas, se usa la segunda
            if inicio_q != fin_q:
                inicio_q = fin_q
                fin_q = fin_q_fin

            # --- Cargar datos de esa quincena ---
            df, path = cargar_datos(nombre_salon, inicio_q, fin_q)

            # --- Asegurar columnas obligatorias y orden correcto ---
            columnas_obligatorias = ["DNI", "NOMBRE Y APELLIDO", "ÁREA"]
            for col in columnas_obligatorias:
                if col not in df.columns:
                    df[col] = ""

            # Reordenar para que DNI esté antes del nombre
            columnas = ["DNI", "NOMBRE Y APELLIDO", "ÁREA"] + [
                c for c in df.columns if c not in ["DNI", "NOMBRE Y APELLIDO", "ÁREA"]
            ]
            df = df[columnas]

            # --- Mostrar tabla ---
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
                st.caption(f"Archivo guardado en: `{os.path.basename(path)}`")

        else:
            st.warning("Selecciona un rango y haz clic en **📤 Aplicar rango** para mostrar los datos.")

    elif menu == "Configuración":
        st.title("⚙️ Configuración del salón")
        st.write("Aquí podrás configurar parámetros futuros.")
        st.warning("Módulo en desarrollo...")

    # --- Cerrar sesión ---
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.rerun()