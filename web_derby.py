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

# --- 1. INICIALIZACIÓN DE ESTADO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""
if "temp_llave" not in st.session_state:
    st.session_state.temp_llave = None
if "partidos" not in st.session_state:
    st.session_state.partidos = []
if "n_gallos" not in st.session_state:
    st.session_state.n_gallos = 2
if "apuestas_abiertas" not in st.session_state:
    st.session_state.apuestas_abiertas = False

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- FUNCIONES DE PERSISTENCIA ---
def guardar_status_apuestas(estado):
    with open(f"status_{st.session_state.id_usuario}.txt", "w") as f:
        f.write("1" if estado else "0")

def cargar_status_apuestas():
    path = f"status_{st.session_state.id_usuario}.txt"
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip() == "1"
    return False

# --- BLINDAJE PARA MANTENER LA APP DESPIERTA ---
components.html(
    """
    <script>
    function keepAlive() {
        fetch(window.location.href);
        console.log("Manteniendo DerbySystem despierto...");
    }
    setInterval(keepAlive, 120000);
    </script>
    """,
    height=0,
    width=0,
)

# --- SIDEBAR: ADMINISTRADOR MAESTRO (HOMERO) ---
with st.sidebar:
    st.markdown("### ⚙️ ADMINISTRACIÓN")
    
    if st.session_state.id_usuario != "":
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True): 
            st.session_state.clear()
            st.rerun()
        st.divider()
    
    acceso = st.text_input("Acceso Maestro:", type="password")
    es_dueño = (acceso == "28days")
    
    if es_dueño:
        st.success("Modo Dueño: Activo")
        st.subheader("📁 Eventos del Sistema")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        
        for arch in archivos:
            nombre_llave = arch.replace("datos_", "").replace(".txt", "")
            with st.expander(f"🔑 {nombre_llave}"):
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👁️", key=f"load_{arch}"):
                        st.session_state.id_usuario = nombre_llave
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_{arch}"):
                        os.remove(arch)
                        if os.path.exists(f"status_{nombre_llave}.txt"): os.remove(f"status_{nombre_llave}.txt")
                        st.rerun()

# --- PANTALLA DE ENTRADA ---
if st.session_state.id_usuario == "":
    año_actual = datetime.now().year
    st.markdown(f"""
        <style>
        .main-container {{ max-width: 500px; margin: 0 auto; padding-top: 2vh; text-align: center; }}
        .brand-logo {{ font-size: 2.8rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 0; line-height: 1; }}
        .brand-system {{ color: #E67E22; }}
        .tagline {{ font-size: 0.7rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #E67E22; margin-top: 2px; margin-bottom: 10px; }}
        .promo-box {{ margin-top: 15px; padding: 18px; background-color: rgba(230, 126, 34, 0.05); border: 1px solid rgba(230, 126, 34, 0.2); border-radius: 10px; }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="brand-logo">Derby<span class="brand-system">System</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Professional Combat Management</div>', unsafe_allow_html=True)

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
            with open(f"datos_{nueva}.txt", "w", encoding="utf-8") as f: pass
            st.success(f"Creado: {nueva}")
            st.info("Usa este código en la pestaña ACCEDER")

    st.markdown('<div class="promo-box"><p style="font-size:0.8rem;">Plataforma profesional de cotejo y apuestas en vivo.</p></div>', unsafe_allow_html=True)
    st.markdown(f'© {año_actual} DerbySystem PRO', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CARGA DE DATOS Y ESTILOS ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080
st.session_state.apuestas_abiertas = cargar_status_apuestas()

st.markdown("""
    <style>
    div.stButton > button { background-color: #E67E22 !important; color: white !important; border-radius: 8px !important; }
    .caja-anillo { background-color: #1a1a1a; color: #E67E22; padding: 2px; border-radius: 0px 0px 5px 5px; font-weight: bold; text-align: center; margin-top: -15px; border: 1px solid #D35400; font-size: 0.8em; }
    .header-azul { background-color: #1a1a1a; color: #E67E22; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px; border-bottom: 2px solid #E67E22; }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; color: black !important; font-size: 11px; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 5px; }
    .card-vs { background: #1a1a1a; border: 1px solid #E67E22; border-radius: 10px; padding: 15px; margin-bottom: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

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

# --- INTERFAZ TÉCNICA (Tabs) ---
st.title("DerbySystem PRO")
st.caption(f"Evento: {st.session_state.id_usuario} | Panel de Control")

t_reg, t_cot, t_man = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📘 MANUAL"])

with t_reg:
    if es_dueño:
        st.markdown("### 🔐 ACTIVACIÓN DE APUESTAS (Solo Dueño)")
        if st.session_state.apuestas_abiertas:
            if st.button("🔴 DESACTIVAR APUESTAS PÚBLICAS", use_container_width=True):
                st.session_state.apuestas_abiertas = False
                guardar_status_apuestas(False); st.rerun()
        else:
            if st.button("🟢 ACTIVAR APUESTAS PÚBLICAS", use_container_width=True):
                st.session_state.apuestas_abiertas = True
                guardar_status_apuestas(True); st.rerun()
        st.divider()

    anillos_act = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g_reg = st.columns([2,1])
    g_sel = col_g_reg.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    
    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_act + i + 1):03}</div>", unsafe_allow_html=True); st.write("")
        if st.form_submit_button("💾 REGISTRAR"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"; lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-final'><thead><tr><th>#</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>AN.</th><th>VERDE</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    html += f"<tr><td>{pelea_n}</td><td style='color:red;'><b>{rojo['PARTIDO']}</b><br>{rojo[col_g]:.3f}</td><td>{an_r:03}</td><td>{d:.3f}</td><td>{an_v:03}</td><td style='color:green;'><b>{verde['PARTIDO']}</b><br>{verde[col_g]:.3f}</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

with t_man:
    st.info("Manual Técnico: Registro libre, Cotejo automático y Anillos secuenciales.")

# --- SECCIÓN DE APUESTAS (VISTA PÚBLICA) ---
if st.session_state.apuestas_abiertas:
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #E67E22;'>🎯 APUESTAS EN VIVO</h2>", unsafe_allow_html=True)
    
    for r in range(1, st.session_state.n_gallos + 1):
        st.subheader(f"Ronda {r}")
        col_g = f"G{r}"; lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
            if v_idx is not None:
                verde = lista.pop(v_idx)
                st.markdown(f"""
                    <div class="card-vs">
                        <div style="display: flex; justify-content: space-around; align-items: center;">
                            <div><b style="color:#ff4b4b;">{rojo['PARTIDO']}</b><br>{rojo[col_g]:.3f}</div>
                            <div style="color:#E67E22; font-weight:900;">VS</div>
                            <div><b style="color:#2ecc71;">{verde['PARTIDO']}</b><br>{verde[col_g]:.3f}</div>
                        </div>
                        <div style="font-size:0.7rem; margin-top:10px;">PAGO ESTIMADO x1.90</div>
                    </div>
                """, unsafe_allow_html=True)
            else: break
