import streamlit as st
import pandas as pd
import os
import json
import hashlib
import re
from datetime import datetime
import pytz  
from io import BytesIO

# Importamos reportlab para el PDF
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

def registrar_usuario(usuario, password):
    users = cargar_usuarios()
    if usuario in users: return False 
    users[usuario] = hashlib.sha256(str.encode(password)).hexdigest()
    with open(USER_DB_FILE, "w") as f: json.dump(users, f)
    return True

def verificar_credenciales(usuario, password):
    users = cargar_usuarios()
    h = hashlib.sha256(str.encode(password)).hexdigest()
    return usuario in users and users[usuario] == h

if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- PANTALLA DE ENTRADA (MANTENIENDO DISEÑO) ---
if st.session_state.id_usuario == "":
    st.markdown("""<style>.stApp { margin-top: -60px !important; } .login-card { max-width: 480px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; border-top: 5px solid #E67E22; color: black; }</style>""", unsafe_allow_html=True)
    col1, col_center, col3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:#E67E22;">DerbySystem</h2>', unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["🔒 ACCESO", "📝 REGISTRO"])
        with tab_login:
            u = st.text_input("Usuario").upper().strip()
            p = st.text_input("Contraseña", type="password")
            if st.button("ENTRAR AL SISTEMA", use_container_width=True):
                if verificar_credenciales(u, p): st.session_state.id_usuario = u; st.rerun()
                else: st.error("Credenciales incorrectas")
        with tab_reg:
            nu = st.text_input("Nuevo Usuario").upper().strip()
            np = st.text_input("Nueva Pass", type="password")
            if st.button("REGISTRAR CUENTA", use_container_width=True):
                if registrar_usuario(nu, np): st.success("Registrado correctamente")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CONSTANTES Y ESTILOS (RESPETADOS) ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

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
        text-align: center; font-weight: bold; border-radius: 5px; border-bottom: 2px solid #E67E22;
    }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; table-layout: fixed; color: black !important; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 5px 2px; color: black !important; font-size: 11px; }
    .nombre-partido { font-weight: bold; font-size: 10px; line-height: 1.1; display: block; color: black !important; }
    .peso-texto { font-size: 10px; color: #2c3e50 !important; display: block; }
    .protocol-step {
        background-color: white; padding: 15px; border-radius: 10px;
        border-left: 6px solid #E67E22; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA (SINFÍN DE CAMBIOS) ---
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

with st.sidebar:
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True): st.session_state.clear(); st.rerun()
    st.divider()
    acceso_admin = st.text_input("Acceso Admin:", type="password", key="admin_key")

# --- PANEL ADMINISTRADOR ACTUALIZADO (MOSTRANDO USUARIOS Y DATOS COMPLETOS) ---
if acceso_admin == "28days":
    st.title("🛠️ Panel de Control Administrador")
    
    # Mostrar Usuarios
    st.subheader("👥 Cuentas de Usuarios")
    db_usuarios = cargar_usuarios()
    if db_usuarios:
        df_u = pd.DataFrame(list(db_usuarios.items()), columns=["Usuario", "Hash Contraseña"])
        st.table(df_u)
    
    st.divider()
    
    # Mostrar Datos de los Archivos .txt
    st.subheader("📄 Registros del Sistema (.txt)")
    archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
    for arch in archivos:
        with st.container():
            col_t, col_b = st.columns([5, 1])
            col_t.markdown(f"**Archivo:** `{arch}`")
            if col_b.button("Eliminar", key=f"del_{arch}"):
                os.remove(arch); st.rerun()
            try:
                df_temp = pd.read_csv(arch, sep="|", header=None)
                st.dataframe(df_temp, use_container_width=True)
            except: st.error(f"No se pudo leer el archivo {arch}")
            st.write("---")
    if st.button("⬅️ VOLVER AL SISTEMA"): st.rerun()
    st.stop()

# --- INTERFAZ NORMAL (RESTAURADA) ---
st.title("DerbySystem PRO")
t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO", "📑 PROTOCOLO DE OPERACIÓN"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Añadir Partido # {len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            # El anillo se genera automático (según instrucción previa)
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True); st.write("") 
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()
    # ... (Resto del código de edición y cotejo se mantiene igual)

with t_ayu:
    st.markdown("## 📖 Guía del Operador")
    st.info("Siga estos pasos para garantizar la integridad del sorteo.")
    st.markdown('<div class="protocol-step"><b>01. Configuración:</b> Defina los gallos por partido.</div>', unsafe_allow_html=True)
    st.markdown('<div class="protocol-step"><b>02. Registro:</b> Ingrese pesos, el anillo es automático.</div>', unsafe_allow_html=True)
    st.markdown('<div class="protocol-step"><b>03. Cotejo:</b> Revise las peleas y descargue el PDF.</div>', unsafe_allow_html=True)
