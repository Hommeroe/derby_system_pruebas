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

# --- SIDEBAR: ACCESO DE ADMINISTRADOR (MOVIDO AL PRINCIPIO) ---
# Al ponerlo aquí, siempre tendrás control, estés en el login o adentro.
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.write("---")
    
    # Botón de Salir (Solo visible si hay usuario)
    if st.session_state.id_usuario != "":
        if st.button("🚪 SALIR DEL EVENTO", use_container_width=True): 
            st.session_state.clear()
            st.rerun()
        st.divider()
    
    # Tu puerta trasera de administrador
    acceso = st.text_input("Llave Maestra (Admin):", type="password")
    if acceso == "28days":
        st.subheader("📁 Visor de Eventos")
        
        # Escaneamos archivos
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        
        if not archivos:
            st.write("No hay eventos activos.")
            
        for arch in archivos:
            nombre_llave = arch.replace("datos_", "").replace(".txt", "")
            
            with st.expander(f"🔑 {nombre_llave}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    # --- LA CORRECCIÓN ESTÁ AQUÍ ---
                    if st.button("👁️ CARGAR", key=f"load_{arch}"):
                        st.session_state.id_usuario = nombre_llave
                        # Borramos la memoria para obligar a recargar los datos
                        if 'partidos' in st.session_state: del st.session_state['partidos']
                        if 'n_gallos' in st.session_state: del st.session_state['n_gallos']
                        st.rerun()
                with col_b:
                    if st.button("🗑️ BORRAR", key=f"del_{arch}"):
                        os.remove(arch)
                        if st.session_state.id_usuario == nombre_llave:
                             st.session_state.id_usuario = "" # Sacar al usuario si borras su evento
                        st.rerun()

# --- PANTALLA DE ENTRADA (SISTEMA DE LLAVES) ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .stApp { margin-top: -60px !important; }
        .block-container { padding-top: 2rem !important; }
        .login-card {
            max-width: 480px; margin: 0 auto; background: #ffffff;
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
        .llave-grande { 
            font-size: 2rem; color: #1a1a1a; background: #f0f2f6; 
            padding: 10px; border-radius: 8px; text-align: center; 
            border: 2px dashed #E67E22; margin: 15px 0; font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    col_1, col_center, col_3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="desc-box"><div style="color:#E67E22; font-weight:bold; font-size:0.85rem; margin-bottom:3px;">ACCESO RÁPIDO</div><div style="font-size:0.75rem; line-height:1.3; color:#ccc;">Sistema sin registros. Usa una <b>Llave de Evento</b> única.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="main-title">DerbySystem</div><div class="main-subtitle">PRO MANAGEMENT</div>', unsafe_allow_html=True)
        
        if not st.session_state.temp_llave:
            tab_entrar, tab_nuevo = st.tabs(["🔑 YA TENGO LLAVE", "✨ CREAR NUEVO"])
            
            with tab_entrar:
                llave_input = st.text_input("Introduce tu Llave:", placeholder="EJ: DERBY-XJ92").upper().strip()
                if st.button("ACCEDER AL SISTEMA", use_container_width=True):
                    if os.path.exists(f"datos_{llave_input}.txt"):
                        st.session_state.id_usuario = llave_input
                        # Limpiamos memoria por si acaso
                        if 'partidos' in st.session_state: del st.session_state['partidos']
                        st.rerun()
                    else:
                        st.error("Esa llave no existe. Verifica o crea un evento nuevo.")
            
            with tab_nuevo:
                st.write("Genera un identificador único para tu torneo.")
                if st.button("GENERAR LLAVE NUEVA", use_container_width=True):
                    chars = string.ascii_uppercase + string.digits
                    nueva = "DERBY-" + "".join(random.choices(chars, k=4))
                    while os.path.exists(f"datos_{nueva}.txt"):
                         nueva = "DERBY-" + "".join(random.choices(chars, k=4))
                    st.session_state.temp_llave = nueva
                    st.rerun()
        
        else:
            st.success("¡Evento Creado!")
            st.markdown(f'<div class="llave-grande">{st.session_state.temp_llave}</div>', unsafe_allow_html=True)
            st.info("⚠️ ANOTA ESTA LLAVE. Es la única forma de volver a entrar.")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("⬅️ CANCELAR", use_container_width=True):
                    st.session_state.temp_llave = None
                    st.rerun()
            with col_b2:
                if st.button("✅ ENTRAR", use_container_width=True, type="primary"):
                    with open(f"datos_{st.session_state.temp_llave}.txt", "w", encoding="utf-8") as f: pass
                    st.session_state.id_usuario = st.session_state.temp_llave
                    st.session_state.temp_llave = None
                    # Limpiamos memoria
                    if 'partidos' in st.session_state: del st.session_state['partidos']
                    st.rerun()
        
        st.markdown('<div class="login-footer">© 2026 DerbySystem PRO | Gestión Segura por Llaves</div>', unsafe_allow_html=True)
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
        t = Table(data, colWidths=[20, 30, 140, 30, 30, 40, 30, 140, 30, 140, 30])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1a1a")), ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E67E22")), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(t); elements.append(Spacer(1, 20))
    doc.build(elements); return buffer.getvalue()

# --- INTERFAZ PRINCIPAL ---
if 'partidos' not in st.session_state: st.session_state.partidos, st.session_state.n_gallos = cargar()
st.title(f"DerbySystem 🏆")
st.caption(f"LLAVE DE EVENTO: **{st.session_state.id_usuario}**")

t_reg, t_cot, t_ayu = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO", "📑 MANUAL DE OPERACIÓN"])

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
            col_g_cot = f"G{r}"; lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g_cot])
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
            <h1>Manual de Operación</h1>
            <p>Guía paso a paso para la gestión técnica del torneo</p>
        </div>
    """, unsafe_allow_html=True)

    row1_col1, row1_col2, row1_col3 = st.columns(3)
    with row1_col1:
        st.markdown("""
            <div class="card-tutorial">
                <div class="step-icon">⚙️</div>
                <div class="step-title">1. Configuración Inicial</div>
                <div class="step-text">
                    Vaya a <b>Registro</b> y elija la cantidad de gallos por partido. 
                </div>
            </div>
        """, unsafe_allow_html=True)
    with row1_col2:
        st.markdown("""
            <div class="card-tutorial">
                <div class="step-icon">⚖️</div>
                <div class="step-title">2. Captura de Pesos</div>
                <div class="step-text">
                    Ingrese el nombre del partido y el peso de cada gallo. El sistema asignará el <span class="highlight-anillo">anillo automático</span> correlativo.
                </div>
            </div>
        """, unsafe_allow_html=True)
    with row1_col3:
        st.markdown("""
            <div class="card-tutorial">
                <div class="step-icon">✏️</div>
                <div class="step-title">3. Edición de Datos</div>
                <div class="step-text">
                    Puede corregir nombres o pesos y el sistema recalculará los cotejos al instante.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    with st.expander("🔍 Reglas de Lógica del Sistema", expanded=True):
        st.markdown("""
        * **Anillos:** Se generan automáticamente de forma secuencial.
        * **Tolerancia:** El sistema marca en rojo diferencias de peso mayores a **80 gramos**.
        """)
