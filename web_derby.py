import streamlit as st
import pandas as pd
import os
import uuid
from io import BytesIO

# Importamos reportlab para el PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- LÓGICA DE USUARIOS ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = str(uuid.uuid4())[:8]

DB_FILE = f"datos_usuario_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS (Texto negro forzado para que no desaparezcan los datos) ---
st.markdown("""
    <style>
    .caja-anillo { background-color: #2c3e50; color: white; padding: 2px; border-radius: 0px 0px 5px 5px; text-align: center; font-size: 0.8em; font-weight: bold; }
    .header-azul { background-color: #2c3e50; color: white; padding: 8px; text-align: center; font-weight: bold; border-radius: 5px; margin-bottom: 5px; }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; table-layout: fixed; color: black !important; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 4px; color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS ---
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

# Inicializar sesión
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# --- INTERFAZ PRINCIPAL ---
st.title("🏆 DerbySystem PRO")
st.sidebar.info(f"ID de Sesión: {st.session_state.id_usuario}")

t_reg, t_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO"])

with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            # Anillo automático [cite: 14-01-2026]
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True)
        
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()

with t_cot:
    if len(st.session_state.partidos) < 2:
        st.warning("Registra al menos 2 partidos.")
    else:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            html = "<table class='tabla-final'><thead><tr><th>#</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>AN.</th><th>VERDE</th></tr></thead><tbody>"
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0); verde = lista.pop(0) # Simplificado para prueba
                d = abs(rojo[col_g] - verde[col_g])
                html += f"<tr><td>{pelea_n}</td><td style='border-left:3px solid red'><b>{rojo['PARTIDO']}</b></td><td>-</td><td>{d:.3f}</td><td>-</td><td style='border-right:3px solid green'><b>{verde['PARTIDO']}</b></td></tr>"
                pelea_n += 1
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)

# --- PANEL DE ADMINISTRADOR ---
st.sidebar.markdown("---")
# Clave: homero2026
clave = st.sidebar.text_input("Acceso Maestro", type="password", help="Escribe la clave y presiona ENTER")

if clave == "homero2026":
    st.sidebar.success("Acceso Concedido")
    st.divider()
    st.header("🕵️ Monitor de Usuarios")
    
    # Listar archivos de todos los usuarios conectados [cite: 18-01-2026]
    archivos = [f for f in os.listdir(".") if f.startswith("datos_usuario_")]
    st.write(f"Usuarios activos: {len(archivos)}")
    
    for arch in archivos:
        with st.expander(f"Ver datos de: {arch}"):
            with open(arch, "r") as f:
                st.text(f.read())
            if st.button("Eliminar Datos", key=arch):
                os.remove(arch)
                st.rerun()
