import streamlit as st
import pandas as pd
import os
import random
import string
import re
from datetime import datetime
import pytz  

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- ESTADOS DE SESIÓN ---
if "id_usuario" not in st.session_state: st.session_state.id_usuario = ""
if "rol" not in st.session_state: st.session_state.rol = "Espectador"
if "partidos" not in st.session_state: st.session_state.partidos = []
if "n_gallos" not in st.session_state: st.session_state.n_gallos = 2
if "apuestas" not in st.session_state: st.session_state.apuestas = {}

# --- PANTALLA DE ACCESO (SIN SIDEBAR NECESARIO) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .main-container { max-width: 500px; margin: 0 auto; text-align: center; padding-top: 5vh; }
        .brand-logo { font-size: 3rem; font-weight: 800; }
        .brand-system { color: #E67E22; }
        .promo-box { background: rgba(230, 126, 34, 0.05); padding: 15px; border-radius: 10px; border: 1px solid #E67E22; margin-top: 20px; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="brand-logo">Derby<span class="brand-system">System</span></div>', unsafe_allow_html=True)
    
    t_acc, t_gen, t_master = st.tabs(["ACCEDER", "NUEVO EVENTO", "⚙️ RECUPERAR"])
    
    with t_acc:
        llave = st.text_input("Código de Evento:", placeholder="DERBY-XXXX").upper().strip()
        rol = st.radio("Entrar como:", ["Espectador (Apuestas)", "Administrador (Mesa)"], horizontal=True)
        if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"):
            if os.path.exists(f"datos_{llave}.txt"):
                st.session_state.id_usuario = llave
                st.session_state.rol = rol
                st.rerun()
            else: st.error("Código no encontrado.")
            
    with t_gen:
        if st.button("GENERAR NUEVO CÓDIGO", use_container_width=True):
            nueva = "DERBY-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            with open(f"datos_{nueva}.txt", "w", encoding="utf-8") as f: pass
            st.success(f"Creado: {nueva}")
            st.info("Copia este código y entra en la pestaña ACCEDER")

    with t_master:
        st.write("Lista de eventos activos:")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for arch in archivos:
            nombre = arch.replace("datos_", "").replace(".txt", "")
            if st.button(f"Entrar a: {nombre}", key=f"rec_{nombre}"):
                st.session_state.id_usuario = nombre
                st.session_state.rol = "Administrador (Mesa)"
                st.rerun()

    st.markdown('<div class="promo-box"><b>DerbySystem PRO:</b> Gestión técnica y apuestas en vivo para palenques.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- LÓGICA DE NEGOCIO (COTEJO, ANILLOS, APUESTAS) ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"

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

if not st.session_state.partidos:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# --- VISTA SEGÚN EL ROL ---
if st.session_state.rol == "Administrador (Mesa)":
    st.title(f"🛠️ Admin: {st.session_state.id_usuario}")
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.id_usuario = ""
        st.rerun()
        
    t_reg, t_cot, t_apu, t_man = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "💰 APUESTAS", "📘 MANUAL"])
    # (Aquí va el código completo de registro, anillos automáticos y tablas que ya teníamos)
else:
    # VISTA LIMPIA PARA EL USUARIO APOSTADOR
    st.title(f"🎰 Peleas y Apuestas: {st.session_state.id_usuario}")
    if st.button("🚪 SALIR"):
        st.session_state.id_usuario = ""
        st.rerun()
    # (Aquí va el diseño de las tarjetas de peleas VS para el público)
