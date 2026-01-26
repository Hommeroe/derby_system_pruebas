import streamlit as st
import pandas as pd
import os
import random
import string
import re
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- INICIALIZACIÓN DE VARIABLES ---
if "id_usuario" not in st.session_state: st.session_state.id_usuario = ""
if "rol" not in st.session_state: st.session_state.rol = "Espectador"
if "partidos" not in st.session_state: st.session_state.partidos = []
if "apuestas_abiertas" not in st.session_state: st.session_state.apuestas_abiertas = False

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card-pelea { background: #1a1a1a; border: 1px solid #E67E22; border-radius: 12px; padding: 20px; margin-bottom: 15px; text-align: center; }
    .vs-text { color: #E67E22; font-weight: 900; font-size: 1.5rem; }
    .status-badge { padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL (TXT) ---
def guardar_datos():
    db_file = f"datos_{st.session_state.id_usuario}.txt"
    status_file = f"status_{st.session_state.id_usuario}.txt"
    # Guardar partidos
    with open(db_file, "w", encoding="utf-8") as f:
        for p in st.session_state.partidos:
            pesos = [f"{v:.3f}" for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")
    # Guardar si las apuestas están abiertas
    with open(status_file, "w") as f:
        f.write("1" if st.session_state.apuestas_abiertas else "0")

def cargar_datos():
    db_file = f"datos_{st.session_state.id_usuario}.txt"
    status_file = f"status_{st.session_state.id_usuario}.txt"
    partidos = []
    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    d = {"PARTIDO": p[0]}
                    for i in range(1, len(p)): d[f"G{i}"] = float(p[i])
                    partidos.append(d)
    
    abiertas = False
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            abiertas = f.read().strip() == "1"
    return partidos, abiertas

# --- PANTALLA DE ACCESO ---
if st.session_state.id_usuario == "":
    st.title("DerbySystem PRO 🏆")
    t_acc, t_gen, t_rec = st.tabs(["ACCEDER", "NUEVO EVENTO", "⚙️ RECUPERAR"])
    
    with t_acc:
        llave = st.text_input("Código de Evento:").upper().strip()
        rol = st.radio("Entrar como:", ["Espectador (Público)", "Administrador (Mesa/Dueño)"], horizontal=True)
        if st.button("ENTRAR", use_container_width=True, type="primary"):
            if os.path.exists(f"datos_{llave}.txt"):
                st.session_state.id_usuario = llave
                st.session_state.rol = rol
                st.session_state.partidos, st.session_state.apuestas_abiertas = cargar_datos()
                st.rerun()
            else: st.error("El código no existe.")

    with t_gen:
        if st.button("CREAR EVENTO NUEVO"):
            nueva = "DERBY-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            open(f"datos_{nueva}.txt", "w").close()
            st.success(f"Código generado: {nueva}")

    with t_rec:
        archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
        for a in archivos:
            n = a.replace("datos_", "").replace(".txt", "")
            if st.button(f"Entrar a: {n}", key=n):
                st.session_state.id_usuario = n
                st.session_state.rol = "Administrador (Mesa/Dueño)"
                st.session_state.partidos, st.session_state.apuestas_abiertas = cargar_datos()
                st.rerun()
    st.stop()

# --- INTERFAZ DE USUARIO ---

if st.session_state.rol == "Administrador (Mesa/Dueño)":
    st.title(f"🛠️ Control Maestro: {st.session_state.id_usuario}")
    
    # INTERRUPTOR MAESTRO (PARA TI DESDE CASA)
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.session_state.apuestas_abiertas:
            st.success("📢 APUESTAS PUBLICADAS: El público está viendo las peleas.")
            if st.button("🔴 OCULTAR APUESTAS AL PÚBLICO", use_container_width=True):
                st.session_state.apuestas_abiertas = False
                guardar_datos()
                st.rerun()
        else:
            st.warning("🔒 APUESTAS OCULTAS: Solo tú y el operador ven los datos.")
            if st.button("🟢 PUBLICAR APUESTAS AHORA", use_container_width=True):
                st.session_state.apuestas_abiertas = True
                guardar_datos()
                st.rerun()
    
    with col2:
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
            st.session_state.id_usuario = ""
            st.rerun()

    t_reg, t_cot = st.tabs(["📝 REGISTRO (OPERADOR)", "📊 COTEJO TÉCNICO"])
    
    with t_reg:
        st.subheader("Registro de Partidos")
        # Aquí el operador en el palenque mete los datos
        with st.form("registro", clear_on_submit=True):
            nombre = st.text_input("Nombre del Partido:").upper()
            p1 = st.number_input("Peso G1", 1.800, 2.600, 2.200, 0.001, format="%.3f")
            p2 = st.number_input("Peso G2", 1.800, 2.600, 2.200, 0.001, format="%.3f")
            if st.form_submit_button("GUARDAR REGISTRO"):
                st.session_state.partidos.append({"PARTIDO": nombre, "G1": p1, "G2": p2})
                guardar_datos()
                st.rerun()
        st.write(st.session_state.partidos)

else:
    # --- MODO ESPECTADOR (LO QUE VE LA GENTE) ---
    st.title(f"🏟️ Derby en Vivo: {st.session_state.id_usuario}")
    
    if not st.session_state.apuestas_abiertas:
        st.markdown("""
            <div style="text-align: center; padding: 50px;">
                <h2 style="color: #E67E22;">⏳ Mesa Técnica Trabajando</h2>
                <p>La cartelera de apuestas se publicará en unos momentos. ¡Mantente atento!</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Aquí se muestran las peleas solo si tú diste la orden
        st.subheader("🎯 Cartelera de Apuestas Abierta")
        for r in [1, 2]:
            st.markdown(f"#### RONDA {r}")
            lista = sorted(st.session_state.partidos, key=lambda x: x[f"G{r}"])
            while len(lista) >= 2:
                rojo = lista.pop(0)
                verde = lista.pop(0)
                st.markdown(f"""
                    <div class="card-pelea">
                        <div style="display: flex; justify-content: space-around; align-items: center;">
                            <div><b style="color:#ff4b4b;">{rojo['PARTIDO']}</b><br>{rojo[f'G{r}']:.3f}</div>
                            <div class="vs-text">VS</div>
                            <div><b style="color:#2ecc71;">{verde['PARTIDO']}</b><br>{verde[f'G{r}']:.3f}</div>
                        </div>
                        <br>
                        <span class="status-badge" style="background:#E67E22; color:black;">PAGA: ROJO x1.9 | VERDE x1.9</span>
                    </div>
                """, unsafe_allow_html=True)
    
    if st.button("SALIR"):
        st.session_state.id_usuario = ""
        st.rerun()
