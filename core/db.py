import os
import pandas as pd
from datetime import datetime


# ==============================
# 🔹 FUNCIONES GENERALES DE ARCHIVOS CSV
# ==============================
def leer_csv_seguro(path: str) -> pd.DataFrame:
    """Lee un CSV si existe, o devuelve un DataFrame vacío."""
    if os.path.exists(path):
        try:
            return pd.read_csv(path, dtype=str)
        except Exception as e:
            print(f"⚠️ Error al leer {path}: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()


def guardar_csv_seguro(path: str, df: pd.DataFrame):
    """Guarda un DataFrame como CSV (creando carpetas si es necesario)."""
    carpeta = os.path.dirname(path)
    os.makedirs(carpeta, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


# ==============================
# 🔹 FUNCIONES DE RANGOS DE FECHAS
# ==============================
def generar_rango_fechas(inicio: datetime, fin: datetime):
    """Genera una lista de fechas formateadas entre dos días."""
    dias = pd.date_range(start=inicio, end=fin)
    return [d.strftime("%d/%m/%Y") for d in dias]


def ruta_archivo_usuario(usuario: str, inicio: datetime, fin: datetime, sede: str = None):
    """
    Devuelve la ruta del CSV para un usuario (salón o financista),
    opcionalmente por sede.
    """
    base = f"data/uploads/{usuario}"
    os.makedirs(base, exist_ok=True)

    if sede:
        nombre = f"{sede}_{inicio.strftime('%Y-%m-%d')}_{fin.strftime('%Y-%m-%d')}.csv"
    else:
        nombre = f"{inicio.strftime('%Y-%m-%d')}_{fin.strftime('%Y-%m-%d')}.csv"

    return os.path.join(base, nombre)


def cargar_datos(usuario: str, inicio: datetime, fin: datetime, sede: str = None):
    """Carga datos existentes o crea uno nuevo con columnas vacías."""
    path = ruta_archivo_usuario(usuario, inicio, fin, sede)
    df = leer_csv_seguro(path)

    columnas_base = ["NOMBRE Y APELLIDO", "ÁREA"]
    columnas_fechas = generar_rango_fechas(inicio, fin)
    columnas = columnas_base + columnas_fechas

    if df.empty:
        df = pd.DataFrame(columns=columnas)
    else:
        # Asegurar columnas obligatorias
        for col in columnas:
            if col not in df.columns:
                df[col] = None

    for col in columnas_base:
        df[col] = df[col].astype(str)

    return df, path