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
from reportlab.lib.styles import getSampleStyleSheet

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

# --- LOGIN ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .stApp { margin-top: -60px !important; }
        .login-card {
            max-width: 480px; margin: 0 auto; background: #ffffff; padding: 25px;
            border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-top: 5px solid #E67E22;
        }
        .main-title { font-size: 2.4rem; font-weight: 800; color: #E67E22; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    col_1, col_center, col_3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="main-title">DerbySystem</div>', unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["🔒 ACCESO", "📝 REGISTRO"])
        with tab_login:
            u = st.text_input("Usuario", key="l_u").upper().strip()
            p = st.text_input("Contraseña", key="l_p", type="password")
            if st.button("ENTRAR", use_container_width=True):
                if verificar_credenciales(u, p): st.session_state.id_usuario = u; st.rerun()
                else: st.error("Error de acceso")
        with tab_reg:
            nu = st.text_input("Nuevo Usuario", key="r_u").upper().strip()
            np = st.text_input("Nueva Pass", key="r_p", type="password")
            if st.button("REGISTRAR", use_container_width=True):
                if nu and np:
                    if registrar_usuario(nu, np): st.success("Registrado")
                    else: st.warning("Ya existe")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS DE LA TABLA (OPTIMIZADA PARA NOMBRES LARGOS) ---
st.markdown("""
    <style>
    div.stButton > button { background-color: #E67E22 !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; }
    
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400; font-size: 0.8em;
    }
    
    .header-azul { 
        background-color: #1a1a1a; color: #E67E22; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px; margin-bottom: 5px;
    }

    /* Tabla adaptable para que quepa en pantalla móvil sin apretar nombres */
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; color: black !important; table-layout: auto; }
    .tabla-final th { background-color: #f8f9fa; color: #333; font-size: 10px; padding: 4px; border: 1px solid #ddd; }
    .tabla-final td { border: 1px solid #ddd; text-align: center; padding: 6px 2px; font-size: 11px; vertical-align: middle; }
    
    /* Ajuste de nombres: permite que el nombre se rompa en varias líneas si es largo */
    .nombre-partido { 
        font-weight: bold; 
        font-size: 11px; 
        line-height: 1.1; 
        display: block; 
        word-wrap: break-word; 
        overflow-wrap: break-word; 
        max-width: 90px; 
        margin: 0 auto;
    }
    .peso-texto { font-size: 10px; color: #666; display: block; margin-top: 2px; }
    
    .protocol-step {
        background-color: white; padding: 15px; border-radius: 10px;
        border-left: 6px solid #E67E22; margin-bottom: 10px; color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
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

# --- INTERFAZ ---
if 'partidos' not in st.session_state: st.session_state.partidos, st.session_state.n_gallos = cargar()

t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📑 PROTOCOLO"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True); st.write("") 
        if st.form_submit_button("💾 GUARDAR", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        df = pd.DataFrame(st.session_state.partidos)
        st.data_editor(df, use_container_width=True, hide_index=True)
        if st.button("🚨 BORRAR TODO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"; lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = "<table class='tabla-final'><thead><tr><th>#</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>AN.</th><th>VERDE</th></tr></thead><tbody>"
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                    c = "style='background:#ffcccc;'" if d > TOLERANCIA else ""
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    html += f"<tr><td>{pelea_n}</td><td style='border-left:3px solid red'><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-texto'>{rojo[col_g]:.3f}</span></td><td>{an_r:03}</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td style='border-right:3px solid green'><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-texto'>{verde[col_g]:.3f}</span></td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

with t_ayu:
    st.markdown('<div class="protocol-step"><b>1. Registro:</b> Ingrese pesos. El anillo es automático.</div>', unsafe_allow_html=True)
    st.markdown('<div class="protocol-step"><b>2. Cotejo:</b> La tabla ajusta los nombres largos automáticamente.</div>', unsafe_allow_html=True)

with st.sidebar:
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True): st.session_state.clear(); st.rerun()
    st.divider()
    acceso = st.text_input("Admin:", type="password")
    if acceso == "28days":
        st.write("**Usuarios:**")
        st.write(cargar_usuarios())
        st.write("**Archivos:**")
        archs = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for a in archs:
            with st.expander(a):
                if st.button("Borrar", key=a): os.remove(a); st.rerun()
