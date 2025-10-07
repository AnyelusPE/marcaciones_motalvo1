import streamlit as st
from core.auth import verificar_login
from roles.salon_app import run_salon_app
from roles.financista_app import run_financista_app

st.set_page_config(page_title="Sistema de Marcación", page_icon="🕒", layout="wide")

# --- Estado global ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# --- Login ---
if not st.session_state.autenticado:
    st.title("🔒 Ingreso al Sistema de Marcación")
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
            st.error("Usuario o contraseña incorrectos.")
else:
    user = st.session_state.usuario
    if user["rol"] == "salon":
        run_salon_app(user)
    else:
        run_financista_app(user)