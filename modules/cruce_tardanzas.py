import pandas as pd
import re
from datetime import timedelta


def extrae_hora_inicio(horario: str) -> str | None:
    """Devuelve la hora de inicio si es un horario; si es un estado especial, lo devuelve tal cual."""
    if not horario or str(horario).strip() == "":
        return None

    texto = str(horario).upper().strip()
    especiales = ["DESCANSO", "PERMISO", "SUSPENSION", "FALTA"]

    for palabra in especiales:
        if palabra in texto:
            return palabra

    m = re.search(r"(\d{1,2})[:;.,](\d{2})\s*(AM|PM|A\.M\.|P\.M\.)?", texto, re.IGNORECASE)
    if not m:
        return None

    h, mnt, ampm = m.groups()
    h = int(h)
    mnt = int(mnt)

    if ampm:
        ampm = ampm.upper()
        if "P" in ampm and h < 12:
            h += 12
        elif "A" in ampm and h == 12:
            h = 0

    return f"{h:02d}:{mnt:02d}"


def horas_a_minutos(hhmm: str | None) -> float | None:
    if not hhmm:
        return None
    if not re.match(r"^\d{1,2}:\d{2}$", hhmm):
        return None
    try:
        h, m = hhmm.split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return None


def calcula_cruce_tardanzas(df_marc, df_hor):
    """Cruza las marcaciones biométricas con la malla horaria y calcula tardanzas."""

    # --- PRIMERA MARCACIÓN POR DÍA ---
    df_marc["FECHA/HORA"] = pd.to_datetime(df_marc["FECHA/HORA"], errors="coerce", dayfirst=True)
    df_marc = df_marc.dropna(subset=["FECHA/HORA"]).copy()
    df_marc["FECHA"] = df_marc["FECHA/HORA"].dt.date

    df_first = (
        df_marc.sort_values("FECHA/HORA")
        .groupby(["DNI", "FECHA"], as_index=False)["FECHA/HORA"]
        .first()
        .rename(columns={"FECHA/HORA": "PRIMERA_MARCACION"})
    )
    df_first["PRIMERA_MIN"] = (
        df_first["PRIMERA_MARCACION"].dt.hour * 60 + df_first["PRIMERA_MARCACION"].dt.minute
    )

    # --- ADAPTAR HORARIOS QUE NO TIENEN COLUMNA "FECHA" ---
    df_hor = df_hor.copy()

    # Si las fechas están como encabezados (ej. "01/09/2025")
    posibles_fechas = [c for c in df_hor.columns if re.match(r"\d{2}/\d{2}/\d{4}", c)]
    registros = []

    if "FECHA" not in df_hor.columns and posibles_fechas:
        for _, fila in df_hor.iterrows():
            for fecha in posibles_fechas:
                registros.append({
                    "DNI": fila.get("DNI"),
                    "NOMBRE Y APELLIDO": fila.get("NOMBRE Y APELLIDO"),
                    "FECHA": pd.to_datetime(fecha, dayfirst=True).date(),
                    "HORARIO_ESPERADO": fila.get(fecha)
                })
        df_hor = pd.DataFrame(registros)

    # Procesar horas esperadas
    df_hor["HORA_INICIO_STR"] = df_hor["HORARIO_ESPERADO"].apply(extrae_hora_inicio)
    df_hor["HORA_INICIO_MIN"] = df_hor["HORA_INICIO_STR"].apply(horas_a_minutos)
    df_hor["DESCANSO"] = df_hor["HORA_INICIO_STR"].isin(["DESCANSO", "PERMISO", "SUSPENSION", "FALTA"])

    # --- UNIR CON BIOMÉTRICO ---
    base = df_hor.merge(df_first, on=["DNI", "FECHA"], how="left")

    def tardanza_row(row):
        if row["DESCANSO"]:
            return row["HORA_INICIO_STR"]
        if pd.isna(row.get("HORA_INICIO_MIN")):
            return "-"
        if pd.isna(row.get("PRIMERA_MIN")):
            return "-"
        delta = int(row["PRIMERA_MIN"] - row["HORA_INICIO_MIN"])
        return max(0, delta)

    base["TARDANZA (min)"] = base.apply(tardanza_row, axis=1)

    df_resultado = base[["DNI", "NOMBRE Y APELLIDO", "FECHA", "HORARIO_ESPERADO", "TARDANZA (min)"]].rename(
        columns={"NOMBRE Y APELLIDO": "NOMBRE", "HORARIO_ESPERADO": "HORARIO"}
    )

    df_pivot = df_resultado.pivot_table(
        index=["DNI", "NOMBRE"],
        columns="FECHA",
        values="TARDANZA (min)",
        aggfunc="first",
    ).reset_index()

    # Total de tardanzas
    cols_val = [c for c in df_pivot.columns if c not in ("DNI", "NOMBRE")]

    def safe_sum(row):
        total = 0
        for x in row:
            if isinstance(x, (int, float)):
                total += x
        return total

    df_pivot["TOTAL_TARDANZA"] = df_pivot[cols_val].apply(safe_sum, axis=1)

    return df_pivot