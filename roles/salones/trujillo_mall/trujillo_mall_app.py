import streamlit as st
from roles.salones.trujillo_mall.subir_horarios import run_subir_horarios
from roles.salones.trujillo_mall.ver_horarios import run_ver_horarios
from roles.salones.trujillo_mall.configuracion import run_configuracion


def run_trujillo_mall():
    # Sidebar de navegación
    st.sidebar.markdown("### 💈 Trujillo Mall")
    st.sidebar.markdown("#### Menú de opciones")

    menu = st.sidebar.radio(
        "Navegación",
        ["📤 Subir horarios", "🗂️ Ver horarios guardados", "⚙️ Configuración"],
        label_visibility="collapsed"
    )

    if menu == "📤 Subir horarios":
        run_subir_horarios()

    elif menu == "🗂️ Ver horarios guardados":
        run_ver_horarios()

    elif menu == "⚙️ Configuración":
        run_configuracion()

    # Cerrar sesión
    st.sidebar.divider()
    if st.sidebar.button("Cerrar sesión", key="cerrar_sesion_trujillo_mall"):
        st.session_state.clear()
        st.rerun()


if __name__ == "__main__":
    run_trujillo_mall()
