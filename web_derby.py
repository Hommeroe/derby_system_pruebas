import streamlit as st
import pandas as pd
import os
import uuid  # Necesario para separar usuarios
from io import BytesIO

# Importamos reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- LÓGICA DE USUARIOS (NUEVO: NO AFECTA EL DISEÑO) ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = str(uuid.uuid4())[:8]

# El archivo ahora es único por usuario para no mezclar datos
DB_FILE = f"datos_usuario_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS ORIGINALES (INTACTOS) ---
st.markdown("""
    <style>
    .caja-anillo {
        background-color: #2c3e50; color: white; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #34495e;
        font-size: 0.8em;
    }
    .header-azul { 
        background-color: #2c3e50; color: white; padding: 8px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 12px; margin-bottom: 5px;
    }
    .tabla-final { 
        width: 100%; border-collapse: collapse; background-color: white; 
        table-layout: fixed; color: black !important;
    }
    .tabla-final td, .tabla-final th { 
        border: 1px solid #bdc3c7; text-align: center; 
        padding: 2px; height: 38px; color: black !important;
    }
    .nombre-partido { 
        font-weight: bold; font-size: 10px; line-height: 1;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
        display: block; width: 100%; color: black !important;
    }
    .peso-texto { font-size: 10px; color: #2c3e50 !important; display: block; }
    .cuadro { font-size: 11px; font-weight: bold; color: black !important; }
    
    .col-num { width: 20px; }
    .col-g { width: 22px; }
    .col-an { width: 32px; }
    .col-e { width: 22px; background-color: #f1f2f6; }
    .col-dif { width: 42px; }
    .col-partido { width: auto; }

    div[data-testid="stNumberInput"] { margin-bottom: 0px; }
    </style>
""", unsafe_allow_html=True)

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
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>COTEJO OFICIAL DE DERBY</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Heading2']))
        col_g = f"G{r}"
        lista = sorted([dict(p) for p in partidos], key=lambda x: x[col_g])
        data = [["#", "G", "ROJO", "AN.", "E", "DIF.", "AN.", "VERDE", "G"]]
        pelea_n = 1
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
            if v_idx is not None:
                verde = lista.pop(v_idx)
                d = abs(rojo[col_g] - verde[col_g])
                idx_r = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                idx_v = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==verde["PARTIDO"])
                an_r, an_v = (idx_r * n_gallos) + r, (idx_v * n_gallos) + r
                data.append([pelea_n, " ", f"{rojo['PARTIDO']}\n({rojo[col_g]:.3f})", f"{an_r:03}", " ", f"{d:.3f}", f"{an_v:03}", f"{verde['PARTIDO']}\n({verde[col_g]:.3f})", " "])
                pelea_n += 1
            else: break
        t = Table(data, colWidths=[20, 25, 140, 35, 25, 45, 35, 140, 25])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2c3e50")), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(t); elements.append(Spacer(1, 20))
    doc.build(elements)
    return buffer.getvalue()

if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title("DERBYsystem")
t_reg, t_cot = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO"])

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
            # Anillo automático según instrucción [cite: 14-01-2026]
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
            st.download_button(label="📥 DESCARGAR COTEJO (PDF)", data=pdf_bytes, file_name="cotejo_derby.pdf", mime="application/pdf", use_container_width=True)
        except Exception as e: st.error(f"Error al generar PDF: {e}")
        st.divider()
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-final'><thead><tr><th class='col-num'>#</th><th class='col-g'>G</th><th class='col-partido'>ROJO</th><th class='col-an'>AN.</th><th class='col-e'>E</th><th class='col-dif'>DIF.</th><th class='col-an'>AN.</th><th class='col-partido'>VERDE</th><th class='col-g'>G</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g]); c = "style='background:#e74c3c;color:white;'" if d > TOLERANCIA else ""
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    n_rojo = (rojo['PARTIDO'][:15] + '..') if len(rojo['PARTIDO']) > 15 else rojo['PARTIDO']
                    n_verde = (verde['PARTIDO'][:15] + '..') if len(verde['PARTIDO']) > 15 else verde['PARTIDO']
                    html += f"<tr><td>{pelea_n}</td><td class='cuadro'>□</td><td style='border-left:3px solid red'><span class='nombre-partido'>{n_rojo}</span><span class='peso-texto'>{rojo[col_g]:.3f}</span></td><td>{an_r:03}</td><td class='cuadro col-e'>□</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td style='border-right:3px solid green'><span class='nombre-partido'>{n_verde}</span><span class='peso-texto'>{verde[col_g]:.3f}</span></td><td class='cuadro'>□</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

# --- ACCESO ADMIN (MONITOREO) ---
with st.sidebar:
    st.write(f"ID Sesión: {st.session_state.id_usuario}")
    acceso = st.text_input("Acceso Admin:", type="password")

if acceso == "homero2026":
    st.divider()
    st.subheader("🕵️ Control de Usuarios Activos")
    archivos = [f for f in os.listdir(".") if f.startswith("datos_usuario_") and f.endswith(".txt")]
    st.write(f"Personas usando el sistema: **{len(archivos)}**")
    for arch in archivos:
        with st.expander(f"Ver datos de: {arch}"):
            with open(arch, "r") as f: st.text(f.read())
            if st.button("Eliminar esta gallera", key=arch):
                os.remove(arch); st.rerun()
