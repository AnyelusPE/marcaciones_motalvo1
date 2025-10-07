import streamlit as st
from roles.financista.horarios import run_horarios
from roles.financista.cruce_horarios import run_cruce_horarios
from roles.financista.historial import run_historial
from roles.financista.configuracion import run_configuracion


def run_financista_app(usuario):
    """Panel principal del Financista"""
    nombre_financista = usuario["usuario"]

    # --- Sidebar ---
    st.sidebar.markdown(f"### 💼 {nombre_financista}")
    st.sidebar.markdown("(financista)")
    menu = st.sidebar.radio("Navegación", ["Horarios", "Cruce de horarios", "Historial", "Configuración"])

    if menu == "Horarios":
        run_horarios(usuario)
    elif menu == "Cruce de horarios":
        run_cruce_horarios(usuario)
    elif menu == "Historial":
        run_historial(usuario)
    elif menu == "Configuración":
        run_configuracion(usuario)

    # Cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
