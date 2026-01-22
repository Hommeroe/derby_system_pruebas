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

# --- PANTALLA DE ENTRADA (DISEÑO AJUSTADO Y PROFESIONAL) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        /* Ajuste de márgenes superiores para evitar espacio muerto */
        .block-container { padding-top: 5rem !important; }
        
        .login-card {
            max-width: 500px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px 30px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-top: 5px solid #E67E22;
        }
        .main-title {
            font-family: 'Helvetica Neue', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            color: #E67E22;
            text-align: center;
            margin-bottom: 0px;
            letter-spacing: -1px;
        }
        .main-subtitle {
            font-size: 0.85rem;
            color: #888;
            text-align: center;
            letter-spacing: 3px;
            margin-bottom: 30px;
            text-transform: uppercase;
            font-weight: 500;
        }
        /* Estilo para los Tabs de login */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            justify-content: center;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: 600 !important;
            color: #555 !important;
        }
        .stTabs [aria-selected="true"] {
            color: #E67E22 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col_1, col_center, col_3 = st.columns([1, 1.8, 1])
    
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="main-title">DerbySystem</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-subtitle">PRO MANAGEMENT</div>', unsafe_allow_html=True)
        
        tab_login, tab_reg = st.tabs(["🔒 ACCESO", "📝 REGISTRO"])
        
        with tab_login:
            u = st.text_input("Usuario", key="l_u", placeholder="INGRESE SU USUARIO").upper().strip()
            p = st.text_input("Contraseña", key="l_p", type="password", placeholder="••••••••")
            st.write("")
            if st.button("ENTRAR AL SISTEMA", use_container_width=True):
                if verificar_credenciales(u, p):
                    st.session_state.id_usuario = u
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
        
        with tab_reg:
            nu = st.text_input("Nuevo Usuario", key="r_u", placeholder="NOMBRE DE USUARIO").upper().strip()
            np = st.text_input("Nueva Pass", key="r_p", type="password", placeholder="CREAR CONTRASEÑA")
            cp = st.text_input("Confirma Pass", key="r_c", type="password", placeholder="REPETIR CONTRASEÑA")
            if st.button("REGISTRAR CUENTA", use_container_width=True):
                if nu and np == cp:
                    if registrar_usuario(nu, np): st.success("Cuenta creada exitosamente")
                    else: st.warning("El usuario ya existe")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#999; font-size:0.75rem; margin-top:15px;'>v2.0 Premium | Mesa de Control Digital</p>", unsafe_allow_html=True)

    st.stop()

# --- TODO EL CÓDIGO SIGUIENTE PERMANECE INALTERADO ---
# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS DE INTERFAZ INTERNA ---
st.markdown("""
    <style>
    div.stButton > button, 
    div.stDownloadButton > button, 
    div.stFormSubmitButton > button {
        background-color: #E67E22 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
    }
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400;
        font-size: 0.8em;
    }
    .header-azul { 
        background-color: #1a1a1a; color: #E67E22; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 14px; margin-bottom: 5px; border-bottom: 2px solid #E67E22;
    }
    .tabla-final { 
        width: 100%; border-collapse: collapse; background-color: white; 
        table-layout: fixed; color: black !important;
    }
    .tabla-final td, .tabla-final th { 
        border: 1px solid #bdc3c7; text-align: center; 
        padding: 5px 2px; height: auto; color: black !important;
    }
    .nombre-partido { 
        font-weight: bold; font-size: 10px; line-height: 1.2;
        white-space: normal; word-wrap: break-word;
        display: block; width: 100%; color: black !important;
    }
    .peso-texto { font-size: 10px; color: #2c3e50 !important; display: block; margin-top: 2px;}
    .cuadro { font-size: 11px; font-weight: bold; color: black !important; }
    .col-num { width: 22px; }
    .col-g { width: 25px; }
    .col-an { width: 35px; }
    .col-e { width: 22px; background-color: #f1f2f6; }
    .col-dif { width: 45px; }
    .col-partido { width: auto; }
    .protocol-step {
        background-color: white; padding: 20px; border-radius: 10px;
        border-left: 6px solid #E67E22; margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .protocol-number { font-size: 1.5rem; font-weight: 900; color: #E67E22; margin-right: 10px; }
    .protocol-title { font-size: 1.1rem; font-weight: bold; color: #1a1a1a; text-transform: uppercase; }
    .protocol-text { color: #444; margin-top: 8px; font-size: 0.95rem; line-height: 1.4; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE APOYO (SIN CAMBIOS) ---
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

def generar_pdf(partidos, n_gallos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    zona_horaria = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(zona_horaria).strftime("%d/%m/%Y %H:%M:%S")
    data_header = [
        [Paragraph("<font color='white' size=22><b>DerbySystem</b></font>", styles['Title'])],
        [Paragraph("<font color='#E67E22' size=14><b>https://tuderby.streamlit.app</b></font>", styles['Normal'])],
        [Paragraph(f"<font color='white' size=9>REPORTE TÉCNICO DE COTEJO | {ahora}</font>", styles['Normal'])]
    ]
    header_table = Table(data_header, colWidths=[500])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('BACKGROUND', (0, 1), (-1, 2), colors.HexColor("#1a1a1a")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table); elements.append(Spacer(1, 20))
    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Heading2'])); elements.append(Spacer(1, 8))
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
                data.append([pelea_n, "[  ]", Paragraph(f"<b>{rojo['PARTIDO']}</b><br/><font size=8>({rojo[col_g]:.3f})</font>", styles['Normal']),
                             f"{an_r:03}", "[  ]", f"{d:.3f}", f"{an_v:03}", Paragraph(f"<b>{verde['PARTIDO']}</b><br/><font size=8>({verde[col_g]:.3f})</font>", styles['Normal']), "[  ]"])
                pelea_n += 1
            else: break
        t = Table(data, colWidths=[20, 30, 140, 30, 30, 40, 30, 140, 30])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1a1a")), ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E67E22")), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(t); elements.append(Spacer(1, 20))
    
    elements.append(Spacer(1, 40))
    data_firmas = [["__________________________", " ", "__________________________"], ["FIRMA JUEZ DE PLAZA", " ", "FIRMA MESA DE CONTROL"]]
    t_firmas = Table(data_firmas, colWidths=[200, 100, 200])
    t_firmas.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 9)]))
    elements.append(t_firmas); elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"<font color='grey' size=8>SISTEMA DE GESTIÓN DIGITAL - DerbySystem v2.0</font>", styles['Normal']))
    doc.build(elements)
    return buffer.getvalue()

# --- INTERFAZ POST-LOGIN ---
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title("DerbySystem ")

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
            p_val = st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True)
            st.write("") 
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        st.markdown("### ✏️ Tabla de Edición")
        display_data = []
        cont_anillo = 1
        for p in st.session_state.partidos:
            item = {"❌": False, "PARTIDO": p["PARTIDO"]}
            for i in range(1, st.session_state.n_gallos + 1):
                item[f"G{i}"] = p[f"G{i}"]; item[f"Anillo {i}"] = f"{cont_anillo:03}"
                cont_anillo += 1
            display_data.append(item)
        df = pd.DataFrame(display_data)
        config = {"❌": st.column_config.CheckboxColumn("B", default=False), "PARTIDO": st.column_config.TextColumn("Partido")}
        for i in range(1, st.session_state.n_gallos + 1):
            config[f"G{i}"] = st.column_config.NumberColumn(f"G{i}", format="%.3f"); config[f"Anillo {i}"] = st.column_config.TextColumn(f"A{i}", disabled=True)
        res = st.data_editor(df, column_config=config, use_container_width=True, num_rows="fixed", hide_index=True)
        if not res.equals(df):
            nuevos = []
            for _, r in res.iterrows():
                if not r["❌"]:
                    p_upd = {"PARTIDO": str(r["PARTIDO"]).upper()}
                    for i in range(1, st.session_state.n_gallos + 1): p_upd[f"G{i}"] = float(r[f"G{i}"])
                    nuevos.append(p_upd)
            st.session_state.partidos = nuevos; guardar(nuevos); st.rerun()
        
        if st.button("🚨 LIMPIAR TODO EL EVENTO", use_container_width=True):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        try:
            pdf_bytes = generar_pdf(st.session_state.partidos, st.session_state.n_gallos)
            st.download_button(label="📥 GENERAR REPORTE OFICIAL (PDF)", data=pdf_bytes, file_name="cotejo_oficial.pdf", mime="application/pdf", use_container_width=True, type="primary")
        except Exception as e: st.error(f"Error: {e}")
        st.divider()
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-final'><thead><tr><th class='col-num'>#</th><th class='col-g'>G</th><th class='col-partido'>ROJO</th><th class='col-an'>AN.</th><th class='col-e'>E</th><th class='col-dif'>DIF.</th><th class='col-an'>AN.</th><th class='col-partido'>VERDE</th><th class='col-g'>G</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g]); c = "style='background:#e74c3c;color:white;'" if d > TOLERANCIA else ""
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    html += f"<tr><td>{pelea_n}</td><td class='cuadro'>□</td><td style='border-left:3px solid red'><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-texto'>{rojo[col_g]:.3f}</span></td><td>{an_r:03}</td><td class='cuadro col-e'>□</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td style='border-right:3px solid green'><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-texto'>{verde[col_g]:.3f}</span></td><td class='cuadro'>□</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

with t_ayu:
    st.markdown("## 📖 Guía del Operador - DerbySystem")
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("""<div class="protocol-step"><span class="protocol-number">01</span><span class="protocol-title">Configuración</span><div class="protocol-text">Defina la modalidad en REGISTRO.</div></div>""", unsafe_allow_html=True)
    with col_der:
        st.markdown("""<div class="protocol-step"><span class="protocol-number">03</span><span class="protocol-title">Validación</span><div class="protocol-text">Revise pesos en COTEJO.</div></div>""", unsafe_allow_html=True)

with st.sidebar:
    st.write("Sesión activa: **SISTEMA PROTEGIDO**")
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.divider()
    acceso = st.text_input("Acceso Admin:", type="password")

if acceso == "28days":
    st.divider()
    archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
    for arch in archivos:
        with st.expander(f"Ver: {arch}"):
            with open(arch, "r") as f: st.text(f.read())
            if st.button("Eliminar", key=arch):
                os.remove(arch); st.rerun()
