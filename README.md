# 🕵️‍♂️ CAAT - Herramienta de Auditoría Automatizada

Este proyecto es una herramienta de auditoría desarrollada en **Python** y **Streamlit**, diseñada para detectar inconsistencias comunes en bases de datos financieras cargadas en formato **Excel**. Es un ejemplo básico de un **CAAT (Computer-Assisted Audit Tool)** que puede usarse para análisis preliminares de pagos.

## 🎯 Funcionalidades

Al subir un archivo `.xlsx`, el sistema detecta las siguientes inconsistencias:

1. **Montos negativos no autorizados**  
   Pagos con valores negativos que podrían representar errores o fraudes.

2. **Datos faltantes o incompletos**  
   Registros que tienen celdas vacías en columnas clave.

3. **Pagos duplicados**  
   Registros repetidos considerando campos como Proveedor, Monto, Nº Factura y Fecha.

4. **Pagos a proveedores inactivos**  
   Detecta si el estado del proveedor es distinto de "Activo".

5. **Fechas fuera del rango permitido**  
   Validación de que las fechas de pago estén dentro del año 2025.

---

## 📁 Requisitos

Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
