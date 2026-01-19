import streamlit as st
import pandas as pd
import os
import uuid 
from io import BytesIO

# Importamos reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- LÓGICA MULTI-USUARIO ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = str(uuid.uuid4())[:8] [cite: 18-01-2026]

DB_FILE = f"datos_derby_{st.session_state.id_usuario}.txt" [cite: 18-01-2026]

# --- TUS ESTILOS (INTACTOS) ---
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

TOLERANCIA = 0.080

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

if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# --- INTERFAZ CON PESTAÑA DE ADMIN ---
st.title("🏆 PRUEBAS")
st.sidebar.info(f"ID Sesión: {st.session_state.id_usuario}")
clave = st.sidebar.text_input("Acceso Maestro", type="password") [cite: 18-01-2026]

# Creamos las pestañas (se añade '🕵️ ADMIN' solo si la clave es correcta)
tabs = ["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO Y ANILLOS"]
if clave == "homero2026":
    tabs.append("🕵️ ADMIN")

t_list = st.tabs(tabs)

with t_list[0]:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Añadir Partido # {len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        for i in range(g_sel):
            p_val = st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True) [cite: 14-01-2026]
            st.write("") 
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()
    # (Resto de tu tabla de edición...)
    if st.session_state.partidos:
        st.markdown("### ✏️ Tabla de Edición")
        df = pd.DataFrame(st.session_state.partidos)
        res = st.data_editor(df, use_container_width=True, hide_index=True)
        if not res.equals(df):
            st.session_state.partidos = res.to_dict('records')
            guardar(st.session_state.partidos)
            st.rerun()

with t_list[1]:
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = """<table class='tabla-final'><thead><tr><th>#</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>AN.</th><th>VERDE</th></tr></thead><tbody>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    d = abs(rojo[col_g] - verde[col_g])
                    c = "style='background:#e74c3c;color:white;'" if d > TOLERANCIA else ""
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    html += f"<tr><td>{pelea_n}</td><td style='border-left:3px solid red'><b>{rojo['PARTIDO']}</b><br>{rojo[col_g]:.3f}</td><td>{an_r:03}</td><td {c}>{d:.3f}</td><td>{an_v:03}</td><td style='border-right:3px solid green'><b>{verde['PARTIDO']}</b><br>{verde[col_g]:.3f}</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

# LÓGICA DE LA PESTAÑA ADMIN (NUEVO)
if clave == "homero2026":
    with t_list[2]:
        st.header("🕵️ Control Maestro de Sesiones")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_derby_")] [cite: 18-01-2026]
        st.metric("Usuarios Conectados", len(archivos))
        for arch in archivos:
            with st.expander(f"Ver Gallera: {arch}"):
                with open(arch, "r", encoding="utf-8") as f:
                    st.text(f.read())
                if st.button("Cerrar Sesión", key=arch):
                    os.remove(arch)
                    st.rerun()
