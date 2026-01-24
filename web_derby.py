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

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- INICIALIZACIÓN DE ESTADO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""
if "temp_llave" not in st.session_state:
    st.session_state.temp_llave = None

# --- SIDEBAR: ADMINISTRADOR ---
with st.sidebar:
    st.markdown("### 🛠️ PANEL ADMIN")
    if st.session_state.id_usuario != "":
        if st.button("🚪 FINALIZAR SESIÓN", use_container_width=True): 
            st.session_state.clear()
            st.rerun()
        st.divider()
    
    acceso = st.text_input("Llave Maestra:", type="password")
    if acceso == "28days":
        st.subheader("📁 Eventos en Servidor")
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

# --- PANTALLA DE BIENVENIDA (DISEÑO PROFESIONAL SIN FONDO NEGRO) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .stApp {
            background-color: #f0f2f6;
            background-image: linear-gradient(180deg, #ffffff 0%, #d7dde8 100%);
        }
        .login-box {
            max-width: 450px;
            margin: 80px auto;
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            text-align: center;
            border-bottom: 5px solid #E67E22;
        }
        .main-title {
            color: #2c3e50;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0px;
        }
        .main-title span { color: #E67E22; }
        .subtitle {
            color: #7f8c8d;
            letter-spacing: 2px;
            font-size: 0.8rem;
            text-transform: uppercase;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Derby<span>System</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Gestión de Combates Profesional</p>', unsafe_allow_html=True)

    if not st.session_state.temp_llave:
        t1, t2 = st.tabs(["INGRESAR", "CREAR EVENTO"])
        with t1:
            llave_input = st.text_input("Código de Acceso:", placeholder="DERBY-XXXX").upper().strip()
            if st.button("ABRIR PANEL", use_container_width=True, type="primary"):
                if os.path.exists(f"datos_{llave_input}.txt"):
                    st.session_state.id_usuario = llave_input
                    if 'partidos' in st.session_state: del st.session_state['partidos']
                    st.rerun()
                else: st.error("Llave no encontrada.")
        with t2:
            if st.button("GENERAR NUEVA LLAVE", use_container_width=True):
                nueva = "DERBY-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
                st.session_state.temp_llave = nueva
                st.rerun()
    else:
        st.success("Llave Generada con Éxito")
        st.code(st.session_state.temp_llave)
        if st.button("COMENZAR AHORA", use_container_width=True, type="primary"):
            with open(f"datos_{st.session_state.temp_llave}.txt", "w", encoding="utf-8") as f: pass
            st.session_state.id_usuario = st.session_state.temp_llave
            st.session_state.temp_llave = None
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- LÓGICA Y ESTILOS INTERNOS (INTACTOS) ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

st.markdown("""
    <style>
    div.stButton > button { background-color: #E67E22 !important; color: white !important; border-radius: 8px !important; }
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400; font-size: 0.8em;
    }
    .header-azul { 
        background-color: #1a1a1a; color: #E67E22; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px; border-bottom: 2px solid #E67E22;
    }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; color: black !important; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 5px; font-size: 11px; }
    
    /* ESTILO MANUAL MEJORADO */
    .manual-card {
        background: white; border-left: 5px solid #E67E22; padding: 15px;
        border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;
    }
    .manual-title { color: #E67E22; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# Funciones de carga/guardado/PDF permanecen iguales...
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
                   [Paragraph("<font color='#E67E22' size=14><b>Reporte Oficial de Cotejo</b></font>", styles['Normal'])],
                   [Paragraph(f"<font color='white' size=9>{ahora}</font>", styles['Normal'])]]
    header_table = Table(data_header, colWidths=[500])
    header_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.black), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
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
                data.append([pelea_n, "[  ]", rojo['PARTIDO'], f"{an_r:03}", "[  ]", f"{d:.3f}", f"{an_v:03}", verde['PARTIDO'], "[  ]"])
                pelea_n += 1
            else: break
        t = Table(data, colWidths=[20, 25, 145, 30, 25, 40, 30, 145, 25])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1a1a")), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTSIZE', (0,0), (-1,-1), 8), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        elements.append(t); elements.append(Spacer(1, 20))
    doc.build(elements); return buffer.getvalue()

if 'partidos' not in st.session_state: st.session_state.partidos, st.session_state.n_gallos = cargar()

# Títulos del Sistema
st.title("DerbySystem PRO 🏆")
st.info(f"Evento Activo: {st.session_state.id_usuario}")

t_reg, t_cot, t_man = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📑 MANUAL"])

with t_reg:
    # Lógica de registro intacta...
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g_reg = st.columns([2,1])
    g_sel = col_g_reg.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader("Nuevo Partido")
        nombre = st.text_input("NOMBRE PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True); st.write("") 
        if st.form_submit_button("💾 GUARDAR", use_container_width=True):
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
        config = {"❌": st.column_config.CheckboxColumn("B"), "PARTIDO": st.column_config.TextColumn("Partido")}
        for i in range(1, st.session_state.n_gallos + 1):
            config[f"G{i}"] = st.column_config.NumberColumn(f"G{i}", format="%.3f"); config[f"Anillo {i}"] = st.column_config.TextColumn(f"A{i}", disabled=True)
        res = st.data_editor(df, column_config=config, use_container_width=True, hide_index=True)
        if not res.equals(df):
            nuevos = []
            for _, r in res.iterrows():
                if not r["❌"]:
                    p_upd = {"PARTIDO": str(r["PARTIDO"]).upper()}
                    for i in range(1, st.session_state.n_gallos + 1): p_upd[f"G{i}"] = float(r[f"G{i}"])
                    nuevos.append(p_upd)
            st.session_state.partidos = nuevos; guardar(nuevos); st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        pdf_b = generar_pdf(st.session_state.partidos, st.session_state.n_gallos)
        st.download_button("📥 DESCARGAR COTEJO PDF", data=pdf_b, file_name="cotejo.pdf", use_container_width=True)
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g_cot = f"G{r}"; lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g_cot])
            html = """<table class='tabla-final'><thead><tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>E</th><th>DIF.</th><th>AN.</th><th>VERDE</th><th>G</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g_cot] - verde[col_g_cot]); c = "style='background:#ffcccc;'" if d > TOLERANCIA else ""
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    html += f"<tr><td>{pelea_n}</td><td>□</td><td><b>{rojo['PARTIDO']}</b><br>{rojo[col_g_cot]:.3f}</td><td>{an_r:03}</td><td>□</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td><b>{verde['PARTIDO']}</b><br>{verde[col_g_cot]:.3f}</td><td>□</td></tr>"; pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

with t_man:
    st.markdown("### 📘 Guía de Uso Rápido")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="manual-card">
            <div class="manual-title">1. Configuración de Gallos</div>
            <p>Antes de registrar, selecciona cuántos gallos pelea cada partido (2 a 6). Una vez registrado el primer partido, esta opción se bloquea para mantener la consistencia.</p>
        </div>
        <div class="manual-card">
            <div class="manual-title">2. Registro de Pesos</div>
            <p>Ingresa el nombre del partido y los pesos. El sistema asigna el <b>Anillo Automático</b> correlativo basado en el orden de llegada.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="manual-card">
            <div class="manual-title">3. Sistema de Cotejo</div>
            <p>El algoritmo empareja por peso similar (menor a mayor) evitando peleas contra el mismo socio. Las diferencias > 0.080kg se marcan en color de advertencia.</p>
        </div>
        <div class="manual-card">
            <div class="manual-title">4. Edición y Borrado</div>
            <p>En la tabla inferior de Registro, marca la casilla ❌ para eliminar un partido o edita directamente los pesos si hubo un error de captura.</p>
        </div>
        """, unsafe_allow_html=True)
