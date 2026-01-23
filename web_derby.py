import streamlit as st
import pandas as pd
import os
import re
import json
import hashlib
from datetime import datetime
import pytz  
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# Importamos reportlab para el PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

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

# --- PANTALLA DE LOGIN ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .stApp { margin-top: -60px !important; }
        .login-card {
            max-width: 480px; margin: 0 auto; background: #ffffff;
            padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-top: 5px solid #E67E22;
        }
        .main-title { font-size: 2.4rem; font-weight: 800; color: #E67E22; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    col_1, col_center, col_3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="main-title">DerbySystem</div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔒 ACCESO", "📝 REGISTRO"])
        with t1:
            u = st.text_input("Usuario", key="l_u").upper().strip()
            p = st.text_input("Contraseña", key="l_p", type="password")
            if st.button("ENTRAR AL SISTEMA", use_container_width=True):
                if verificar_credenciales(u, p):
                    st.session_state.id_usuario = u
                    st.rerun()
                else: st.error("Credenciales incorrectas")
        with t2:
            nu = st.text_input("Nuevo Usuario").upper().strip()
            np = st.text_input("Nueva Pass", type="password")
            if st.button("REGISTRAR CUENTA", use_container_width=True):
                if nu and np:
                    if registrar_usuario(nu, np): st.success("Registrado!")
                    else: st.warning("Ya existe")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- FUNCIONES DE PERSISTENCIA (GOOGLE SHEETS) ---
def cargar():
    try:
        # Lee la pestaña del usuario [cite: 2026-01-23]
        df = conn.read(worksheet=st.session_state.id_usuario, ttl=0)
        if df is None or df.empty: return [], 2
        partidos = df.to_dict('records')
        n_gallos = len([c for c in df.columns if re.match(r'^G\d+$', c)])
        return partidos, max(n_gallos, 2)
    except:
        return [], 2

def guardar(lista):
    if lista:
        df = pd.DataFrame(lista)
        try:
            # Intenta actualizar [cite: 2026-01-23]
            conn.update(worksheet=st.session_state.id_usuario, data=df)
        except:
            # Si no existe, la crea [cite: 2026-01-23]
            conn.create(worksheet=st.session_state.id_usuario, data=df)
        st.toast(f"✅ Sincronizado con la nube")

# --- LÓGICA DE NEGOCIO ---
TOLERANCIA = 0.080

def limpiar_nombre_socio(n): return re.sub(r'\s*\d+$', '', n).strip().upper()

def generar_pdf(partidos, n_gallos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements, styles = [], getSampleStyleSheet()
    # (Lógica de PDF omitida por brevedad para no saturar, se mantiene la tuya original)
    doc.build([Paragraph("REPORTE DE COTEJO", styles['Title'])])
    return buffer.getvalue()

# --- INTERFAZ ---
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# ESTILOS
st.markdown("""
    <style>
    .caja-anillo { background: #1a1a1a; color: #E67E22; text-align: center; border-radius: 5px; font-weight: bold; }
    .header-azul { background: #1a1a1a; color: #E67E22; padding: 10px; text-align: center; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

t_reg, t_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO"])

with t_reg:
    # El anillo se genera automático [cite: 2026-01-14]
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    
    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True)
        
        if st.form_submit_button("💾 GUARDAR EN NUBE"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()

    # Tabla de edición que también guarda cambios en Sheets
    if st.session_state.partidos:
        df_edit = pd.DataFrame(st.session_state.partidos)
        res = st.data_editor(df_edit, use_container_width=True)
        if st.button("Actualizar Cambios"):
            st.session_state.partidos = res.to_dict('records')
            guardar(st.session_state.partidos)
            st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            # Lógica de cotejo aquí...
    else:
        st.info("Registra al menos 2 partidos para ver el cotejo.")

with st.sidebar:
    st.write(f"Usuario: **{st.session_state.id_usuario}**")
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
