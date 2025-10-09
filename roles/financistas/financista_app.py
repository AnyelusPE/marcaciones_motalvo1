import streamlit as st
from roles.financistas.gabriela.gabriela_app import run_gabriela_app
from roles.financistas.ely.ely_app import run_ely_app
from roles.financistas.arturo.arturo_app import run_arturo_app
from roles.financistas.efrain.efrain_app import run_efrain_app

def run_financistas_app(usuario):
    nombre = usuario["usuario"].lower()

    if nombre == "gabriela":
        run_gabriela_app()
    elif nombre == "ely":
        run_ely_app()
    elif nombre == "arturo":
        run_arturo_app()
    elif nombre == "efrain":
        run_efrain_app()
    else:
        st.error(f"No existe carpeta para el usuario '{nombre}'.")
