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

# Eliminamos la gestión de usuarios compleja (DB_FILE se mantiene dinámico)
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- PANTALLA DE ENTRADA SIMPLIFICADA ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .stApp { margin-top: -60px !important; }
        .block-container { padding-top: 2rem !important; }
        .login-card {
            max-width: 480px; margin: 0 auto; background: #ffffff;
            padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-top: 5px solid #E67E22;
        }
        .desc-box {
            background-color: #1a1a1a; color: #f2f2f2; padding: 12px;
            border-radius: 8px; margin-bottom: 15px; text-align: center;
        }
        .main-title {
            font-size: 2.4rem; font-weight: 800; color: #E67E22;
            text-align: center; margin-bottom: 0px;
        }
        .main-subtitle {
            font-size: 0.75rem; color: #888; text-align: center;
            letter-spacing: 3px; margin-bottom: 15px; text-transform: uppercase;
        }
        .login-footer {
            text-align: center; font-size: 0.7rem; color: #999;
            margin-top: 25px; border-top: 1px solid #eee; padding-top: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    col_1, col_center, col_3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="desc-box"><div style="color:#E67E22; font-weight:bold; font-size:0.85rem; margin-bottom:3px;">ACCESO RÁPIDO</div><div style="font-size:0.75rem; line-height:1.3; color:#ccc;">Escriba el nombre de su evento para comenzar.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="main-title">DerbySystem</div><div class="main-subtitle">PRO MANAGEMENT</div>', unsafe_allow_html=True)
        
        # Entrada simplificada sin contraseña
        evento_id = st.text_input("IDENTIFICADOR DEL EVENTO", placeholder="EJ: TORNEO_AZTECA_2026").upper().strip()
        st.info("💡 Este nombre servirá para recuperar sus datos después.")
        
        if st.button("ACCEDER AL SISTEMA", use_container_width=True):
            if evento_id:
                # El ID de usuario ahora es simplemente el nombre que elijan
                st.session_state.id_usuario = evento_id
                st.rerun()
            else:
                st.error("Por favor, asigne un nombre a su evento.")
        
        st.markdown('<div class="login-footer">© 2026 DerbySystem PRO | Acceso Instantáneo</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CONSTANTES ---
# El archivo de datos se crea automáticamente con el nombre del evento
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS INTERNOS (Mantenidos igual) ---
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
    
    .tutorial-header {
        background: #1a1a1a; color: #E67E22; padding: 20px;
        border-radius: 10px; text-align: center; border-left: 10px solid #E67E22;
        margin-bottom: 25px;
    }
    .card-tutorial {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 4px solid #E67E22;
        height: 100%; transition: 0.3s;
    }
    .step-title { font-weight: 900; color: #1a1a1a; font-size: 1.1rem; margin-bottom: 10px; }
    .step-text { font-size: 0.9rem; color: #555; line-height: 1.4; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA (Mantenidas intactas) ---
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

# ... (Aquí sigue tu función generar_pdf y el resto de la interfaz igual)
# NOTA: He omitido la repetición de generar_pdf por brevedad, pero en tu código real 
# se queda exactamente igual.

# --- INTERFAZ (Se mantiene todo el sistema de anillos y tablas) ---
if 'partidos' not in st.session_state: 
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title(f"DerbySystem - {st.session_state.id_usuario}") # Ahora muestra el nombre del evento

# ... (El resto del código de pestañas, formularios y edición se mantiene IDÉNTICO)
# (Solo asegúrate de copiar tu bloque de t_reg, t_cot y t_ayu aquí)

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g_reg = st.columns([2,1])
    g_sel = col_g_reg.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Añadir Partido # {len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            # El anillo se genera automático según tus instrucciones [cite: 2026-01-14]
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True); st.write("") 
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

# --- SIDEBAR ADMINISTRADOR (Tu acceso secreto) ---
with st.sidebar:
    st.write(f"Evento: **{st.session_state.id_usuario}**")
    if st.button("🚪 SALIR DEL EVENTO", use_container_width=True): 
        st.session_state.clear(); st.rerun()
    
    st.divider()
    acceso = st.text_input("Llave Maestra Admin:", type="password")
    if acceso == "28days":
        st.subheader("📂 Eventos Activos")
        # Listamos todos los archivos de datos para que veas qué eventos hay
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for arch in archivos:
            event_name = arch.replace("datos_", "").replace(".txt", "")
            with st.expander(f"🏟️ {event_name}"):
                try:
                    with open(arch, "r", encoding="utf-8") as f:
                        contenido = f.read()
                    st.code(contenido, language="text")
                except: st.error("Error")
                if st.button("Eliminar Evento", key=f"del_{arch}"):
                    os.remove(arch); st.rerun()
