import streamlit as st

# 1. Configuración de la página (opcional pero recomendada)
st.set_page_config(page_title="DERBYsystem PRO", page_icon="🏆")

# 2. Estilo CSS para centrar los elementos nativos de Streamlit (input y botón)
st.markdown("""
    <style>
    /* Centrar etiquetas de texto de Streamlit */
    .stTextInput label {
        display: flex;
        justify-content: center;
        width: 100%;
        color: white !important;
    }
    /* Ajustar el ancho de los inputs y botones y centrarlos */
    .stTextInput, .stButton {
        max-width: 500px;
        margin: 0 auto;
    }
    /* Estilo para el botón */
    div.stButton > button {
        background-color: #E67E22;
        color: white;
        border: 2px solid #D35400;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #D35400;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Diseño del encabezado y cuadro de explicación
# Se cambió el cuadro azul a un naranja oscuro (#D35400) y se centró el texto
contenido_html = """
<div style="background-color: #E67E22; padding: 30px; border-radius: 15px; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <h3 style="color: white; margin-bottom: 5px; letter-spacing: 2px; font-weight: 300;">BIENVENIDOS</h3>
    <h1 style="color: white; margin-top: 0px; font-size: 2.8rem; font-weight: bold;">DERBYsystem</h1>
    
    <div style="background-color: #D35400; color: white; padding: 25px; border-radius: 12px; text-align: center; max-width: 550px; margin: 20px auto; border: 1px solid rgba(255,255,255,0.2);">
        <h4 style="margin-top: 0;">¿Qué es DERBYsystem?</h4>
        <p style="font-size: 1.05rem; line-height: 1.5;">
            <b>DERBYsystem PRO</b> es una plataforma integral diseñada para la gestión profesional de eventos de competencia. 
            El sistema <b>automatiza el registro</b> de participantes y asegura la transparencia total mediante un motor de <b>sorteo digital</b>.
        </p>
        <p style="font-size: 1.05rem; line-height: 1.5;">
            Nuestra tecnología garantiza que cada encuentro sea <b>justo y equitativo</b>, eliminando errores manuales y facilitando el control de mesa en tiempo real.
        </p>
        
        <p style="font-size: 0.85rem; margin-top: 20px; color: #FAD7A0; font-style: italic;">
            Ingresa la clave de tu evento para comenzar.
        </p>
    </div>
</div>
<br>
"""

# Renderizar el HTML
st.markdown(contenido_html, unsafe_allow_html=True)

# 4. Formulario de entrada centrado usando columnas
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    nombre_evento = st.text_input("NOMBRE DEL EVENTO / CLAVE DE MESA:", placeholder="Ej: DERBY_FERIA_2026")
    
    # Nota: El anillo se genera automático según tus preferencias guardadas
    if st.button("ENTRAR AL SISTEMA"):
        if nombre_evento:
            st.success(f"Accediendo a la mesa: {nombre_evento}")
        else:
            st.warning("Por favor, introduce una clave válida.")
