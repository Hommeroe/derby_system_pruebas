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

# --- PANTALLA DE ENTRADA (DISEÑO PROFESIONAL) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .main { background-color: #f4f7f6; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            border-radius: 5px 5px 0 0;
            padding: 10px 20px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    html_bienvenida = (
        "<div style='text-align:center; background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%); padding:40px; border-radius:20px; color:white; font-family:sans-serif; box-shadow: 0 10px 25px rgba(0,0,0,0.2);'>"
        "<div style='font-size:0.9rem; letter-spacing:4px; opacity:0.8; margin-bottom:10px;'>PLATAFORMA DE GESTIÓN</div>"
        "<div style='font-size:3.5rem; font-weight:900; line-height:1; margin-bottom:10px; color: #E67E22;'>DerbySystem</div>"
        "<div style='font-size:1.1rem; font-weight:300; margin-bottom:30px; opacity:0.9;'>Transparencia y precisión en cada sorteo.</div>"
        "<div style='background-color:rgba(255,255,255,0.05); padding:25px; border-radius:15px; margin:0 auto; max-width:550px; border:1px solid rgba(230,126,34,0.3); text-align:left;'>"
        "<div style='color:#E67E22; font-weight:bold; font-size:1.3rem; margin-bottom:10px; text-align:center;'>Módulo de Acceso</div>"
        "<div style='color:#f2f2f2; font-size:1rem; line-height:1.6; text-align:center;'>"
        "Inicie sesión para gestionar sus eventos. El sistema garantiza un emparejamiento inteligente basado en parámetros técnicos y pesos oficiales."
        "</div>"
        "</div></div>"
    )
    
    st.markdown(html_bienvenida, unsafe_allow_html=True)
    st.write("") 
    
    col_spacer_L, col_center, col_spacer_R = st.columns([0.25, 0.5, 0.25])
    
    with col_center:
        tab_login, tab_registro = st.tabs(["🔐 INICIAR SESIÓN", "📝 CREAR CUENTA"])
        
        with tab_login:
            usuario_login = st.text_input("USUARIO:", key="login_user").upper().strip()
            pass_login = st.text_input("CONTRASEÑA:", type="password", key="login_pass")
            if st.button("ACCEDER AL PANEL", use_container_width=True, key="btn_login"):
                if verificar_credenciales(usuario_login, pass_login):
                    if "partidos" in st.session_state: del st.session_state["partidos"]
                    st.session_state.id_usuario = usuario_login
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")

        with tab_registro:
            nuevo_usuario = st.text_input("NUEVO USUARIO:", key="reg_user").upper().strip()
            nueva_pass = st.text_input("CONTRASEÑA:", type="password", key="reg_pass")
            confirmar_pass = st.text_input("CONFIRMAR:", type="password", key="reg_pass_conf")
            if st.button("REGISTRAR CUENTA", use_container_width=True, key="btn_registro"):
                if nuevo_usuario and nueva_pass == confirmar_pass:
                    if registrar_usuario(nuevo_usuario, nueva_pass):
                        st.success("Cuenta creada. Ya puede iniciar sesión.")
                    else: st.warning("El usuario ya existe.")
    st.stop()

# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS DE INTERFAZ INTERNA (REDISEÑO PROFESIONAL) ---
st.markdown("""
    <style>
    /* Estilo General */
    .stApp { background-color: #f8fafc; }
    
    /* Botones Pro */
    div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #E67E22 0%, #D35400 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
        box-shadow: 0 4px 6px rgba(211, 84, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(211, 84, 0, 0.3) !important;
    }
    
    /* Etiquetas de Anillo */
    .caja-anillo {
        background-color: #1e293b; color: #fb923c; padding: 4px;
        border-radius: 0px 0px 8px 8px; font-weight: bold; 
        text-align: center; margin-top: -16px; border: 1px solid #334155;
        font-size: 0.85em; letter-spacing: 1px;
    }

    /* Headers de Ronda */
    .header-azul { 
        background: #1e293b; color: white; padding: 12px; 
        text-align: center; font-weight: 700; border-radius: 12px 12px 0 0;
        font-size: 16px; letter-spacing: 2px;
        border-bottom: 3px solid #E67E22;
    }

    /* Tablas de Cotejo Pro */
    .tabla-final { 
        width: 100%; border-collapse: separate; border-spacing: 0;
        background-color: white; border-radius: 0 0 12px 12px;
        overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        color: #1e293b !important;
    }
    .tabla-final th {
        background-color: #f1f5f9; color: #64748b;
        font-size: 11px; text-transform: uppercase; padding: 12px;
        border-bottom: 1px solid #e2e8f0;
    }
    .tabla-final td { 
        border-bottom: 1px solid #f1f5f9; text-align: center; 
        padding: 10px 5px; vertical-align: middle;
    }
    .nombre-partido { 
        font-weight: 800; font-size: 13px; color: #1e293b !important;
        display: block; text-transform: uppercase;
    }
    .peso-texto { font-size: 11px; color: #64748b !important; font-weight: 500;}
    
    /* Indicadores de Diferencia */
    .diff-badge {
        padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;
    }
    .diff-ok { background-color: #f1f5f9; color: #1e293b; }
    .diff-alert { background-color: #fee2e2; color: #ef4444; border: 1px solid #fecaca; }

    /* Protocolo de Operación */
    .protocol-step {
        background-color: white; padding: 25px; border-radius: 15px;
        border-top: 5px solid #E67E22; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONALIDAD (SIN CAMBIOS) ---
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
    data_header = [
        [Paragraph("<font color='white' size=22><b>DerbySystem PRO</b></font>", styles['Title'])],
        [Paragraph(f"<font color='white' size=9>REPORTE TÉCNICO | GENERADO: {ahora}</font>", styles['Normal'])]
    ]
    header_table = Table(data_header, colWidths=[500])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1e293b")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15), ('TOPPADDING', (0, 0), (-1, -1), 15),
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
                data.append([pelea_n, "[ ]", Paragraph(f"<b>{rojo['PARTIDO']}</b><br/>{rojo[col_g]:.3f}", styles['Normal']),
                             f"{an_r:03}", "[ ]", f"{d:.3f}", f"{an_v:03}", Paragraph(f"<b>{verde['PARTIDO']}</b><br/>{verde[col_g]:.3f}", styles['Normal']), "[ ]"])
                pelea_n += 1
            else: break
        t = Table(data, colWidths=[20, 25, 145, 30, 25, 40, 30, 145, 25])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")), ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#64748b")), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)]))
        elements.append(t); elements.append(Spacer(1, 20))
    doc.build(elements)
    return buffer.getvalue()

# --- INTERFAZ ---
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title("DerbySystem PRO")

t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO DE EVENTO", "🏆 PANEL DE COTEJO", "📑 PROTOCOLO"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    c1, c2 = st.columns([2,1])
    g_sel = c2.selectbox("GALLOS / PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Inscribir Partido # {len(st.session_state.partidos) + 1}")
        nombre = st.text_input("IDENTIFICACIÓN DEL PARTIDO:").upper().strip()
        f_cols = st.columns(g_sel)
        for i in range(g_sel):
            with f_cols[i]:
                p_val = st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
                st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True)
        if st.form_submit_button("💾 REGISTRAR PARTIDO EN BASE DE DATOS", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        st.divider()
        st.markdown("### 📊 Gestión de Inscritos")
        display_data = []
        cont_anillo = 1
        for p in st.session_state.partidos:
            item = {"ELIM.": False, "PARTIDO": p["PARTIDO"]}
            for i in range(1, st.session_state.n_gallos + 1):
                item[f"G{i}"] = p[f"G{i}"]; item[f"AN.{i}"] = f"{cont_anillo:03}"
                cont_anillo += 1
            display_data.append(item)
        df = pd.DataFrame(display_data)
        res = st.data_editor(df, use_container_width=True, hide_index=True)
        if not res.equals(df):
            nuevos = []
            for _, r in res.iterrows():
                if not r["ELIM."]:
                    p_upd = {"PARTIDO": str(r["PARTIDO"]).upper()}
                    for i in range(1, st.session_state.n_gallos + 1): p_upd[f"G{i}"] = float(r[f"G{i}"])
                    nuevos.append(p_upd)
            st.session_state.partidos = nuevos; guardar(nuevos); st.rerun()
        
        if st.button("🚨 REINICIAR TODO EL EVENTO", use_container_width=True):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        try:
            pdf_bytes = generar_pdf(st.session_state.partidos, st.session_state.n_gallos)
            st.download_button(label="📄 DESCARGAR REPORTE TÉCNICO (PDF)", data=pdf_bytes, file_name="cotejo.pdf", mime="application/pdf", use_container_width=True)
        except: st.error("Error al generar PDF")
        
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA DE COMBATE {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-final'><thead><tr><th>#</th><th>G</th><th style='text-align:left'>PARTIDO ROJO</th><th>AN.</th><th>E</th><th>DIF.</th><th>AN.</th><th style='text-align:right'>PARTIDO VERDE</th><th>G</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                    diff_class = "diff-alert" if d > TOLERANCIA else "diff-ok"
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    html += f"<tr><td>{pelea_n}</td><td>□</td><td style='text-align:left; border-left:4px solid #ef4444; padding-left:10px'><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-texto'>{rojo[col_g]:.3f}</span></td><td><b>{an_r:03}</b></td><td>□</td><td><span class='diff-badge {diff_class}'>{d:.3f}</span></td><td><b>{an_v:03}</b></td><td style='text-align:right; border-right:4px solid #22c55e; padding-right:10px'><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-texto'>{verde[col_g]:.3f}</span></td><td>□</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)
    else: st.info("Se requieren al menos 2 partidos para generar el cotejo.")

with t_ayu:
    st.markdown("### Protocolo de Operación Profesional")
    st.markdown("""
    <div class="protocol-step">
        <b style="color:#E67E22">1. Registro Técnico:</b> Ingrese los nombres de los partidos y pesos exactos. 
        El sistema genera un ID de anillo único e inalterable para cada gallo.
    </div>
    <div class="protocol-step">
        <b style="color:#E67E22">2. Algoritmo de Sorteo:</b> El sistema ordena por peso y busca el oponente más cercano, 
        asegurando que ningún partido pelee contra sí mismo en la misma ronda.
    </div>
    <div class="protocol-step">
        <b style="color:#E67E22">3. Certificación:</b> Las celdas rojas indican una diferencia mayor a 80g. 
        Genere el PDF oficial para la firma de los jueces de plaza.
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### **DerbySystem PRO**")
    st.caption(f"Operador: {st.session_state.id_usuario}")
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
        st.session_state.clear(); st.rerun()
    st.divider()
    acceso = st.text_input("Admin Key:", type="password")

if acceso == "28days":
    archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
    for arch in archivos:
        with st.expander(f"Data: {arch}"):
            if st.button("Borrar", key=arch): os.remove(arch); st.rerun()
