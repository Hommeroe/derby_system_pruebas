import streamlit as st
import pandas as pd
import os
import random
import string
import re
from datetime import datetime
import pytz  
from io import BytesIO

# Importamos reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# --- 1. INICIALIZACIÓN DE ESTADO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""
if "temp_llave" not in st.session_state:
    st.session_state.temp_llave = None
if "partidos" not in st.session_state:
    st.session_state.partidos = []
if "n_gallos" not in st.session_state:
    st.session_state.n_gallos = 2
if "apuestas" not in st.session_state:
    st.session_state.apuestas = {} # Diccionario para guardar dinero por pelea

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- SIDEBAR: ADMINISTRADOR ---
with st.sidebar:
    st.markdown("### ⚙️ ADMINISTRACIÓN")
    if st.session_state.id_usuario != "":
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True): 
            st.session_state.clear()
            st.rerun()
        st.divider()
    
    acceso = st.text_input("Acceso Maestro:", type="password")
    if acceso == "28days":
        st.subheader("📁 Eventos")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for arch in archivos:
            nombre_llave = arch.replace("datos_", "").replace(".txt", "")
            with st.expander(f"🔑 {nombre_llave}"):
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👁️", key=f"load_{arch}"):
                        st.session_state.id_usuario = nombre_llave
                        if 'partidos' in st.session_state: del st.session_state['partidos']
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_{arch}"):
                        os.remove(arch)
                        if st.session_state.id_usuario == nombre_llave: st.session_state.id_usuario = ""
                        st.rerun()

# --- PANTALLA DE ENTRADA (MANTIENE TU DISEÑO) ---
if st.session_state.id_usuario == "":
    año_actual = datetime.now().year
    st.markdown(f"""
        <style>
        @media (prefers-color-scheme: light) {{ .stApp {{ background-color: #ffffff; }} .brand-derby {{ color: #000000; }} }}
        @media (prefers-color-scheme: dark) {{ .stApp {{ background-color: #0e1117; }} .brand-derby {{ color: #ffffff; }} }}
        .main-container {{ max-width: 500px; margin: 0 auto; padding-top: 2vh; text-align: center; }}
        .brand-logo {{ font-size: 2.8rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 0; line-height: 1; }}
        .brand-system {{ color: #E67E22; }}
        .tagline {{ font-size: 0.7rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #E67E22; margin-top: 2px; margin-bottom: 10px; }}
        .promo-box {{ margin-top: 10px; padding: 12px; background-color: rgba(230, 126, 34, 0.05); border: 1px solid rgba(230, 126, 34, 0.2); border-radius: 8px; }}
        .promo-title {{ color: #E67E22; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; margin-bottom: 4px; }}
        .promo-text {{ font-size: 0.75rem; line-height: 1.3; opacity: 0.9; margin: 0; }}
        .footer {{ margin-top: 15px; font-size: 0.65rem; color: gray; text-transform: uppercase; letter-spacing: 1px; }}
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="brand-logo"><span class="brand-derby">Derby</span><span class="brand-system">System</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Professional Combat Management</div>', unsafe_allow_html=True)
    if not st.session_state.temp_llave:
        t_acc, t_gen = st.tabs(["ACCEDER", "NUEVO EVENTO"])
        with t_acc:
            llave_input = st.text_input("Código de Evento:", placeholder="DERBY-XXXX", label_visibility="collapsed").upper().strip()
            if st.button("INICIAR SESIÓN", use_container_width=True, type="primary"):
                if os.path.exists(f"datos_{llave_input}.txt"):
                    st.session_state.id_usuario = llave_input
                    st.rerun()
                else: st.error("Código no encontrado.")
        with t_gen:
            if st.button("GENERAR CREDENCIAL", use_container_width=True):
                nueva = "DERBY-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
                st.session_state.temp_llave = nueva
                st.rerun()
    else:
        st.code(st.session_state.temp_llave)
        if st.button("CONFIRMAR Y ENTRAR", use_container_width=True, type="primary"):
            with open(f"datos_{st.session_state.temp_llave}.txt", "w", encoding="utf-8") as f: pass
            st.session_state.id_usuario = st.session_state.temp_llave
            st.session_state.temp_llave = None
            st.rerun()
    st.markdown('<div class="promo-box"><div class="promo-title">🛡️ EXCELENCIA EN PALENQUES</div><p class="promo-text">Gestión técnica avanzada. Automatiza el cotejo oficial y garantiza trazabilidad de anillos.</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="footer">© {año_actual} DerbySystem PRO</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- LÓGICA DE DATOS ---
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

if not st.session_state.partidos:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# --- ESTILOS DE TABLAS Y APUESTAS ---
st.markdown("""
    <style>
    .header-azul { background-color: #1a1a1a; color: #E67E22; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px; border-bottom: 2px solid #E67E22; }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; color: black !important; margin-bottom: 20px;}
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 8px; font-size: 12px; }
    .apuesta-card { background: #1a1a1a; border: 1px solid #E67E22; border-radius: 10px; padding: 15px; margin-bottom: 10px; color: white; }
    .vs-text { color: #E67E22; font-weight: 900; font-size: 1.2rem; }
    .pago-badge { background: #2ecc71; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

st.title("DerbySystem PRO 🏆")
t_reg, t_cot, t_apu, t_man = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "💰 APUESTAS", "📘 MANUAL"])

# --- (Pestañas Registro y Cotejo se mantienen igual que tu código anterior) ---
with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g_reg = st.columns([2,1])
    g_sel = col_g_reg.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
        if st.form_submit_button("💾 REGISTRAR", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g_cot = f"G{r}"; lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g_cot])
            html = "<table class='tabla-final'><thead><tr><th>#</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>AN.</th><th>VERDE</th></tr></thead><tbody>"
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g_cot] - verde[col_g_cot])
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    html += f"<tr><td>{pelea_n}</td><td style='color:red'><b>{rojo['PARTIDO']}</b><br>{rojo[col_g_cot]:.3f}</td><td>{an_r:03}</td><td>{d:.3f}</td><td>{an_v:03}</td><td style='color:green'><b>{verde['PARTIDO']}</b><br>{verde[col_g_cot]:.3f}</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

# --- NUEVA PESTAÑA: APUESTAS ---
with t_apu:
    st.header("🎰 Centro de Apuestas en Vivo")
    comision = st.slider("Comisión de la Casa (%)", 0, 20, 10)
    
    if len(st.session_state.partidos) < 2:
        st.warning("Se requieren al menos 2 partidos registrados para abrir apuestas.")
    else:
        for r in range(1, st.session_state.n_gallos + 1):
            st.subheader(f"Ronda {r}")
            col_g = f"G{r}"; lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    p_id = f"R{r}_P{pelea_n}"
                    
                    if p_id not in st.session_state.apuestas:
                        st.session_state.apuestas[p_id] = {"rojo": 0.0, "verde": 0.0}
                    
                    # Interfaz de Apuesta
                    with st.container():
                        st.markdown(f"""
                        <div class="apuesta-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="text-align: center; width: 40%;">
                                    <span style="color: #ff4b4b; font-size: 1.1rem; font-weight: bold;">{rojo['PARTIDO']}</span><br>
                                    <small>Peso: {rojo[col_g]:.3f}</small>
                                </div>
                                <div class="vs-text">VS</div>
                                <div style="text-align: center; width: 40%;">
                                    <span style="color: #2ecc71; font-size: 1.1rem; font-weight: bold;">{verde['PARTIDO']}</span><br>
                                    <small>Peso: {verde[col_g]:.3f}</small>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2, c3 = st.columns([1, 1, 1])
                        with c1:
                            m_rojo = st.number_input(f"Apostar Rojo ($)", 0, 100000, 0, step=100, key=f"in_r_{p_id}")
                            if st.button(f"Confirmar Rojo", key=f"btn_r_{p_id}"):
                                st.session_state.apuestas[p_id]["rojo"] += m_rojo
                                st.rerun()
                        with c2:
                            m_verde = st.number_input(f"Apostar Verde ($)", 0, 100000, 0, step=100, key=f"in_v_{p_id}")
                            if st.button(f"Confirmar Verde", key=f"btn_v_{p_id}"):
                                st.session_state.apuestas[p_id]["verde"] += m_verde
                                st.rerun()
                        with c3:
                            # Cálculo de Momios (Cuánto paga por cada $1)
                            total_r = st.session_state.apuestas[p_id]["rojo"]
                            total_v = st.session_state.apuestas[p_id]["verde"]
                            bolsa_neta = (total_r + total_v) * (1 - (comision/100))
                            
                            pago_r = (bolsa_neta / total_r) if total_r > 0 else 0
                            pago_v = (bolsa_neta / total_v) if total_v > 0 else 0
                            
                            st.write("**Resumen de Bolsa:**")
                            st.write(f"Rojo: ${total_r:,.0f} | Verde: ${total_v:,.0f}")
                            st.markdown(f"Paga Rojo: <span class='pago-badge'>x{pago_r:.2f}</span>", unsafe_allow_html=True)
                            st.markdown(f"Paga Verde: <span class='pago-badge'>x{pago_v:.2f}</span>", unsafe_allow_html=True)
                    st.divider()
                    pelea_n += 1
                else: break

# --- MANUAL ---
with t_man:
    st.header("📘 Manual de Usuario")
    st.write("Bienvenido al sistema profesional. Aquí el resumen de uso:")
    st.info("1. Registre los partidos y pesos. 2. Consulte el cotejo automático. 3. Abra las apuestas y gestione el dinero de la casa.")
