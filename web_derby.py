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
    st.markdown("""
        <div style='text-align:center; background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%); padding:40px; border-radius:20px; color:white; box-shadow: 0 10px 25px rgba(0,0,0,0.2);'>
            <h1 style='color: #E67E22; margin-bottom:10px;'>DerbySystem</h1>
            <p style='opacity:0.9;'>Transparencia y precisión en cada sorteo digital.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_spacer_L, col_center, col_spacer_R = st.columns([0.1, 0.8, 0.1])
    with col_center:
        t1, t2 = st.tabs(["🔐 LOGIN", "📝 REGISTRO"])
        with t1:
            u = st.text_input("USUARIO:").upper().strip()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.button("ACCEDER", use_container_width=True):
                if verificar_credenciales(u, p):
                    st.session_state.id_usuario = u
                    st.rerun()
                else: st.error("Error de acceso.")
        with t2:
            nu = st.text_input("NUEVO USUARIO:").upper().strip()
            np = st.text_input("NUEVA CONTRASEÑA:", type="password")
            if st.button("CREAR CUENTA", use_container_width=True):
                if nu and np:
                    if registrar_usuario(nu, np): st.success("Creado. Inicie sesión.")
                    else: st.warning("Ya existe.")
    st.stop()

# --- CONSTANTES Y ESTILOS ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

st.markdown("""
    <style>
    /* Ajuste para que el contenido use todo el ancho en móviles */
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    
    /* Botones Pro */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(135deg, #E67E22 0%, #D35400 100%) !important;
        color: white !important; font-weight: bold !important; border-radius: 10px !important;
        border: none !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    /* Headers de Ronda ajustados */
    .header-ronda { 
        background: #1e293b; color: #E67E22; padding: 10px; 
        text-align: center; font-weight: 800; border-radius: 8px 8px 0 0;
        font-size: 14px; letter-spacing: 1px; border-bottom: 2px solid #E67E22;
        margin-top: 15px;
    }

    /* Tablas Compactas para mejor ajuste a pantalla */
    .tabla-final { 
        width: 100%; border-collapse: collapse; background: white; 
        font-size: 11px; table-layout: fixed;
    }
    .tabla-final th {
        background: #f8fafc; color: #64748b; padding: 8px 2px;
        border-bottom: 1px solid #e2e8f0; font-size: 10px;
    }
    .tabla-final td { 
        padding: 8px 2px; border-bottom: 1px solid #f1f5f9; text-align: center;
        word-wrap: break-word; overflow-wrap: break-word;
    }
    .nombre-partido { font-weight: 800; color: #1e293b; display: block; line-height: 1;}
    .peso-texto { font-size: 9px; color: #64748b; font-weight: 500;}
    
    /* Badges */
    .diff-badge { padding: 2px 4px; border-radius: 4px; font-weight: bold; font-size: 10px; }
    .diff-ok { background: #f1f5f9; color: #1e293b; }
    .diff-alert { background: #fee2e2; color: #ef4444; }

    /* Estilo de anillos */
    .caja-anillo {
        background: #1e293b; color: #fb923c; padding: 3px;
        border-radius: 0 0 8px 8px; font-weight: bold; text-align: center;
        margin-top: -16px; border: 1px solid #334155; font-size: 0.8em;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
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

# --- PDF MEJORADO ---
def generar_pdf_pro(partidos, n_gallos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    zona_horaria = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(zona_horaria).strftime("%d/%m/%Y %H:%M")
    
    # Encabezado PDF elegante
    header_data = [[Paragraph("<font color='white' size=18><b>DerbySystem PRO</b></font>", styles['Title']), 
                    Paragraph(f"<font color='white' size=8>REPORTE OFICIAL COTEJO<br/>{ahora}</font>", styles['Normal'])]]
    h_table = Table(header_data, colWidths=[380, 120])
    h_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1e293b")), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 12)]))
    elements.append(h_table); elements.append(Spacer(1, 15))

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
                
                data.append([pelea_n, "[ ]", Paragraph(f"<b>{rojo['PARTIDO']}</b><br/><font size=7>Peso: {rojo[col_g]:.3f}</font>", styles['Normal']),
                             f"{an_r:03}", "[ ]", f"{d:.3f}", f"{an_v:03}", Paragraph(f"<b>{verde['PARTIDO']}</b><br/><font size=7>Peso: {verde[col_g]:.3f}</font>", styles['Normal']), "[ ]"])
                pelea_n += 1
            else: break
            
        t = Table(data, colWidths=[20, 25, 150, 30, 25, 35, 30, 150, 25])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#64748b")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        elements.append(t); elements.append(Spacer(1, 15))
    
    doc.build(elements)
    return buffer.getvalue()

# --- INTERFAZ ---
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📑 PROTOCOLO"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    c1, c2 = st.columns([1,1])
    with c2: g_sel = st.selectbox("GALLOS/PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("NOMBRE PARTIDO:").upper().strip()
        f_cols = st.columns(min(g_sel, 3)) # Adaptable a pantalla
        for i in range(g_sel):
            with f_cols[i % 3]:
                st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
                st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales+i+1):03}</div>", unsafe_allow_html=True)
        if st.form_submit_button("💾 GUARDAR", use_container_width=True):
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
        if st.button("🚨 LIMPIAR EVENTO", use_container_width=True):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        pdf = generar_pdf_pro(st.session_state.partidos, st.session_state.n_gallos)
        st.download_button("📥 DESCARGAR REPORTE (PDF)", data=pdf, file_name="cotejo.pdf", use_container_width=True)
        
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-ronda'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-final'><thead><tr><th width='20'>#</th><th width='25'>G</th><th>ROJO</th><th width='35'>AN.</th><th width='25'>E</th><th width='40'>DIF.</th><th width='35'>AN.</th><th>VERDE</th><th width='25'>G</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    badge = "diff-alert" if d > TOLERANCIA else "diff-ok"
                    html += f"<tr><td>{pelea_n}</td><td>□</td><td style='border-left:3px solid #ef4444; text-align:left; padding-left:5px;'><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-texto'>{rojo[col_g]:.3f}</span></td><td><b>{an_r:03}</b></td><td>□</td><td><span class='diff-badge {badge}'>{d:.3f}</span></td><td><b>{an_v:03}</b></td><td style='border-right:3px solid #22c55e; text-align:right; padding-right:5px;'><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-texto'>{verde[col_g]:.3f}</span></td><td>□</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

with t_ayu:
    st.info("Sistema configurado para emparejamiento automático por peso y transparencia total.")

with st.sidebar:
    st.write(f"Operador: **{st.session_state.id_usuario}**")
    if st.button("🚪 SALIR", use_container_width=True): st.session_state.clear(); st.rerun()
