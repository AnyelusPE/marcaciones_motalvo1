import streamlit as st
import pandas as pd
import os
from datetime import datetime
from roles.financista.utils import listar_salones, calcular_resumen


def run_horarios(usuario):
    nombre_financista = usuario["usuario"]

    st.title(f"📋 Horarios - {nombre_financista}")
    st.info("Selecciona una sede, mes y quincena para revisar o editar los horarios cargados por el salón.")

    salones = listar_salones()
    if not salones:
        st.error("⚠️ No hay salones registrados en 'data/uploads/'.")
        return

    salon_sel = st.selectbox("🏢 Selecciona la sede:", salones)
    hoy = datetime.today()

    col1, col2, col3 = st.columns([1, 1, 0.7])
    año_sel = col1.number_input("📅 Año", min_value=2023, max_value=2100, value=hoy.year)
    mes_sel = col2.selectbox("🗓️ Mes", options=list(range(1, 13)),
                             format_func=lambda x: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
                                                    "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][x - 1],
                             index=hoy.month - 1)
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

    # Mostrar tabla
    if "df_financista" in st.session_state and st.session_state.df_financista is not None:
        st.markdown("#### 🧾 Cuadro de horarios del personal")
        edited_df = st.data_editor(
            st.session_state.df_financista,
            num_rows="dynamic",
            use_container_width=True,
        )

        colg1, colg2 = st.columns([1, 1])
        with colg1:
            if st.button("💾 Guardar cambios", type="primary"):
                edited_df.to_csv(st.session_state.path_financista, index=False, encoding="utf-8-sig")
                st.session_state.df_financista = edited_df
                st.success("✅ Cambios guardados correctamente.")

        with colg2:
            if st.button("📈 Mostrar resumen"):
                resumen = calcular_resumen(st.session_state.df_financista)
                if not resumen.empty:
                    st.dataframe(resumen, use_container_width=True)
                    st.success(f"⏰ Total de horas trabajadas: {resumen['HORAS TOTALES'].sum()} hrs")
                else:
                    st.info("No hay datos suficientes para generar el resumen.")