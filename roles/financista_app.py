import streamlit as st
from modules.cruce_viewer import mostrar_cruce
from modules.horario_viewer import mostrar_vista

def run_financista_app(usuario):
    st.sidebar.title(f"👤 {usuario['usuario'].capitalize()}")
    st.sidebar.caption(f"({usuario['rol']})")

    menu = st.sidebar.radio("Navegación", ["Inicio", "Cruce de Asistencia", "Reportes", "Configuración"])

    if st.sidebar.button("🔓 Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # --- INICIO ---
    if menu == "Inicio":
        st.session_state["render_vista"] = False  # Resetea al entrar
        st.title("📅 Malla Horaria")
        st.info("Visualiza la malla horaria general cargada por los salones.")
        mostrar_vista(usuario["salones"])

    # --- CRUCE ---
    elif menu == "Cruce de Asistencia":
        st.title("📋 Cruce de Asistencia")
        mostrar_cruce(usuario)

    # --- REPORTES ---
    elif menu == "Reportes":
        st.title("📊 Reportes Generales")
        st.info("Módulo en desarrollo")

    # --- CONFIGURACIÓN ---
    elif menu == "Configuración":
        st.title("⚙️ Configuración del sistema")
        st.info("Aquí podrás ajustar parámetros o ver logs.")