import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# --- 1. SEGURIDAD ---
if "autenticado" not in st.session_state:
    st.title("Acceso Privado")
    password = st.text_input("Clave de Acceso:", type="password")
    if st.button("Entrar"):
        if password == "2026":
            st.session_state["autenticado"] = True
            st.rerun()
    st.stop()

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRUEBAS", layout="wide")

st.markdown("""
    <style>
    .software-brand { color: #555; font-size: 10px; letter-spacing: 3px; text-align: center; text-transform: uppercase; margin-bottom: 5px; }
    .main .block-container { padding: 10px 5px !important; }
    .stButton > button { border-radius: 2px; font-size: 11px; height: 28px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"

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

# --- PROCESO ---
partidos_actuales, gallos_en_archivo = cargar_datos()
hay_datos = len(partidos_actuales) > 0

st.markdown('<p class="software-brand">DerbySystem PRUEBAS</p>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["REGISTRO", "COTEJO"])

with tab1:
    # Bloqueo automático de selección de gallos
    if hay_datos:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=[2,3,4].index(gallos_en_archivo), horizontal=True, disabled=True)
    else:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], horizontal=True)
    
    if "edit_idx" not in st.session_state: st.session_state.edit_idx = None
    
    col_izq, col_der = st.columns([1.2, 2.5])
    
    with col_izq:
        st.write("### DATOS")
        v_nombre = ""
        v_pesos = [1.800] * tipo_derby
        
        if st.session_state.edit_idx is not None:
            idx = st.session_state.edit_idx
            p_edit = partidos_actuales[idx]
            v_nombre = p_edit["PARTIDO"]
            for i in range(tipo_derby): v_pesos[i] = p_edit.get(f"Peso {i+1}", 1.800)
            st.info(f"Editando fila {idx + 1}")

        with st.form("registro", clear_on_submit=True):
            n = st.text_input("NOMBRE:", value=v_nombre).upper()
            pesos_in = [st.number_input(f"G{i+1}", 1.000, 4.000, v_pesos[i], 0.001, format="%.3f") for i in range(tipo_derby)]
            if st.form_submit_button("GUARDAR"):
                if n:
                    nuevo = {"PARTIDO": n}
                    for i, v in enumerate(pesos_in): nuevo[f"Peso {i+1}"] = v
                    if st.session_state.edit_idx is not None:
                        partidos_actuales[st.session_state.edit_idx] = nuevo
                        st.session_state.edit_idx = None
                    else: 
                        partidos_actuales.append(nuevo)
                    guardar_todos(partidos_actuales); st.rerun()

    with col_der:
        if hay_datos:
            st.write("### LISTA")
            df = pd.DataFrame(partidos_actuales)
            df.index = range(1, len(df) + 1)
            
            # --- SOLUCIÓN AL 1.8 vs 1.800 ---
            # Forzamos a que todas las columnas de 'Peso' tengan 3 decimales exactos
            for c in df.columns:
                if "Peso" in c:
                    df[c] = df[c].apply(lambda x: f"{x:,.3f}")
            
            st.table(df)
            
            st.write("*ACCIONES:*")
            for i in range(len(partidos_actuales)):
                c1, c2, _ = st.columns([1, 1, 4])
                if c1.button(f"CORREGIR {i+1}", key=f"e{i}"):
                    st.session_state.edit_idx = i; st.rerun()
                if c2.button(f"ELIMINAR {i+1}", key=f"b{i}"):
                    partidos_actuales.pop(i); guardar_todos(partidos_actuales); st.rerun()
            
            if st.button("BORRAR TODA LA LISTA"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_idx = None; st.rerun()

with tab2:
    if hay_datos and len(partidos_actuales) >= 2:
        c1, c2 = st.columns(2)
        nombre_t = c1.text_input("Torneo:", "DERBY DE GALLOS")
        fecha_t = c2.date_input("Fecha:", datetime.now())

        # Estilo de impresión profesional
        html = f"<html><head><style>body {{ font-family: Arial; }} table {{ width: 100%; border-collapse: collapse; }} th {{ background: #222; color: white; border: 1px solid #000; padding: 5px; }} td {{ border: 1px solid #000; text-align: center; padding: 5px; }} .rojo {{ border-left: 10px solid #d32f2f; font-weight: bold; }} .verde {{ border-right: 10px solid #388e3c; font-weight: bold; }}</style></head><body><h2 style='text-align:center;'>{nombre_t}</h2><p style='text-align:center;'>FECHA: {fecha_t.strftime('%d/%m/%Y')}</p>"

        # El anillo se genera automático [2026-01-14]
        contador_anillo = 1
        pesos_k = [f"Peso {i+1}" for i in range(gallos_en_archivo)]
        for r_idx, r_col in enumerate(pesos_k):
            st.markdown(f"*RONDA {r_idx+1}*")
            html += f"<div style='background:#eee; padding:5px; border:1px solid #000; text-align:center; font-weight:bold;'>RONDA {r_idx+1}</div>"
            html += "<table><tr><th>G</th><th>ROJO</th><th>An.</th><th>DIFERENCIA</th><th>An.</th><th>VERDE</th><th>G</th></tr>"
            
            lista = partidos_actuales.copy()
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0); verde = lista.pop(0)
                p_r, p_v = rojo.get(r_col, 0.0), verde.get(r_col, 0.0)
                an1, an2 = f"{contador_anillo:03}", f"{contador_anillo+1:03}"
                contador_anillo += 2
                
                # Formato de 3 decimales también en la impresión
                html += f"<tr><td>[ ]</td><td class='rojo'>{rojo['PARTIDO']}<br>{p_r:.3f}</td><td>{an1}</td><td>P{pelea_n}<br>DIF: {abs(p_r-p_v):.3f}</td><td>{an2}</td><td class='verde'>{verde['PARTIDO']}<br>{p_v:.3f}</td><td>[ ]</td></tr>"
                st.write(f"P{pelea_n}: {rojo['PARTIDO']} ({p_r:.3f}) vs {verde['PARTIDO']} ({p_v:.3f})")
                pelea_n += 1
            html += "</table><br>"
        
        if st.button("GENERAR IMPRESIÓN"):
            js = f"<script>var win = window.open('', '_blank'); win.document.write({json.dumps(html)}); win.document.close(); setTimeout(function(){{ win.print(); }}, 500);</script>"
            st.components.v1.html(js, height=0)

st.markdown('<p style="text-align:center; font-size:10px; color:#aaa;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
