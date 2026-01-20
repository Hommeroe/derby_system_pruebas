import streamlit as st
import pandas as pd
import os
import uuid
import re
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

# --- LÓGICA DE ACCESO SEGURO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- PANTALLA DE ENTRADA ---
if st.session_state.id_usuario == "":
    html_bienvenida = (
        "<div style='text-align:center; background-color:#E67E22; padding:25px; border-radius:15px; color:white; font-family:sans-serif;'>"
        "<div style='font-size:1.1rem; letter-spacing:2px; margin-bottom:5px;'>BIENVENIDOS A</div>"
        "<div style='font-size:2.2rem; font-weight:900; line-height:1; margin-bottom:20px;'>DerbySystem</div>"
        "<div style='background-color:#1a1a1a; padding:20px; border-radius:12px; margin:0 auto; max-width:500px; border:1px solid #D35400; text-align:left;'>"
        "<div style='color:#E67E22; font-weight:bold; font-size:1.2rem; margin-bottom:10px; text-align:center;'>¿Qué es este sistema?</div>"
        "<div style='color:#f2f2f2; font-size:0.95rem; line-height:1.5; text-align:center;'>"
        "Plataforma de <b>sorteo digital.</b> Garantiza transparencia total, orden y combates gallisticos 100% justos mediante tecnología de emparejamiento inteligente."
        "</div>"
        "<hr style='border:0.5px solid #333; margin:15px 0;'>"
        "<div style='font-size:0.85rem; color:#E67E22; font-style:italic; text-align:center;'>Esta clave es tu llave de acceso privada. Evita nombres comunes. Si alguien más la usa podrá visualizar tu información. Usa una combinación compleja para proteger tus registros.</div>"
        "</div></div>"
    )
    
    st.markdown(html_bienvenida, unsafe_allow_html=True)
    st.write("") 
    
    col_a, col_b, col_c = st.columns([0.05, 0.9, 0.05])
    with col_b:
        nombre_acceso = st.text_input("NOMBRE DEL EVENTO / CLAVE DE MESA:", placeholder="Ingresa tu clave aquí").upper().strip()
        
        if st.button("ENTRAR AL SISTEMA", use_container_width=True):
            if nombre_acceso:
                st.session_state.id_usuario = nombre_acceso
                st.rerun()
            else:
                st.warning("⚠️ Por favor, escribe un nombre para proteger tus registros.")
    st.stop()

# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS DE INTERFAZ INTERNA ---
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #E67E22 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
    }

    button[description="generar_reporte_pdf"] {
        background-color: #27ae60 !important;
        color: white !important;
        font-size: 20px !important;
        height: 60px !important;
        border: 2px solid #1e8449 !important;
        box-shadow: 0px 4px 15px rgba(39, 174, 96, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    button[description="generar_reporte_pdf"]:hover {
        background-color: #2ecc71 !important;
        box-shadow: 0px 6px 20px rgba(46, 204, 113, 0.6) !important;
        transform: translateY(-2px);
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

    .manual-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-left: 5px solid #E67E22;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .manual-header {
        color: #1a1a1a;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
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

# --- FUNCIÓN DE PDF ---
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
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Heading2']))
        elements.append(Spacer(1, 8))
        
        col_g = f"G{r}"
        lista = sorted([dict(p) for p in partidos], key=lambda x: x[col_g])
        data = [["#", "G", "PARTIDO (ROJO)", "AN.", "E", "DIF.", "AN.", "PARTIDO (VERDE)", "G"]]
        
        pelea_n = 1
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
            
            if v_idx is not None:
                verde = lista.pop(v_idx)
                d = abs(rojo[col_g] - verde[col_g])
                idx_r = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                idx_v = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==verde["PARTIDO"])
                an_r, an_v = (idx_r * n_gallos) + r, (idx_v * n_gallos) + r
                
                data.append([
                    pelea_n, "[  ]", 
                    Paragraph(f"<b>{rojo['PARTIDO']}</b><br/><font size=8>({rojo[col_g]:.3f})</font>", styles['Normal']),
                    f"{an_r:03}", "[  ]", f"{d:.3f}", f"{an_v:03}", 
                    Paragraph(f"<b>{verde['PARTIDO']}</b><br/><font size=8>({verde[col_g]:.3f})</font>", styles['Normal']),
                    "[  ]"
                ])
                pelea_n += 1
            else: break
        
        t = Table(data, colWidths=[20, 30, 140, 30, 30, 40, 30, 140, 30])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a1a1a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E67E22")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBEFORE', (2,1), (2,-1), 2, colors.red),
            ('LINEAFTER', (7,1), (7,-1), 2, colors.green),
            ('BACKGROUND', (1,1), (1,-1), colors.whitesmoke),
            ('BACKGROUND', (4,1), (4,-1), colors.whitesmoke),
            ('BACKGROUND', (8,1), (8,-1), colors.whitesmoke),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
    
    elements.append(Spacer(1, 40))
    data_firmas = [
        ["__________________________", " ", "__________________________"],
        ["FIRMA JUEZ DE PLAZA", " ", "FIRMA MESA DE CONTROL"]
    ]
    t_firmas = Table(data_firmas, colWidths=[200, 100, 200])
    t_firmas.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    elements.append(t_firmas)
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"<font color='grey' size=8>SISTEMA DE GESTIÓN DIGITAL - DerbySystem v2.0</font>", styles['Normal']))
    doc.build(elements)
    return buffer.getvalue()

# --- INTERFAZ ---
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# Cambio solicitado: Título genérico y clave en pequeño debajo
st.title("Panel de Control")
st.markdown(f"<small style='color:gray;'>ID de Mesa: {st.session_state.id_usuario}</small>", unsafe_allow_html=True)

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
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()

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
        if st.button("🚨 LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        try:
            pdf_bytes = generar_pdf(st.session_state.partidos, st.session_state.n_gallos)
            st.download_button(
                label="📥 GENERAR REPORTE OFICIAL (PDF)", 
                data=pdf_bytes, 
                file_name=f"cotejo_{st.session_state.id_usuario}.pdf", 
                mime="application/pdf", 
                use_container_width=True,
                help="Haz clic aquí para finalizar el sorteo e imprimir el reporte oficial.",
                type="primary"
            )
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
    st.write("### DERBYSYSTEM v2.0 | DOCUMENTACIÓN TÉCNICA")
    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown("""<div class="manual-card"><div class="manual-header">01. INICIALIZACIÓN DE DATOS</div><p style='color:#333; font-size:0.85rem;'><b>Pestaña Registro:</b> Configure la modalidad de combate (2-6 gallos).<br><br><b>Ingreso:</b> Capture el nombre oficial y asigne pesos con 3 decimales.</p></div><div class="manual-card"><div class="manual-header">02. IDENTIFICACIÓN AUTOMATIZADA</div><p style='color:#333; font-size:0.85rem;'><b>Folios de Anillo:</b> Generación automática por índice de registro.</p></div>""", unsafe_allow_html=True)
    with col_2:
        st.markdown("""<div class="manual-card"><div class="manual-header">03. PROCESAMIENTO DE SORTEO</div><p style='color:#333; font-size:0.85rem;'><b>Pestaña Cotejo:</b> Emparejamiento por proximidad de masa.<br><br><b>Seguridad:</b> Bloqueo de enfrentamientos intragrupales.</p></div><div class="manual-card"><div class="manual-header">04. CERTIFICACIÓN PDF</div><p style='color:#333; font-size:0.85rem;'><b>Emisión:</b> Generación del documento legal del evento.</p></div>""", unsafe_allow_html=True)
    st.markdown("<div style='text-align:right; font-size:0.7rem; color:gray;'>© 2026 DerbySystem PRO - All Rights Reserved</div>", unsafe_allow_html=True)

with st.sidebar:
    st.write(f"Sesión activa: **{st.session_state.id_usuario}**")
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
        st.session_state.id_usuario = ""; st.rerun()
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
