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

# --- PANTALLA DE ENTRADA (BALANCEADA AL 50%) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .block-container { padding-top: 2rem !important; }
        .stTextInput { margin-bottom: 5px; }
        </style>
    """, unsafe_allow_html=True)

    # Encabezado con especificaciones del sistema
    st.markdown("""
        <div style='text-align:center; padding:25px; background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%); border-radius:15px; margin-bottom:20px; border: 1px solid #E67E22;'>
            <h1 style='color: white; font-size: 2.8rem; font-weight: 900; margin: 0;'>Derby<span style='color:#E67E22'>System</span></h1>
            <p style='color: #E67E22; font-weight: bold; font-size: 1rem; margin: 10px 0;'>Sorteo Digital • Transparencia Total • Emparejamiento Inteligente</p>
            <div style='max-width: 600px; margin: 0 auto; color: #bdc3c7; font-size: 0.95rem; line-height: 1.4;'>
                Plataforma diseñada para garantizar <b>combates 100% justos</b> mediante algoritmos de peso. 
                Optimiza el orden de los anillos y genera reportes técnicos oficiales al instante.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_spacer_L, col_center, col_spacer_R = st.columns([0.25, 0.5, 0.25])
    
    with col_center:
        tab_login, tab_registro = st.tabs(["🔐 ENTRAR AL SISTEMA", "📝 REGISTRARSE"])
        
        with tab_login:
            st.write("")
            usuario_login = st.text_input("USUARIO", key="login_user").upper().strip()
            pass_login = st.text_input("CONTRASEÑA", type="password", key="login_pass")
            if st.button("ACCEDER", use_container_width=True, key="btn_login"):
                if verificar_credenciales(usuario_login, pass_login):
                    if "partidos" in st.session_state: del st.session_state["partidos"]
                    st.session_state.id_usuario = usuario_login
                    st.rerun()
                else: st.error("⚠️ Usuario o contraseña incorrectos.")

        with tab_registro:
            st.write("")
            st.info("Crea una cuenta para gestionar tus eventos de forma independiente.")
            nuevo_usuario = st.text_input("NUEVO USUARIO", key="reg_user").upper().strip()
            nueva_pass = st.text_input("CONTRASEÑA", type="password", key="reg_pass")
            confirmar_pass = st.text_input("CONFIRMAR", type="password", key="reg_pass_conf")
            if st.button("CREAR CUENTA", use_container_width=True, key="btn_registro"):
                if nuevo_usuario and nueva_pass == confirmar_pass:
                    if registrar_usuario(nuevo_usuario, nueva_pass): st.success("✅ ¡Cuenta creada con éxito!")
                    else: st.warning("⚠️ El usuario ya existe.")
    st.stop()

# --- CONSTANTES Y ESTILOS INTERNOS ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

st.markdown("""
    <style>
    div.stButton > button, div.stDownloadButton > button {
        background-color: #E67E22 !important; color: white !important;
        font-weight: bold !important; border-radius: 8px !important;
    }
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0 0 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -16px; border: 1px solid #D35400;
        font-size: 0.8em;
    }
    .header-azul { 
        background-color: #1a1a1a; color: #E67E22; padding: 8px; 
        text-align: center; font-weight: bold; border-radius: 5px; margin-bottom: 5px; border-bottom: 2px solid #E67E22;
    }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; }
    .tabla-final td, .tabla-final th { 
        border: 1px solid #bdc3c7; text-align: center; padding: 4px; color: black !important; font-size: 12px;
    }
    .nombre-partido { font-weight: bold; display: block; }
    .peso-texto { font-size: 10px; color: #333 !important; }
    </style>
""", unsafe_allow_html=True)

# (Aquí continúa el resto de la lógica de tu sistema sin cambios)
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
    ahora = datetime.now(zona_horaria).strftime("%d/%m/%Y %H:%M:%S")
    data_header = [[Paragraph("<font color='white' size=22><b>DerbySystem</b></font>", styles['Title'])],
                   [Paragraph(f"<font color='white' size=9>REPORTE TÉCNICO | {ahora}</font>", styles['Normal'])]]
    header_table = Table(data_header, colWidths=[500])
    header_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1a1a1a")), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(header_table); elements.append(Spacer(1, 20))
    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Heading2']))
        col_g = f"G{r}"
        lista = sorted([dict(p) for p in partidos], key=lambda x: x[col_g])
        data = [["#", "PARTIDO (ROJO)", "AN.", "DIF.", "AN.", "PARTIDO (VERDE)"]]
        pelea_n = 1
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
            if v_idx is not None:
                verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                idx_r = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                idx_v = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==verde["PARTIDO"])
                an_r, an_v = (idx_r * n_gallos) + r, (idx_v * n_gallos) + r
                data.append([pelea_n, f"{rojo['PARTIDO']} ({rojo[col_g]:.3f})", f"{an_r:03}", f"{d:.3f}", f"{an_v:03}", f"{verde['PARTIDO']} ({verde[col_g]:.3f})"])
                pelea_n += 1
            else: break
        t = Table(data, colWidths=[30, 170, 40, 50, 40, 170])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1a1a")), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        elements.append(t); elements.append(Spacer(1, 15))
    doc.build(elements)
    return buffer.getvalue()

# --- INTERFAZ ---
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title("DerbySystem PRO")

t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📑 AYUDA"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    c1, c2 = st.columns([2,1])
    g_sel = c2.selectbox("MODALIDAD (GALLOS):", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Nuevo Partido #{len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        p_cols = st.columns(g_sel)
        for i in range(g_sel):
            with p_cols[i]:
                st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
                st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales+i+1):03}</div>", unsafe_allow_html=True)
        st.write("")
        if st.form_submit_button("💾 GUARDAR DATOS DEL PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        df = pd.DataFrame(st.session_state.partidos)
        res = st.data_editor(df, use_container_width=True, hide_index=True)
        if not res.equals(df):
            st.session_state.partidos = res.to_dict('records'); guardar(st.session_state.partidos); st.rerun()
        if st.button("🚨 BORRAR EVENTO COMPLETO", use_container_width=True):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        st.download_button("📥 GENERAR REPORTE PDF", generar_pdf(st.session_state.partidos, st.session_state.n_gallos), "cotejo_oficial.pdf", use_container_width=True)
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
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
                    c = "style='background:#e74c3c;color:white;'" if d > TOLERANCIA else ""
                    html += f"<tr><td>{pelea_n}</td><td><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-texto'>{rojo[col_g]:.3f}</span></td><td>{an_r:03}</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-texto'>{verde[col_g]:.3f}</span></td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

with t_ayu:
    st.subheader("Manual de Uso Rápido")
    st.markdown("""
    1. **Registro:** Ingresa el nombre y pesos. Los anillos se asignan en orden automático.
    2. **Cotejo:** El sistema busca el peso más cercano y evita que pelees contra ti mismo.
    3. **Tolerancia:** Si la diferencia de peso supera los 80g, verás la celda en rojo.
    4. **PDF:** Genera el documento oficial para la mesa de control y el juez.
    """)

with st.sidebar:
    st.info(f"Conectado como: {st.session_state.id_usuario}")
    if st.button("CERRAR SESIÓN", use_container_width=True):
        st.session_state.clear(); st.rerun()
