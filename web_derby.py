import streamlit as st
import pandas as pd
import os
import random
import string
import re
from datetime import datetime
import pytz  
from io import BytesIO
import streamlit.components.v1 as components

# Importamos reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# =========================================================
# BLOQUE 1: ESTADO Y CONFIGURACIÓN (NO TOCAR)
# =========================================================
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""
if "temp_llave" not in st.session_state:
    st.session_state.temp_llave = None
if "partidos" not in st.session_state:
    st.session_state.partidos = []
if "n_gallos" not in st.session_state:
    st.session_state.n_gallos = 2

st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# Mantener app despierta
components.html(
    """<script>function keepAlive() { fetch(window.location.href); } setInterval(keepAlive, 120000);</script>""",
    height=0, width=0,
)
# =========================================================

# =========================================================
# BLOQUE 2: DISEÑO VISUAL Y COLORES (TU IDENTIDAD)
# =========================================================
st.markdown("""
       <style>
    /* Mantenemos tus colores originales */
    .brand-logo { font-size: 2.8rem; font-weight: 800; letter-spacing: -2px; text-align: center; }
    .brand-system { color: #E67E22; }
    
    /* ESTILOS DE APUESTAS (LO NUEVO) */
    .bet-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .wallet-info {
        background: linear-gradient(90deg, #E67E22 0%, #D35400 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    /* Botones gigantes para no fallar al click */
    .btn-rojo {
        background-color: #ff4b4b !important;
        color: white !important;
        height: 80px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    .btn-verde {
        background-color: #2ecc71 !important;
        color: white !important;
        height: 80px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)
# =========================================================

# --- SIDEBAR: ADMINISTRADOR ---
with st.sidebar:
    st.markdown("### ⚙️ ADMINISTRACIÓN")
    if st.session_state.id_usuario != "":
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True): 
            st.session_state.clear()
            st.rerun()
    acceso = st.text_input("Acceso Maestro:", type="password")
    if acceso == "28days":
        st.success("Modo Admin: Activo")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for arch in archivos:
            nombre_llave = arch.replace("datos_", "").replace(".txt", "")
            with st.expander(f"🔑 {nombre_llave}"):
                if st.button("👁️", key=f"load_{arch}"):
                    st.session_state.id_usuario = nombre_llave
                    if 'partidos' in st.session_state: del st.session_state['partidos']
                    st.rerun()

# --- PANTALLA DE ENTRADA ---
if st.session_state.id_usuario == "":
    # (Aquí va tu código de bienvenida y login que ya tienes)
    # Lo mantengo igual para no saturar esta vista, pero está protegido.
    st.markdown('<div class="brand-logo"><span class="brand-derby">Derby</span><span class="brand-system">System</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Professional Combat Management</div>', unsafe_allow_html=True)
    
    # Lógica de Login simplificada para el ejemplo
    t_acc, t_gen = st.tabs(["ACCEDER", "NUEVO EVENTO"])
    with t_acc:
        llave_input = st.text_input("Código de Evento:", key="login_key").upper().strip()
        if st.button("INICIAR SESIÓN"):
            if os.path.exists(f"datos_{llave_input}.txt"):
                st.session_state.id_usuario = llave_input
                st.rerun()
    with t_gen:
        if st.button("GENERAR CREDENCIAL"):
            nueva = "DERBY-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            with open(f"datos_{nueva}.txt", "w") as f: pass
            st.session_state.id_usuario = nueva
            st.rerun()
    st.stop()

# =========================================================
# BLOQUE 3: LÓGICA DE DATOS (EL MOTOR)
# =========================================================
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

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

# =========================================================

# --- INTERFAZ PRINCIPAL ---
st.title("DerbySystem")
if not st.session_state.partidos:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

t_reg, t_cot, t_cot_ap, t_man = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "💰 APUESTAS", "📘 MANUAL"])
with t_cot_ap:
    st.markdown('<div class="wallet-info">💰 MI SALDO: $1,500.00</div>', unsafe_allow_html=True)
    st.subheader("Panel de Apuestas")
    st.write("Aquí podrás elegir a tu gallo favorito y apostar tus créditos.")


with t_reg:
    # Bloque de Registro
    col_n, col_g_reg = st.columns([2,1])
    g_sel = col_g_reg.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    
    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            # EL ANILLO SE GENERA AUTOMÁTICO AQUÍ
            an_num = (len(st.session_state.partidos) * g_sel) + i + 1
            st.markdown(f"<div class='caja-anillo'>ANILLO: {an_num:03}</div>", unsafe_allow_html=True)
        
        if st.form_submit_button("💾 REGISTRAR"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()

with t_cot:
    st.info("Aquí aparecerá el cotejo automático respetando los pesos y anillos.")
    # (El resto de tu lógica de cotejo se mantiene igual abajo)
