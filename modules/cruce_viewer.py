import os
import re
import io
import streamlit as st
import pandas as pd
from modules.cruce_calculador import leer_biometrico, leer_horario
from modules.cruce_tardanzas import calcula_cruce_tardanzas


# ----------------------------------------------------
# LIMPIA NOMBRES Y MAPEA ARCHIVOS DE HORARIOS
# ----------------------------------------------------
def listar_y_mapear_archivos_horario(ruta_horarios):
    """
    Escanea ruta_horarios y devuelve:
      - lista de salones limpios
      - mapa salon -> ruta archivo correspondiente
    Maneja nombres con corchetes, comillas y otros caracteres raros.
    """
    archivos = [
        f for f in os.listdir(ruta_horarios)
        if "formato" in f.lower() and f.lower().endswith((".csv", ".xlsx"))
    ]

    salones = []
    mapa = {}

    for f in archivos:
        base = os.path.splitext(f)[0]

        # quitar "_formato" o " formato"
        base = re.sub(r'[_\s]*formato$', '', base, flags=re.IGNORECASE).strip()

        # quitar corchetes y comillas externas
        base = base.strip('[]\'" ')

        # separar por comas si es lista dentro de string
        posibles = [s.strip(' "\'') for s in re.split(r',\s*', base) if s.strip()]
        for salon in posibles:
            if salon not in mapa:
                mapa[salon] = os.path.join(ruta_horarios, f)
                salones.append(salon)

    return salones, mapa


# ----------------------------------------------------
# MOSTRAR CRUCE CONSOLIDADO
# ----------------------------------------------------
def mostrar_cruce(usuario):
    st.title("📊 Cruce Biométrico y Malla Horaria")
    st.subheader(f"Cruce de Asistencia - {usuario['usuario'].upper()}")

    ruta_horarios = os.path.join("data", "uploads")

    # obtener salones y mapa archivo -> ruta
    salones_disponibles, mapa_archivos = listar_y_mapear_archivos_horario(ruta_horarios)

    if not salones_disponibles:
        st.warning("⚠️ No hay archivos de horarios subidos por los salones todavía.")
        return

    st.markdown("### 🏢 Selecciona los salones a procesar:")
    cols = st.columns(3)
    salones_seleccionados = [
        s for i, s in enumerate(salones_disponibles) if cols[i % 3].checkbox(s, value=True)
    ]

    st.markdown("### 📂 Sube el archivo del biométrico general")
    file_bio = st.file_uploader("Arrastra o selecciona el archivo biométrico", type=["xls", "xlsx", "csv"])

    if st.button("🚀 Procesar Cruce Consolidado", use_container_width=True):
        if not file_bio:
            st.warning("⚠️ Debes subir el archivo del biométrico general.")
            return

        try:
            df_bio = leer_biometrico(file_bio)
            all_results = []

            for salon in salones_seleccionados:
                archivo_horario = mapa_archivos.get(salon)
                if not archivo_horario or not os.path.exists(archivo_horario):
                    st.warning(f"⚠️ No se encontró el archivo de horario para {salon}.")
                    continue

                df_hor = leer_horario(archivo_horario)
                df_resultado = calcula_cruce_tardanzas(df_bio, df_hor)
                df_resultado["salon"] = salon
                all_results.append(df_resultado)

            if not all_results:
                st.error("❌ No se generó ningún resultado válido.")
                return

            df_final = pd.concat(all_results, ignore_index=True)

            st.success(f"✅ Cruce consolidado completado correctamente ({len(salones_seleccionados)} salones).")
            st.dataframe(df_final, use_container_width=True)

            # descarga en Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_final.to_excel(writer, index=False, sheet_name="Cruce Consolidado")
            buffer.seek(0)

            st.download_button(
                label="📥 Descargar Cruce Consolidado",
                data=buffer,
                file_name="Cruce_Consolidado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"❌ Error durante el procesamiento: {e}")