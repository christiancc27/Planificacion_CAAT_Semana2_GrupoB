import streamlit as st
import pandas as pd

st.set_page_config(page_title="CAAT - Herramienta de Auditoría", layout="centered")

# --- Título e instrucciones ---
st.title("🕵️‍♂️ CAAT - Herramienta de Auditoría Automatizada")
st.write("""
Esta herramienta permite detectar inconsistencias en pagos a partir de un archivo Excel.

**Instrucciones:**
1. Adjunta el archivo Excel (.xlsx) que deseas analizar.
2. Relaciona las columnas de tu archivo con las requeridas por el sistema.
3. Haz clic en "Ejecutar análisis" para ver los resultados.
""")

# --- Cargar archivo ---
archivo = st.file_uploader("📂 Subir archivo Excel", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)

    st.write("✅ Archivo cargado correctamente. Vista previa:")
    st.dataframe(df.head())

    # --- Selección de columnas ---
    columnas = df.columns.tolist()

    col_monto = st.selectbox("Columna de Monto", columnas)
    col_proveedor = st.selectbox("Columna de Proveedor", columnas)
    col_factura = st.selectbox("Columna de Nº Factura", columnas)
    col_fecha = st.selectbox("Columna de Fecha de Pago", columnas)
    col_estado = st.selectbox("Columna de Estado del Proveedor (opcional)", ["-- No usar --"] + columnas)

    if st.button("🚀 Ejecutar análisis"):
        resultados = {}

        # --- 1. Montos negativos ---
        negativos = df[df[col_monto] < 0]
        resultados["Montos negativos no autorizados"] = negativos

        # --- 2. Datos faltantes ---
        faltantes = df[df[[col_monto, col_proveedor, col_factura, col_fecha]].isnull().any(axis=1)]
        resultados["Datos faltantes o incompletos"] = faltantes

        # --- 3. Pagos duplicados ---
        duplicados = df[df.duplicated(subset=[col_proveedor, col_monto, col_factura, col_fecha], keep=False)]
        resultados["Pagos duplicados"] = duplicados

        # --- 4. Proveedores inactivos (solo si hay columna) ---
        if col_estado != "-- No usar --":
            inactivos = df[df[col_estado].astype(str).str.lower() != "activo"]
            resultados["Pagos a proveedores inactivos"] = inactivos
        else:
            st.info("ℹ No se analizó el estado de proveedores porque no se seleccionó esa columna.")

        # --- 5. Fechas fuera de rango ---
        try:
            df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
            fechas_fuera = df[~df[col_fecha].dt.year.isin([2025])]
            resultados["Fechas fuera del rango permitido"] = fechas_fuera
        except Exception as e:
            st.warning(f"No se pudo analizar las fechas: {e}")

        # --- Mostrar resultados ---
        st.subheader("📊 Resultados del análisis")
        for nombre, data in resultados.items():
            st.markdown(f"### {nombre} ({len(data)})")
            if not data.empty:
                st.dataframe(data)
            else:
                st.write("✅ No se encontraron problemas en esta categoría.")
