import streamlit as st
import pandas as pd
import os
import uuid
import re
import json
import hashlib
from datetime import datetime
import pytz  
from io import BytesIO

# Importamos reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- GESTIÓN DE USUARIOS ---
USER_DB_FILE = "usuarios_db.json"

def cargar_usuarios():
    if not os.path.exists(USER_DB_FILE): return {}
    try:
        with open(USER_DB_FILE, "r") as f: return json.load(f)
    except: return {}

def guardar_usuario_db(users):
    with open(USER_DB_FILE, "w") as f: json.dump(users, f)

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def verificar_credenciales(usuario, password):
    users = cargar_usuarios()
    return usuario in users and users[usuario] == hash_password(password)

def registrar_usuario(usuario, password):
    users = cargar_usuarios()
    if usuario in users: return False 
    users[usuario] = hash_password(password)
    guardar_usuario_db(users)
    return True

if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- PANTALLA DE ENTRADA CORREGIDA ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        /* Eliminar el espacio blanco superior */
        .stApp { margin-top: -60px !important; }
        .block-container { padding-top: 2rem !important; }
        
        .login-card {
            max-width: 480px;
            margin: 0 auto;
            background: #ffffff;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-top: 5px solid #E67E22;
        }
        .desc-box {
            background-color: #1a1a1a;
            color: #f2f2f2;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            text-align: center;
        }
        .main-title {
            font-size: 2.4rem;
            font-weight: 800;
            color: #E67E22;
            text-align: center;
            margin-bottom: 0px;
        }
        .main-subtitle {
            font-size: 0.75rem;
            color: #888;
            text-align: center;
            letter-spacing: 3px;
            margin-bottom: 15px;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)

    col_1, col_center, col_3 = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("""
            <div class="desc-box">
                <div style="color:#E67E22; font-weight:bold; font-size:0.85rem; margin-bottom:3px;">¿QUÉ ES ESTE SISTEMA?</div>
                <div style="font-size:0.75rem; line-height:1.3; color:#ccc;">
                    Plataforma de <b>sorteo digital</b> que garantiza transparencia y combates gallisticos justos mediante emparejamiento inteligente.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-title">DerbySystem</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-subtitle">PRO MANAGEMENT</div>', unsafe_allow_html=True)
        
        tab_login, tab_reg = st.tabs(["🔒 ACCESO", "📝 REGISTRO"])
        
        with tab_login:
            u = st.text_input("Usuario", key="l_u", placeholder="USUARIO").upper().strip()
            p = st.text_input("Contraseña", key="l_p", type="password", placeholder="••••••••")
            if st.button("ENTRAR AL SISTEMA", use_container_width=True):
                if verificar_credenciales(u, p):
                    st.session_state.id_usuario = u
                    st.rerun()
                else: st.error("Credenciales incorrectas")
        
        with tab_reg:
            nu = st.text_input("Nuevo Usuario", key="r_u", placeholder="NUEVO USUARIO").upper().strip()
            np = st.text_input("Nueva Pass", key="r_p", type="password", placeholder="CONTRASEÑA")
            cp = st.text_input("Confirma Pass", key="r_c", type="password", placeholder="CONFIRMAR")
            if st.button("REGISTRAR CUENTA", use_container_width=True):
                if nu and np == cp:
                    if registrar_usuario(nu, np): st.success("Registrado correctamente")
                    else: st.warning("El usuario ya existe")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS INTERNOS (RESTAURADOS) ---
st.markdown("""
    <style>
    div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
        background-color: #E67E22 !important; color: white !important; font-weight: bold !important;
        border-radius: 8px !important; border: none !important;
    }
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400; font-size: 0.8em;
    }
    .header-azul { 
        background-color: #1a1a1a; color: #E67E22; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 14px; margin-bottom: 5px; border-bottom: 2px solid #E67E22;
    }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; table-layout: fixed; color: black !important; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 5px 2px; color: black !important; font-size: 11px; }
    .nombre-partido { font-weight: bold; font-size: 10px; line-height: 1.1; display: block; color: black !important; }
    .peso-texto { font-size: 10px; color: #2c3e50 !important; display: block; }
    .col-num { width: 22px; } .col-g { width: 25px; } .col-an { width: 35px; } 
    .col-e { width: 22px; background-color: #f1f2f6; } .col-dif { width: 45px; }
    .protocol-step {
        background-color: white; padding: 15px; border-radius: 10px;
        border-left: 6px solid #E67E22; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .protocol-number { font-size: 1.3rem; font-weight: 900; color: #E67E22; margin-right: 10px; }
    .protocol-title { font-size: 1rem; font-weight: bold; color: #1a1a1a; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA (SIN CAMBIOS) ---
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

def generar_pdf(partidos, n_gallos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para centrar nombres en PDF
    style_center = ParagraphStyle(name='Center', parent=styles['Normal'], alignment=TA_CENTER)
    
    zona_horaria = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(zona_horaria
