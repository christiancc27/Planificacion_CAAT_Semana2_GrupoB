import streamlit as st
import pandas as pd

st.set_page_config(page_title="CAAT Auditor", layout="wide")

st.title("🕵️‍♂️ CAAT - Herramienta de Auditoría Automatizada")

st.markdown("""
### 🔎 Funciones de auditoría disponibles

1. **Montos negativos:** detecta pagos con valores negativos que pueden ser errores contables o posibles fraudes.
2. **Datos faltantes o incompletos:** identifica registros que no tienen toda la información necesaria.
3. **Pagos duplicados:** encuentra transacciones repetidas en la base de datos.
4. **Pagos a proveedores inactivos:** verifica si se realizaron pagos a proveedores cuyo estado no es "Activo".
5. **Fechas fuera del rango permitido:** comprueba si las fechas de pago están fuera del período fiscal permitido (año 2025).
""")

# Subida de archivo
uploaded_file = st.file_uploader("📤 Sube tu archivo Excel (.xlsx)", type=["xlsx"])

# Función de validaciones
def ejecutar_validaciones(df):
    resultados = {}

    # 1. Montos negativos no autorizados
    negativos = df[df["Monto"] < 0]
    resultados["Montos negativos"] = negativos

    # 2. Datos faltantes
    faltantes = df[df.isnull().any(axis=1)]
    resultados["Datos faltantes o incompletos"] = faltantes

    # 3. Pagos duplicados (basado en Proveedor + Monto + Nº Factura + Fecha)
    duplicados = df[df.duplicated(subset=["Proveedor", "Monto", "Nº Factura", "Fecha pago"], keep=False)]
    resultados["Pagos duplicados"] = duplicados

    # 4. Pagos a proveedores inactivos
    inactivos = df[df["Estado"].str.lower() != "activo"]
    resultados["Pagos a proveedores inactivos"] = inactivos

    # 5. Fechas fuera de rango
    df["Fecha pago"] = pd.to_datetime(df["Fecha pago"], errors="coerce")
    fecha_min = pd.to_datetime("2025-01-01")
    fecha_max = pd.to_datetime("2025-12-31")
    fuera_rango = df[(df["Fecha pago"] < fecha_min) | (df["Fecha pago"] > fecha_max)]
    resultados["Fechas fuera del rango permitido"] = fuera_rango

    return resultados

# Procesamiento si se sube archivo
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Archivo cargado correctamente.")

        st.subheader("📊 Vista previa de los datos")
        st.dataframe(df)

        st.markdown("---")
        st.subheader("🔍 Resultados de las validaciones")

        resultados = ejecutar_validaciones(df)

        for nombre, datos in resultados.items():
            with st.expander(f"📌 {nombre} ({len(datos)} registros encontrados)"):
                if not datos.empty:
                    st.dataframe(datos)
                else:
                    st.success("Sin inconsistencias detectadas.")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
