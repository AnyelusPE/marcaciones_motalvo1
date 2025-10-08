import pandas as pd
import streamlit as st
from datetime import datetime
import os


def run_cruces():
    st.title("📊 Cruce de Asistencia General")
    st.caption("Compara automáticamente las marcaciones del biométrico con los horarios de los salones asignados.")
    st.markdown("---")

    archivo_biometrico = st.file_uploader("📂 Carga el archivo del biométrico (Excel o CSV)", type=["xlsx", "csv"])

    if archivo_biometrico:
        try:
            # Lectura del archivo biométrico
            if archivo_biometrico.name.endswith(".xlsx"):
                bio_df = pd.read_excel(archivo_biometrico)
            else:
                bio_df = pd.read_csv(archivo_biometrico)

            st.success("✅ Archivo biométrico cargado correctamente.")
            st.markdown("---")

            # Normalizar nombres de columnas
            bio_df.columns = [c.strip().lower() for c in bio_df.columns]
            posibles_dni = [c for c in bio_df.columns if c in ["dni", "documento", "doc", "numdoc"]]
            posibles_hora = [c for c in bio_df.columns if "hora" in c or "entrada" in c or "marcacion" in c]

            if not posibles_dni or not posibles_hora:
                st.error("⚠️ El archivo biométrico debe tener columnas con el DNI y la HORA de marcación.")
                st.stop()

            dni_col = posibles_dni[0]
            hora_col = posibles_hora[0]

            # === Selección de salones ===
            st.subheader("🏢 Selecciona los salones a cruzar")
            todos_los_salones = ["FM_BELLAVISTA", "FM_BARRANCO", "FM_JAVIER_PRADO", "TRUJILLO_MALL"]
            seleccionados = [s for s in todos_los_salones if st.checkbox(s, True)]

            if not seleccionados:
                st.warning("⚠️ Debes seleccionar al menos un salón.")
                st.stop()

            # === Selección de quincena ===
            st.subheader("🗓️ Selecciona la quincena")
            periodo = st.radio("Periodo", ["Q1 (1–15)", "Q2 (16–fin)"], horizontal=True)
            st.markdown("---")

            # === Procesar Cruce ===
            if st.button("📊 Realizar Cruce Consolidado"):
                st.info("⏳ Procesando cruces seleccionados...")

                resultado = procesar_cruce_general(bio_df, dni_col, hora_col, seleccionados, periodo)

                if not resultado.empty:
                    st.success("✅ Cruce consolidado generado correctamente.")
                    st.dataframe(resultado, use_container_width=True)

                    # === Guardar archivo ===
                    os.makedirs("data/cruces", exist_ok=True)
                    año = datetime.now().year
                    mes = f"{datetime.now().month:02d}"
                    quin = periodo.split()[0]

                    ruta_salida = f"data/cruces/CRUCE_GENERAL_{año}-{mes}-{quin}.xlsx"
                    resultado.to_excel(ruta_salida, index=False, sheet_name=f"{quin}_{mes}")

                    st.success(f"📁 Cruce consolidado guardado correctamente: {os.path.basename(ruta_salida)}")

                    with open(ruta_salida, "rb") as f:
                        st.download_button("📥 Descargar Cruce Consolidado", f, file_name=os.path.basename(ruta_salida))
                else:
                    st.warning("⚠️ No se encontró información para generar el cruce.")

        except Exception as e:
            st.error(f"🚫 Error al procesar el archivo biométrico: {e}")


def procesar_cruce_general(bio_df, dni_col, hora_col, salones, periodo):
    """
    Cruza horarios vs biométrico (corrige comparación de DNI y hora, simplifica resultados).
    """
    resultado_final = pd.DataFrame()
    base_path = "data/uploads"
    encontrados = 0

    # 🔹 Normalizar DNIs en el biométrico
    bio_df[dni_col] = (
        bio_df[dni_col]
        .astype(str)
        .str.strip()
        .str.replace(r"\D", "", regex=True)
        .str.lstrip("0")
    )

    # 🔹 Normalizar hora: extraer solo HH:MM aunque venga con fecha
    bio_df[hora_col] = bio_df[hora_col].astype(str).str.extract(r"(\d{1,2}:\d{2})")[0]

    for salon in salones:
        try:
            carpeta_salon = os.path.join(base_path, salon)
            año = datetime.now().year
            mes = f"{datetime.now().month:02d}"
            quin = periodo.split()[0]

            archivo_horario = os.path.join(carpeta_salon, f"{salon}_{año}-{mes}-{quin}.csv")

            if not os.path.exists(archivo_horario):
                st.warning(f"⚠️ No se encontró el horario para {salon}: {archivo_horario}")
                continue

            encontrados += 1
            horario = pd.read_csv(archivo_horario)
            horario.columns = [c.strip().upper() for c in horario.columns]

            st.info(f"📁 Procesando {salon} → {os.path.basename(archivo_horario)}")

            fechas = [c for c in horario.columns if "/" in c]
            df_salon = horario[["DNI", "NOMBRE Y APELLIDO", "ÁREA"]].copy()
            df_salon.insert(0, "SALÓN", salon)

            # 🔹 Normalizar DNIs en el horario también
            df_salon["DNI"] = (
                df_salon["DNI"]
                .astype(str)
                .str.strip()
                .str.replace(r"\D", "", regex=True)
                .str.lstrip("0")
            )
            horario["DNI"] = (
                horario["DNI"]
                .astype(str)
                .str.strip()
                .str.replace(r"\D", "", regex=True)
                .str.lstrip("0")
            )

            # === CRUCE: comparar hora programada con primera marcación ===
            for fecha in fechas:
                col_resultados = []

                for _, fila in horario.iterrows():
                    dni = str(fila["DNI"]).strip()
                    horario_prog = str(fila[fecha]).strip()

                    # Casos especiales
                    if horario_prog.upper() in ["DESCANSO", "PERMISO", "SUSPENSION", "FALTA", "VACACIONES", "X", "-"]:
                        col_resultados.append(horario_prog)
                        continue

                    registros = bio_df[bio_df[dni_col] == dni]
                    if registros.empty:
                        col_resultados.append("-")
                        continue

                    try:
                        hora_marca = sorted(registros[hora_col].dropna().tolist())[0]
                        hora_inicio = horario_prog.split("-")[0].strip()

                        h_prog_dt = datetime.strptime(hora_inicio, "%H:%M")
                        h_marca_dt = datetime.strptime(hora_marca, "%H:%M")
                        diff_min = int((h_marca_dt - h_prog_dt).total_seconds() / 60)

                        # Mostrar 0 si llega a tiempo o antes, y solo minutos si llega tarde
                        if diff_min <= 0:
                            col_resultados.append("0")
                        else:
                            col_resultados.append(f"{diff_min} min")

                    except Exception:
                        col_resultados.append("-")

                df_salon[fecha] = col_resultados

            resultado_final = pd.concat([resultado_final, df_salon], ignore_index=True)

        except Exception as e:
            st.error(f"❌ Error procesando {salon}: {e}")
            continue

    if encontrados == 0:
        st.error("🚫 No se encontró ningún archivo de horario válido dentro de 'data/uploads/'.")
    return resultado_final
