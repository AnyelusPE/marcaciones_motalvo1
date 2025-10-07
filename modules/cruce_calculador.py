import pandas as pd
import io
import os

def leer_excel_bytes(uploaded_file):
    return uploaded_file.getvalue() if uploaded_file else b""

def limpiar_dni(df):
    """Asegura que la columna DNI sea texto sin .0"""
    if "DNI" in df.columns:
        df["DNI"] = df["DNI"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    return df

def leer_biometrico(file):
    """Lee el archivo de marcaciones biométricas (Excel o CSV)."""
    nombre = file.name.lower()
    if nombre.endswith(".csv"):
        df = pd.read_csv(file, dtype=str)
    else:
        data = leer_excel_bytes(file)
        df = pd.read_excel(io.BytesIO(data), dtype=str)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = limpiar_dni(df)
    return df

def leer_horario(path):
    """Lee los horarios desde la carpeta uploads (Excel o CSV)."""
    nombre = os.path.basename(path).lower()
    if nombre.endswith(".csv"):
        df = pd.read_csv(path, dtype=str)
    else:
        df = pd.read_excel(path, dtype=str)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = limpiar_dni(df)
    return df