import pandas as pd
import streamlit as st
import os

def mostrar_editor(nombre_salon):
    path = f"data/uploads/{nombre_salon}_formato.csv"

    # Fechas base (como en tu Excel)
    fechas = pd.date_range("2025-09-01", "2025-09-15").strftime("%d/%m/%Y").tolist()

    # Columnas fijas + fechas
    columnas = ["#", "DNI", "NOMBRE Y APELLIDO", "ÁREA"] + fechas

    # Si no existe el CSV, creamos la plantilla vacía
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columnas)
        df.to_csv(path, index=False)
    else:
        df = pd.read_csv(path)

    st.markdown(f"### 📋 Formato de Asistencia - {nombre_salon}")

    # Permitir edición con número variable de filas
    df_editable = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key=f"editor_{nombre_salon}",
        hide_index=True
    )

    # Botón para guardar cambios
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Guardar Cambios", key=f"save_{nombre_salon}"):
            df_editable.to_csv(path, index=False)
            st.success("Formato guardado correctamente ✅")

    # Mostrar vista previa (opcional)
    with col2:
        if st.checkbox("👁️ Ver vista previa del CSV guardado"):
            st.dataframe(df_editable)