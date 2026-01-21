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
    return usuario in users and users[usuario] == hash_password(password)

def registrar_usuario(usuario, password):
    users = cargar_usuarios()
    if usuario in users: return False 
    users[usuario] = hash_password(password)
    guardar_usuario_db(users)
    return True

# --- LÓGICA DE ACCESO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

if st.session_state.id_usuario == "":
    html_bienvenida = (
        "<div style='text-align:center; background: linear-gradient(135deg, #E67E22 0%, #D35400 100%); padding:30px; border-radius:15px; color:white; font-family:sans-serif;'>"
        "<div style='font-size:2.5rem; font-weight:900;'>DerbySystem</div>"
        "<div style='background-color:rgba(0,0,0,0.2); padding:15px; border-radius:10px; margin:10px auto; max-width:500px;'>"
        "Plataforma de sorteo digital con emparejamiento inteligente."
        "</div></div>"
    )
    st.markdown(html_bienvenida, unsafe_allow_html=True)
    
    col_spacer_L, col_center, col_spacer_R = st.columns([0.1, 0.8, 0.1])
    with col_center:
        tab_login, tab_registro = st.tabs(["🔐 ENTRAR", "📝 REGISTRARSE"])
        with tab_login:
            u = st.text_input("USUARIO:", key="l_u").upper().strip()
            p = st.text_input("CONTRASEÑA:", type="password", key="l_p")
            if st.button("INGRESAR", use_container_width=True):
                if verificar_credenciales(u, p):
                    st.session_state.id_usuario = u
                    st.rerun()
                else: st.error("Acceso denegado.")
        with tab_registro:
            nu = st.text_input("NUEVO USUARIO:", key="r_u").upper().strip()
            np = st.text_input("CONTRASEÑA:", type="password", key="r_p")
            if st.button("CREAR CUENTA", use_container_width=True):
                if nu and np:
                    if registrar_usuario(nu, np): st.success("Cuenta creada.")
                    else: st.warning("El usuario ya existe.")
    st.stop()

# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS DE INTERFAZ ---
st.markdown("""
    <style>
    /* Estilo de Botones */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(135deg, #E67E22 0%, #D35400 100%) !important;
        color: white !important; font-weight: bold !important; border-radius: 10px !important; border: none !important;
    }
    
    /* Contenedor de Anillos (Registro) */
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0px 0px 8px 8px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400;
        font-size: 0.8em;
    }

    /* Diseño Profesional de Rondas (Cotejo) */
    .header-ronda { 
        background-color: #1e293b; color: white; padding: 12px; 
        text-align: center; font-weight: 800; border-radius: 10px 10px 0 0;
        font-size: 16px; margin-top: 20px; border-bottom: 3px solid #E67E22;
        letter-spacing: 1px;
    }
    .tabla-final { 
        width: 100%; border-collapse: collapse; background-color: white; 
        table-layout: fixed; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 0 0 10px 10px; overflow: hidden;
    }
    .tabla-final th { 
        background-color: #f8fafc; color: #64748b; font-size: 11px; 
        text-transform: uppercase; padding: 10px 5px; border-bottom: 1px solid #e2e8f0;
    }
    .tabla-final td { 
        border-bottom: 1px solid #f1f5f9; text-align: center; 
        padding: 12px 2px; vertical-align: middle; color: #1e293b;
    }
    .nombre-partido { 
        font-weight: 800; font-size: 13px; line-height: 1.1;
        display: block; color: #0f172a;
    }
    .peso-texto { font-size: 11px; color: #64748b; font-weight: 500;}
    
    /* Badges de Diferencia */
    .diff-badge {
        padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 11px;
    }
    .diff-ok { background-color: #f1f5f9; color: #475569; }
    .diff-alert { background-color: #fee2e2; color: #ef4444; border: 1px solid #fecaca; }

    /* Protocolo */
    .protocol-step {
        background-color: white; padding: 20px; border-radius: 12px;
        border-left: 6px solid #E67E22; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES TÉCNICAS ---
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
    
    # Header del PDF
    header_data = [[Paragraph("<font color='white' size=20><b>DerbySystem PRO</b></font>", styles['Title']), 
                    Paragraph(f"<font color='white' size=8>REPORTE TÉCNICO<br/>{ahora}</font>", styles['Normal'])]]
    header_table = Table(header_data, colWidths=[350, 150])
    header_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1e293b")), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 10)]))
    elements.append(header_table); elements.append(Spacer(1, 20))

    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Heading2']))
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
                data.append([pelea_n, "[ ]", Paragraph(f"<b>{rojo['PARTIDO']}</b><br/>{rojo[col_g]:.3f}", styles['Normal']),
                             f"{an_r:03}", "[ ]", f"{d:.3f}", f"{an_v:03}", Paragraph(f"<b>{verde['PARTIDO']}</b><br/>{verde[col_g]:.3f}", styles['Normal']), "[ ]"])
                pelea_n += 1
            else: break
        t = Table(data, colWidths=[20, 25, 150, 30, 25, 35, 30, 150, 25])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(t); elements.append(Spacer(1, 20))
    
    doc.build(elements)
    return buffer.getvalue()

# --- INTERFAZ ---
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title("DerbySystem PRO")

t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📑 PROTOCOLO"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("MODALIDAD:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        f_cols = st.columns(min(g_sel, 4))
        for i in range(g_sel):
            with f_cols[i % 4]:
                st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
                st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True)
                st.write("") 
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        st.divider()
        df = pd.DataFrame(st.session_state.partidos)
        res = st.data_editor(df, use_container_width=True, hide_index=True)
        if not res.equals(df):
            st.session_state.partidos = res.to_dict('records'); guardar(st.session_state.partidos); st.rerun()
        if st.button("🚨 BORRAR EVENTO", use_container_width=True):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        pdf_bytes = generar_pdf(st.session_state.partidos, st.session_state.n_gallos)
        st.download_button(label="📥 DESCARGAR REPORTE TÉCNICO (PDF)", data=pdf_bytes, file_name="cotejo_oficial.pdf", mime="application/pdf", use_container_width=True)
        
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-ronda'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-final'><thead><tr><th width='25'>#</th><th width='30'>G</th><th>PARTIDO ROJO</th><th width='40'>AN.</th><th width='30'>E</th><th width='60'>DIF.</th><th width='40'>AN.</th><th>PARTIDO VERDE</th><th width='30'>G</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    badge_cls = "diff-alert" if d > TOLERANCIA else "diff-ok"
                    html += f"<tr><td>{pelea_n}</td><td>□</td><td style='border-left:4px solid #ef4444; text-align:left; padding-left:10px;'><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-texto'>{rojo[col_g]:.3f}</span></td><td><b>{an_r:03}</b></td><td>□</td><td><span class='diff-badge {badge_cls}'>{d:.3f}</span></td><td><b>{an_v:03}</b></td><td style='border-right:4px solid #22c55e; text-align:right; padding-right:10px;'><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-texto'>{verde[col_g]:.3f}</span></td><td>□</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

with t_ayu:
    st.markdown("### Guía Operativa")
    st.info("Siga el protocolo para garantizar la transparencia del Derby.")

with st.sidebar:
    st.caption(f"Sesión: {st.session_state.id_usuario}")
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
        st.session_state.clear(); st.rerun()
