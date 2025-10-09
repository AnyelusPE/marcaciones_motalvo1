import streamlit as st
import pandas as pd
import os

def run_trujillo_mall():
    st.title("📋 Trujillo Mall — Horarios Quincenales")

    ruta = "data/uploads/TRUJILLO_MALL.csv"

    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
    else:
        df = pd.DataFrame(columns=["DNI", "NOMBRE Y APELLIDO", "ÁREA", "01/10/2025", "02/10/2025"])

    st.data_editor(df, num_rows="dynamic", key="tabla_horarios")

    if st.button("💾 Guardar cambios"):
        df.to_csv(ruta, index=False, encoding="utf-8-sig")
        st.success("✅ Cambios guardados correctamente.")
