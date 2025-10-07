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
    Panel del salón con persistencia en sesión, control de quincenas y guardado por salón.
    """
    nombre_salon = usuario["usuario"]

    # --- Estado persistente en sesión ---
    if "df_salon" not in st.session_state:
        st.session_state.df_salon = None
    if "path_salon" not in st.session_state:
        st.session_state.path_salon = None
    if "rango_salon" not in st.session_state:
        st.session_state.rango_salon = None

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

        # === Aplicar rango ===
        if aplicar:
            if fin < inicio:
                st.error("⚠️ La fecha final no puede ser menor que la inicial.")
                st.stop()

            # Detectar quincena a partir de la fecha inicial
            q_inicial, inicio_q, fin_q = obtener_quincena(inicio)
            q_final, inicio_q_fin, fin_q_fin = obtener_quincena(fin)

            # Si el rango cruza dos quincenas, se usa la segunda
            if q_inicial != q_final:
                inicio_q = inicio_q_fin
                fin_q = fin_q_fin

            # Crear nombre único por salón
            nombre_archivo = f"{nombre_salon}_{inicio_q.year}-{inicio_q.month:02d}-{q_final}.csv"

            df, path = cargar_datos(nombre_salon, inicio_q, fin_q, nombre_archivo)

            # Asegurar columnas y orden
            columnas_obligatorias = ["DNI", "NOMBRE Y APELLIDO", "ÁREA"]
            for col in columnas_obligatorias:
                if col not in df.columns:
                    df[col] = ""

            columnas = ["DNI", "NOMBRE Y APELLIDO", "ÁREA"] + [
                c for c in df.columns if c not in columnas_obligatorias
            ]
            df = df[columnas]

            # Guardar en sesión
            st.session_state.df_salon = df
            st.session_state.path_salon = path
            st.session_state.rango_salon = (inicio_q, fin_q)

        # === Mostrar tabla persistente ===
        if st.session_state.df_salon is not None:
            st.markdown("#### 🧾 Cuadro de horarios del personal")

            edited_df = st.data_editor(
                st.session_state.df_salon,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "DNI": st.column_config.TextColumn("DNI"),
                    "NOMBRE Y APELLIDO": st.column_config.TextColumn("NOMBRE Y APELLIDO"),
                    "ÁREA": st.column_config.TextColumn("ÁREA"),
                },
            )

            # Actualizar el dataframe en sesión
            st.session_state.df_salon = edited_df

            # Guardar cambios
            if st.button("💾 Guardar cambios", type="primary"):
                guardar_csv_seguro(st.session_state.path_salon, edited_df)
                st.success("✅ Cambios guardados correctamente.")
                st.caption(f"Archivo guardado en: `{os.path.basename(st.session_state.path_salon)}`")

        else:
            st.warning("Selecciona un rango y haz clic en **📤 Aplicar rango** para mostrar los datos.")

    elif menu == "Configuración":
        st.title("⚙️ Configuración del salón")
        st.write("Aquí podrás configurar parámetros futuros.")
        st.warning("Módulo en desarrollo...")

    # --- Cerrar sesión ---
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()