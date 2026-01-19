import streamlit as st
import pandas as pd
import os
import uuid

# --- CONFIGURACIÓN Y ESTILO ORIGINAL ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# Lógica de usuario para que no se mezclen los datos
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = str(uuid.uuid4())[:8]

DB_FILE = f"datos_{st.session_state.id_usuario}.txt"

st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .caja-anillo { 
        background-color: #2c3e50; color: white; padding: 5px; 
        border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 10px;
    }
    .header-azul { 
        background-color: #2c3e50; color: white; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px; margin: 10px 0;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2130; border-radius: 4px 4px 0 0; padding: 10px; color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #2c3e50; border-bottom: 2px solid red; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
def cargar():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, sep="|")
        return df.to_dict('records'), len(df.columns) - 1
    return [], 2

def guardar(lista):
    if lista:
        pd.DataFrame(lista).to_csv(DB_FILE, sep="|", index=False)

if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

# --- INTERFAZ ---
st.title("🏆 PRUEBAS")

# Acceso Maestro en la barra lateral
with st.sidebar:
    st.write(f"ID Sesión: {st.session_state.id_usuario}")
    clave = st.text_input("Acceso Maestro", type="password")

# Pestañas
pestanas = ["📝 REGISTRO", "🏆 COTEJO"]
if clave == "homero2026":
    pestanas.append("🕵️ ADMIN")

t = st.tabs(pestanas)

with t[0]:
    col1, col2 = st.columns([2,1])
    g_sel = col2.selectbox("GALLOS:", [2,3,4,5,6], index=st.session_state.n_gallos-2)
    st.session_state.n_gallos = g_sel

    with st.form("registro", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper()
        pesos = []
        for i in range(g_sel):
            p = st.number_input(f"Peso Gallo {i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f")
            # Anillo automático como en tu foto [cite: 14-01-2026]
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(len(st.session_state.partidos)*g_sel + i + 1):03}</div>", unsafe_allow_html=True)
            pesos.append(p)
        
        if st.form_submit_button("💾 GUARDAR PARTIDO"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i, p in enumerate(pesos): nuevo[f"G{i+1}"] = p
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()

    if st.session_state.partidos:
        st.write("### Lista de Partidos")
        df_edit = pd.DataFrame(st.session_state.partidos)
        st.dataframe(df_edit, use_container_width=True, hide_index=True)
        if st.button("🚨 BORRAR TODO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []
            st.rerun()

with t[1]:
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            df = pd.DataFrame(st.session_state.partidos).sort_values(f"G{r}")
            st.table(df[["PARTIDO", f"G{r}"]]) # Tabla simple para evitar errores de diseño

# Pestaña de Administrador
if clave == "homero2026":
    with t[2]:
        st.header("🕵️ Monitor de Sesiones")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_")]
        for arch in archivos:
            with st.expander(f"Usuario: {arch}"):
                st.dataframe(pd.read_csv(arch, sep="|"))
                if st.button("Eliminar Datos", key=arch):
                    os.remove(arch)
                    st.rerun()
