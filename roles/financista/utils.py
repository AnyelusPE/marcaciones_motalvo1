import os
import pandas as pd
from datetime import datetime

def listar_salones():
    base_path = os.path.join("data", "uploads")
    if not os.path.exists(base_path):
        return []
    return [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

def calcular_resumen(df):
    resumen = []
    for _, row in df.iterrows():
        dni = row.get("DNI", "")
        nombre = row.get("NOMBRE Y APELLIDO", "")
        total_horas = 0
        tardanzas = 0
        dias = 0
        for val in row.values:
            if isinstance(val, str) and "-" in val:
                try:
                    e, s = [datetime.strptime(x.strip(), "%H:%M") for x in val.split("-")]
                    if s > e:
                        total_horas += (s - e).seconds / 3600
                        dias += 1
                        if e > datetime.strptime("08:15", "%H:%M"):
                            tardanzas += (e - datetime.strptime("08:15", "%H:%M")).seconds / 60
                except Exception:
                    pass
        resumen.append({
            "DNI": dni,
            "NOMBRE Y APELLIDO": nombre,
            "DÍAS": dias,
            "HORAS TOTALES": round(total_horas, 2),
            "MINUTOS TARDANZA": round(tardanzas, 1)
        })
    return pd.DataFrame(resumen)
