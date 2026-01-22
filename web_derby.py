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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

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

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def verificar_credenciales(usuario, password):
    users = cargar_usuarios()
    return usuario in users and users[usuario] == hash_password(password)

def registrar_usuario(usuario, password):
    users = cargar_usuarios()
    if usuario in users: return False 
    users[usuario] = hash_password(password)
    guardar_usuario_db(users)
    return True

if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- PANTALLA DE ENTRADA (SOLO CAMBIO DE CSS PARA EL RECTÁNGULO) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        /* ELIMINA EL ENCABEZADO Y EL ESPACIO BLANCO SUPERIOR */
        [data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container {
            padding-top: 0px !important;
            margin-top: -30px !important;
        }
        #root > div:nth-child(1) > div > div > div > div > section > div {
            padding-top: 0rem !important;
        }
        
        .login-card {
            max-width: 480px; 
            margin: 0 auto;
            background: #ffffff;
            padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-top: 5px solid #E67E22;
        }
        .desc-box {
            background-color: #1a1a1a; color: #f2f2f2; padding: 12px;
            border-radius: 8px; margin-bottom: 15px; text-align: center;
        }
        .main-title {
            font-size: 2.4rem; font-weight: 800; color: #E67E22;
            text-align: center; margin-bottom: 0px;
        }
        .main-subtitle {
            font-size: 0.75rem; color: #888; text-align: center;
            letter-spacing: 3px; margin-bottom: 15px; text-transform: uppercase;
        }
        .login-footer {
            text-align: center; font-size: 0.7rem; color: #999;
            margin-top: 25px; border-top: 1px solid #eee; padding-top: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    col_1, col_center, col_3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="desc-box"><div style="color:#E67E22; font-weight:bold; font-size:0.85rem; margin-bottom:3px;">¿QUÉ ES ESTE SISTEMA?</div><div style="font-size:0.75rem; line-height:1.3; color:#ccc;">Plataforma de <b>sorteo digital</b> que garantiza transparencia y combates gallisticos justos.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="main-title">DerbySystem</div><div class="main-subtitle">PRO MANAGEMENT</div>', unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["🔒 ACCESO", "📝 REGISTRO"])
        with tab_login:
            u = st.text_input("Usuario", key="l_u", placeholder="USUARIO").upper().strip()
            p = st.text_input("Contraseña", key="l_p", type="password", placeholder="••••••••")
            if st.button("ENTRAR AL SISTEMA", use_container_width=True):
                if verificar_credenciales(u, p):
                    st.session_state.id_usuario = u
                    st.rerun()
                else: st.error("Credenciales incorrectas")
        with tab_reg:
            nu = st.text_input("Nuevo Usuario", key="r_u", placeholder="NUEVO USUARIO").upper().strip()
            np = st.text_input("Nueva Pass", key="r_p", type="password", placeholder="CONTRASEÑA")
            cp = st.text_input("Confirma Pass", key="r_c", type="password", placeholder="CONFIRMAR")
            if st.button("REGISTRAR CUENTA", use_container_width=True):
                if nu and np == cp:
                    if registrar_usuario(nu, np): st.success("Registrado correctamente")
                    else: st.warning("El usuario ya existe")
        
        st.markdown('<div class="login-footer">© 2026 DerbySystem PRO | Plataforma Actualizada | Gestión Segura</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS INTERNOS ---
st.markdown("""
    <style>
    div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
        background-color: #E67E22 !important; color: white !important; font-weight: bold !important;
        border-radius: 8px !important; border: none !important;
    }
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400; font-size: 0.8em;
    }
    .header-azul { 
        background-color: #1a1a1a; color: #E67E22; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 14px; margin-bottom: 5px; border-bottom: 2px solid #E67E22;
    }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; table-layout: fixed; color: black !important; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 5px 2px; color: black !important; font-size: 11px; }
    .nombre-partido { font-weight: bold; font-size: 10px; line-height: 1.1; display: block; color: black !important; }
    .peso-texto { font-size: 10px; color: #2c3e50 !important; display: block; }
    .col-num { width: 22px; } .col-g { width: 25px; } .col-an { width: 35px; } 
    .col-e { width: 22px; background-color: #f1f2f6; } .col-dif { width: 45px; }
    
    .tutorial-header {
        background: #1a1a1a; color: #E67E22; padding: 20px;
        border-radius: 10px; text-align: center; border-left: 10px solid #E67E22;
        margin-bottom: 25px;
    }
    .card-tutorial {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 4px solid #E67E22;
        height: 100%; transition: 0.3s;
    }
    .card-tutorial:hover { transform: translateY(-5px); }
    .step-icon { font-size: 2.5rem; margin-bottom: 10px; }
    .step-title { font-weight: 900; color: #1a1a1a; font-size: 1.1rem; margin-bottom: 10px; }
    .step-text { font-size: 0.9rem; color: #555; line-height: 1.4; }
    .highlight-anillo { color: #E67E22; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
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
    elements, styles = [], getSampleStyleSheet()
    style_center = ParagraphStyle(name='Center', parent=styles['Normal'], alignment=TA_CENTER)
    ahora = datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S")
    
    data_header = [[Paragraph("<font color='white' size=22><b>DerbySystem</b></font>", styles['Title'])],
                   [Paragraph("<font color='#E67E22' size=14><b>https://tuderby.streamlit.app</b></font>", styles['Normal'])],
                   [Paragraph(f"<font color='white' size=9>REPORTE TÉCNICO DE COTEJO | {ahora}</font>", styles['Normal'])]]
    header_table = Table(data_header, colWidths=[500])
    header_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.black), ('BACKGROUND', (0,1), (-1,2), colors.HexColor("#1a1a1a")), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(header_table); elements.append(Spacer(1, 20))
    
    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Heading2']))
        col_g = f"G{r}"; lista = sorted([dict(p) for p in partidos], key=lambda x: x[col_g])
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
                rojo_p = Paragraph(f"<b>{rojo['PARTIDO']}</b><br/><font size=8>({rojo[col_g]:.3f})</font>", style_center)
                verde_p = Paragraph(f"<b>{verde['PARTIDO']}</b><br/><font size=8>({verde[col_g]:.3f})</font>", style_center)
                data.append([pelea_n, "[  ]", rojo_p, f"{an_r:03}", "[  ]", f"{d:.3f}", f"{an_v:03}", verde_p, "[  ]"])
                pelea_n += 1
            else: break
        t = Table(data, colWidths=[20, 30, 140, 30, 30, 40, 30, 140, 30])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1a1a")), ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E67E22")), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(t); elements.append(Spacer(1, 20))
    doc.build(elements); return buffer.getvalue()

# --- INTERFAZ ---
if 'partidos' not in st.session_state: st.session_state.partidos, st.session_state.n_gallos = cargar()
st.title("DerbySystem ")
t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO", "📑 PROTOCOLO DE OPERACIÓN"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g_reg = st.columns([2,1])
    g_sel = col_g_reg.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Añadir Partido # {len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True); st.write("") 
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
                item[f"G{i}"] = p[f"G{i}"]; item[f"Anillo {i}"] = f"{cont_anillo:03}"; cont_anillo += 1
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
            st.download_button(label="📥 GENERAR PDF OFICIAL", data=pdf_bytes, file_name="cotejo.pdf", mime="application/pdf", use_container_width=True, type="primary")
        except: st.error("Error al generar PDF")
        st.divider()
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g_cot = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g_cot])
            html = """<table class='tabla-final'><thead><tr><th class='col-num'>#</th><th class='col-g'>G</th><th>ROJO</th><th class='col-an'>AN.</th><th class='col-e'>E</th><th class='col-dif'>DIF.</th><th class='col-an'>AN.</th><th>VERDE</th><th class='col-g'>G</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g_cot] - verde[col_g_cot]); c = "style='background:#e74c3c;color:white;'" if d > TOLERANCIA else ""
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    html += f"<tr><td>{pelea_n}</td><td>□</td><td style='border-left:3px solid red'><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-texto'>{rojo[col_g_cot]:.3f}</span></td><td>{an_r:03}</td><td class='col-e'>□</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td style='border-right:3px solid green'><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-texto'>{verde[col_g_cot]:.3f}</span></td><td>□</td></tr>"; pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

with t_ayu:
    st.markdown("""
        <div class="tutorial-header">
            <h1>Manual de Operación Maestro</h1>
            <p>Guía paso a paso para la gestión técnica del torneo</p>
        </div>
    """, unsafe_allow_html=True)
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1: st.markdown('<div class="card-tutorial"><div class="step-icon">⚙️</div><div class="step-title">1. Configuración</div><div class="step-text">Defina la cantidad de gallos en Registro. Se bloquea al guardar el primer partido.</div></div>', unsafe_allow_html=True)
    with r1c2: st.markdown('<div class="card-tutorial"><div class="step-icon">⚖️</div><div class="step-title">2. Captura</div><div class="step-text">Ingrese pesos. El sistema asigna el <span class="highlight-anillo">anillo automático</span> correlativo.</div></div>', unsafe_allow_html=True)
    with r1c3: st.markdown('<div class="card-tutorial"><div class="step-icon">✏️</div><div class="step-title">3. Edición</div><div class="step-text">Use la tabla para corregir errores. Todo se recalcula al instante.</div></div>', unsafe_allow_html=True)
    st.write("")
    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1: st.markdown('<div class="card-tutorial"><div class="step-icon">📊</div><div class="step-title">4. Cotejo</div><div class="step-text">Emparejamiento inteligente que evita peleas entre el mismo partido.</div></div>', unsafe_allow_html=True)
    with r2c2: st.markdown('<div class="card-tutorial"><div class="step-icon">📄</div><div class="step-title">5. PDF</div><div class="step-text">Genere el reporte oficial con todos los datos validados para los jueces.</div></div>', unsafe_allow_html=True)
    with r2c3: st.markdown('<div class="card-tutorial"><div class="step-icon">🧹</div><div class="step-title">6. Cierre</div><div class="step-text">Limpie los datos al terminar para preparar el siguiente evento.</div></div>', unsafe_allow_html=True)
    st.divider()
    with st.expander("🔍 Reglas de Lógica", expanded=True):
        st.markdown("* **Anillos:** Secuenciales automáticos. [cite: 2026-01-14]\n* **Tolerancia:** Alerta roja en diferencias > 0.080.\n* **Filtro:** Nunca empareja socios iguales.")

with st.sidebar:
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True): st.session_state.clear(); st.rerun()
    st.divider(); acceso = st.text_input("Acceso Admin:", type="password")
    if acceso == "28days":
        u_db = cargar_usuarios(); st.json(u_db) if u_db else None
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for arch in archivos:
            with st.expander(f"📄 {arch}"):
                try:
                    with open(arch, "r", encoding="utf-8") as f: st.code(f.read())
                    if st.button("Eliminar", key=f"del_{arch}"): os.remove(arch); st.rerun()
                except: st.error("Error")
