import streamlit as st
import pandas as pd
import os
import uuid
import re
from datetime import datetime
import pytz  
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

# --- PANTALLA DE ENTRADA ---
if st.session_state.id_usuario == "":
    html_bienvenida = (
        "<div style='text-align:center; background-color:#E67E22; padding:25px; border-radius:15px; color:white; font-family:sans-serif;'>"
        "<div style='font-size:1.1rem; letter-spacing:2px; margin-bottom:5px;'>BIENVENIDOS A</div>"
        "<div style='font-size:2.2rem; font-weight:900; line-height:1; margin-bottom:20px;'>DerbySystem</div>"
        "<div style='background-color:#1a1a1a; padding:20px; border-radius:12px; margin:0 auto; max-width:500px; border:1px solid #D35400; text-align:left;'>"
        "<div style='color:#E67E22; font-weight:bold; font-size:1.2rem; margin-bottom:10px; text-align:center;'>¿Qué es este sistema?</div>"
        "<div style='color:#f2f2f2; font-size:0.95rem; line-height:1.5; text-align:center;'>"
        "Plataforma de <b>sorteo digital.</b> Garantiza transparencia total, orden y combates gallisticos 100% justos mediante tecnología de emparejamiento inteligente."
        "</div>"
        "<hr style='border:0.5px solid #333; margin:15px 0;'>"
        "<div style='font-size:0.85rem; color:#E67E22; font-style:italic; text-align:center;'>Introduce tu clave de mesa para acceder al panel de control.</div>"
        "</div></div>"
    )
    
    st.markdown(html_bienvenida, unsafe_allow_html=True)
    st.write("") 
    
    col_a, col_b, col_c = st.columns([0.05, 0.9, 0.05])
    with col_b:
        # CAMBIO: type="password" para que nadie vea la clave al escribirla
        nombre_acceso = st.text_input("CLAVE DE ACCESO A MESA:", placeholder="••••••••", type="password").upper().strip()
        
        if st.button("ENTRAR AL SISTEMA", use_container_width=True):
            if nombre_acceso:
                st.session_state.id_usuario = nombre_acceso
                st.rerun()
            else:
                st.warning("⚠️ Se requiere la clave de acceso.")
    st.stop()

# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS DE INTERFAZ ---
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #E67E22 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
    }
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400;
        font-size: 0.8em;
    }
    .header-azul { 
        background-color: #1a1a1a; color: #E67E22; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 14px; margin-bottom: 5px; border-bottom: 2px solid #E67E22;
    }
    .tabla-final { 
        width: 100%; border-collapse: collapse; background-color: white; 
        table-layout: fixed; color: black !important;
    }
    .tabla-final td, .tabla-final th { 
        border: 1px solid #bdc3c7; text-align: center; 
        padding: 5px 2px; height: auto; color: black !important;
    }
    .nombre-partido { 
        font-weight: bold; font-size: 10px; line-height: 1.2;
        white-space: normal; word-wrap: break-word;
        display: block; width: 100%; color: black !important;
    }
    .peso-texto { font-size: 10px; color: #2c3e50 !important; display: block; margin-top: 2px;}
    </style>
""", unsafe_allow_html=True)

# (Aquí irían tus funciones cargar, guardar, limpiar_nombre_socio y generar_pdf intactas)
def limpiar_nombre_socio(n): return re.sub(r'\s*\d+$', '', n).strip().upper()
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

# --- TÍTULO SEGURO (SIN CLAVE EXPUESTA) ---
st.title("🏆 MESA DE CONTROL")
st.markdown(f"<p style='color:gray; font-size:10px; margin-top:-20px;'>SISTEMA OPERATIVO | ID-SESSION: {st.session_state.id_usuario[:3]}***</p>", unsafe_allow_html=True)

t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO", "📑 PROTOCOLO"])

with t_reg:
    # (Todo el código de tu formulario de registro se mantiene igual aquí)
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Añadir Partido # {len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        for i in range(g_sel):
            p_val = st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True)
            st.write("") 
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

# (El resto de tus pestañas de COTEJO y PROTOCOLO siguen exactamente igual)

with st.sidebar:
    # Clave en letras muy pequeñas y botón de salida
    st.markdown(f"<small style='color:gray;'>Sesión: {st.session_state.id_usuario}</small>", unsafe_allow_html=True)
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
        st.session_state.id_usuario = ""; st.rerun()
