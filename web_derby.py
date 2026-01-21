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

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verificar_credenciales(usuario, password):
    users = cargar_usuarios()
    if usuario in users and users[usuario] == hash_password(password): return True
    return False

def registrar_usuario(usuario, password):
    users = cargar_usuarios()
    if usuario in users: return False 
    users[usuario] = hash_password(password)
    guardar_usuario_db(users)
    return True

# --- LÓGICA DE ACCESO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- PANTALLA DE PRESENTACIÓN Y ACCESO (DISEÑO 50%) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .block-container { padding-top: 1.5rem !important; }
        .stTextInput { margin-bottom: 5px; }
        /* Estilo para los tabs de login */
        div[data-baseweb="tab-list"] { gap: 20px; }
        div[data-baseweb="tab"] { font-size: 14px; padding: 10px 20px; }
        </style>
    """, unsafe_allow_html=True)

    # Banner de Presentación Compacto
    st.markdown("""
        <div style='text-align:center; padding:20px; background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%); border-radius:12px; margin-bottom:20px; border: 1px solid #E67E22;'>
            <h1 style='color: white; font-size: 2.5rem; font-weight: 900; margin: 0;'>Derby<span style='color:#E67E22'>System</span></h1>
            <div style='display: flex; justify-content: center; gap: 15px; margin: 10px 0;'>
                <span style='color: #E67E22; font-size: 0.85rem; font-weight: bold;'>✔ SORTEO AUTOMATIZADO</span>
                <span style='color: #E67E22; font-size: 0.85rem; font-weight: bold;'>✔ ANILLADO SECUENCIAL</span>
                <span style='color: #E67E22; font-size: 0.85rem; font-weight: bold;'>✔ REPORTES PDF</span>
            </div>
            <p style='color: #bdc3c7; font-size: 0.95rem; max-width: 800px; margin: 0 auto; line-height: 1.3;'>
                Optimice la gestión técnica de su evento con emparejamientos precisos por peso, 
                eliminando errores manuales y garantizando transparencia total en cada ronda.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_L, col_center, col_R = st.columns([0.3, 0.4, 0.3])
    
    with col_center:
        tab_login, tab_registro = st.tabs(["🔐 INICIAR SESIÓN", "📝 NUEVA CUENTA"])
        with tab_login:
            st.write("")
            u_log = st.text_input("USUARIO", key="login_user").upper().strip()
            p_log = st.text_input("CONTRASEÑA", type="password", key="login_pass")
            if st.button("ENTRAR AL PANEL", use_container_width=True):
                if verificar_credenciales(u_log, p_log):
                    st.session_state.id_usuario = u_log
                    st.rerun()
                else: st.error("Acceso denegado.")

        with tab_registro:
            st.write("")
            u_reg = st.text_input("CREAR USUARIO", key="reg_user").upper().strip()
            p_reg = st.text_input("CREAR CONTRASEÑA", type="password", key="reg_pass")
            if st.button("REGISTRARME", use_container_width=True):
                if u_reg and p_reg:
                    if registrar_usuario(u_reg, p_reg): st.success("¡Registro exitoso!")
                    else: st.warning("El usuario ya existe.")
    st.stop()

# --- INTERFAZ DE TRABAJO ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

st.markdown("""
    <style>
    /* Compactar área de trabajo */
    .block-container { padding-top: 1rem !important; }
    
    /* Botones y Estética Interna */
    div.stButton > button, div.stDownloadButton > button {
        background-color: #E67E22 !important; color: white !important;
        font-weight: bold !important; border-radius: 6px !important;
        height: 35px;
    }
    
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0 0 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -16px; border: 1px solid #D35400;
        font-size: 0.75rem;
    }
    
    .header-ronda { 
        background-color: #1a1a1a; color: #E67E22; padding: 6px; 
        text-align: center; font-weight: bold; border-radius: 4px;
        font-size: 14px; margin: 10px 0 5px 0; border-bottom: 2px solid #E67E22;
    }
    
    .tabla-cotejo { width: 100%; border-collapse: collapse; background-color: white; }
    .tabla-cotejo td, .tabla-cotejo th { 
        border: 1px solid #bdc3c7; text-align: center; padding: 3px; 
        color: black !important; font-size: 11px;
    }
    .p-nombre { font-weight: bold; font-size: 11px; display: block; color: black !important; }
    .p-peso { font-size: 10px; color: #444 !important; }
    </style>
""", unsafe_allow_html=True)

# Lógica de carga/guardado
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

# --- TÍTULO Y TABS ---
st.markdown("<h2 style='margin:0;'>DerbySystem Control Panel</h2>", unsafe_allow_html=True)

t_reg, t_cot, t_inf = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📑 PROTOCOLO"])

with t_reg:
    anillos_act = len(st.session_state.partidos) * st.session_state.n_gallos
    col_info, col_opt = st.columns([2, 1])
    g_sel = col_opt.selectbox("GALLOS POR EQUIPO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_reg", clear_on_submit=True):
        c_n, c_p = st.columns([1, 2])
        nom = c_n.text_input("NOMBRE PARTIDO:").upper()
        with c_p:
            p_cols = st.columns(g_sel)
            for i in range(g_sel):
                with p_cols[i]:
                    st.number_input(f"G{i+1}", 1.80, 2.60, 2.20, 0.001, format="%.3f", key=f"p_{i}")
                    st.markdown(f"<div class='caja-anillo'>{(anillos_act+i+1):03}</div>", unsafe_allow_html=True)
        if st.form_submit_button("💾 REGISTRAR PARTIDO", use_container_width=True):
            if nom:
                d = {"PARTIDO": nom}
                for i in range(g_sel): d[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(d); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        df = pd.DataFrame(st.session_state.partidos)
        ed = st.data_editor(df, use_container_width=True, hide_index=True)
        if not ed.equals(df):
            st.session_state.partidos = ed.to_dict('records'); guardar(st.session_state.partidos); st.rerun()
        if st.button("🚨 REINICIAR TODO EL EVENTO", use_container_width=True):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        st.info("Visualización optimizada para lectura rápida en mesa.")
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-ronda'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-cotejo'><thead><tr><th>#</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>AN.</th><th>VERDE</th></tr></thead><tbody>"""
            p_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    c = "style='background:#e74c3c;color:white;'" if d > TOLERANCIA else ""
                    html += f"<tr><td>{p_n}</td><td><span class='p-nombre'>{rojo['PARTIDO']}</span><span class='p-peso'>{rojo[col_g]:.3f}</span></td><td>{an_r:03}</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td><span class='p-nombre'>{verde['PARTIDO']}</span><span class='p-peso'>{verde[col_g]:.3f}</span></td></tr>"
                    p_n += 1
                else: break
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

with t_inf:
    st.subheader("Especificaciones Técnicas")
    st.write("**Emparejamiento:** Algoritmo de peso mínimo diferencial.")
    st.write("**Anillos:** Generación automática secuencial según orden de registro.")
    st.write("**Tolerancia:** Límite visual de 0.080kg (80 gramos).")
    st.markdown("---")
    st.warning("Asegúrese de que todos los pesos estén en Kilogramos (ej: 2.250).")

with st.sidebar:
    st.write(f"Sesión: **{st.session_state.id_usuario}**")
    if st.button("CERRAR SESIÓN", use_container_width=True):
        st.session_state.clear(); st.rerun()
