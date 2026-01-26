import streamlit as st
import pandas as pd
import os
import random
import string
import re
from datetime import datetime
import pytz  
from io import BytesIO
import streamlit.components.v1 as components

# Importamos reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# --- 1. INICIALIZACIÓN DE ESTADO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""
if "temp_llave" not in st.session_state:
    st.session_state.temp_llave = None
if "partidos" not in st.session_state:
    st.session_state.partidos = []
if "n_gallos" not in st.session_state:
    st.session_state.n_gallos = 2

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- BLINDAJE PARA MANTENER LA APP DESPIERTA ---
components.html(
    """
    <script>
    function keepAlive() {
        fetch(window.location.href);
        console.log("Manteniendo DerbySystem despierto...");
    }
    setInterval(keepAlive, 120000);
    </script>
    """,
    height=0,
    width=0,
)

# --- SIDEBAR: ADMINISTRADOR ---
with st.sidebar:
    st.markdown("### ⚙️ ADMINISTRACIÓN")
    
    if st.session_state.id_usuario != "":
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True): 
            st.session_state.clear()
            st.rerun()
        st.divider()
    
    acceso = st.text_input("Acceso Maestro:", type="password")
    
    if acceso == "28days":
        st.success("Modo Admin: Activo")
        st.subheader("📁 Eventos")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        
        if not archivos:
            st.info("No hay eventos registrados.")
            
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

# --- PANTALLA DE ENTRADA ---
if st.session_state.id_usuario == "":
    año_actual = datetime.now().year
    st.markdown(f"""
        <style>
        @media (prefers-color-scheme: light) {{
            .stApp {{ background-color: #ffffff; }}
            .brand-derby {{ color: #000000; }}
        }}
        @media (prefers-color-scheme: dark) {{
            .stApp {{ background-color: #0e1117; }}
            .brand-derby {{ color: #ffffff; }}
        }}
        .main-container {{ max-width: 500px; margin: 0 auto; padding-top: 2vh; text-align: center; }}
        .brand-logo {{ font-size: 2.8rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 0; line-height: 1; }}
        .brand-system {{ color: #E67E22; }}
        .tagline {{ font-size: 0.7rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #E67E22; margin-top: 2px; margin-bottom: 10px; }}
        
        .promo-box {{ 
            margin-top: 15px; 
            padding: 18px; 
            background-color: rgba(230, 126, 34, 0.05); 
            border: 1px solid rgba(230, 126, 34, 0.2); 
            border-radius: 10px; 
        }}
        .promo-title {{ 
            color: #E67E22; 
            font-weight: 800; 
            text-transform: uppercase; 
            font-size: 0.75rem; 
            margin-bottom: 8px; 
            text-align: center;
        }}
        .promo-text {{ 
            font-size: 0.82rem; 
            line-height: 1.5; 
            opacity: 0.9; 
            margin: 0; 
            text-align: justify; 
            text-align-last: center; 
        }}
        .footer {{ 
            margin-top: 15px; 
            font-size: 0.65rem; 
            color: gray; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
            text-align: center; 
            width: 100%;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="brand-logo"><span class="brand-derby">Derby</span><span class="brand-system">System</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Professional Combat Management</div>', unsafe_allow_html=True)

    if not st.session_state.temp_llave:
        t_acc, t_gen = st.tabs(["ACCEDER", "NUEVO EVENTO"])
        with t_acc:
            llave_input = st.text_input("Código de Evento:", placeholder="DERBY-XXXX", label_visibility="collapsed").upper().strip()
            if st.button("INICIAR SESIÓN", use_container_width=True, type="primary"):
                if os.path.exists(f"datos_{llave_input}.txt"):
                    st.session_state.id_usuario = llave_input
                    st.rerun()
                else: st.error("Código no encontrado.")
        with t_gen:
            if st.button("GENERAR CREDENCIAL", use_container_width=True):
                nueva = "DERBY-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
                st.session_state.temp_llave = nueva
                st.rerun()
    else:
        st.code(st.session_state.temp_llave)
        if st.button("CONFIRMAR Y ENTRAR", use_container_width=True, type="primary"):
            with open(f"datos_{st.session_state.temp_llave}.txt", "w", encoding="utf-8") as f: pass
            st.session_state.id_usuario = st.session_state.temp_llave
            st.session_state.temp_llave = None
            st.rerun()

    st.markdown("""
        <div class="promo-box">
            <div class="promo-title">🛡️ EXCELENCIA TÉCNICA Y TRANSPARENCIA</div>
            <p class="promo-text">
                Seguridad y transparencia en cada gramo. Nuestro sistema optimiza la logística del palenque con un 
                <b>cotejo automatizado</b>, asignación de anillos inalterable y alertas estrictas de peso. 
                Una plataforma robusta que garantiza la equidad en el combate y brinda a los participantes 
                la confianza de un evento regido por la precisión técnica y la integridad total.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="footer">© {año_actual} DerbySystem PRO • VIGENTE</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 2. LÓGICA DE NEGOCIO ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

st.markdown("""
    <style>
    div.stButton > button { background-color: #E67E22 !important; color: white !important; border-radius: 8px !important; border:none !important; }
    .caja-anillo { background-color: #1a1a1a; color: #E67E22; padding: 2px; border-radius: 0px 0px 5px 5px; font-weight: bold; text-align: center; margin-top: -15px; border: 1px solid #D35400; font-size: 0.8em; }
    .header-azul { background-color: #1a1a1a; color: #E67E22; padding: 10px; text-align: center; font-weight: bold; border-radius: 5px; border-bottom: 2px solid #E67E22; }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; color: black !important; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 5px; font-size: 11px; }
    .man-card { background: rgba(230,126,34,0.05); padding: 18px; border-radius: 10px; border-left: 5px solid #E67E22; margin-bottom: 15px; }
    .man-card h3 { color: #E67E22; margin-top: 0; font-size: 1.1rem; }
    .man-card p, .man-card li { font-size: 0.9rem; opacity: 0.9; }
    </style>
""", unsafe_allow_html=True)

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

if not st.session_state.partidos:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title("DerbySystem")
st.caption(f"Evento: {st.session_state.id_usuario} | Panel Técnico")

t_reg, t_cot, t_man = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📘 MANUAL COMPLETO"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g_reg = st.columns([2,1])
    g_sel = col_g_reg.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True); st.write("") 
        if st.form_submit_button("💾 REGISTRAR", use_container_width=True):
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
        res = st.data_editor(df, use_container_width=True, hide_index=True)
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
        st.download_button("📥 REPORTE PDF", data=pdf_b, file_name="cotejo.pdf", use_container_width=True)
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
                    html += f"<tr><td>{pelea_n}</td><td>□</td><td style='border-left: 5px solid #ff4b4b; padding-left: 8px;'><b>{rojo['PARTIDO']}</b><br>{rojo[col_g_cot]:.3f}</td><td>{an_r:03}</td><td>□</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td style='border-left: 5px solid #2ecc71; padding-left: 8px;'><b>{verde['PARTIDO']}</b><br>{verde[col_g_cot]:.3f}</td><td>□</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

        # --- NUEVA FUNCIÓN: CALCULADORA DE LOGÍSTICA (MESA) ---
        st.divider()
        with st.expander("📊 CALCULADORA DE LOGÍSTICA DE MESA (PRIVADO)"):
            st.caption("Uso exclusivo para el organizador - Control de comisiones y premios")
            cl1, cl2 = st.columns(2)
            with cl1:
                monto_total = st.number_input("Monto Total de Jugada ($):", min_value=0, step=100, format="%d")
            with cl2:
                pct_casa = st.slider("Comisión Casa (%):", 0, 20, 10)
            
            ganancia_casa = monto_total * (pct_casa / 100)
            a_repartir = monto_total - ganancia_casa
                
            st.markdown(f"""
                <div style="background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #E67E22;">
                    <table style="width:100%; color: white; border: none;">
                        <tr style="border: none;">
                            <td style="font-size: 0.9rem; opacity: 0.8; border: none; text-align: left;">GANANCIA ORGANIZADOR:</td>
                            <td style="text-align: right; font-size: 1.2rem; color: #2ecc71; font-weight: bold; border: none;">${ganancia_casa:,.2f}</td>
                        </tr>
                        <tr style="border: none;">
                            <td style="font-size: 0.9rem; opacity: 0.8; border: none; text-align: left;">FONDO A REPARTIR:</td>
                            <td style="text-align: right; font-size: 1.2rem; color: #E67E22; font-weight: bold; border: none;">${a_repartir:,.2f}</td>
                        </tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)

with t_man:
    st.header("📘 Guía Maestra de Operación")
    
    st.markdown("""
    <div class="man-card">
        <h3>1. Configuración del Derby</h3>
        <p>Al iniciar un evento nuevo, lo primero es seleccionar el número de gallos por partido (2, 3, 4, 5 o 6). 
        <b>Nota:</b> Esta opción se bloqueará automáticamente tras registrar el primer partido para asegurar la integridad de la competencia.</p>
    </div>

    <div class="man-card">
        <h3>2. Registro de Pesos y Anillos</h3>
        <ul>
            <li>Ingrese el nombre del partido en mayúsculas.</li>
            <li>Capture el peso exacto de cada gallo (el sistema soporta hasta 3 decimales).</li>
            <li><b>Sistema de Anillos:</b> El software asigna los números de anillo de forma automática y secuencial. Usted podrá ver el número asignado justo debajo de cada campo de peso antes de guardar.</li>
        </ul>
    </div>

    <div class="man-card">
        <h3>3. Inteligencia de Cotejo</h3>
        <p>El algoritmo de emparejamiento procesa los datos bajo tres reglas estrictas:</p>
        <ol>
            <li><b>Ordenamiento:</b> Organiza los ejemplares de menor a mayor peso por cada ronda.</li>
            <li><b>Filtro de Socios:</b> Bloquea automáticamente cualquier pelea entre gallos del mismo partido o "socios" (nombres similares).</li>
            <li><b>Alerta de Tolerancia:</b> Si la diferencia entre dos oponentes supera los <b>80 gramos (0.080)</b>, el sistema sombreará la celda en rojo como advertencia técnica.</li>
        </ol>
    </div>

    <div class="man-card">
        <h3>4. Exportación y Reportes</h3>
        <p>En la pestaña de <b>Cotejo</b>, encontrará el botón para descargar el reporte en PDF. Este documento incluye:</p>
        <ul>
            <li>Cabezal oficial con fecha y hora de generación.</li>
            <li>Tablas desglosadas por ronda con espacios para anotaciones del juez (G/E).</li>
            <li>Números de anillo de ambos competidores para validación en ring.</li>
        </ul>
    </div>

    <div class="man-card">
        <h3>5. Gestión Administrativa</h3>
        <p>A través del panel lateral (Sidebar), el administrador puede monitorear todos los eventos activos, cargar bases de datos anteriores o eliminar registros de pruebas utilizando la contraseña maestra.</p>
    </div>
    """, unsafe_allow_html=True)
