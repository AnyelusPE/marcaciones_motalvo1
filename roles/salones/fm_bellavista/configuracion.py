import streamlit as st

def run_configuracion():
    # Encabezado general
    st.title("⚙️ Configuración del Salón")
    st.markdown("Esta sección está diseñada para administrar las preferencias del salón **FM Bellavista**.")
    st.divider()

    # Sección general de información
    with st.expander("🏷️ Información del salón", expanded=True):
        st.text_input("Nombre del salón", "FM Bellavista", disabled=True)
        st.text_input("Ubicación", "Bellavista, Callao", disabled=True)
        st.text_input("Responsable", "Administrador local", disabled=True)
        st.markdown("> *(Estos campos son informativos. Podrás editarlos más adelante desde el panel central de administración.)*")

    st.divider()

    # Preferencias visuales (en futuro)
    with st.expander("🎨 Preferencias visuales (próximamente)", expanded=False):
        st.markdown("Aquí podrás cambiar el tema, colores o fondo del sistema.")
        st.info("🔧 Esta función aún no está habilitada.")

    st.divider()

    # Usuarios del salón
    with st.expander("👥 Gestión de usuarios (próximamente)", expanded=False):
        st.markdown("Desde aquí podrás agregar o eliminar usuarios asociados al salón.")
        st.warning("⚠️ Solo el área de TI podrá habilitar esta opción más adelante.")

    st.divider()

    # Botón de soporte
    st.markdown("### 💬 Soporte técnico")
    st.markdown("Si necesitas ayuda con el sistema o actualizar tus datos, contacta al área de soporte TI.")
    if st.button("📨 Enviar solicitud de soporte"):
        st.success("Tu solicitud fue registrada correctamente. El área de TI se comunicará contigo pronto.")
