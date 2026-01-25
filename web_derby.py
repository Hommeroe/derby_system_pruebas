import streamlit as st
import pandas as pd
import os
import random
import string
import re
from datetime import datetime
import pytz  
from io import BytesIO

# Importamos reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# --- 1. INICIALIZACIÓN DE ESTADO (Al principio para evitar errores) ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""
if "temp_llave" not in st.session_state:
    st.session_state.temp_llave = None
if "partidos" not in st.session_state:
    st.session_state.partidos = []
if "n_gallos" not in st.session_state:
    st.session_state.n_gallos = 2

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- SIDEBAR: ADMINISTRADOR (LÓGICA INTACTA) ---
with st.sidebar:
    st.markdown("### ⚙️ ADMINISTRACIÓN")
    if st.session_state.id_usuario != "":
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True): 
            st.session_state.clear()
            st.rerun()
        st.divider()
    
    acceso = st.text_input("Acceso Maestro:", type="password")
    if acceso == "28days":
        st.subheader("📁 Eventos")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for arch in archivos:
            nombre_llave = arch.replace("datos_", "").replace(".txt", "")
            with st.expander(f"🔑 {nombre_llave}"):
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👁️", key=f"load_{arch}"):
                        st.session_state.id_usuario = nombre_llave
                        if 'partidos' in st.session_state: del st.session_state['partidos']
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_{arch}"):
                        os.remove(arch)
                        if st.session_state.id_usuario == nombre_llave: st.session_state.id_usuario = ""
                        st.rerun()

# --- PANTALLA DE ENTRADA (MODIFICADA PARA MÁS RELLENO Y TEXTO) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        /* Fondo Adaptativo */
        @media (prefers-color-scheme: light) {
            .stApp { background-color: #ffffff; }
            .brand-derby { color: #000000; }
            .text-muted { color: #555555; }
            .info-box { background-color: #f8f9fa; border: 1px solid #eeeeee; }
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background-color: #0e1117; }
            .brand-derby { color: #ffffff; }
            .text-muted { color: #bbbbbb; }
            .info-box { background-color: #1e2127; border: 1px solid #333333; }
        }

        .main-container {
            max-width: 550px;
            margin: 8vh auto;
            text-align: center;
        }
        .brand-logo { font-size: 3.8rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 0; }
        .brand-system { color: #E67E22; }
        .tagline { 
            font-size: 0.9rem; font-weight: 700; letter-spacing: 2px; 
            text-transform: uppercase; color: #E67E22; margin-top: -5px; margin-bottom: 30px;
        }
        
        .info-box {
            padding: 20px;
            border-radius: 12px;
            margin-top: 40px;
            text-align: center;
        }
        .info-title {
            color: #E67E22;
            font-size: 0.9rem;
            font-weight: 800;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        .info-text {
            font-size: 0.85rem;
            line-height: 1.5;
        }

        /* Eliminar bordes y fondos de pestañas y contenedores */
        .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; }
        .stTabs [data-baseweb="tab"] { font-weight: 700 !important; }
        div[data-testid="stVerticalBlock"] > div { background-color: transparent !important; border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="brand-logo"><span class="brand-derby">Derby</span><span class="brand-system">System</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Gestión Profesional de Palenques</div>', unsafe_allow_html=True)

    if not st.session_state.temp_llave:
        t_acc, t_gen = st.tabs(["ACCEDER", "CREAR EVENTO"])
        with t_acc:
            st.write("")
            llave_input = st.text_input("Código de Evento:", placeholder="DERBY-XXXX").upper().strip()
            if st.button("INICIAR PANEL DE CONTROL", use_container_width=True, type="primary"):
                if os.path.exists(f"datos_{llave_input}.txt"):
                    st.session_state.id_usuario = llave_input
                    if 'partidos' in st.session_state: del st.session_state['partidos']
                    st.rerun()
                else: st.error("Código no encontrado.")
        with t_gen:
            st.write("")
            st.markdown('<p class="text-muted">Inicie una nueva base de datos para su torneo o derby.</p>', unsafe_allow_html=True)
            if st.button("GENERAR NUEVA CREDENCIAL", use_container_width=True):
                nueva = "DERBY-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
                st.session_state.temp_llave = nueva
                st.rerun()
    else:
        st.success("Evento Configurado")
        st.code(st.session_state.temp_llave)
        if st.button("ACCEDER AHORA", use_container_width=True, type="primary"):
            with open(f"datos_{st.session_state.temp_llave}.txt", "w", encoding="utf-8") as f: pass
            st.session_state.id_usuario = st.session_state.temp_llave
            st.session_state.temp_llave = None
            st.rerun()

    # --- SECCIÓN SOLICITADA (CON MÁS RELLENO Y DETALLE) ---
    st.markdown("""
        <div class="info-box">
            <div class="info-title">🏆 Software Especializado para Combates de Gallos</div>
            <p class="text-muted info-text">
                Plataforma integral diseñada para la organización de <b>Derbys y Palenques</b>. 
                Garantizamos la transparencia en la optimización de cotejos por peso, 
                trazabilidad absoluta de anillos secuenciales y generación inmediata de reportes 
                técnicos profesionales para jueces y organizadores.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 2. LÓGICA DE NEGOCIO (SIN CAMBIOS) ---
# ... (El resto del código se mantiene exactamente igual a tu original)
