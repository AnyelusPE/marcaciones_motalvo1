import streamlit as st
from roles.salones.fm_barranco.fm_barranco_app import run_fm_barranco
from roles.salones.fm_bellavista.fm_bellavista_app import run_fm_bellavista
from roles.salones.fm_javier_prado.fm_javier_prado_app import run_fm_javier_prado
from roles.salones.trujillo_mall.trujillo_mall_app import run_trujillo_mall


def run_salones_app(usuario):
    st.title("🏢 Panel de Salones")

    salon = usuario["usuario"].lower()

    if "barranco" in salon:
        run_fm_barranco()
    elif "bellavista" in salon:
        run_fm_bellavista()
    elif "prado" in salon:
        run_fm_javier_prado()
    elif "trujillo" in salon:
        run_trujillo_mall()
    else:
        st.error(f"Salón no reconocido: {salon}")
