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

# --- GESTIÓN DE USUARIOS (DATABASE JSON) ---
USER_DB_FILE = "usuarios_db.json"

def cargar_usuarios():
    if not os.path.exists(USER_DB_FILE):
        return {}
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_usuario_db(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verificar_credenciales(usuario, password):
    users = cargar_usuarios()
    if usuario in users and users[usuario] == hash_password(password):
        return True
    return False

def registrar_usuario(usuario, password):
    users = cargar_usuarios()
    if usuario in users:
        return False 
    users[usuario] = hash_password(password)
    guardar_usuario_db(users)
    return True

# --- LÓGICA DE ACCESO SEGURO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- PANTALLA DE ENTRADA COMPACTA ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        /* Reducir espacio superior de Streamlit */
        .block-container { padding-top: 1rem !important; }
        div[data-baseweb="tab-list"] { display: flex; justify-content: center; border-bottom: 1px solid #333; }
        .stTextInput { margin-bottom: -10px; }
        </style>
    """, unsafe_allow_html=True)

    # Banner mucho más corto
    st.markdown("""
        <div style='text-align:center; padding:15px; background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%); border-radius:15px; margin-bottom:15px; border: 1px solid #E67E22;'>
            <h1 style='color: white; font-size: 2.2rem; font-weight: 900; margin: 0;'>Derby<span style='color:#E67E22'>System</span></h1>
            <p style='color: #bdc3c7; font-size: 0.9rem; margin: 5px 0;'>Transparencia digital para una competencia justa.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_spacer_L, col_center, col_spacer_R = st.columns([0.3, 0.4, 0.3])
    
    with col_center:
        tab_login, tab_registro = st.tabs(["🔐 ACCESO", "📝 REGISTRO"])
        
        with tab_login:
            usuario_login = st.text_input("USUARIO", key="login_user").upper().strip()
            pass_login = st.text_input("CONTRASEÑA", type="password", key="login_pass")
            st.write("")
            if st.button("INICIAR SESIÓN", use_container_width=True, key="btn_login"):
                if verificar_credenciales(usuario_login, pass_login):
                    if "partidos" in st.session_state: del st.session_state["partidos"]
                    st.session_state.id_usuario = usuario_login
                    st.rerun()
                else:
                    st.error("⚠️ Error de acceso.")

        with tab_registro:
            nuevo_usuario = st.text_input("NUEVO USUARIO", key="reg_user").upper().strip()
            nueva_pass = st.text_input("CONTRASEÑA", type="password", key="reg_pass")
            confirmar_pass = st.text_input("CONFIRMAR", type="password", key="reg_pass_conf")
            if st.button("CREAR CUENTA", use_container_width=True, key="btn_registro"):
                if nuevo_usuario and nueva_pass == confirmar_pass:
                    if registrar_usuario(nuevo_usuario, nueva_pass):
                        st.success("✅ Creado.")
                    else: st.warning("⚠️ Ya existe.")
    st.stop()

# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS INTERNOS COMPACTOS ---
st.markdown("""
    <style>
    /* Compactar todo el layout */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
        background-color: #E67E22 !important; color: white !important;
        font-weight: bold !important; border-radius: 6px !important;
        padding: 0.25rem 0.75rem !important;
    }
    
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 1px;
        border-radius: 0 0 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -18px; border: 1px solid #D35400;
        font-size: 0.75em;
    }
    .header-azul { 
        background-color: #1a1a1a; color: #E67E22; padding: 5px; 
        text-align: center; font-weight: bold; border-radius: 4px;
        font-size: 13px; margin-top: 5px; border-bottom: 2px solid #E67E22;
    }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; table-layout: fixed; }
    .tabla-final td, .tabla-final th { 
        border: 1px solid #bdc3c7; text-align: center; 
        padding: 2px 1px; font-size: 11px; color: black !important;
    }
    .nombre-partido { font-weight: bold; font-size: 10px; color: black !important; display: block; }
    .peso-texto { font-size: 9px; color: #555 !important; display: block; }
    
    /* Protocolo más pequeño */
    .protocol-step {
        padding: 10px; border-radius: 8px; border-left: 4px solid #E67E22;
        margin-bottom: 10px; background: white; box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    .protocol-title { font-size: 0.9rem; font-weight: bold; color: #1a1a1a; }
    .protocol-text { font-size: 0.8rem; color: #444; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE FUNCIONAMIENTO ---
def limpiar_nombre_socio(n):
    return re.sub(r'\s*\d+$', '', n).strip().upper()

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

def generar_pdf(partidos, n_gallos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    zona_horaria = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(zona_horaria).strftime("%d/%m/%Y %H:%M")
    
    data_header = [[Paragraph("<font color='white' size=18><b>DerbySystem</b></font>", styles['Title']),
                    Paragraph(f"<font color='white' size=8>COTEJO OFICIAL | {ahora}</font>", styles['Normal'])]]
    header_table = Table(data_header, colWidths=[350, 150])
    header_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(header_table); elements.append(Spacer(1, 10))

    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Normal']))
        col_g = f"G{r}"
        lista = sorted([dict(p) for p in partidos], key=lambda x: x[col_g])
        data = [["#", "G", "PARTIDO (ROJO)", "AN.", "E", "DIF.", "AN.", "PARTIDO (VERDE)", "G"]]
        pelea_n = 1
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
            if v_idx is not None:
                verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                idx_r = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                idx_v = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==verde["PARTIDO"])
                an_r, an_v = (idx_r * n_gallos) + r, (idx_v * n_gallos) + r
                data.append([pelea_n, " ", Paragraph(f"<b>{rojo['PARTIDO']}</b> ({rojo[col_g]:.3f})", styles['Normal']),
                             f"{an_r:03}", " ", f"{d:.3f}", f"{an_v:03}", Paragraph(f"<b>{verde['PARTIDO']}</b> ({verde[col_g]:.3f})", styles['Normal']), " "])
                pelea_n += 1
            else: break
        t = Table(data, colWidths=[20, 25, 145, 30, 25, 35, 30, 145, 25])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 7), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(t); elements.append(Spacer(1, 10))
    doc.build(elements)
    return buffer.getvalue()

# --- INTERFAZ ---
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# Título más pequeño
st.markdown("<h3 style='margin:0;'>DerbySystem PRO</h3>", unsafe_allow_html=True)

t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📑 AYUDA"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    c1, c2 = st.columns([2,1])
    g_sel = c2.selectbox("GALLOS/PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        col_part, col_pesos = st.columns([1, 2])
        nombre = col_part.text_input("PARTIDO:").upper().strip()
        with col_pesos:
            p_cols = st.columns(g_sel)
            for i in range(g_sel):
                with p_cols[i]:
                    st.number_input(f"G{i+1}", 1.80, 2.60, 2.20, 0.001, format="%.3f", key=f"p_{i}")
                    st.markdown(f"<div class='caja-anillo'>{(anillos_actuales+i+1):03}</div>", unsafe_allow_html=True)
        if st.form_submit_button("💾 GUARDAR", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        df = pd.DataFrame(st.session_state.partidos)
        res = st.data_editor(df, use_container_width=True, hide_index=True)
        if not res.equals(df):
            st.session_state.partidos = res.to_dict('records'); guardar(st.session_state.partidos); st.rerun()
        if st.button("🚨 LIMPIAR", use_container_width=True):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        st.download_button("📥 DESCARGAR PDF", generar_pdf(st.session_state.partidos, st.session_state.n_gallos), "cotejo.pdf", use_container_width=True)
        
        # Mostrar rondas en columnas si son muchas
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-final'><thead><tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>E</th><th>DIF.</th><th>AN.</th><th>VERDE</th><th>G</th></tr></thead><tbody>"""
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
                    html += f"<tr><td>{pelea_n}</td><td>□</td><td><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-texto'>{rojo[col_g]:.3f}</span></td><td>{an_r:03}</td><td style='background:#f1f2f6'>□</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-texto'>{verde[col_g]:.3f}</span></td><td>□</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

with t_ayu:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='protocol-step'><span class='protocol-title'>1. Registro:</span><div class='protocol-text'>Defina gallos y capture pesos. Los anillos se crean solos.</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='protocol-step'><span class='protocol-title'>2. Cotejo:</span><div class='protocol-text'>El sistema empareja por peso automáticamente.</div></div>", unsafe_allow_html=True)

with st.sidebar:
    st.write(f"Usuario: **{st.session_state.id_usuario}**")
    if st.button("🚪 SALIR", use_container_width=True):
        st.session_state.clear(); st.rerun()
