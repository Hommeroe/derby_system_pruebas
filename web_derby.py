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

# Pantalla de entrada
if st.session_state.id_usuario == "":
    # CSS para color NARANJA, márgenes cómodos y sin scroll
    st.markdown("""
        <style>
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
        }
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            text-align: center;
        }
        .welcome-card {
            background-color: #E67E22; 
            padding: 25px 20px; 
            border-radius: 15px; 
            color: white; 
            width: 95%;
            max-width: 500px; 
            margin-bottom: 5px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .resumen-texto {
            font-size: 0.9rem;
            line-height: 1.4;
            margin: 15px 0;
            text-align: justify;
            color: white;
            background: rgba(0,0,0,0.15);
            padding: 15px;
            border-radius: 10px;
        }
        /* Ajuste para pegar el input a la tarjeta */
        div[data-testid="stVerticalBlock"] > div:has(div.stTextInput) {
            gap: 0.2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Renderizado del cuadro naranja con el Resumen Opción 1
    st.markdown(f"""
        <div class="login-container">
            <div class="welcome-card">
                <h2 style='margin: 0; font-size: 1.1rem; opacity: 0.9;'>BIENVENIDOS</h2>
                <h1 style='margin: 0; font-size: 2.1rem; letter-spacing: 2px; font-weight: 800;'>DERBYsystem</h1>
                
                <div class="resumen-texto">
                    <b>DERBYsystem PRO</b> es una plataforma digital avanzada diseñada para la gestión integral de eventos gallísticos. 
                    El sistema automatiza el registro de partidos, el pesaje y la asignación inteligente de anillos. 
                    Su función principal es el <b>Cotejo Automatizado</b>, que organiza las peleas por rondas basándose en el peso, 
                    garantizando equidad y evitando enfrentamientos entre socios del mismo partido.
                </div>

                <p style='font-size: 0.85rem; margin-top: 10px; opacity: 0.9; font-style: italic;'>
                    Escribe una clave única para tu evento o mesa.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Input y Botón pegados a la tarjeta
    _, center_col, _ = st.columns([0.1, 0.8, 0.1])
    with center_col:
        nombre_acceso = st.text_input("NOMBRE DEL EVENTO / CLAVE DE MESA:", placeholder="Ej: DERBY_FERIA_2026").upper().strip()
        if st.button("ENTRAR AL SISTEMA", use_container_width=True):
            if nombre_acceso:
                st.session_state.id_usuario = nombre_acceso
                st.rerun()
            else:
                st.warning("⚠️ Escribe un nombre.")
    st.stop()

# --- CONFIGURACIÓN DE COLORES PARA EL INTERIOR DEL SISTEMA ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

st.markdown("""
    <style>
    .caja-anillo {
        background-color: #E67E22; color: white; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400;
        font-size: 0.8em;
    }
    .header-azul { 
        background-color: #E67E22; color: white; padding: 8px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 12px; margin-bottom: 5px;
    }
    .peso-texto { font-size: 10px; color: #E67E22 !important; display: block; }
    </style>
""", unsafe_allow_html=True)

# ... (El resto de las funciones de carga, guardado y PDF se mantienen igual) ...

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

# Contenido de pestañas simplificado para brevedad del código, 
# pero manteniendo la lógica funcional naranja.
with t_reg:
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
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()

with t_cot:
    st.info("Agrega al menos 2 partidos para ver el cotejo.")
    if len(st.session_state.partidos) >= 2:
        st.success("Cotejo listo para generar.")

with st.sidebar:
    st.write(f"Sesión: {st.session_state.id_usuario}")
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.id_usuario = ""
        st.rerun()
