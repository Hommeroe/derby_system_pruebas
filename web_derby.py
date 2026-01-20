import streamlit as st
import pandas as pd
import os
import uuid
import re
from io import BytesIO

# Importamos reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- LÓGICA DE ACCESO SEGURO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- ESTILOS PARA ELIMINAR EL CUADRO BLANCO Y CORREGIR EL DISEÑO ---
st.markdown("""
    <style>
    /* 1. ELIMINA EL FONDO BLANCO DE TODA LA APP */
    .stApp, .main, .block-container, [data-testid="stAppViewContainer"] {
        background-color: #0e1117 !important; /* Color oscuro profundo */
    }
    
    /* 2. OCULTA ELEMENTOS SOBRANTES */
    header, footer, #MainMenu {visibility: hidden !important;}
    
    /* 3. CONTENEDOR DE BIENVENIDA RESPONSIVO */
    .login-card {
        background-color: #2c3e50;
        padding: 30px 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        width: 100%;
        max-width: 450px;
        margin: 0 auto;
        text-align: center;
        color: white;
    }
    
    /* 4. TÍTULO DIGITAL SIN CORTES */
    .digital-title {
        font-family: 'Courier New', Courier, monospace;
        font-size: clamp(22px, 8vw, 38px); /* Tamaño que se ajusta al ancho del celular */
        font-weight: bold;
        letter-spacing: 2px;
        color: #ffffff;
        margin: 15px 0;
        white-space: nowrap;
    }
    
    .security-box {
        font-size: 13px;
        background-color: rgba(0,0,0,0.3);
        padding: 15px;
        border-radius: 10px;
        line-height: 1.4;
        border-left: 5px solid #e74c3c;
        text-align: left;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Pantalla de entrada Profesional
if st.session_state.id_usuario == "":
    st.markdown("""
        <div style="padding-top: 20px;">
            <div class="login-card">
                <h2 style='margin:0; font-size: 18px; opacity: 0.8;'>BIENVENIDO A</h2>
                <div class="digital-title">DERBYsystem</div>
                <p style="font-size: 15px; opacity: 0.9;">Escribe una clave única para tu evento.</p>
                <div class="security-box">
                    <strong>SEGURIDAD:</strong> Esta clave es tu llave privada. 
                    Evita nombres comunes. Si alguien más la usa, podrá ver tus datos. 
                    Usa una clave compleja para proteger tus registros.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Espacio
    
    # Input y Botón centrados
    col1, col2, col3 = st.columns([0.05, 0.9, 0.05])
    with col2:
        nombre_acceso = st.text_input("NOMBRE DEL EVENTO / CLAVE DE MESA:", placeholder="").upper().strip()
        if st.button("ENTRAR AL SISTEMA", use_container_width=True):
            if nombre_acceso:
                st.session_state.id_usuario = nombre_acceso
                st.rerun()
            else:
                st.error("⚠️ Debes ingresar una clave.")
    st.stop()

# --- EL RESTO DEL CÓDIGO PERMANECE FIJO (DISEÑO Y ANILLOS AUTOMÁTICOS) ---
# [cite: 2026-01-17, 2026-01-14]

DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

st.markdown("""
    <style>
    .caja-anillo {
        background-color: #2c3e50; color: white; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #34495e;
        font-size: 0.8em;
    }
    .header-azul { 
        background-color: #2c3e50; color: white; padding: 8px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 12px; margin-bottom: 5px;
    }
    .tabla-final { 
        width: 100%; border-collapse: collapse; background-color: white; 
        table-layout: fixed; color: black !important;
    }
    .tabla-final td, .tabla-final th { 
        border: 1px solid #bdc3c7; text-align: center; 
        padding: 2px; height: 38px; color: black !important;
    }
    .nombre-partido { 
        font-weight: bold; font-size: 10px; line-height: 1;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
        display: block; width: 100%; color: black !important;
    }
    .peso-texto { font-size: 10px; color: #2c3e50 !important; display: block; }
    .cuadro { font-size: 11px; font-weight: bold; color: black !important; }
    
    .col-num { width: 20px; }
    .col-g { width: 22px; }
    .col-an { width: 32px; }
    .col-e { width: 22px; background-color: #f1f2f6; }
    .col-dif { width: 42px; }
    .col-partido { width: auto; }
    div[data-testid="stNumberInput"] { margin-bottom: 0px; }
    </style>
""", unsafe_allow_html=True)

# Lógica de carga/guardado y funciones PDF omitidas por brevedad (se mantienen igual que en versiones anteriores)
def limpiar_nombre_socio(n):
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

if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title(f"DERBYsystem - {st.session_state.id_usuario}")
t_reg, t_cot = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO"])

# (Aquí va el resto de la lógica de registro y cotejo que ya tienes funcionando correctamente)
