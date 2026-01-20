import streamlit as st

# Definimos el contenido en una variable
contenido_html = """
<div style="background-color: #E67E22; padding: 20px; border-radius: 15px; text-align: center;">
    <h3 style="color: white; margin-bottom: 0px;">BIENVENIDOS</h3>
    <h1 style="color: white; margin-top: 0px;">DERBYsystem</h1>
    
    <div style="background-color: #1E2630; color: white; padding: 20px; border-radius: 10px; text-align: left;">
        <b>DERBYsystem PRO</b> es una herramienta...<br>
        El sistema automatiza el registro...<br>
        Su función principal es el <b>sorteo</b>...<br>
        garantizando equidad y evitando errores.
        
        <p style="font-size: 0.85rem; margin-top: 15px; color: #ced4da;">
            Escribe una clave única para tu evento.
        </p>
    </div>
</div>
"""

# ESTA ES LA LÍNEA CLAVE:
st.markdown(contenido_html, unsafe_allow_html=True)

# Debajo puedes continuar con tus inputs normales de Streamlit
st.text_input("NOMBRE DEL EVENTO / CLAVE DE MESA:", placeholder="Ej: DERBY_FERIA_2026")
st.button("ENTRAR AL SISTEMA")
