import os
import pandas as pd
import streamlit as st
from datetime import date

def obtener_rango_quincena(año, mes, quincena):
    if quincena == "Q1":
        inicio = date(año, mes, 1)
        fin = date(año, mes, 15)
    else:
        if mes == 12:
            fin = date(año, 12, 31)
        else:
            siguiente = date(año, mes + 1, 1)
            fin = siguiente.replace(day=1) - pd.Timedelta(days=1)
        inicio = date(año, mes, 16)
    return pd.date_range(inicio, fin)


def run_subir_horarios():
    st.title("📤 Subir o editar horario quincenal")

    col1, col2, col3 = st.columns(3)
    with col1:
        año = st.number_input("Año", min_value=2024, max_value=2030, value=date.today().year)
    with col2:
        meses_nombres = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        mes_nombre = st.selectbox("Mes", meses_nombres, index=date.today().month - 1)
        mes = meses_nombres.index(mes_nombre) + 1
    with col3:
        quincena = st.radio("Quincena", ["Q1 (1–15)", "Q2 (16–fin)"], horizontal=True)

    q = "Q1" if "Q1" in quincena else "Q2"

    carpeta = os.path.join("data", "uploads", "fm_bellavista")
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = f"FM_BELLAVISTA_{año}-{mes:02d}-{q}.csv"
    ruta_archivo = os.path.join(carpeta, nombre_archivo)

    fechas = obtener_rango_quincena(año, mes, q)
    columnas = ["DNI", "NOMBRE Y APELLIDO", "ÁREA"] + [f.strftime("%d/%m/%Y") for f in fechas]

    if os.path.exists(ruta_archivo):
        df = pd.read_csv(ruta_archivo, dtype=str)
        st.success(f"✅ Archivo cargado: {nombre_archivo}")
    else:
        df = pd.DataFrame(columns=columnas)
        st.info("📄 No existe horario previo, se creará uno nuevo al guardar.")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_bellavista"
    )

    if st.button("💾 Guardar cambios", key="guardar_bellavista"):
        edited_df.to_csv(ruta_archivo, index=False, encoding="utf-8-sig")
        st.success(f"Horario guardado correctamente como **{nombre_archivo}**")

    st.info("💡 Este módulo es solo para subir y editar horarios.")
