import streamlit as st
import pandas as pd
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURACIÓN DE USUARIOS (Ejemplo para control de renta) ---
# En el futuro, esto se lee de una base de datos protegida
USUARIOS = {
    "galpon_azteca": "clave123",
    "derby_nacional": "pavo2026",
    "homero_admin": "admin77"
}

def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("### 🔑 Acceso al Sistema DerbySystem PRO")
        user = st.text_input("Usuario (ID de Gallera)").lower().strip()
        pw = st.text_input("Contraseña", type="password")
        
        if st.button("Entrar al Sistema", use_container_width=True):
            if user in USUARIOS and USUARIOS[user] == pw:
                st.session_state.autenticado = True
                st.session_state.usuario_id = user
                st.rerun()
            else:
                st.error("Credenciales incorrectas o cuenta vencida.")
        return False
    return True

# --- INICIO DEL PROGRAMA ---
if login():
    # El nombre del archivo ahora es único por usuario para que no se mezclen
    USER_DB = f"datos_{st.session_state.usuario_id}.txt"
    
    st.sidebar.title(f"👤 {st.session_state.usuario_id.upper()}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # --- AQUÍ CONTINÚA TU LÓGICA DE CARGAR/GUARDAR USANDO 'USER_DB' ---
    # (El resto del código de registro y PDF permanece igual, 
    # solo asegúrate de que DB_FILE use USER_DB)
    
    st.title(f"🏆 Panel de Control: {st.session_state.usuario_id.upper()}")
    # ... Resto del código ...
