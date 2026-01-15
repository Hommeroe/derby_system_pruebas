import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# --- 1. CONFIGURACIÓN DE PÁGINA E IDENTIDAD ---
st.set_page_config(page_title="DerbySystem PRUEBAS", layout="wide")

# Estilo CSS para replicar exactamente tus fotos
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 10px; }
    .software-brand { color: #666; font-size: 12px; letter-spacing: 2px; text-align: center; text-transform: uppercase; margin-bottom: 20px; font-family: sans-serif; }
    /* Ajuste de tabla para que se vea como en tu captura */
    .stTable { width: 100%; border: 1px solid #f0f0f0; border-radius: 5px; }
    /* Botones pequeños y minimalistas */
    .stButton > button { 
        border-radius: 4px; 
        font-size: 12px; 
        height: 32px; 
        background-color: white; 
        color: #333; 
        border: 1px solid #ccc;
    }
    .stButton > button:hover { border-color: #000; color: #000; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"

# --- FUNCIONES DE DATOS ---
def cargar_datos():
    partidos = []
    num_gallos_detectado = 2
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                p = linea.strip().split("|")
                if len(p) >= 2:
                    num_gallos_detectado = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, num_gallos_detectado + 1):
                        d[f"Peso {i}"] = float(p[i]) if p[i] else 0.0
                    partidos.append(d)
    return partidos, num_gallos_detectado

def guardar_todos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- LÓGICA INICIAL ---
partidos_actuales, gallos_en_archivo = cargar_datos()
hay_datos = len(partidos_actuales) > 0

st.markdown('<p class="software-brand">DERBYSYSTEM PRUEBAS</p>', unsafe_allow_html=True)

# Tabs como en tu imagen
tab1, tab2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO"])

with tab1:
    # Selector de gallos (se bloquea si hay datos)
    if hay_datos:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=[2,3,4].index(gallos_en_archivo), horizontal=True, disabled=True)
    else:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=0, horizontal=True)

    col_form, col_tabla = st.columns([1, 2.5])

    with col_form:
        st.write("### REGISTRO")
        if "edit_idx" not in st.session_state: st.session_state.edit_idx = None
        
        v_nombre = ""
        v_pesos = [1.800] * tipo_derby
        
        if st.session_state.edit_idx is not None:
            idx = st.session_state.edit_idx
            p_edit = partidos_actuales[idx]
            v_nombre = p_edit["PARTIDO"]
            for i in range(tipo_derby): v_pesos[i] = p_edit.get(f"Peso {i+1}", 1.800)
            st.info(f"Editando: {v_nombre}")

        with st.form("form_reg", clear_on_submit=True):
            n = st.text_input("NOMBRE DEL PARTIDO:", value=v_nombre).upper()
            pesos_in = []
            for i in range(tipo_derby):
                pesos_in.append(st.number_input(f"Peso G{i+1}:", 1.000, 4.500, v_pesos[i], 0.001, format="%.3f"))
            
            submit = st.form_submit_button("💾 GUARDAR PARTIDO")
            if submit and n:
                nuevo = {"PARTIDO": n}
                for i, v in enumerate(pesos_in): nuevo[f"Peso {i+1}"] = v
                if st.session_state.edit_idx is not None:
                    partidos_actuales[st.session_state.edit_idx] = nuevo
                    st.session_state.edit_idx = None
                else:
                    partidos_actuales.append(nuevo)
                guardar_todos(partidos_actuales)
                st.rerun()

    with col_tabla:
        st.write("### LISTA DE PARTIDOS")
        if hay_datos:
            df = pd.DataFrame(partidos_actuales)
            df.index = range(1, len(df) + 1)
            
            # Formato idéntico a tu foto: 3 decimales (1.800)
            for c in df.columns:
                if "Peso" in c:
                    df[c] = df[c].apply(lambda x: f"{x:,.3f}")
            
            st.table(df)

            # Sección de acciones como en tu foto (Seleccionar para corregir)
            st.write("---")
            st.write("Seleccione el número para corregir:")
            cols_accion = st.columns(len(partidos_actuales) if len(partidos_actuales) < 8 else 😎
            for i in range(len(partidos_actuales)):
                if cols_accion[i % 8].button(f"✏️ {i+1}", key=f"edit_{i}"):
                    st.session_state.edit_idx = i
                    st.rerun()

            if st.button("🗑️ VACIAR TODA LA LISTA", use_container_width=True):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_idx = None
                st.rerun()
        else:
            st.info("No hay partidos registrados.")

with tab2:
    if hay_datos and len(partidos_actuales) >= 2:
        st.write("### GENERACIÓN DE COTEJO")
        # El anillo se genera automático [2026-01-14]
        # (Aquí va tu lógica de impresión y cotejo que ya tenías)
        st.success("Listo para generar impresión de pesos y anillos.")
    else:
        st.warning("Se necesitan al menos 2 partidos para el cotejo.")

st.markdown('---')
st.markdown('<p style="text-align:center; font-size:10px; color:gray;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
