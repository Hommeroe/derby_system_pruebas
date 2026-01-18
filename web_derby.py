import streamlit as st
from fpdf import FPDF

def exportar_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Título del PDF
    pdf.cell(190, 10, "DERBYsystem - Reporte de Cotejo", ln=True, align='C')
    pdf.ln(10)
    
    # Encabezados de tabla
    pdf.set_font("Arial", "B", 10)
    pdf.cell(10, 10, "#", 1)
    pdf.cell(40, 10, "ROJO", 1)
    pdf.cell(25, 10, "ANILLO", 1)
    pdf.cell(20, 10, "DIF.", 1)
    pdf.cell(25, 10, "ANILLO", 1)
    pdf.cell(40, 10, "VERDE", 1)
    pdf.ln()

    # Datos (Aquí recorres tu lista de peleas)
    pdf.set_font("Arial", "", 10)
    for fila in datos:
        pdf.cell(10, 10, str(fila['num']), 1)
        pdf.cell(40, 10, fila['rojo'], 1)
        pdf.cell(25, 10, str(fila['anillo_r']), 1)
        pdf.cell(20, 10, str(fila['dif']), 1)
        pdf.cell(25, 10, str(fila['anillo_v']), 1)
        pdf.cell(40, 10, fila['verde'], 1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1')

# --- En tu app de Streamlit ---
# Solo necesitas llamar a la función cuando se presione el botón
# (Asegúrate de pasarle los datos de tu tabla actual)

st.download_button(
    label="📄 Descargar Cotejo en PDF",
    data=exportar_pdf(tus_datos_aqui),
    file_name="cotejo_derby.pdf",
    mime="application/pdf"
)
