import streamlit as st
import pandas as pd
import os
import random
import string
import re
from datetime import datetime
import pytz  

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""
if "rol" not in st.session_state:
    st.session_state.rol = "Espectador"  # Por defecto
if "partidos" not in st.session_state:
    st.session_state.partidos = []
if "n_gallos" not in st.session_state:
    st.session_state.n_gallos = 2
if "apuestas" not in st.session_state:
    st.session_state.apuestas = {}

st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- LÓGICA DE DATOS ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
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

# --- PANTALLA DE ACCESO (DISEÑO COMPACTO) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .main-container { max-width: 500px; margin: 0 auto; text-align: center; padding-top: 5vh; }
        .brand-logo { font-size: 2.5rem; font-weight: 800; }
        .brand-system { color: #E67E22; }
        .promo-box { background: rgba(230, 126, 34, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #E67E22; margin-top: 20px; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="brand-logo">Derby<span class="brand-system">System</span></div>', unsafe_allow_html=True)
    
    llave = st.text_input("Código de Evento:", placeholder="DERBY-XXXX").upper().strip()
    rol = st.radio("Entrar como:", ["Espectador (Solo Apuestas)", "Administrador (Mesa Técnica)"], horizontal=True)
    
    if st.button("INGRESAR AL SISTEMA", use_container_width=True, type="primary"):
        if os.path.exists(f"datos_{llave}.txt"):
            st.session_state.id_usuario = llave
            st.session_state.rol = rol
            st.rerun()
        else:
            st.error("Código de evento no válido.")
    
    st.markdown('<div class="promo-box"><b>Modo Espectador:</b> Consulte peleas y momios en vivo.<br><b>Modo Admin:</b> Control de pesaje y anillos.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CARGA DE DATOS ---
if not st.session_state.partidos:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# --- INTERFAZ SEGÚN EL ROL ---

if st.session_state.rol == "Administrador (Mesa Técnica)":
    # --- VISTA COMPLETA PARA TI (REGISTRO + COTEJO + APUESTAS) ---
    st.title(f"🛠️ Panel Técnico: {st.session_state.id_usuario}")
    t_reg, t_cot, t_apu = st.tabs(["📝 REGISTRO DE PESOS", "🏆 TABLA DE COTEJO", "💰 CONTROL DE APUESTAS"])
    
    with t_reg:
        st.subheader("Entrada de Gallos")
        # (Aquí va tu código de registro que ya tienes funcional)
        st.info("Aquí registras partidos y el sistema genera los anillos automáticamente.")

    with t_cot:
        st.subheader("Cotejo Oficial")
        # (Aquí va tu tabla de cotejo con los nombres y pesos)
        st.write("Visualización técnica para el juez.")

    with t_apu:
        st.subheader("Gestión de Dinero")
        # Aquí tú mueves los montos que la gente te da en efectivo
        st.write("Controlas los montos totales y la comisión de la casa.")

else:
    # --- VISTA PARA EL USUARIO (SOLO APUESTAS Y PELEAS) ---
    st.title(f"🎰 Apuestas en Vivo: {st.session_state.id_usuario}")
    st.markdown("---")
    
    if len(st.session_state.partidos) < 2:
        st.info("Esperando a que la mesa técnica termine el cotejo...")
    else:
        # Solo mostramos las peleas listas para apostar
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"### RONDA {r}")
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    
                    # Diseño limpio para el apostador
                    st.markdown(f"""
                        <div style="background: #1a1a1a; padding: 20px; border-radius: 15px; border-left: 10px solid #E67E22; margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-around; align-items: center; color: white;">
                                <div style="text-align: center;">
                                    <h2 style="color: #ff4b4b; margin:0;">{rojo['PARTIDO']}</h2>
                                    <p>Peso: {rojo[col_g]:.3f}</p>
                                </div>
                                <div style="font-size: 2rem; font-weight: 800; color: #E67E22;">VS</div>
                                <div style="text-align: center;">
                                    <h2 style="color: #2ecc71; margin:0;">{verde['PARTIDO']}</h2>
                                    <p>Peso: {verde[col_g]:.3f}</p>
                                </div>
                            </div>
                            <div style="text-align: center; margin-top: 10px;">
                                <span style="background: #E67E22; color: black; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                                    PAGO ESTIMADO: ROJO x1.90 | VERDE x1.90
                                </span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else: break

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.id_usuario = ""
    st.rerun()
