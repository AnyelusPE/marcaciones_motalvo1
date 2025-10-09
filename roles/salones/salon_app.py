import streamlit as st
from roles.salones.fm_bellavista.fm_bellavista_app import run_fm_bellavista
from roles.salones.fm_barranco.fm_barranco_app import run_fm_barranco
from roles.salones.fm_javier_prado.fm_javier_prado_app import run_fm_javier_prado
from roles.salones.trujillo_mall.trujillo_mall_app import run_trujillo_mall

def run_salones_app(usuario):
    nombre = usuario["usuario"].lower()

    if nombre == "fm_bellavista":
        run_fm_bellavista()
    elif nombre == "fm_barranco":
        run_fm_barranco()
    elif nombre == "fm_javier_prado":
        run_fm_javier_prado()
    elif nombre == "trujillo_mall":
        run_trujillo_mall()
    else:
        st.error(f"No existe carpeta para el salón '{nombre}'.")
