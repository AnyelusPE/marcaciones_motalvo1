import pandas as pd
import streamlit as st
from datetime import datetime
import os
import re  # Para regex en parsing

# Silenciar mensajes UI durante el cruce (solo descargar Excel)
VERBOSE = False

def _log(level, msg):
    if not VERBOSE:
        return
    try:
        getattr(st, level)(msg)
    except Exception:
        pass

# ============================================================
# 🧩 FUNCIÓN AUXILIAR: NORMALIZAR DNI
# ============================================================
def normalizar_dni(dni_str):
    """Normaliza DNI: elimina caracteres no numéricos, trim y rellena a 8 dígitos."""
    if pd.isna(dni_str):
        return ""
    dni = str(dni_str).strip()
    dni = re.sub(r"\D", "", dni)  # eliminar todo lo que no sea número
    return dni.zfill(8)

# ============================================================
# 🧩 FUNCIÓN AUXILIAR: FORMATEAR FECHA
# ============================================================
def formatear_fecha(f):
    """Convierte string a datetime; intenta múltiples formatos comunes."""
    try:
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"]:
            try:
                return datetime.strptime(f.strip(), fmt)
            except ValueError:
                continue
        return None
    except Exception:
        return None

# ============================================================
# 🧩 FUNCIÓN AUXILIAR: PARSEAR HORA DE ENTRADA
# ============================================================
def parsear_hora_entrada(horario_str):
    """Extrae la hora de entrada de un string tipo '08:00-17:00'."""
    if pd.isna(horario_str) or not isinstance(horario_str, str):
        return ""
    horario = str(horario_str).strip().upper()

    especiales = {"DESCANSO", "PERMISO", "SUSPENSION", "VACACIONES", "FALTA", "X", "-"}
    if horario in especiales:
        return horario  # deja texto especial

    # Normaliza guiones y espacios
    horario = re.sub(r"[–—]", "-", horario)
    horario = re.sub(r"\s*-\s*", "-", horario)

    partes = [p.strip() for p in horario.split("-") if p.strip()]
    if not partes:
        return ""
    hora_prog = partes[0]
    if re.match(r"\d{4}$", hora_prog):  # ejemplo: 0900 -> 09:00
        hora_prog = f"{hora_prog[:2]}:{hora_prog[2:]}"
    return hora_prog if len(hora_prog) >= 4 else ""

# Versión robusta para normalizar rangos y distintos guiones
def _parse_hora_entrada(horario_str):
    if pd.isna(horario_str) or not isinstance(horario_str, str):
        return ""
    horario = str(horario_str).strip().upper()
    especiales = {"DESCANSO", "PERMISO", "SUSPENSION", "VACACIONES", "FALTA", "X", "-"}
    if horario in especiales:
        return horario
    # Normaliza guiones Unicode a '-'
    horario = re.sub(r"[\u2010-\u2015\u2212]", "-", horario)
    horario = re.sub(r"\s*-\s*", "-", horario)
    partes = [p.strip() for p in horario.split("-") if p.strip()]
    if not partes:
        return ""
    hora_prog = partes[0]
    if re.match(r"^\d{4}$", hora_prog):
        hora_prog = f"{hora_prog[:2]}:{hora_prog[2:]}"
    if re.match(r"^\d{1,2}:\d{2}$", hora_prog):
        h, m = hora_prog.split(":")
        return f"{int(h):02d}:{int(m):02d}"
    return ""

# ============================================================
# 🧩 FUNCIÓN PRINCIPAL DE CRUCE
# ============================================================
def procesar_cruce_general(bio_df, dni_col, fecha_col, salones, periodo):
    resultado_final = pd.DataFrame()
    base_path = "data/uploads"
    encontrados = 0
    cruces_exitosos = 0
    total_intentos = 0

    # === Normalizar el biométrico ===
    bio_df[dni_col] = bio_df[dni_col].apply(normalizar_dni)
    bio_df = bio_df.dropna(subset=[dni_col, fecha_col])
    bio_df["FECHA_OBJ"] = pd.to_datetime(bio_df[fecha_col], errors="coerce", dayfirst=True)
    bio_df["HORA"] = bio_df["FECHA_OBJ"].dt.strftime("%H:%M")
    bio_df["FECHA_STR"] = bio_df["FECHA_OBJ"].dt.strftime("%d/%m/%Y")
    bio_df = bio_df.dropna(subset=["FECHA_OBJ"])

    # Primer marcación por DNI y FECHA_OBJ
    primer_marcado = (
        bio_df.groupby([dni_col, "FECHA_OBJ"], as_index=False)["HORA"]
        .min()
        .rename(columns={"HORA": "HORA_PRIMERA"})
    )
    _log("info", f"📊 Biométrico procesado: {len(primer_marcado)} registros únicos (DNI + fecha).")

    # === Recorremos cada salón ===
    # Preparar primer marcación por DNI y día calendario
    try:
        bio_df["FECHA_D"] = bio_df["FECHA_OBJ"].dt.date
        primer_marcado_diario = (
            bio_df.groupby([dni_col, "FECHA_D"], as_index=False)["HORA"].min()
            .rename(columns={"HORA": "HORA_PRIMERA"})
        )
    except Exception:
        primer_marcado_diario = pd.DataFrame(columns=[dni_col, "FECHA_D", "HORA_PRIMERA"])

    q_key = periodo.split()[0].lower()
    for salon in salones:
        try:
            carpeta_salon = os.path.join(base_path, salon)
            if not os.path.exists(carpeta_salon):
                _log("warning", f"⚠️ Carpeta no existe: {carpeta_salon}")
                continue

            archivos_posibles = [
                f for f in os.listdir(carpeta_salon)
                if f.lower().endswith(".csv") and any(
                    key in f.lower()
                    for key in [q_key, f"quincena{q_key[-1]}", f"{q_key[-1]}-15" if q_key == "q1" else f"{q_key[-1]}-fin"]
                )
            ]
            if not archivos_posibles:
                _log("warning", f"⚠️ No se encontró archivo de horario para {salon}.")
                continue

            ruta_archivo = os.path.join(carpeta_salon, archivos_posibles[0])
            _log("info", f"📁 Procesando {salon} → {os.path.basename(ruta_archivo)}")

            df_horario = pd.read_csv(ruta_archivo, dtype=str)
            df_horario.columns = [str(c).strip().upper() for c in df_horario.columns]

            if "DNI" not in df_horario.columns:
                _log("error", f"❌ Falta columna 'DNI' en {salon}")
                continue

            df_horario["DNI_NORM"] = df_horario["DNI"].apply(normalizar_dni)
            df_horario = df_horario[df_horario["DNI_NORM"] != ""]

            fechas_cols = [c for c in df_horario.columns if "/" in str(c)]
            if not fechas_cols:
                _log("warning", f"⚠️ No se encontraron columnas de fechas en {salon}")
                continue

            fecha_objs = {}
            for col in fechas_cols:
                fecha_objs[col] = pd.to_datetime(formatear_fecha(col), dayfirst=True)
                if fecha_objs[col] is None:
                    _log("warning", f"⚠️ Fecha inválida en columna: {col}")

            area_col = "ÁREA" if "ÁREA" in df_horario.columns else ("AREA" if "AREA" in df_horario.columns else None)
            base_cols = [c for c in ["DNI", "NOMBRE Y APELLIDO", area_col, "DNI_NORM"] if c is not None]
            df_salon = df_horario[base_cols].copy()
            df_salon = df_salon.drop("DNI_NORM", axis=1, errors="ignore")
            df_salon.insert(0, "SALON", salon)

            # === CRUCE DNI + FECHA ===
            for col_fecha in fechas_cols:
                fecha_match_obj = fecha_objs[col_fecha]
                if fecha_match_obj is None:
                    continue
                col_resultado = []

                for _, fila in df_horario.iterrows():
                    total_intentos += 1
                    try:
                        dni_norm = fila["DNI_NORM"]
                        horario_raw = fila[col_fecha]
                        resultado = _parse_hora_entrada(horario_raw)

                        # Casos especiales
                        if resultado in ["DESCANSO", "PERMISO", "SUSPENSION", "VACACIONES", "FALTA", "X", "-"]:
                            col_resultado.append(resultado)
                            continue

                        if resultado == "":
                            col_resultado.append("-")
                            continue

                        hora_prog = resultado

                        # Comparar por día calendario (DNI + fecha)
                        fecha_d = fecha_match_obj.date()
                        fila_marca = primer_marcado_diario[
                            (primer_marcado_diario[dni_col] == dni_norm)
                            & (primer_marcado_diario["FECHA_D"] == fecha_d)
                        ]

                        if fila_marca.empty:
                            col_resultado.append("-")
                            continue

                        hora_marca = str(fila_marca.iloc[0]["HORA_PRIMERA"]).strip()
                        if len(hora_marca) < 4 or ":" not in hora_marca:
                            col_resultado.append("-")
                            continue

                        h_prog = datetime.strptime(hora_prog, "%H:%M")
                        h_marca = datetime.strptime(hora_marca, "%H:%M")
                        diff = int((h_marca - h_prog).total_seconds() / 60)
                        resultado_final_val = "0" if diff <= 0 else f"{diff} min"
                        col_resultado.append(resultado_final_val)
                        cruces_exitosos += 1

                    except Exception:
                        col_resultado.append("-")

                df_salon[col_fecha] = col_resultado

            resultado_final = pd.concat([resultado_final, df_salon], ignore_index=True)
            encontrados += 1

        except Exception as e:
            _log("error", f"❌ Error procesando {salon}: {e}")
            continue

    _log("success", f"✅ Cruce completado: {encontrados} salones, {cruces_exitosos}/{total_intentos} cruces válidos.")
    if encontrados == 0:
        _log("error", "🚫 No se encontró ningún horario válido.")
    return resultado_final

# ============================================================
# 🔁 COMPATIBILIDAD CON SISTEMA PRINCIPAL
# ============================================================

def run_cruces(bio_df=None, dni_col="DNI", fecha_col="Fecha/Hora", salones=None, periodo="Q1 (1–15)"):
    """
    Wrapper para mantener compatibilidad con versiones anteriores del sistema.
    Simplemente ejecuta la función principal procesar_cruce_general().
    """
    if bio_df is None or salones is None:
        _log("error", "❌ Faltan datos para ejecutar el cruce.")
        return pd.DataFrame()
    try:
        return procesar_cruce_general(bio_df, dni_col, fecha_col, salones, periodo)
    except Exception as e:
        _log("error", f"❌ Error al ejecutar run_cruces: {e}")
        return pd.DataFrame()
