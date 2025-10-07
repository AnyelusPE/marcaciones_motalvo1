import os
import pandas as pd
import streamlit as st
from pathlib import Path

# === Ruta base ===
BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "data" / "uploads"


def normalizar_nombre(nombre: str) -> str:
    """Limpia el nombre de salón o archivo de forma estándar."""
    if not isinstance(nombre, str):
        return ""
    return (
        nombre.replace("[", "")
        .replace("]", "")
        .replace("'", "")
        .replace('"', "")
        .replace("`", "")
        .replace("  ", " ")
        .replace(" ", "_")
        .replace("__", "_")
        .strip()
        .lower()
    )


def buscar_archivo(nombre_salon: str):
    """Busca un CSV que coincida con el nombre del salón."""
    try:
        archivos = os.listdir(UPLOAD_DIR)
    except FileNotFoundError:
        st.error(f"❌ Carpeta no encontrada: {UPLOAD_DIR}")
        return None

    nombre_normalizado = normalizar_nombre(nombre_salon)

    for archivo in archivos:
        archivo_normalizado = normalizar_nombre(archivo)
        if nombre_normalizado in archivo_normalizado and "formato.csv" in archivo_normalizado:
            return UPLOAD_DIR / archivo

    return None


def cargar_horario(nombre_salon: str):
    """Carga el archivo CSV si existe."""
    path = buscar_archivo(nombre_salon)
    if not path:
        st.warning(f"⚠️ No se encontró formato cargado para: {nombre_salon}")
        return None

    try:
        df = pd.read_csv(path, dtype=str)
        df.fillna("-", inplace=True)
        return df
    except Exception as e:
        st.error(f"⚠️ Error al leer '{path.name}': {e}")
        return None


def mostrar_vista(lista_salones):
    """Renderiza los horarios sin duplicar encabezados ni mensajes."""
    # --- Evita render duplicado ---
    if "render_vista" in st.session_state and st.session_state["render_vista"]:
        return
    st.session_state["render_vista"] = True

    # --- Mostrar cada salón ---
    for salon in lista_salones:
        st.markdown(f"### 🏢 {salon.upper()}")
        df = cargar_horario(salon)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)