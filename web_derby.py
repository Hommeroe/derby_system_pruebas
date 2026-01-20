import streamlit as st
import pandas as pd
import os
import re
from io import BytesIO

# Importamos reportlab para los PDFs
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- LÓGICA DE ACCESO SEGURO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- PANTALLA DE ENTRADA (DISEÑO REPARADO) ---
if st.session_state.id_usuario == "":
    # Definimos el HTML en una sola línea de texto para evitar errores de procesamiento
    html_header = (
        "<div style='text-align:center;background-color:#E67E22;padding:25px;border-radius:15px;color:white;font-family:sans-serif;'>"
        "<div style='font-size:1.1rem;letter-spacing:2px;margin-bottom:5px;'>BIENVENIDOS A</div>"
        "<div style='font-size:2.2rem;font-weight:900;line-height:1;'>DERBYsystem</div>"
        "<div style='background-color:#1a1a1a;padding:20px;border-radius:12px;margin:20px auto;max-width:500px;border:1px solid #D35400;'>"
        "<div style='color:#E67E22;font-weight:bold;font-size:1.2rem;margin-bottom:10px;'>¿Qué es este sistema?</div>"
        "<div style='color:#f2f2f2;font-size:0.95rem;line-height:1.4;'>"
        "Es una plataforma profesional que <b>automatiza el pesaje</b> y asegura transparencia absoluta mediante un <b>sorteo digital</b> avanzado."
        "</div><br>"
        "<div style='color:#f2f2f2;font-size:0.95rem;line-height:1.4;'>"
        "Garantiza combates <b>justos y equitativos</b>, eliminando errores manuales y facilitando el control de mesa."
        "</div>"
        "<hr style='border:0.5px solid #333;margin:15px 0;'>"
        "<div style='font-size:0.85rem;color:#E67E22;font-style:italic;'>Escribe la clave única de tu evento para ingresar.</div>"
        "</div></div>"
    )
    
    st.markdown(html_header, unsafe_allow_html=True)
    st.write("") # Espacio visual
    
    col_a, col_b, col_c = st.columns([0.05, 0.9, 0.05])
    with col_b:
        nombre_acceso = st.text_input("NOMBRE DEL EVENTO / CLAVE DE MESA:", placeholder="Ingresa tu clave aquí").upper().strip()
        if st.button("ENTRAR AL SISTEMA", use_container_width=True):
            if nombre_acceso:
                st.session_state.id_usuario = nombre_acceso
                st.rerun()
            else:
                st.warning("⚠️ Por favor, ingresa una clave.")
    st.stop()

# --- LÓGICA DE DATOS ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS DE TABLAS Y BOTONES ---
st.markdown("""
    <style>
    .header-seccion { 
        background-color: #1a1a1a; color: #E67E22; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 14px; margin-bottom: 5px; border-bottom: 2px solid #E67E22;
    }
    div.stButton > button {
        background-color: #E67E22 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES AUXILIARES ---
def limpiar_nombre(n):
    return re.sub(r'\s*\d+$', '', n).strip().upper()

def cargar():
    partidos, n_gallos = [], 2
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    n_gallos = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, n_gallos + 1): d[f"G{i}"] = float(p[i])
                    partidos.append(d)
    return partidos, n_gallos

def guardar(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [f"{v:.3f}" for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- INTERFAZ PRINCIPAL ---
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title(f"🏆 {st.session_state.id_usuario}")
tab1, tab2 = st.tabs(["📝 REGISTRO", "📊 COTEJO"])

with tab1:
    col_1, col_2 = st.columns([2,1])
    n_gallos = col_2.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2)
    st.session_state.n_gallos = n_gallos
    
    with st.form("registro_partido", clear_on_submit=True):
        nombre_p = st.text_input("NOMBRE DEL PARTIDO:").upper()
        pesos = []
        for i in range(n_gallos):
            pesos.append(st.number_input(f"Peso G{i+1}", 1.80, 2.60, 2.20, 0.001, format="%.3f"))
        
        if st.form_submit_button("💾 GUARDAR PARTIDO"):
            if nombre_p:
                nuevo = {"PARTIDO": nombre_p}
                for idx, peso in enumerate(pesos): nuevo[f"G{idx+1}"] = peso
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.success("Guardado.")
                st.rerun()

with tab2:
    if len(st.session_state.partidos) < 2:
        st.info("Necesitas al menos 2 partidos para el cotejo.")
    else:
        st.write("Sistema de cotejo listo.")
        # Aquí continúa tu lógica de cotejo...

with st.sidebar:
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.id_usuario = ""
        st.rerun()
