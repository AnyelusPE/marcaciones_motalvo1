import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar


def crear_dataframe_vacio(inicio, fin):
    """Genera un DataFrame vacío con las columnas base (DNI, NOMBRE, ÁREA, fechas)."""
    fechas = pd.date_range(inicio, fin)
    columnas = ["DNI", "NOMBRE Y APELLIDO", "ÁREA"] + [f.strftime("%d/%m/%Y") for f in fechas]
    df = pd.DataFrame(columns=columnas)
    return df


def generar_nombre_archivo(nombre_salon, inicio):
    """Genera el nombre de archivo en base al mes y quincena."""
    if inicio.day <= 15:
        quincena = "Q1"
    else:
        quincena = "Q2"
    return f"{nombre_salon}_{inicio.year}-{inicio.month:02d}-{quincena}.csv"


def run_salon_app(usuario):
    nombre_salon = usuario["usuario"]

    # --- Barra lateral ---
    st.sidebar.markdown(f"### 💇‍♂️ {nombre_salon}")
    st.sidebar.markdown("(salón)")
    menu = st.sidebar.radio("Navegación", ["Inicio", "Configuración"])

    if menu == "Inicio":
        st.title(f"📅 Panel del salón - {nombre_salon}")
        st.info("Puedes editar los datos directamente en la tabla. Los cambios se pueden guardar.")

        # === Selección de rango de fechas ===
        st.markdown("### 📆 Selecciona el rango de fechas:")
        col1, col2, col3 = st.columns([1, 1, 0.8])
        inicio = col1.date_input("Desde", datetime.today().replace(day=1))
        fin = col2.date_input("Hasta", datetime.today().replace(day=15))
        aplicar = col3.button("📤 Aplicar rango", type="primary")

        if aplicar:
            if fin < inicio:
                st.error("⚠️ La fecha final no puede ser menor que la inicial.")
                st.stop()

            # Carpeta del salón
            carpeta_salon = os.path.join("data", "uploads", nombre_salon)
            os.makedirs(carpeta_salon, exist_ok=True)

            # Determinar nombre de archivo (Q1 o Q2)
            nombre_archivo = generar_nombre_archivo(nombre_salon, inicio)
            path = os.path.join(carpeta_salon, nombre_archivo)

            # Si existe, leerlo; si no, crear base vacía
            if os.path.exists(path):
                df = pd.read_csv(path, dtype=str).fillna("")
                st.session_state.df_salon = df
                st.session_state.path_salon = path
                st.success(f"✅ Archivo cargado: {nombre_archivo}")
            else:
                df = crear_dataframe_vacio(inicio, fin)
                df.to_csv(path, index=False, encoding="utf-8-sig")
                st.session_state.df_salon = df
                st.session_state.path_salon = path
                st.success(f"🆕 Archivo nuevo creado: {nombre_archivo}")

        # Mostrar tabla si ya hay DataFrame cargado
        if "df_salon" in st.session_state and st.session_state.df_salon is not None:
            st.markdown("### 🧾 Cuadro de horarios del personal")

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

            if st.button("💾 Guardar cambios", type="primary"):
                edited_df.to_csv(st.session_state.path_salon, index=False, encoding="utf-8-sig")
                st.session_state.df_salon = edited_df
                st.success("✅ Cambios guardados correctamente.")
                st.caption(f"Archivo actualizado: `{st.session_state.path_salon}`")

        else:
            st.warning("Selecciona un rango y haz clic en **📤 Aplicar rango** para mostrar o crear la tabla.")

    elif menu == "Configuración":
        st.title("⚙️ Configuración del salón")
        st.write("Módulo en desarrollo...")

    # Cierre de sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()