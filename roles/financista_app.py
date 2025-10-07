import streamlit as st
import pandas as pd
import os
import calendar
from datetime import datetime, timedelta


def listar_salones():
    """Devuelve todas las carpetas dentro de data/uploads (los salones)."""
    base_path = os.path.join("data", "uploads")
    if not os.path.exists(base_path):
        return []
    return [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]


def calcular_resumen(df):
    """Calcula horas trabajadas y tardanzas por colaborador."""
    resumen = []

    if "DNI" not in df.columns or "NOMBRE Y APELLIDO" not in df.columns:
        return pd.DataFrame()

    for _, row in df.iterrows():
        dni = row.get("DNI", "")
        nombre = row.get("NOMBRE Y APELLIDO", "")

        # Filtrar solo columnas de horas (formato HH:MM)
        horas_cols = [c for c in df.columns if ":" in str(df[c].astype(str).iloc[0]) or "entrada" in c.lower() or "salida" in c.lower()]

        total_horas = timedelta()
        tardanzas = 0
        dias_trabajados = 0

        for col in horas_cols:
            try:
                valor = str(row[col]).strip()
                if valor and "-" not in valor and len(valor) >= 4:
                    partes = valor.split("-")
                    if len(partes) == 2:  # entrada-salida
                        entrada, salida = partes
                        h1 = datetime.strptime(entrada.strip(), "%H:%M")
                        h2 = datetime.strptime(salida.strip(), "%H:%M")
                        if h2 > h1:
                            total_horas += (h2 - h1)
                            dias_trabajados += 1
                            # Tardanza (si entra después de 08:15, por ejemplo)
                            if h1 > datetime.strptime("08:15", "%H:%M"):
                                tardanzas += (h1 - datetime.strptime("08:15", "%H:%M")).seconds / 60
            except Exception:
                continue

        resumen.append({
            "DNI": dni,
            "NOMBRE Y APELLIDO": nombre,
            "DÍAS TRABAJADOS": dias_trabajados,
            "HORAS TOTALES": round(total_horas.total_seconds() / 3600, 2),
            "MINUTOS TARDANZA": round(tardanzas, 1)
        })

    return pd.DataFrame(resumen)


def run_financista_app(usuario):
    """
    Panel para el rol de financista.
    Permite seleccionar salón, mes y quincena, ver horarios y resumen estadístico.
    """
    nombre_financista = usuario["usuario"]

    # Sidebar
    st.sidebar.markdown(f"### 💼 {nombre_financista}")
    st.sidebar.markdown("(financista)")
    menu = st.sidebar.radio("Navegación", ["Cruce de horarios", "Historial", "Configuración"])

    if menu == "Cruce de horarios":
        st.title(f"📊 Panel de Financista - {nombre_financista}")
        st.info("Selecciona una sede, mes y quincena para revisar o editar los horarios cargados por el salón.")

        # === Selección de sede ===
        salones = listar_salones()
        if not salones:
            st.error("⚠️ No hay salones registrados en la carpeta 'data/uploads/'.")
            st.stop()

        salon_sel = st.selectbox("🏢 Selecciona la sede:", salones)

        # === Selección de mes, año y quincena ===
        meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }

        hoy = datetime.today()
        col1, col2, col3 = st.columns([1, 1, 0.7])

        año_sel = col1.number_input("📅 Año", min_value=2023, max_value=2100, value=hoy.year)
        mes_sel = col2.selectbox("🗓️ Mes", options=list(meses.keys()), format_func=lambda x: meses[x], index=hoy.month - 1)
        quincena_sel = col3.radio("🕒 Quincena", ["Q1 (1-15)", "Q2 (16-fin)"])

        aplicar = st.button("📤 Aplicar selección", type="primary")

        if aplicar:
            quincena_codigo = "Q1" if "Q1" in quincena_sel else "Q2"
            nombre_archivo = f"{salon_sel}_{año_sel}-{mes_sel:02d}-{quincena_codigo}.csv"
            path = os.path.join("data", "uploads", salon_sel, nombre_archivo)

            if os.path.exists(path):
                df = pd.read_csv(path, dtype=str).fillna("")
                st.session_state.df_financista = df
                st.session_state.path_financista = path
                st.success(f"✅ Archivo cargado: {nombre_archivo}")
            else:
                st.session_state.df_financista = None
                st.warning(f"⚠️ El archivo `{nombre_archivo}` aún no ha sido generado por el salón `{salon_sel}`.")

        # === Mostrar tabla si hay datos ===
        if "df_financista" in st.session_state and st.session_state.df_financista is not None:
            st.markdown("#### 🧾 Cuadro de horarios del personal")

            edited_df = st.data_editor(
                st.session_state.df_financista,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "DNI": st.column_config.TextColumn("DNI"),
                    "NOMBRE Y APELLIDO": st.column_config.TextColumn("NOMBRE Y APELLIDO"),
                    "ÁREA": st.column_config.TextColumn("ÁREA"),
                },
            )

            # Botones en línea
            colg1, colg2 = st.columns([1, 1])
            with colg1:
                if st.button("💾 Guardar cambios", type="primary"):
                    edited_df.to_csv(st.session_state.path_financista, index=False, encoding="utf-8-sig")
                    st.session_state.df_financista = edited_df
                    st.success("✅ Cambios guardados correctamente.")
                    st.caption(f"Archivo actualizado: `{st.session_state.path_financista}`")

            with colg2:
                if st.button("📈 Mostrar resumen"):
                    resumen = calcular_resumen(st.session_state.df_financista)
                    if not resumen.empty:
                        st.markdown("#### 📊 Resumen de Asistencia y Tardanzas")
                        st.dataframe(resumen, use_container_width=True)

                        # Totales generales
                        total_horas = resumen["HORAS TOTALES"].sum()
                        total_tardanzas = resumen["MINUTOS TARDANZA"].sum()
                        st.success(f"**⏰ Total de horas trabajadas:** {round(total_horas, 2)} hrs")
                        st.warning(f"**🕐 Total de tardanzas acumuladas:** {round(total_tardanzas, 1)} min")
                    else:
                        st.info("No hay datos suficientes para calcular el resumen.")

        else:
            st.warning("Selecciona un rango y haz clic en **📤 Aplicar selección** para cargar el horario.")

    elif menu == "Historial":
        st.title("🕓 Historial de cruces")
        st.write("Aquí podrás consultar registros previos por quincena y salón (en desarrollo).")

    elif menu == "Configuración":
        st.title("⚙️ Configuración")
        st.warning("Módulo de configuración en desarrollo...")

    # Botón cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
