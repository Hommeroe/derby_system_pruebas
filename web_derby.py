import streamlit as st
import pandas as pd
import os
import json
import hashlib
import re
from datetime import datetime
import pytz  
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- LÓGICA DE USUARIOS (Sin cambios) ---
USER_DB_FILE = "usuarios_db.json"
def cargar_usuarios():
    if not os.path.exists(USER_DB_FILE): return {}
    try:
        with open(USER_DB_FILE, "r") as f: return json.load(f)
    except: return {}

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def verificar_credenciales(usuario, password):
    users = cargar_usuarios()
    return usuario in users and users[usuario] == hash_password(password)

if "id_usuario" not in st.session_state: st.session_state.id_usuario = ""

# --- LOGIN (Diseño limpio) ---
if st.session_state.id_usuario == "":
    st.markdown("<style>.stApp { background-color: #f4f7f6; }</style>", unsafe_allow_html=True)
    col1, col_center, col3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown(f"""
            <div style='background:white; padding:30px; border-radius:15px; border-top:8px solid #E67E22; box-shadow:0 10px 25px rgba(0,0,0,0.1); margin-top:50px;'>
                <h1 style='text-align:center; color:#1a1a1a; margin-bottom:0;'>DerbySystem</h1>
                <p style='text-align:center; color:#E67E22; font-weight:bold; letter-spacing:2px;'>MANAGEMENT PRO</p>
            </div>
        """, unsafe_allow_html=True)
        u = st.text_input("Usuario").upper().strip()
        p = st.text_input("Contraseña", type="password")
        if st.button("ACCEDER AL PANEL", use_container_width=True):
            if verificar_credenciales(u, p): st.session_state.id_usuario = u; st.rerun()
            else: st.error("Acceso denegado")
    st.stop()

# --- ESTILOS MEJORADOS (PROFESIONALES) ---
st.markdown("""
    <style>
    /* Botones */
    div.stButton > button {
        background-color: #E67E22 !important; color: white !important; border-radius: 8px !important;
        font-weight: bold !important; border: none !important; height: 3em !important;
    }
    
    /* Diseño de Tabla de Cotejo Adaptable */
    .cotejo-container {
        background: #f9f9f9; border-radius: 12px; padding: 15px; margin-bottom: 20px;
        border: 1px solid #ddd;
    }
    .peleas-grid {
        display: grid; grid-template-columns: 1fr; gap: 10px;
    }
    .pelea-card {
        display: flex; align-items: center; background: white; border-radius: 8px;
        padding: 10px; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .pelea-num { background: #1a1a1a; color: #E67E22; padding: 5px 12px; border-radius: 5px; font-weight: 900; margin-right: 15px; }
    .equipo { flex: 1; padding: 5px 10px; overflow: hidden; }
    .nombre-p { font-weight: 800; font-size: 14px; color: #333; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-transform: uppercase; }
    .peso-p { font-family: monospace; font-size: 13px; color: #E67E22; font-weight: bold; }
    .vs { font-weight: 900; color: #ccc; padding: 0 10px; font-style: italic; }
    .dif-box { width: 80px; text-align: center; border-left: 1px solid #eee; border-right: 1px solid #eee; font-size: 12px; font-weight: bold; }
    .anillo-label { font-size: 10px; color: #999; display: block; }

    /* Estilo Protocolo (Tutorial) */
    .step-box {
        background: white; border-left: 6px solid #E67E22; padding: 20px;
        border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .step-num { font-size: 24px; font-weight: 900; color: #E67E22; opacity: 0.3; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
DB_FILE = f"datos_{st.session_state.id_usuario}.txt"
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

if 'partidos' not in st.session_state: st.session_state.partidos, st.session_state.n_gallos = cargar()

# --- SIDEBAR & ADMIN ---
with st.sidebar:
    st.write(f"👤 Usuario: **{st.session_state.id_usuario}**")
    if st.button("CERRAR SESIÓN", use_container_width=True): st.session_state.clear(); st.rerun()
    st.divider()
    admin_pass = st.text_input("Llave Admin", type="password")

# --- NAVEGACIÓN ---
t_reg, t_cot, t_pro, t_adm = st.tabs(["📝 REGISTRO", "🏆 COTEJO", "📑 PROTOCOLO", "🛠️ PANEL ADMIN"])

with t_reg:
    # (Mantenemos tu lógica de registro y anillos intacta)
    st.subheader("Captura de Pesos")
    # ... código de registro existente ...

# --- COTEJO REDISEÑADO (PROFESIONAL) ---
with t_cot:
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"### 🏁 RONDA {r}")
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    dif = abs(rojo[col_g] - verde[col_g])
                    
                    # Calcular anillos automáticos según posición original
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r = (idx_r * st.session_state.n_gallos) + r
                    an_v = (idx_v * st.session_state.n_gallos) + r

                    color_dif = "#c0392b" if dif > TOLERANCIA else "#27ae60"

                    st.markdown(f"""
                        <div class="pelea-card">
                            <div class="pelea-num">{pelea_n}</div>
                            <div class="equipo" style="border-left: 4px solid #e74c3c;">
                                <span class="nombre-p">{rojo['PARTIDO']}</span>
                                <span class="peso-p">{rojo[col_g]:.3f} kg</span>
                                <span class="anillo-label">ANILLO: {an_r:03}</span>
                            </div>
                            <div class="dif-box">
                                <span style="color:{color_dif}">DIF.<br>{dif:.3f}</span>
                            </div>
                            <div class="equipo" style="border-right: 4px solid #27ae60; text-align:right;">
                                <span class="nombre-p">{verde['PARTIDO']}</span>
                                <span class="peso-p">{verde[col_g]:.3f} kg</span>
                                <span class="anillo-label">ANILLO: {an_v:03}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    pelea_n += 1
                else: break

# --- PROTOCOLO REDISEÑADO (TUTORIAL COMPLETO) ---
with t_pro:
    st.title("📚 Manual de Operación y Protocolo")
    
    st.markdown("""
    <div class="step-box">
        <span class="step-num">01</span>
        <h3>Configuración de Mesa</h3>
        <p>Antes de pesar, defina la modalidad (Ej. Derby de 4 gallos). Ingrese los nombres de los partidos tal cual aparecen en la inscripción oficial.</p>
    </div>
    <div class="step-box">
        <span class="step-num">02</span>
        <h3>Registro de Pesos y Anillos</h3>
        <p>El sistema asigna los <b>Anillos Automáticos</b> según el orden de registro. Asegúrese de que el pesador dicte el peso en kilogramos con tres decimales (Ej: 2.150).</p>
    </div>
    <div class="step-box">
        <span class="step-num">03</span>
        <h3>Validación de Emparejamiento</h3>
        <p>En la pestaña <b>Cotejo</b>, el sistema ordena por peso y busca al rival más próximo. Si la diferencia excede los <b>80 gramos</b>, el marcador se pondrá en rojo, indicando una pelea fuera de norma.</p>
    </div>
    <div class="step-box">
        <span class="step-num">04</span>
        <h3>Cierre y Auditoría</h3>
        <p>Revise que ningún partido pelee contra sí mismo. Una vez validado, genere el reporte PDF para las autoridades del evento.</p>
    </div>
    """, unsafe_allow_html=True)

# --- PANEL ADMIN CORREGIDO ---
with t_adm:
    if admin_pass == "28days":
        st.subheader("🛠️ Auditoría General")
        
        # Mostrar Usuarios y Pass
        st.write("### Usuarios Registrados")
        db_u = cargar_usuarios()
        st.table([{"Usuario": k, "Contraseña (Hash)": v} for k, v in db_u.items()])
        
        st.divider()
        
        # Mostrar Contenido de Archivos .txt
        st.write("### Datos de Combates (.txt)")
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for arch in archivos:
            with st.expander(f"Ver contenido de: {arch}", expanded=True):
                try:
                    df_temp = pd.read_csv(arch, sep="|", header=None)
                    st.dataframe(df_temp, use_container_width=True)
                    if st.button("Eliminar", key=f"del_{arch}"):
                        os.remove(arch); st.rerun()
                except: st.write("Archivo vacío.")
    else:
        st.info("Ingrese la llave maestra en el menú lateral para ver los datos de administración.")
