import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DERBYsystem", page_icon="🐔", layout="centered")

# --- ESTILOS PERSONALIZADOS (Para mantener tu diseño) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2c3e50; color: white; }
    .rojo-text { color: #c00000; font-weight: bold; }
    .verde-text { color: #008000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PARA GENERAR EL PDF ---
def generar_pdf_cotejo(datos_r1, datos_r2):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    
    # Encabezado del reporte
    pdf.cell(190, 10, "DERBYsystem - REPORTE DE COTEJO", ln=True, align='C')
    pdf.ln(5)

    def dibujar_tabla(titulo, datos):
        pdf.set_font("helvetica", "B", 12)
        pdf.set_fill_color(44, 62, 80) 
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 8, titulo, ln=True, align='C', fill=True)
        
        # Encabezados de columnas
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "B", 8)
        headers = [("#", 10), ("ROJO", 45), ("AN.", 20), ("E", 10), ("DIF.", 20), ("AN.", 20), ("VERDE", 45), ("G", 20)]
        for col, ancho in headers:
            pdf.cell(ancho, 8, col, 1, 0, 'C')
        pdf.ln()

        # Filas de datos
        pdf.set_font("helvetica", "", 8)
        for d in datos:
            pdf.cell(10, 10, str(d['num']), 1, 0, 'C')
            
            # Nombre Rojo
            pdf.set_text_color(200, 0, 0)
            pdf.cell(45, 10, d['rojo'], 1, 0, 'C')
            pdf.set_text_color(0, 0, 0)
            
            # Anillo R (automático), Empate, Diferencia, Anillo V (automático)
            pdf.cell(20, 10, str(d['anillo_r']), 1, 0, 'C')
            pdf.cell(10, 10, "", 1, 0, 'C')
            pdf.cell(20, 10, str(d['dif']), 1, 0, 'C')
            pdf.cell(20, 10, str(d['anillo_v']), 1, 0, 'C')
            
            # Nombre Verde
            pdf.set_text_color(0, 128, 0)
            pdf.cell(45, 10, d['verde'], 1, 0, 'C')
            pdf.set_text_color(0, 0, 0)
            
            pdf.cell(20, 10, "", 1, 0, 'C')
            pdf.ln()
        pdf.ln(5)

    dibujar_tabla("RONDA 1", datos_r1)
    dibujar_tabla("RONDA 2", datos_r2)
    
    return pdf.output()

# --- INTERFAZ PRINCIPAL ---
st.title("🐔 DERBYsystem")

tab1, tab2 = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO"])

with tab2:
    st.markdown("### RONDA 1")
    # Aquí iría tu lógica actual de la tabla de Ronda 1
    # Ejemplo de datos para que el botón funcione:
    datos_r1 = [
        {"num": 1, "rojo": "HOMERO 1", "anillo_r": "001", "dif": "0.000", "anillo_v": "003", "verde": "HOMERO 2"},
        {"num": 2, "rojo": "HOMERO 3", "anillo_r": "005", "dif": "0.003", "anillo_v": "009", "verde": "HOMERO 5"}
    ]
    st.table(datos_r1)

    st.markdown("### RONDA 2")
    datos_r2 = [
        {"num": 1, "rojo": "HOMERO 5", "anillo_r": "010", "dif": "0.002", "anillo_v": "008", "verde": "HOMERO 4"}
    ]
    st.table(datos_r2)

    st.divider()

    # --- BOTÓN DE DESCARGA PDF ---
    pdf_bytes = generar_pdf_cotejo(datos_r1, datos_r2)
    
    st.download_button(
        label="📥 DESCARGAR COTEJO COMPLETO (PDF)",
        data=pdf_bytes,
        file_name="cotejo_derby.pdf",
        mime="application/pdf"
    )

st.info("Nota: Los números de anillo se generan automáticamente conforme al reglamento.")
