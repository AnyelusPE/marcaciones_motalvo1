import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --------------------------
# FUNCIONES AUXILIARES
# --------------------------
def cargar_datos_salon(nombre_salon: str):
    """Carga los datos del salón desde un archivo o crea una tabla vacía."""
    path = f"data/uploads/{nombre_salon}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, dtype={"NOMBRE Y APELLIDO": str, "ÁREA": str})
    else:
        columnas = ["#", "DNI", "NOMBRE Y APELLIDO", "ÁREA",
                    "01/09/2025", "02/09/2025", "03/09/2025",
                    "04/09/2025", "05/09/2025"]
        df = pd.DataFrame(columns=columnas)
    return df


def guardar_datos_salon(nombre_salon: str, df: pd.DataFrame):
    """Guarda los datos del salón en la carpeta data/uploads."""
    os.makedirs("data/uploads", exist_ok=True)
    path = f"data/uploads/{nombre_salon}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")


# --------------------------
# APP PRINCIPAL
# --------------------------
def run_salon_app(usuario):
    """Interfaz del panel de salón."""
    nombre_salon = usuario["usuario"]

    st.sidebar.markdown(f"### 👤 {nombre_salon}")
    st.sidebar.markdown("(salon)")

    menu = st.sidebar.radio("Navegación", ["Inicio", "Configuración"])

    if menu == "Inicio":
        st.title(f"📅 Panel del salón - {nombre_salon}")
        st.info("📝 Puedes editar los datos directamente en la tabla. Los cambios se pueden guardar.")

        # Cargar datos
        df = cargar_datos_salon(nombre_salon)

        # 🔧 Forzar tipo texto en columnas editables
        for col in ["NOMBRE Y APELLIDO", "ÁREA"]:
            if col in df.columns:
                df[col] = df[col].astype(str)

        # 📋 Mostrar tabla editable
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "#": st.column_config.NumberColumn("#", disabled=True),
                "DNI": st.column_config.NumberColumn("DNI"),
                "NOMBRE Y APELLIDO": st.column_config.TextColumn("NOMBRE Y APELLIDO"),
                "ÁREA": st.column_config.TextColumn("ÁREA"),
            }
        )

        # 💾 Botón para guardar cambios
        if st.button("💾 Guardar cambios"):
            guardar_datos_salon(nombre_salon, edited_df)
            st.success(f"✅ Cambios guardados correctamente en data/uploads/{nombre_salon}.csv")

        st.caption("Los cambios se guardan en la carpeta `data/uploads` con el nombre correspondiente.")

    elif menu == "Configuración":
        st.title("⚙️ Configuración del salón")
        st.write("Aquí podrás ajustar opciones futuras específicas del salón.")
        st.warning("Módulo en desarrollo...")

    # 🔒 Botón cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.rerun()