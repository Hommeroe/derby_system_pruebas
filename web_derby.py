import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRUEBAS", layout="wide")

# Estilo para imitar tu interfaz (colores y botones)
st.markdown("""
    <style>
    .software-brand { color: #555; font-size: 14px; font-weight: bold; letter-spacing: 2px; text-align: center; margin-bottom: 20px; }
    .stTable { width: 100%; }
    /* Botones de acción minimalistas como en tu foto */
    .stButton > button { 
        border-radius: 2px; 
        font-size: 10px; 
        height: 25px; 
        width: 100%;
        padding: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"

def cargar_datos():
    partidos = []
    num_gallos = 2
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                p = linea.strip().split("|")
                if len(p) >= 2:
                    num_gallos = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, num_gallos + 1):
                        d[f"Peso {i}"] = float(p[i]) if p[i] else 0.0
                    partidos.append(d)
    return partidos, num_gallos

def guardar_todos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- LÓGICA DE DATOS ---
partidos_actuales, gallos_en_archivo = cargar_datos()
hay_datos = len(partidos_actuales) > 0

st.markdown('<p class="software-brand">DERBYSYSTEM PRUEBAS</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["REGISTRO", "COTEJO"])

with tab1:
    # Selector de gallos bloqueado si hay datos
    if hay_datos:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=[2,3,4].index(gallos_en_archivo), horizontal=True, disabled=True)
    else:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=0, horizontal=True)

    col_registro, col_lista = st.columns([1, 2.2])

    with col_registro:
        st.write("### DATOS PARTIDO")
        if "edit_idx" not in st.session_state: st.session_state.edit_idx = None
        
        v_nombre = ""
        v_pesos = [1.800] * tipo_derby
        
        if st.session_state.edit_idx is not None:
            idx = st.session_state.edit_idx
            p_edit = partidos_actuales[idx]
            v_nombre = p_edit["PARTIDO"]
            for i in range(tipo_derby): v_pesos[i] = p_edit.get(f"Peso {i+1}", 1.800)
            st.warning(f"Modificando: {v_nombre}")

        with st.form("registro_form", clear_on_submit=True):
            n = st.text_input("NOMBRE DEL PARTIDO:", value=v_nombre).upper()
            pesos_in = []
            for i in range(tipo_derby):
                pesos_in.append(st.number_input(f"Peso G{i+1}:", 1.000, 4.500, v_pesos[i], 0.001, format="%.3f"))
            
            if st.form_submit_button("GUARDAR"):
                if n:
                    nuevo = {"PARTIDO": n}
                    for i, v in enumerate(pesos_in): nuevo[f"Peso {i+1}"] = v
                    if st.session_state.edit_idx is not None:
                        partidos_actuales[st.session_state.edit_idx] = nuevo
                        st.session_state.edit_idx = None
                    else:
                        partidos_actuales.append(nuevo)
                    guardar_todos(partidos_actuales)
                    st.rerun()
        
        if st.session_state.edit_idx is not None:
            if st.button("CANCELAR EDICION"):
                st.session_state.edit_idx = None
                st.rerun()

    with col_lista:
        st.write("### LISTA DE PARTIDOS")
        if hay_datos:
            # Crear DataFrame para la tabla
            df = pd.DataFrame(partidos_actuales)
            df.index = range(1, len(df) + 1)
            
            # Formato de 3 decimales idéntico a tu foto
            for c in df.columns:
                if "Peso" in c:
                    df[c] = df[c].apply(lambda x: f"{x:.3f}")
            
            # Mostrar la tabla limpia
            st.table(df)

            # Botones de Acción (Corregir y Eliminar) como en tu pantalla
            st.write("*ACCIONES:*")
            for i in range(len(partidos_actuales)):
                c1, c2, c3 = st.columns([1, 1, 3])
                if c1.button(f"CORREGIR {i+1}", key=f"edit_{i}"):
                    st.session_state.edit_idx = i
                    st.rerun()
                if c2.button(f"ELIMINAR {i+1}", key=f"del_{i}"):
                    partidos_actuales.pop(i)
                    guardar_todos(partidos_actuales)
                    st.rerun()

            st.write("---")
            if st.button("LIMPIAR TODA LA LISTA"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_idx = None
                st.rerun()
        else:
            st.info("Esperando registros...")

with tab2:
    if hay_datos and len(partidos_actuales) >= 2:
        st.write("### CONFIGURACION DE COTEJO")
        # Aquí se mantiene tu lógica de impresión de la versión anterior
        if st.button("GENERAR PDF / IMPRIMIR"):
            st.write("Generando documento...")
