import streamlit as st

# 1. Configuración de la página
st.set_page_config(page_title="DERBYsystem PRO", page_icon="🏆", layout="centered")

# 2. Estilos CSS personalizados para centrar y dar color a los elementos de Streamlit
st.markdown("""
    <style>
    /* Centrar etiquetas y campos de entrada */
    .stTextInput {
        text-align: center;
        max-width: 500px;
        margin: 0 auto;
    }
    
    /* Centrar y dar color naranja al botón */
    div.stButton > button {
        display: block;
        margin: 0 auto;
        width: 100%;
        max-width: 500px;
        background-color: #E67E22;
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
    }
    
    div.stButton > button:hover {
        background-color: #D35400;
        color: white;
    }

    /* Estilo para que el texto de la etiqueta sea blanco */
    .stTextInput label {
        color: white !important;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Estructura visual con HTML (Renderizado correctamente)
# El secreto está en usar unsafe_allow_html=True
html_header = """
<div style="background-color: #E67E22; padding: 30px; border-radius: 15px; text-align: center; font-family: sans-serif; color: white;">
    <h3 style="margin-bottom: 0px; letter-spacing: 2px;">BIENVENIDOS</h3>
    <h1 style="margin-top: 0px; font-size: 3rem; font-weight: bold;">DERBYsystem</h1>
    
    <div style="background-color: #D35400; padding: 25px; border-radius: 12px; text-align: center; max-width: 500px; margin: 20px auto;">
        <h4 style="margin-top: 0;">¿Qué es este sistema?</h4>
        <p style="font-size: 1.05rem; line-height: 1.6;">
            <b>DERBYsystem PRO</b> es una plataforma profesional diseñada para optimizar eventos de competencia. 
            El sistema <b>automatiza el registro</b> y asegura transparencia absoluta mediante un <b>sorteo digital</b>.
        </p>
        <p style="font-size: 1.05rem; line-height: 1.6;">
            Garantizamos equidad total, eliminando errores manuales y facilitando el control de mesa en tiempo real.
        </p>
        <p style="font-size: 0.85rem; margin-top: 15px; color: #FAD7A0;">
            Ingresa la clave de tu evento para comenzar.
        </p>
    </div>
</div>
<br>
"""

# Renderizamos el HTML
st.markdown(html_header, unsafe_allow_html=True)

# 4. Inputs de la aplicación (Centrados)
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    clave_evento = st.text_input("NOMBRE DEL EVENTO / CLAVE DE MESA:", placeholder="Ej: DERBY_FERIA_2026")
    st.write("") # Espacio
    if st.button("ENTRAR AL SISTEMA"):
        if clave_evento:
            st.success(f"Accediendo a: {clave_evento}")
        else:
            st.error("Por favor, ingresa una clave.")
