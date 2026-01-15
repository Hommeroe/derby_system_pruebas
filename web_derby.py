import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRUEBAS", layout="wide")

# Estilo para imitar tu interfaz exacta
st.markdown("""
    <style>
    .software-brand { color: #555; font-size: 14px; font-weight: bold; letter-spacing: 2px; text-align: center; margin-bottom: 20px; }
    .stTable { width: 100%; border: 1px solid #f0f0f0; }
    /* Botones de acción como en tu captura */
    .stButton > button { 
        border-radius: 4px; 
        font-size: 12px; 
        height: 35px; 
        width: 100%;
        background-color: white;
        border: 1px solid #ccc;
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
    # Bloqueo automático de gallos si ya hay registros
    if hay_datos:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=[2,3,4].index(gallos_en_archivo), horizontal=True, disabled=True)
    else:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=0, horizontal=True)

    col_reg, col_view = st.columns([1, 2.2])

    with col_reg:
        st.write("### DATOS DEL PARTIDO")
        # Estado de edición
        if "edit_idx" not in st.session_state: st.session_state.edit_idx = None
        
        v_nombre = ""
        v_pesos = [1.800] * tipo_derby
        
        # Si hay alguien seleccionado para editar
        if st.session_state.edit_idx is not None:
            idx = st.session_state.edit_idx
            p_edit = partidos_actuales[idx]
            v_nombre = p_edit["PARTIDO"]
            for i in range(tipo_derby): v_pesos[i] = p_edit.get(f"Peso {i+1}", 1.800)
            st.warning(f"Editando: {v_nombre}")

        with st.form("form_registro", clear_on_submit=True):
            n = st.text_input("NOMBRE DEL PARTIDO:", value=v_nombre).upper()
            pesos_in = []
            for i in range(tipo_derby):
                pesos_in.append(st.number_input(f"Peso G{i+1}:", 1.000, 4.500, v_pesos[i], 0.001, format="%.3f"))
            
            label_boton = "ACTUALIZAR DATOS" if st.session_state.edit_idx is not None else "GUARDAR PARTIDO"
            if st.form_submit_button(label_boton):
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

    with col_view:
        st.write("### LISTA DE PARTIDOS")
        if hay_datos:
            df = pd.DataFrame(partidos_actuales)
            df.index = range(1, len(df) + 1)
            # Formato de 3 decimales (1.800) como en la foto
            for c in df.columns:
                if "Peso" in c: df[c] = df[c].map('{:,.3f}'.format)
            
            st.table(df)

            # --- SECCIÓN DE SELECCIÓN (IDÉNTICO A TU OTRA APP) ---
            st.write("---")
            nombres_partidos = [f"{i+1}. {p['PARTIDO']}" for i, p in enumerate(partidos_actuales)]
            seleccion = st.selectbox("Seleccionar para Corregir/Eliminar:", ["--- Elija un partido ---"] + nombres_partidos)
            
            if seleccion != "--- Elija un partido ---":
                idx_sel = int(seleccion.split(".")[0]) - 1
                
                c1, c2 = st.columns(2)
                if c1.button("EDITAR SELECCIONADO"):
                    st.session_state.edit_idx = idx_sel
                    st.rerun()
                
                if c2.button("ELIMINAR SELECCIONADO"):
                    partidos_actuales.pop(idx_sel)
                    guardar_todos(partidos_actuales)
                    st.session_state.edit_idx = None
                    st.rerun()

            if st.button("LIMPIAR TODO EL EVENTO"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_idx = None
                st.rerun()
        else:
            st.info("No hay registros en la lista.")

with tab2:
    if hay_datos and len(partidos_actuales) >= 2:
        st.write("### COTEJO Y PESOS")
        # El anillo se genera automático [2026-01-14]
        st.info("Lógica de cotejo lista para impresión.")
    else:
        st.warning("Se requieren mínimo 2 partidos.")

st.markdown('<p style="text-align:center; font-size:10px; color:#aaa; margin-top:50px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
