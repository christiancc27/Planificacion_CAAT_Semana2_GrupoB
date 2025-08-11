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

from pathlib import Path

# Mostrar README completo (Markdown)
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    st.markdown(content)  # no hace falta unsafe_allow_html en la mayoría de casos
else:
    st.info("No se encontró README.md en la carpeta del proyecto.")

uploaded_file = st.file_uploader("📤 Sube tu archivo Excel (.xlsx)", type=["xlsx"])

# ---------- Función de validaciones ----------
def ejecutar_validaciones(df):
    required = ["Proveedor", "Estado", "Fecha pago", "Monto", "Nº Factura"]
    resultados = {}

    # trabajamos sobre una copia
    df = df.copy()

    # conversiones seguras
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")
    df["Estado"] = df["Estado"].astype(str).str.strip().fillna("")
    df["Fecha pago"] = pd.to_datetime(df["Fecha pago"], errors="coerce")

    # 1. Montos negativos
    negativos = df[df["Monto"] < 0]
    resultados["Montos negativos"] = negativos

    # 2. Datos faltantes (en campos requeridos)
    faltantes = df[df[required].isnull().any(axis=1)]
    resultados["Datos faltantes o incompletos"] = faltantes

    # 3. Pagos duplicados (Proveedor + Monto + Nº Factura + Fecha)
    duplicados = df[df.duplicated(subset=["Proveedor", "Monto", "Nº Factura", "Fecha pago"], keep=False)]
    resultados["Pagos duplicados"] = duplicados

    # 4. Pagos a proveedores inactivos (todo lo que no sea 'activo' en minúsculas)
    inactivos = df[~df["Estado"].str.lower().eq("activo")]
    resultados["Pagos a proveedores inactivos"] = inactivos

    # 5. Fechas fuera de rango (2025)
    fecha_min = pd.Timestamp("2025-01-01")
    fecha_max = pd.Timestamp("2025-12-31")
    fuera_rango = df[df["Fecha pago"].notna() & ((df["Fecha pago"] < fecha_min) | (df["Fecha pago"] > fecha_max))]
    resultados["Fechas fuera del rango permitido"] = fuera_rango

    return resultados

# ---------- Helpers para mapeo automático ----------
def find_best_column(columns, keywords):
    """Devuelve la primera columna que contenga alguna de las keywords (case-insensitive)."""
    cols_lower = [str(c).lower() for c in columns]
    for kw in keywords:
        for i, c in enumerate(cols_lower):
            if kw in c:
                return columns[i]
    return None

if uploaded_file:
    try:
        df_original = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Error leyendo el archivo: {e}")
        st.stop()

    st.success("✅ Archivo cargado correctamente.")
    st.subheader("📊 Vista previa (primeras filas)")
    st.dataframe(df_original.head())

    st.markdown("---")
    st.subheader("🔗 Mapea las columnas de tu archivo a los campos requeridos")

    columnas_excel = [str(c) for c in df_original.columns]

    # sugerencias automáticas simples
    sugerencia_proveedor = find_best_column(columnas_excel, ["proveedor", "proveedores", "supplier", "vendor"])
    sugerencia_estado = find_best_column(columnas_excel, ["estado", "estado de proveedor", "status", "estado proveedor"])
    sugerencia_fecha = find_best_column(columnas_excel, ["fecha", "día", "dia", "pago", "fecha pago", "fecha_de_pago"])
    sugerencia_monto = find_best_column(columnas_excel, ["monto", "valor", "importe", "amount", "total"])
    sugerencia_factura = find_best_column(columnas_excel, ["factura", "#", "nº", "numero", "nro", "no factura"])

    # índices por defecto (si hubo sugerencia)
    def idx_or_zero(lst, val):
        return lst.index(val) if (val in lst) else 0

    col_proveedor = st.selectbox("Selecciona la columna para **Proveedor**", columnas_excel,
                                index=idx_or_zero(columnas_excel, sugerencia_proveedor))
    col_estado = st.selectbox("Selecciona la columna para **Estado**", columnas_excel,
                              index=idx_or_zero(columnas_excel, sugerencia_estado))
    col_fecha = st.selectbox("Selecciona la columna para **Fecha pago**", columnas_excel,
                             index=idx_or_zero(columnas_excel, sugerencia_fecha))
    col_monto = st.selectbox("Selecciona la columna para **Monto**", columnas_excel,
                             index=idx_or_zero(columnas_excel, sugerencia_monto))
    col_factura = st.selectbox("Selecciona la columna para **Nº Factura**", columnas_excel,
                               index=idx_or_zero(columnas_excel, sugerencia_factura))

    # Verificar que las selecciones sean únicas
    seleccionadas = [col_proveedor, col_estado, col_fecha, col_monto, col_factura]
    if len(set(seleccionadas)) < len(seleccionadas):
        st.warning("⚠️ Has seleccionado la misma columna para más de un campo. Por favor elige columnas diferentes.")
        st.stop()

    if st.button("Ejecutar validaciones"):
        # renombrar según el mapeo
        mapping = {
            col_proveedor: "Proveedor",
            col_estado: "Estado",
            col_fecha: "Fecha pago",
            col_monto: "Monto",
            col_factura: "Nº Factura"
        }
        df = df_original.rename(columns=mapping)

        # comprobar que las columnas renombradas existan (por seguridad)
        required = ["Proveedor", "Estado", "Fecha pago", "Monto", "Nº Factura"]
        missing = [r for r in required if r not in df.columns]
        if missing:
            st.error(f"Faltan las siguientes columnas tras el mapeo: {missing}")
            st.stop()

        # ejecutar validaciones
        resultados = ejecutar_validaciones(df)

        st.markdown("---")
        st.subheader("🔍 Resultados de las validaciones")
        for nombre, datos in resultados.items():
            with st.expander(f"📌 {nombre} ({len(datos)} registros encontrados)"):
                if not datos.empty:
                    st.dataframe(datos)
                else:
                    st.success("Sin inconsistencias detectadas.")
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
