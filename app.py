import streamlit as st
from core.auth import verificar_login

# Routers principales
from roles.admin.admin_app import run_admin_app
from roles.financistas.financistas_app import run_financistas_app
from roles.salones.salones_app import run_salones_app

st.set_page_config(page_title="Sistema Montalvo", page_icon="🕒", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# --- LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Ingreso al Sistema de Marcaciones")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        user = verificar_login(u, p)
        if user:
            st.session_state.autenticado = True
            st.session_state.usuario = user
            st.success(f"✅ Bienvenido {user['usuario']} ({user['rol']})")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")
else:
    usuario = st.session_state.usuario
    rol = usuario["rol"].lower()

    if rol == "admin":
        run_admin_app(usuario)
    elif rol == "financista":
        run_financistas_app(usuario)
    elif rol == "salon":
        run_salones_app(usuario)
    else:
        st.error(f"Rol desconocido: {rol}")
