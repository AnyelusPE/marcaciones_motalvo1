import streamlit as st
from roles.financistas.gabriela.horarios import run_horarios
from roles.financistas.gabriela.cruces import run_cruces
from roles.financistas.gabriela.reportes import run_reportes
from roles.financistas.gabriela.configuracion import run_configuracion

def run_gabriela_app():
    st.sidebar.markdown("### 👩‍💼 Gabriela - Financista")
    st.sidebar.markdown("(Acceso a 4 salones asignados)")

    menu = st.sidebar.radio(
        "Navegación",
        ["📅 Horarios", "🔍 Cruce de Asistencia", "📊 Reportes", "⚙️ Configuración"],
        label_visibility="collapsed"
    )

    if menu == "📅 Horarios":
        run_horarios()
    elif menu == "🔍 Cruce de Asistencia":
        run_cruces()
    elif menu == "📊 Reportes":
        run_reportes()
    elif menu == "⚙️ Configuración":
        run_configuracion()

    st.sidebar.divider()
    if st.sidebar.button("Cerrar sesión", key="cerrar_sesion_gabriela"):
        st.session_state.clear()
        st.rerun()
