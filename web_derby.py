import streamlit as st
import pandas as pd
import os
import uuid  # Crea el identificador único para cada persona
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem Multi-Usuario", layout="wide")
TOLERANCIA = 0.080

# --- LÓGICA DE AISLAMIENTO (La clave de todo) ---
# Si la persona es nueva en la página, le damos su propio ID secreto
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = str(uuid.uuid4())[:8]

# Cada usuario tendrá su propio archivo de texto basado en su ID
# Ejemplo: datos_temp_a1b2c3d4.txt
DB_FILE = f"datos_usuario_{st.session_state.id_usuario}.txt"

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .caja-anillo { background-color: #2c3e50; color: white; padding: 2px; border-radius: 0px 0px 5px 5px; text-align: center; font-size: 0.8em; font-weight: bold; }
    .header-azul { background-color: #2c3e50; color: white; padding: 8px; text-align: center; font-weight: bold; border-radius: 5px; margin-bottom: 10px; }
    .tabla-final { width: 100%; border-collapse: collapse; table-layout: fixed; background: white; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 4px; height: 35px; font-size: 11px; }
    .badge-rojo { background-color: #e74c3c; color: white; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
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

# Cargar datos solo de esta sesión
if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# --- INTERFAZ DE USUARIO ---
st.title("🏆 DerbySystem PRO")
st.sidebar.info(f"ID de Sesión Privada: **{st.session_state.id_usuario}**")
st.sidebar.caption("Tus datos están aislados de otros usuarios en este momento.")

t_reg, t_cot = st.tabs(["📝 REGISTRO DE PESOS", "🏆 TABLA DE COTEJO"])

with t_reg:
    # Lógica de registro con Anillos Automáticos (Instrucción 14-01-2026)
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2, 
                            disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso Gallo {i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True)
        
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()

    if st.session_state.partidos:
        st.write("---")
        st.subheader("📋 Lista de Partidos")
        df = pd.DataFrame(st.session_state.partidos)
        res = st.data_editor(df, use_container_width=True, hide_index=True)
        if not res.equals(df):
            st.session_state.partidos = res.to_dict('records')
            guardar(st.session_state.partidos)
            st.rerun()
        
        if st.button("🚨 BORRAR TODOS MIS DATOS"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []
            st.rerun()

with t_cot:
    if len(st.session_state.partidos) < 2:
        st.warning("Debes registrar al menos 2 partidos para generar el cotejo.")
    else:
        st.success("Cotejo generado exitosamente.")
        # Generación visual de las rondas
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            # Ordenar por peso para buscar la pareja más cercana
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            
            html = "<table class='tabla-final'><thead><tr><th>#</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>AN.</th><th>VERDE</th></tr></thead><tbody>"
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    d = abs(rojo[col_g] - verde[col_g])
                    c_style = "class='badge-rojo'" if d >= TOLERANCIA else ""
                    
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    
                    html += f"<tr><td>{pelea_n}</td><td style='border-left:4px solid red'><b>{rojo['PARTIDO']}</b><br>{rojo[col_g]:.3f}</td><td>{an_r:03}</td><td><span {c_style}>{d:.3f}</span></td><td>{an_v:03}</td><td style='border-right:4px solid green'><b>{verde['PARTIDO']}</b><br>{verde[col_g]:.3f}</td></tr>"
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)
