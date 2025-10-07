import pandas as pd
import os


def cargar_datos(nombre_salon, inicio, fin, nombre_archivo):
    """
    Carga o crea el archivo CSV del salón con nombre único por quincena.
    Estructura: data/uploads/{salon}/{salon}_{YYYY-MM-QX}.csv
    """
    # Carpeta del salón
    carpeta = os.path.join("data", "uploads", nombre_salon)
    os.makedirs(carpeta, exist_ok=True)

    # Ruta completa
    path = os.path.join(carpeta, nombre_archivo)

    # Si existe, cargarlo; si no, crear DataFrame vacío con columnas base
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, dtype=str).fillna("")  # Evita NaN
        except Exception:
            df = pd.DataFrame(columns=["DNI", "NOMBRE Y APELLIDO", "ÁREA"])
    else:
        df = pd.DataFrame(columns=["DNI", "NOMBRE Y APELLIDO", "ÁREA"])

    return df, path


def guardar_csv_seguro(path, df):
    """
    Guarda el archivo de manera segura en formato UTF-8 con BOM,
    sin perder columnas ni duplicar registros.
    """
    # Normalizar DataFrame
    df = df.fillna("")  # Evita valores NaN
    df = df.loc[:, ~df.columns.duplicated()]  # Evita columnas repetidas

    # Crear carpeta si no existe
    carpeta = os.path.dirname(path)
    os.makedirs(carpeta, exist_ok=True)

    # Guardar
    df.to_csv(path, index=False, encoding="utf-8-sig")

    # Confirmación en consola (útil para depurar en Streamlit Cloud)
    print(f"[✅ Guardado correctamente]: {path}")
