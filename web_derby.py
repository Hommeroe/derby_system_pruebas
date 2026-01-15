import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRUEBAS", layout="wide")

# Estilos CSS para replicar tu diseño de las fotos
st.markdown("""
    <style>
    .software-brand { color: #555; font-size: 14px; font-weight: bold; letter-spacing: 2px; text-align: center; margin-bottom: 20px; text-transform: uppercase; }
    .stTable { width: 100%; }
    .stButton > button { border-radius: 4px; font-size: 12px; height: 35px; width: 100%; background-color: white; border: 1px solid #ccc; }
    
    /* Estilo de la tabla de cotejo igual a tu foto del celular */
    .tabla-cotejo { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-family: sans-serif; }
    .tabla-cotejo th { background: #1a1a1a; color: white; border: 1px solid #000; padding: 6px; font-size: 12px; text-align: center; }
    .tabla-cotejo td { border: 1px solid #000; text-align: center; padding: 8px; font-size: 13px; }
    .celda-roja { border-left: 10px solid #d32f2f !important; font-weight: bold; width: 35%; }
    .celda-verde { border-right: 10px solid #388e3c !important; font-weight: bold; width: 35%; }
    .header-ronda { background: #f0f0f0; font-weight: bold; text-align: center; border: 2px solid #000; padding: 8px; margin-top: 20px; font-size: 16px; }
    .box-g { width: 18px; height: 18px; border: 2px solid #000; margin: auto; }
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

# Cargar información inicial
partidos_actuales, gallos_en_archivo = cargar_datos()
hay_datos = len(partidos_actuales) > 0

st.markdown('<p class="software-brand">DERBYSYSTEM PRUEBAS</p>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO"])

with tab1:
    if hay_datos:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=[2,3,4].index(gallos_en_archivo), horizontal=True, disabled=True)
    else:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], index=0, horizontal=True)

    col_izq, col_der = st.columns([1, 2.2])
    with col_izq:
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

        with st.form("registro_p", clear_on_submit=True):
            n = st.text_input("NOMBRE DEL PARTIDO:", value=v_nombre).upper()
            pesos_in = [st.number_input(f"Peso G{i+1}:", 1.000, 4.500, v_pesos[i], 0.001, format="%.3f") for i in range(tipo_derby)]
            if st.form_submit_button("GUARDAR DATOS"):
                if n:
                    nuevo = {"PARTIDO": n}
                    for i, v in enumerate(pesos_in): nuevo[f"Peso {i+1}"] = v
                    if st.session_state.edit_idx is not None:
                        partidos_actuales[st.session_state.edit_idx] = nuevo
                        st.session_state.edit_idx = None
                    else: partidos_actuales.append(nuevo)
                    guardar_todos(partidos_actuales); st.rerun()

    with col_der:
        st.write("### LISTA DE PARTIDOS")
        if hay_datos:
            df = pd.DataFrame(partidos_actuales)
            df.index = range(1, len(df) + 1)
            for c in df.columns:
                if "Peso" in c: df[c] = df[c].map('{:,.3f}'.format)
            st.table(df)
            
            st.write("---")
            nombres = [f"{i+1}. {p['PARTIDO']}" for i, p in enumerate(partidos_actuales)]
            sel = st.selectbox("Seleccione para Corregir o Eliminar:", ["--- Seleccionar ---"] + nombres)
            if sel != "--- Seleccionar ---":
                idx_s = int(sel.split(".")[0]) - 1
                c1, c2 = st.columns(2)
                if c1.button("EDITAR SELECCIONADO"): st.session_state.edit_idx = idx_s; st.rerun()
                if c2.button("ELIMINAR SELECCIONADO"): 
                    partidos_actuales.pop(idx_s); guardar_todos(partidos_actuales); st.rerun()
            if st.button("BORRAR TODO EL EVENTO"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_idx = None; st.rerun()

with tab2:
    if hay_datos and len(partidos_actuales) >= 2:
        st.write("### COTEJO Y PESOS")
        
        # Botón de impresión (HTML)
        html_imprimir = "<html><head><style>body{font-family:Arial;} table{width:100%; border-collapse:collapse; margin-bottom:15px;} th{background:#000; color:#fff; border:1px solid #000; padding:5px; font-size:12px;} td{border:1px solid #000; text-align:center; padding:5px; font-size:12px;} .rojo{border-left:12px solid #d32f2f; font-weight:bold;} .verde{border-right:12px solid #388e3c; font-weight:bold;} .ronda-header{background:#eee; font-weight:bold; text-align:center; border:1px solid #000; padding:5px;}</style></head><body>"

        anillo_count = 1
        columnas_peso = [f"Peso {i+1}" for i in range(gallos_en_archivo)]

        for idx, col_p in enumerate(columnas_peso):
            # Título de Ronda
            titulo_r = f"RONDA {idx+1}"
            st.markdown(f"<div class='header-ronda'>{titulo_r}</div>", unsafe_allow_html=True)
            html_imprimir += f"<div class='ronda-header'>{titulo_r}</div>"
            
            # Tabla de Cotejo
            tabla_html = "<table class='tabla-cotejo'><tr><th>G</th><th>ROJO</th><th>An.</th><th>DIF.</th><th>An.</th><th>VERDE</th><th>G</th></tr>"
            
            temp_lista = partidos_actuales.copy()
            while len(temp_lista) >= 2:
                r, v = temp_lista.pop(0), temp_lista.pop(0)
                p_r, p_v = r.get(col_p, 0.0), v.get(col_p, 0.0)
                an1, an2 = f"{anillo_count:03}", f"{anillo_count+1:03}"
                anillo_count += 2
                
                dif = abs(p_r - p_v)
                fila = f"<tr><td><div class='box-g'></div></td><td class='celda-roja'>{r['PARTIDO']}<br>{p_r:.3f}</td><td>{an1}</td><td>{dif:.3f}</td><td>{an2}</td><td class='celda-verde'>{v['PARTIDO']}<br>{p_v:.3f}</td><td><div class='box-g'></div></td></tr>"
                tabla_html += fila
            
            tabla_html += "</table>"
            st.markdown(tabla_html, unsafe_allow_html=True)
            html_imprimir += tabla_html

        if st.button("📄 GENERAR IMPRESIÓN"):
            js = f"<script>var w=window.open('','_blank');w.document.write({json.dumps(html_imprimir)});w.document.close();setTimeout(function(){{w.print();}},500);</script>"
            st.components.v1.html(js, height=0)
    else:
        st.info("Registre al menos 2 partidos para ver el cotejo.")

st.markdown('<p style="text-align:center; font-size:10px; color:#aaa; margin-top:50px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
