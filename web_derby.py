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
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURACIÓN Y ESTADO ---
if "id_usuario" not in st.session_state: st.session_state.id_usuario = ""
if "temp_llave" not in st.session_state: st.session_state.temp_llave = None
if "partidos" not in st.session_state: st.session_state.partidos = []
if "n_gallos" not in st.session_state: st.session_state.n_gallos = 2

st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- ESTILOS VISUALES (BLINDAJE DE DISEÑO) ---
st.markdown("""
    <style>
    .brand-logo { font-size: 2.8rem; font-weight: 800; letter-spacing: -2px; text-align: center; line-height: 1; }
    .brand-system { color: #E67E22; }
    .tagline { font-size: 0.7rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #E67E22; text-align: center; margin-bottom: 10px; }
    div.stButton > button { background-color: #E67E22 !important; color: white !important; border-radius: 8px !important; }
    .wallet-info { background: linear-gradient(90deg, #E67E22 0%, #D35400 100%); color: white; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }
    .bet-card { background: #1a1a1a; border: 1px solid #333; border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    .caja-anillo { background-color: #1a1a1a; color: #E67E22; padding: 2px; border-radius: 0px 0px 5px 5px; font-weight: bold; text-align: center; margin-top: -15px; border: 1px solid #D35400; font-size: 0.8em; }
    .header-azul { background-color: #1a1a1a; color: #E67E22; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px; border-bottom: 2px solid #E67E22; }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; color: black !important; font-size: 11px; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE BASE DE DATOS ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

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

# --- PANTALLA DE ENTRADA / LOGIN ---
if st.session_state.id_usuario == "":
    st.markdown('<div class="brand-logo"><span style="color:white">Derby</span><span class="brand-system">System</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Professional Combat Management</div>', unsafe_allow_html=True)
    t_acc, t_gen = st.tabs(["ACCEDER", "NUEVO EVENTO"])
    with t_acc:
        llave_input = st.text_input("Código de Evento:", placeholder="DERBY-XXXX").upper().strip()
        if st.button("INICIAR SESIÓN", use_container_width=True):
            if os.path.exists(f"datos_{llave_input}.txt"):
                st.session_state.id_usuario = llave_input
                st.rerun()
    with t_gen:
        if st.button("GENERAR NUEVO EVENTO", use_container_width=True):
            nueva = "DERBY-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            with open(f"datos_{nueva}.txt", "w") as f: pass
            st.session_state.id_usuario = nueva
            st.rerun()
    st.stop()

# --- INTERFAZ PRINCIPAL ---
if not st.session_state.partidos:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

t_reg, t_cot, t_apuesta, t_man = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "💰 APUESTAS", "📘 MANUAL"])

with t_reg:
    col_n, col_g_reg = st.columns([2,1])
    g_sel = col_g_reg.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
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
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = "<table class='tabla-final'><thead><tr><th>#</th><th>ROJO</th><th>DIF.</th><th>VERDE</th></tr></thead><tbody>"
            p_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                    c = "style='background:#ffcccc;'" if d > TOLERANCIA else ""
                    html += f"<tr><td>{p_n}</td><td>{rojo['PARTIDO']}<br>{rojo[col_g]:.3f}</td><td {c}>{d:.3f}</td><td>{verde['PARTIDO']}<br>{verde[col_g]:.3f}</td></tr>"
                    p_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

with t_apuesta:
    st.markdown('<div class="wallet-info">💰 MI SALDO: $1,500.00 Créditos</div>', unsafe_allow_html=True)
    if len(st.session_state.partidos) >= 2:
        st.subheader("Peleas en Vivo")
        lista_ap = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x["G1"])
        while len(lista_ap) >= 2:
            r, v = lista_ap.pop(0), lista_ap.pop(0)
            with st.container():
                st.markdown(f'<div class="bet-card"><div style="display:flex; justify-content:space-between;"><b>🔴 {r["PARTIDO"]}</b> <span>VS</span> <b>🟢 {v["PARTIDO"]}</b></div></div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.button(f"APOSTAR ROJO", key=f"r_{r['PARTIDO']}_{random.random()}", use_container_width=True)
                c2.button(f"APOSTAR VERDE", key=f"v_{v['PARTIDO']}_{random.random()}", use_container_width=True)
    else: st.info("Registra partidos para activar apuestas.")

with t_man:
    st.write("Manual de usuario en construcción...")
