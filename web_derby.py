import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRUEBAS", layout="wide")

# Estilo para imitar tu interfaz exacta y la tabla de la foto
st.markdown("""
    <style>
    .software-brand { color: #555; font-size: 14px; font-weight: bold; letter-spacing: 2px; text-align: center; margin-bottom: 20px; }
    .stTable { width: 100%; border: 1px solid #f0f0f0; }
    .stButton > button { border-radius: 4px; font-size: 12px; height: 35px; width: 100%; background-color: white; border: 1px solid #ccc; }
    
    /* Estilos para la tabla de cotejo en pantalla */
    .cotejo-table { width: 100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 20px; }
    .cotejo-table th { background: #333; color: white; border: 1px solid #000; padding: 4px; font-size: 12px; }
    .cotejo-table td { border: 1px solid #000; text-align: center; padding: 5px; font-size: 12px; }
    .rojo-celda { border-left: 10px solid #d32f2f !important; font-weight: bold; }
    .verde-celda { border-right: 10px solid #388e3c !important; font-weight: bold; }
    .ronda-header { background: #eeeeee; font-weight: bold; text-align: center; border: 1px solid #000; padding: 5px; margin-top: 10px; }
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

partidos_actuales, gallos_en_archivo = cargar_datos()
hay_datos = len(partidos_actuales) > 0

st.markdown('<p class="software-brand">DERBYSYSTEM PRUEBAS</p>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO"])

with tab1:
    if hay_datos:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=[2,3,4].index(gallos_en_archivo), horizontal=True, disabled=True)
    else:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=0, horizontal=True)

    col_reg, col_view = st.columns([1, 2.2])
    with col_reg:
        st.write("### DATOS DEL PARTIDO")
        if "edit_idx" not in st.session_state: st.session_state.edit_idx = None
        v_nombre = ""
        v_pesos = [1.800] * tipo_derby
        
        if st.session_state.edit_idx is not None:
            idx = st.session_state.edit_idx
            p_edit = partidos_actuales[idx]
            v_nombre = p_edit["PARTIDO"]
            for i in range(tipo_derby): v_pesos[i] = p_edit.get(f"Peso {i+1}", 1.800)
            st.warning(f"Modificando: {v_nombre}")

        with st.form("form_registro", clear_on_submit=True):
            n = st.text_input("NOMBRE DEL PARTIDO:", value=v_nombre).upper()
            pesos_in = [st.number_input(f"Peso G{i+1}:", 1.000, 4.500, v_pesos[i], 0.001, format="%.3f") for i in range(tipo_derby)]
            if st.form_submit_button("GUARDAR"):
                if n:
                    nuevo = {"PARTIDO": n}
                    for i, v in enumerate(pesos_in): nuevo[f"Peso {i+1}"] = v
                    if st.session_state.edit_idx is not None:
                        partidos_actuales[st.session_state.edit_idx] = nuevo
                        st.session_state.edit_idx = None
                    else: partidos_actuales.append(nuevo)
                    guardar_todos(partidos_actuales); st.rerun()

    with col_view:
        st.write("### LISTA DE PARTIDOS")
        if hay_datos:
            df = pd.DataFrame(partidos_actuales)
            df.index = range(1, len(df) + 1)
            for c in df.columns:
                if "Peso" in c: df[c] = df[c].map('{:,.3f}'.format)
            st.table(df)
            
            st.write("---")
            nombres_partidos = [f"{i+1}. {p['PARTIDO']}" for i, p in enumerate(partidos_actuales)]
            seleccion = st.selectbox("Seleccionar para Corregir/Eliminar:", ["--- Elija un partido ---"] + nombres_partidos)
            if seleccion != "--- Elija un partido ---":
                idx_sel = int(seleccion.split(".")[0]) - 1
                c1, c2 = st.columns(2)
                if c1.button("EDITAR"): st.session_state.edit_idx = idx_sel; st.rerun()
                if c2.button("ELIMINAR"): partidos_actuales.pop(idx_sel); guardar_todos(partidos_actuales); st.rerun()

with tab2:
    if hay_datos and len(partidos_actuales) >= 2:
        # El anillo se genera automático
        contador_anillos = 1
        pesos_cols = [f"Peso {i+1}" for i in range(gallos_en_archivo)]
        
        # HTML para Impresión (Idéntico a tu foto del cel)
        html_impresion = "<html><head><style>body{font-family:Arial;} table{width:100%; border-collapse:collapse; margin-bottom:15px;} th{background:#333; color:white; border:1px solid #000; padding:5px; font-size:12px;} td{border:1px solid #000; text-align:center; padding:5px; font-size:12px;} .rojo{border-left:12px solid #d32f2f; font-weight:bold;} .verde{border-right:12px solid #388e3c; font-weight:bold;} .box{width:15px; height:15px; border:1px solid #000; margin:auto;}</style></head><body>"

        for r_idx, r_col in enumerate(pesos_cols):
            ronda_html = f"<div class='ronda-header'>RONDA {r_idx+1}</div>"
            tabla_html = "<table class='cotejo-table'><tr><th>G</th><th>ROJO</th><th>An.</th><th>DIF.</th><th>An.</th><th>VERDE</th><th>G</th></tr>"
            
            lista = partidos_actuales.copy()
            while len(lista) >= 2:
                rojo, verde = lista.pop(0), lista.pop(0)
                pr, pv = rojo.get(r_col, 0.0), verde.get(r_col, 0.0)
                a1, a2 = f"{contador_anillos:03}", f"{contador_anillos+1:03}"
                contador_anillos += 2
                
                fila = f"<tr><td>☐</td><td class='rojo-celda'>{rojo['PARTIDO']}<br>{pr:.3f}</td><td>{a1}</td><td>{abs(pr-pv):.3f}</td><td>{a2}</td><td class='verde-celda'>{verde['PARTIDO']}<br>{pv:.3f}</td><td>☐</td></tr>"
                tabla_html += fila
            
            tabla_html += "</table>"
            st.markdown(ronda_header + tabla_html, unsafe_allow_html=True)
            html_impresion += ronda_html + tabla_html

        html_impresion += "</body></html>"
        
        if st.button("📄 IMPRIMIR COTEJO"):
            js = f"<script>var w=window.open('','_blank');w.document.write({json.dumps(html_impresion)});w.document.close();setTimeout(function(){{w.print();}},500);</script>"
            st.components.v1.html(js, height=0)
    else:
        st.info("Necesitas al menos 2 partidos para el cotejo.")

st.markdown('<p style="text-align:center; font-size:10px; color:#aaa; margin-top:50px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
