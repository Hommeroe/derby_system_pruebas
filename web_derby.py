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

# --- GESTIÓN DE USUARIOS ---
USER_DB_FILE = "usuarios_db.json"

def cargar_usuarios():
    if not os.path.exists(USER_DB_FILE): return {}
    try:
        with open(USER_DB_FILE, "r") as f: return json.load(f)
    except: return {}

def guardar_usuario_db(users):
    with open(USER_DB_FILE, "w") as f: json.dump(users, f)

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def verificar_credenciales(usuario, password):
    users = cargar_usuarios()
    return usuario in users and users[usuario] == hash_password(password)

def registrar_usuario(usuario, password):
    users = cargar_usuarios()
    if usuario in users: return False 
    users[usuario] = hash_password(password)
    guardar_usuario_db(users)
    return True

if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""

# --- LOGIN ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .stApp { margin-top: -60px !important; }
        .login-card {
            max-width: 480px; margin: 0 auto; background: #ffffff; padding: 25px;
            border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-top: 5px solid #E67E22;
        }
        .main-title { font-size: 2.4rem; font-weight: 800; color: #E67E22; text-align: center; margin-bottom: 0px; }
        .main-subtitle { font-size: 0.75rem; color: #888; text-align: center; letter-spacing: 3px; margin-bottom: 15px; text-transform: uppercase; }
        </style>
    """, unsafe_allow_html=True)

    col_1, col_center, col_3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="main-title">DerbySystem</div><div class="main-subtitle">PRO MANAGEMENT</div>', unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["🔒 ACCESO", "📝 REGISTRO"])
        with tab_login:
            u = st.text_input("Usuario", key="l_u").upper().strip()
            p = st.text_input("Contraseña", key="l_p", type="password")
            if st.button("ENTRAR AL SISTEMA", use_container_width=True):
                if verificar_credenciales(u, p): st.session_state.id_usuario = u; st.rerun()
                else: st.error("Credenciales incorrectas")
        with tab_reg:
            nu = st.text_input("Nuevo Usuario", key="r_u").upper().strip()
            np = st.text_input("Nueva Pass", key="r_p", type="password")
            if st.button("REGISTRAR CUENTA", use_container_width=True):
                if nu and np:
                    if registrar_usuario(nu, np): st.success("Registrado correctamente")
                    else: st.warning("El usuario ya existe")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CONSTANTES ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
TOLERANCIA = 0.080

# --- ESTILOS INTERNOS ---
st.markdown("""
    <style>
    /* Estilo de botones */
    div.stButton > button, div.stDownloadButton > button {
        background-color: #E67E22 !important; color: white !important; font-weight: bold !important;
        border-radius: 8px !important; border: none !important; transition: 0.3s;
    }
    /* Tabla Profesional de Cotejo */
    .tabla-profesional {
        width: 100%; border-collapse: separate; border-spacing: 0;
        background-color: white; color: black !important;
        border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px; table-layout: fixed;
    }
    .tabla-profesional th {
        background-color: #1a1a1a; color: #E67E22; font-size: 12px;
        padding: 12px 5px; text-transform: uppercase; letter-spacing: 1px;
    }
    .tabla-profesional td {
        border-bottom: 1px solid #eee; padding: 10px 5px;
        text-align: center; vertical-align: middle; font-size: 12px;
        word-wrap: break-word; overflow-wrap: break-word;
    }
    .nombre-partido {
        font-weight: 800; font-size: 13px; color: #1a1a1a;
        display: block; line-height: 1.2; text-transform: uppercase;
    }
    .peso-badge {
        background: #f1f2f6; padding: 2px 6px; border-radius: 4px;
        font-family: monospace; font-weight: bold; color: #E67E22;
    }
    /* Protocolo de Operación */
    .tutorial-card {
        background: white; border-left: 5px solid #E67E22;
        padding: 20px; border-radius: 8px; margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05); color: #333;
    }
    .tutorial-card h4 { color: #1a1a1a; margin-top: 0; display: flex; align-items: center; }
    .tutorial-card span {
        background: #1a1a1a; color: #E67E22; width: 25px; height: 25px;
        display: inline-flex; justify-content: center; align-items: center;
        border-radius: 50%; margin-right: 10px; font-size: 14px;
    }
    .caja-anillo {
        background-color: #1a1a1a; color: #E67E22; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #D35400; font-size: 0.8em;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
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

# --- INTERFAZ ---
if 'partidos' not in st.session_state: st.session_state.partidos, st.session_state.n_gallos = cargar()

with st.sidebar:
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True): st.session_state.clear(); st.rerun()
    st.divider()
    acceso_admin = st.text_input("Acceso Admin:", type="password")

t_reg, t_cot, t_ayu, t_adm = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📑 PROTOCOLO", "🛠️ ADMIN"])

# TAB 1: REGISTRO Y EDICIÓN
with t_reg:
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel
    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Nuevo Partido #{len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        for i in range(g_sel):
            st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True); st.write("") 
        if st.form_submit_button("💾 GUARDAR"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo); guardar(st.session_state.partidos); st.rerun()

    if st.session_state.partidos:
        df = pd.DataFrame(st.session_state.partidos)
        st.dataframe(df, use_container_width=True)
        if st.button("🚨 LIMPIAR EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

# TAB 2: COTEJO PROFESIONAL
with t_cot:
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"### RONDA {r}")
            col_g = f"G{r}"; lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            
            html = """<table class='tabla-profesional'>
            <thead><tr>
                <th style='width:40px'>#</th>
                <th style='width:40px'>G</th>
                <th>PARTIDO (ROJO)</th>
                <th style='width:60px'>AN.</th>
                <th style='width:70px'>DIF.</th>
                <th style='width:60px'>AN.</th>
                <th>PARTIDO (VERDE)</th>
                <th style='width:40px'>G</th>
            </tr></thead><tbody>"""
            
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if limpiar_nombre_socio(x["PARTIDO"]) != limpiar_nombre_socio(rojo["PARTIDO"])), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx); d = abs(rojo[col_g] - verde[col_g])
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                    
                    c_alerta = "background:#ffeded;color:#c0392b;font-weight:bold;" if d > TOLERANCIA else ""
                    
                    html += f"""<tr>
                        <td>{pelea_n}</td>
                        <td>□</td>
                        <td style='border-left:4px solid #e74c3c'><span class='nombre-partido'>{rojo['PARTIDO']}</span><span class='peso-badge'>{rojo[col_g]:.3f}</span></td>
                        <td>{an_r:03}</td>
                        <td style='{c_alerta}'>{d:.3f}</td>
                        <td>{an_v:03}</td>
                        <td style='border-right:4px solid #27ae60'><span class='nombre-partido'>{verde['PARTIDO']}</span><span class='peso-badge'>{verde[col_g]:.3f}</span></td>
                        <td>□</td>
                    </tr>"""
                    pelea_n += 1
                else: break
            st.markdown(html + "</tbody></table>", unsafe_allow_html=True)

# TAB 3: PROTOCOLO / TUTORIAL RELLENADO
with t_ayu:
    st.title("📖 Manual de Operación DerbySystem")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="tutorial-card">
            <h4><span>1</span> Configuración de Modalidad</h4>
            <p>Al iniciar el evento, elija el número de gallos por partido (2, 3, 4, 5 o 6). 
            <b>Nota:</b> Una vez registrado el primer partido, esta opción se bloquea para evitar errores en el sorteo.</p>
        </div>
        <div class="tutorial-card">
            <h4><span>2</span> Registro de Participantes</h4>
            <p>Ingrese el nombre del partido y los pesos exactos en kilogramos (Ej: 2.250). El sistema generará el <b>anillo automático</b> de forma ascendente según el orden de llegada.</p>
        </div>
        <div class="tutorial-card">
            <h4><span>3</span> Edición y Corrección</h4>
            <p>Si cometió un error en el peso, puede corregirlo en la tabla inferior de la pestaña Registro. Al modificar un dato, el sistema re-calcula el cotejo al instante.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_b:
        st.markdown("""
        <div class="tutorial-card">
            <h4><span>4</span> Entendiendo el Cotejo</h4>
            <p>El sistema ordena a todos los ejemplares por peso y busca al oponente más cercano, garantizando que <b>nunca pelee un partido contra sí mismo</b> en la misma ronda.</p>
        </div>
        <div class="tutorial-card">
            <h4><span>5</span> Alertas de Tolerancia</h4>
            <p>Si la diferencia entre dos gallos supera los <b>80 gramos</b>, el sistema marcará la celda "DIF" en rojo como advertencia para la mesa técnica.</p>
        </div>
        <div class="tutorial-card">
            <h4><span>6</span> Reporte PDF</h4>
            <p>Al finalizar el pesaje, descargue el PDF. Este reporte está diseñado para ser entregado a los jueces de arena y contiene los espacios para anotaciones manuales.</p>
        </div>
        """, unsafe_allow_html=True)

# TAB 4: ADMIN MEJORADO
with t_adm:
    if acceso_admin == "28days":
        st.subheader("👥 Base de Datos de Usuarios")
        users = cargar_usuarios()
        st.table([{"Usuario": k, "Hash": v} for k, v in users.items()])
        
        st.subheader("📁 Archivos de Registro (.txt)")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for arch in archivos:
            col1, col2 = st.columns([4,1])
            col1.text(f"Archivo: {arch}")
            if col2.button("Ver Contenido", key=arch):
                with open(arch, "r") as f: st.code(f.read())
    else:
        st.warning("Ingrese la clave de administrador en la barra lateral.")
