import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

def run_salon_app(usuario):
    st.sidebar.title(f"👤 {usuario['usuario'].upper()}")
    st.sidebar.caption(f"({usuario['rol']})")

    menu = st.sidebar.radio("Navegación", ["Inicio", "Configuración"])
    if st.sidebar.button("🔓 Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # === VARIABLES ===
    salon_name = usuario["usuario"].strip().upper()
    file_path = os.path.join("data", "uploads", f"['{salon_name}']_formato.csv")

    # === SECCIÓN INICIO ===
    if menu == "Inicio":
        st.title(f"📅 Panel del salón - {salon_name}")
        st.info("✏️ Puedes editar los datos directamente en la tabla. Los cambios se pueden guardar.")

        # Si no existe el archivo, creamos un formato vacío base
        if not os.path.exists(file_path):
            columnas_base = ["#", "DNI", "NOMBRE Y APELLIDO", "ÁREA"]
            # Generar 15 días de fechas
            inicio = datetime(2025, 9, 1)
            dias = [(inicio + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(15)]
            columnas = columnas_base + dias
            df = pd.DataFrame(columns=columnas)
            df.to_csv(file_path, index=False)
        else:
            df = pd.read_csv(file_path)

            # Detectar si faltan columnas de fecha y completarlas hasta 15 días
            columnas_base = ["#", "DNI", "NOMBRE Y APELLIDO", "ÁREA"]
            columnas_actuales = list(df.columns)
            columnas_fecha = [c for c in columnas_actuales if "/" in c]

            # Si hay menos de 15 columnas de fecha, añadimos las faltantes
            if len(columnas_fecha) < 15:
                if columnas_fecha:
                    ultima = datetime.strptime(columnas_fecha[-1], "%d/%m/%Y")
                else:
                    ultima = datetime(2025, 9, 1)
                faltan = 15 - len(columnas_fecha)
                nuevas = [(ultima + timedelta(days=i + 1)).strftime("%d/%m/%Y") for i in range(faltan)]
                for n in nuevas:
                    df[n] = ""

        # --- Editor interactivo de horarios ---
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{salon_name}"
        )

        # --- Guardar cambios ---
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 Guardar cambios"):
                edited_df.to_csv(file_path, index=False)
                st.success("✅ Cambios guardados correctamente.")

        with col2:
            st.caption("Los cambios se guardan en la carpeta `data/uploads` con el nombre correspondiente.")

    # === SECCIÓN CONFIGURACIÓN ===
    elif menu == "Configuración":
        st.title("⚙️ Configuración del salón")
        st.info("Aquí podrás añadir futuras opciones de personalización del sistema (pendiente de desarrollo).")
