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

# --- LÓGICA DE PERSISTENCIA PARA APUESTAS ---
def guardar_status_apuestas(estado):
    with open(f"status_{st.session_state.id_usuario}.txt", "w") as f:
        f.write("1" if estado else "0")

def cargar_status_apuestas():
    path = f"status_{st.session_state.id_usuario}.txt"
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip() == "1"
    return False

# --- SIDEBAR: ADMINISTRADOR ---
with st.sidebar:
    st.markdown("### ⚙️ ADMINISTRACIÓN")
    if st.session_state.id_usuario != "":
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True): 
            st.session_state.clear()
            st.rerun()
        st.divider()
    
    acceso = st.text_input("Acceso Maestro:", type="password")
    es_admin = (acceso == "28days")
    
    if es_admin:
        st.success("Modo Admin: Activo")
        st.subheader("📁 Eventos")
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
                        os.remove(arch); os.remove(f"status_{nombre_llave}.txt") if os.path.exists(f"status_{nombre_llave}.txt") else None
                        st.rerun()

# --- PANTALLA DE ENTRADA ---
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
        .promo-box {{ margin-top: 15px; padding: 18px; background-color: rgba(230, 126, 34, 0.05); border: 1px solid rgba(230, 126, 34, 0.2); border-radius: 10px; }}
        .promo-title {{ color: #E67E22; font-weight: 800; text-transform: uppercase; font-size: 0.75rem; margin-bottom: 8px; text-align: center; }}
        .promo-text {{ font-size: 0.82rem; line-height: 1.5; opacity: 0.9; margin: 0; text-align: justify; text-align-last: center; }}
        .footer {{ margin-top: 15px; font-size: 0.65rem; color: gray; text-transform: uppercase; letter-spacing: 1px; text-align: center; width: 100%; }}
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

    st.markdown("""<div class="promo-box"><div class="promo-title">🛡️ EXCELENCIA TÉCNICA Y TRANSPARENCIA</div><p class="promo-text">Seguridad y transparencia en cada gramo. Nuestro sistema optimiza la logística con un <b>cotejo automatizado</b> y brinda confianza total.</p></div>""", unsafe_allow_html=True)
    st.markdown(f'<div class="footer">© {año_actual} DerbySystem PRO • VIGENTE</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- LÓGICA DE NEGOCIO ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080
st.session_state.apuestas_abiertas = cargar_status_apuestas()

st.markdown("""
    <style>
    div.stButton > button { background-color: #E67E22 !important; color: white !important; border-radius: 8px !important; border:none !important; }
    .caja-anillo { background-color: #1a1a1a; color: #E67E22; padding: 2px; border-radius: 0px 0px 5px 5px; font-weight: bold; text-align: center; margin-top: -15px; border: 1px solid #D35400; font-size: 0.8em; }
    .header-azul { background-color: #1a1a1a; color: #E67E22; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px; border-bottom: 2px solid #E67E22; }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; color: black !important; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 5px; font-size: 11px; }
    .card-apuesta { background: #1a1a1a; border: 1px solid #E67E22; border-radius: 12px; padding: 15px; margin-bottom: 10px; text-align: center; }
    .vs-text { color: #E67E22; font-weight: 800; font-size: 1.2rem; }
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

# --- MODO ESPECTADOR (PÚBLICO) ---
if acceso != "28days":
    st.title("🏟️ Derby en Vivo")
    st.caption(f"Evento: {st.session_state.id_usuario}")
    
    if not st.session_state.apuestas_abiertas:
        st.info("⌛ Mesa técnica trabajando... Las peleas se publicarán en breve.")
    else:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"; lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    st.markdown(f"""
                        <div class="card-apuesta">
                            <div style="display: flex; justify-content: space-around; align-items: center;">
                                <div><b style="color:#ff4b4b; font-size:1.1rem;">{rojo['PARTIDO']}</b><br>{rojo[col_g]:.3f}</div>
                                <div class="vs-text">VS</div>
                                <div><b style="color:#2ecc71; font-size:1.1rem;">{verde['PARTIDO']}</b><br>{verde[col_g]:.3f}</div>
                            </div>
                            <div style="margin-top:10px; font-size:0.8rem; color:#E67E22;">PAGA: ROJO x1.90 | VERDE x1.90</div>
                        </div>
                    """, unsafe_allow_html=True)
                else: break
    st.stop()

# --- MODO ADMINISTRADOR (TU CÓDIGO ORIGINAL INTACTO) ---
st.title("DerbySystem")
st.caption(f"Evento: {st.session_state.id_usuario} | Panel Técnico")

t_reg, t_cot, t_man = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📘 MANUAL COMPLETO"])

with t_reg:
    # --- MANDO A DISTANCIA ---
    st.markdown("### 📢 Control de Publicación")
    if st.session_state.apuestas_abiertas:
        st.success("✅ APUESTAS PUBLICADAS: El público puede ver las peleas ahora.")
        if st.button("🔴 OCULTAR APUESTAS AL PÚBLICO"):
            st.session_state.apuestas_abiertas = False
            guardar_status_apuestas(False); st.rerun()
    else:
        st.warning("🔒 APUESTAS OCULTAS: Solo tú ves los datos.")
        if st.button("🟢 PUBLICAR APUESTAS AHORA"):
            st.session_state.apuestas_abiertas = True
            guardar_status_apuestas(True); st.rerun()
    st.divider()

    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g_reg = st.columns([2,1])
    g_sel = col_g_reg.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True); st.write("") 
        if st.form_submit_button("💾 REGISTRAR", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        st.write("---")
        display_data = []
        cont_anillo = 1
        for p in st.session_state.partidos:
            item = {"❌": False, "PARTIDO": p["PARTIDO"]}
            for i in range(1, st.session_state.n_gallos + 1):
                item[f"G{i}"] = p[f"G{i}"]; item[f"Anillo {i}"] = f"{cont_anillo:03}"; cont_anillo += 1
            display_data.append(item)
        df = pd.DataFrame(display_data)
        res = st.data_editor(df, use_container_width=True, hide_index=True)
        if not res.equals(df):
            nuevos = []
            for _, r in res.iterrows():
                if not r["❌"]:
                    p_upd = {"PARTIDO": str(r["PARTIDO"]).upper()}
                    for i in range(1, st.session_state.n_gallos + 1): p_upd[f"G{i}"] = float(r[f"G{i}"])
                    nuevos.append(p_upd)
            st.session_state.partidos = nuevos; guardar(nuevos); st.rerun()

with t_cot:
    # ... (Aquí va todo tu código de Cotejo y PDF que ya tienes, se mantiene idéntico)
    if len(st.session_state.partidos) >= 2:
        # (Lógica de PDF y tablas de cotejo idéntica a tu código original)
        pass # Pegar aquí el resto de tu pestaña t_cot original

with t_man:
    # ... (Aquí va tu Manual Completo, se mantiene idéntico)
    pass
