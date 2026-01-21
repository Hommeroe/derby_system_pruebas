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

# --- PANTALLA DE ENTRADA (DISEÑO ORIGINAL COMPACTADO) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .block-container { padding-top: 1.5rem !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='text-align:center; padding:20px; background: #E67E22; border-radius:15px; margin-bottom:15px;'>
            <h3 style='color: white; font-size: 1rem; margin:0;'>BIENVENIDOS A</h3>
            <h1 style='color: white; font-size: 3rem; font-weight: 900; margin: 0;'>DerbySystem</h1>
            <div style='background-color: #1a1a1a; padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #333;'>
                <h4 style='color: #E67E22; margin:0 0 10px 0;'>¿Qué es este sistema?</h4>
                <p style='color: white; font-size: 0.95rem; margin:0;'>Plataforma de <b>sorteo digital</b>. Garantiza transparencia total, orden y combates gallísticos 100% justos mediante tecnología de emparejamiento inteligente.</p>
                <p style='color: #E67E22; font-size: 0.85rem; margin-top: 10px; font-style: italic;'>Sistema seguro. Por favor inicia sesión o crea una cuenta nueva para gestionar tus eventos.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_spacer_L, col_center, col_spacer_R = st.columns([0.25, 0.5, 0.25])
    
    with col_center:
        tab_login, tab_registro = st.tabs(["🔐 INICIAR SESIÓN", "📝 CREAR CUENTA"])
        with tab_login:
            st.write("")
            usuario_login = st.text_input("USUARIO", key="login_user").upper().strip()
            pass_login = st.text_input("CONTRASEÑA", type="password", key="login_pass")
            if st.button("ENTRAR AL SISTEMA", use_container_width=True):
                if verificar_credenciales(usuario_login, pass_login):
                    st.session_state.id_usuario = usuario_login
                    st.rerun()
                else: st.error("⚠️ Usuario o contraseña incorrectos.")

        with tab_registro:
            st.write("")
            nuevo_usuario = st.text_input("NUEVO USUARIO", key="reg_user").upper().strip()
            nueva_pass = st.text_input("CONTRASEÑA", type="password", key="reg_pass")
            confirmar_pass = st.text_input("CONFIRMAR CONTRASEÑA", type="password", key="reg_pass_conf")
            if st.button("CREAR MI CUENTA", use_container_width=True):
                if nuevo_usuario and nueva_pass == confirmar_pass:
                    if registrar_usuario(nuevo_usuario, nueva_pass): st.success("✅ ¡Cuenta creada!")
                    else: st.warning("⚠️ El usuario ya existe.")
    st.stop()

# --- ESTILOS INTERNOS (RESTABLECIDOS) ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    div.stButton > button, div.stDownloadButton > button {
        background-color: #E67E22 !important; color: white !important;
        font-weight: bold !important; border-radius: 8px !important;
        border: none !important;
    }
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0 0 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400;
        font-size: 0.8em;
    }
    .header-azul { 
        background-color: #1a1a1a; color: #E67E22; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px; margin-bottom: 5px; border-bottom: 2px solid #E67E22;
    }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; table-layout: fixed; }
    .tabla-final td, .tabla-final th { 
        border: 1px solid #bdc3c7; text-align: center; padding: 5px; color: black !important; font-size: 11px;
    }
    .nombre-partido { font-weight: bold; font-size: 11px; color: black !important; display: block; }
    .peso-texto { font-size: 9px; color: #2c3e50 !important; display: block; }
    
    /* Estilo Protocolo Original */
    .protocol-step {
        background-color: white; padding: 15px; border-radius: 10px;
        border-left: 6px solid #E67E22; margin-bottom: 12px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .protocol-number { font-size: 1.5rem; font-weight: 900; color: #E67E22; margin-right: 10px; }
    .protocol-title { font-size: 1.1rem; font-weight: bold; color: #1a1a1a; text-transform: uppercase; }
    .protocol-text { color: #444; margin-top: 8px; font-size: 0.95rem; line-height: 1.4; }
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

if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# --- INTERFAZ ---
st.markdown("<h2 style='margin:0;'>DerbySystem PRO</h2>", unsafe_allow_html=True)

t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO DE EVENTO", "🏆 PANEL DE COTEJO", "📑 PROTOCOLO DE OPERACIÓN"])

with t_reg:
    anillos_act = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Añadir Partido # {len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        p_cols = st.columns(g_sel)
        for i in range(g_sel):
            with p_cols[i]:
                st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
                st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_act + i + 1):03}</div>", unsafe_allow_html=True)
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        st.markdown("### ✏️ Tabla de Edición")
        df = pd.DataFrame(st.session_state.partidos)
        res = st.data_editor(df, use_container_width=True, hide_index=True)
        if not res.equals(df):
            st.session_state.partidos = res.to_dict('records'); guardar(st.session_state.partidos); st.rerun()
        if st.button("🚨 REINICIAR EVENTO", use_container_width=True):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        st.button("📄 DESCARGAR REPORTE TÉCNICO (PDF)", use_container_width=True)
        st.divider()
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA DE COMBATE {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-final'><thead><tr><th>#</th><th>G</th><th>PARTIDO ROJO</th><th>AN.</th><th>E</th><th>DIF.</th><th>AN.</th><th>PARTIDO VERDE</th><th>G</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    c = "style='background:#e74c3c;color:white;'" if d > TOLERANCIA else ""
                    html += f"<tr><td>{pelea_n}</td><td>□</td><td style='border-left:3px solid red'><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-texto'>{rojo[col_g]:.3f}</span></td><td>{an_r:03}</td><td style='background:#f1f2f6'>□</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td style='border-right:3px solid green'><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-texto'>{verde[col_g]:.3f}</span></td><td>□</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

with t_ayu:
    st.markdown("## 📖 PROTOCOLO TÉCNICO")
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("""
        <div class="protocol-step">
            <span class="protocol-number">01</span><span class="protocol-title">Configuración Inicial</span>
            <div class="protocol-text">Defina la modalidad (gallos por partido) en la pestaña de registro.</div>
        </div>
        <div class="protocol-step">
            <span class="protocol-number">02</span><span class="protocol-title">Captura de Pesos</span>
            <div class="protocol-text">Ingrese nombres y pesos. Los anillos se asignan automáticamente de forma secuencial.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_der:
        st.markdown("""
        <div class="protocol-step">
            <span class="protocol-number">03</span><span class="protocol-title">Validación de Cotejo</span>
            <div class="protocol-text">El algoritmo empareja por peso similar evitando enfrentamientos del mismo dueño.</div>
        </div>
        <div class="protocol-step">
            <span class="protocol-number">04</span><span class="protocol-title">Supervisión de Tolerancia</span>
            <div class="protocol-text">Diferencias mayores a 80g se resaltan en rojo para revisión del juez.</div>
        </div>
        """, unsafe_allow_html=True)

with st.sidebar:
    st.write(f"Sesión Activa: **{st.session_state.id_usuario}**")
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
        st.session_state.clear(); st.rerun()
