import io
import pandas as pd
import streamlit as st

from roles.financistas.gabriela.horarios import run_horarios
from roles.financistas.gabriela.cruces import procesar_cruce_general
from roles.financistas.gabriela.reportes import run_reportes
from roles.financistas.gabriela.configuracion import run_configuracion

SALONES_GABRIELA = {
    "FM Bellavista": "fm_bellavista",
    "FM Barranco": "fm_barranco",
    "FM Javier Prado": "fm_javier_prado",
    "Trujillo Mall": "trujillo_mall",
}

SESSION_KEY_RESULTADO = "gabriela_cruce_resultado"
SESSION_KEY_RESUMEN = "gabriela_cruce_resumen"


def run_gabriela_app():
    st.sidebar.markdown("### Gabriela - Financista")
    st.sidebar.markdown("(Acceso a 4 salones asignados)")

    menu = st.sidebar.radio(
        "Navegación",
        ["📅 Horarios", "🔍 Cruce de Asistencia", "📊 Reportes", "⚙️ Configuración"],
        label_visibility="collapsed",
    )

    if menu == "📅 Horarios":
        run_horarios()

    elif menu == "🔍 Cruce de Asistencia":
        st.title("Cruce de Asistencia")
        st.caption("Sube el biométrico, elige los salones y revisa el cruce antes de descargarlo.")

        archivo_bio = st.file_uploader(
            "Archivo biométrico (CSV/XLSX)", type=["csv", "xls", "xlsx"], key="bio_gabriela"
        )

        periodo = st.radio("Periodo", ["Q1 (1-15)", "Q2 (16-fin)"], horizontal=True)

        salon_labels = list(SALONES_GABRIELA.keys())
        salones_elegidos = st.multiselect(
            "Salones a cruzar",
            options=salon_labels,
            default=salon_labels,
        )
        salones_sel = [SALONES_GABRIELA[label] for label in salones_elegidos]

        if archivo_bio is None:
            st.session_state.pop(SESSION_KEY_RESULTADO, None)
            st.session_state.pop(SESSION_KEY_RESUMEN, None)

        if st.button("Generar Cruce", use_container_width=True):
            if not archivo_bio:
                st.warning("Debes cargar el archivo biométrico.")
                st.session_state.pop(SESSION_KEY_RESULTADO, None)
                st.session_state.pop(SESSION_KEY_RESUMEN, None)
            elif not salones_sel:
                st.warning("Debes seleccionar al menos un salón.")
                st.session_state.pop(SESSION_KEY_RESULTADO, None)
                st.session_state.pop(SESSION_KEY_RESUMEN, None)
            else:
                try:
                    archivo_bio.seek(0)
                    nombre = getattr(archivo_bio, "name", "").lower()
                    if nombre.endswith(".csv"):
                        df_bio = pd.read_csv(archivo_bio, dtype=str, encoding_errors="ignore")
                    else:
                        df_bio = pd.read_excel(archivo_bio, dtype=str)
                    df_bio.columns = [str(c).strip() for c in df_bio.columns]

                    cols = [c.lower() for c in df_bio.columns]
                    dni_col = next((c for c in df_bio.columns if "dni" in c.lower()), None)
                    fecha_col = None
                    for cand in ["fecha/hora", "fecha_hora", "fecha hora", "fechahora", "fecha"]:
                        for idx, lc in enumerate(cols):
                            if cand == lc:
                                fecha_col = df_bio.columns[idx]
                                break
                        if fecha_col:
                            break
                    if fecha_col is None:
                        for idx, lc in enumerate(cols):
                            if ("fecha" in lc) or ("hora" in lc):
                                fecha_col = df_bio.columns[idx]
                                break

                    if not dni_col or not fecha_col:
                        st.error("No se detectaron las columnas de DNI y Fecha/Hora en el biométrico.")
                        st.session_state.pop(SESSION_KEY_RESULTADO, None)
                        st.session_state.pop(SESSION_KEY_RESUMEN, None)
                    else:
                        resultado = procesar_cruce_general(df_bio, dni_col, fecha_col, salones_sel, periodo)
                        if resultado is not None and not resultado.empty:
                            st.session_state[SESSION_KEY_RESULTADO] = resultado
                            st.session_state[SESSION_KEY_RESUMEN] = {
                                "archivo": getattr(archivo_bio, "name", ""),
                                "periodo": periodo,
                                "salones": salones_elegidos,
                            }
                            st.success("Cruce generado correctamente.")
                        else:
                            st.error("No se generó resultado para descargar.")
                            st.session_state.pop(SESSION_KEY_RESULTADO, None)
                            st.session_state.pop(SESSION_KEY_RESUMEN, None)
                except Exception as e:
                    st.error(f"Error durante el cruce: {e}")
                    st.session_state.pop(SESSION_KEY_RESULTADO, None)
                    st.session_state.pop(SESSION_KEY_RESUMEN, None)

        resultado_guardado = st.session_state.get(SESSION_KEY_RESULTADO)
        if isinstance(resultado_guardado, pd.DataFrame) and not resultado_guardado.empty:
            resumen = st.session_state.get(SESSION_KEY_RESUMEN, {})
            configuracion = []
            archivo_actual = resumen.get("archivo")
            if archivo_actual:
                configuracion.append(f"Archivo: {archivo_actual}")
            periodo_usado = resumen.get("periodo")
            if periodo_usado:
                configuracion.append(f"Periodo: {periodo_usado}")
            salones_usados = resumen.get("salones")
            if salones_usados:
                configuracion.append("Salones: " + ", ".join(salones_usados))
            if configuracion:
                st.caption(" | ".join(configuracion))

            st.dataframe(resultado_guardado, use_container_width=True)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                resultado_guardado.to_excel(writer, index=False, sheet_name="Cruce")
            buffer.seek(0)
            st.download_button(
                "Descargar Cruce (Excel)",
                buffer,
                file_name="CRUCE_GENERAL.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    elif menu == "📊 Reportes":
        run_reportes()

    elif menu == "⚙️ Configuración":
        run_configuracion()

    st.sidebar.divider()
    if st.sidebar.button("Cerrar sesión", key="cerrar_sesion_gabriela"):
        st.session_state.clear()
        st.rerun()
