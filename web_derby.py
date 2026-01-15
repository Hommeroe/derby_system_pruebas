import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRUEBAS", layout="wide")

st.markdown("""
    <style>
    .software-brand { color: #555; font-size: 14px; font-weight: bold; letter-spacing: 2px; text-align: center; margin-bottom: 20px; }
    .stTable { width: 100%; border: 1px solid #f0f0f0; }
    .stButton > button { border-radius: 4px; font-size: 12px; height: 35px; width: 100%; background-color: white; border: 1px solid #ccc; }
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
tab1, tab2 = st.tabs(["REGISTRO", "COTEJO"])

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
            st.warning(f"Editando: {v_nombre}")

        with st.form("form_registro", clear_on_submit=True):
            n = st.text_input("NOMBRE DEL PARTIDO:", value=v_nombre).upper()
            pesos_in = [st.number_input(f"Peso G{i+1}:", 1.000, 4.500, v_pesos[i], 0.001, format="%.3f") for i in range(tipo_derby)]
            if st.form_submit_button("GUARDAR PARTIDO"):
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
                if c1.button("EDITAR SELECCIONADO"):
                    st.session_state.edit_idx = idx_sel; st.rerun()
                if c2.button("ELIMINAR SELECCIONADO"):
                    partidos_actuales.pop(idx_sel); guardar_todos(partidos_actuales); st.rerun()
            if st.button("LIMPIAR TODO EL EVENTO"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_idx = None; st.rerun()

with tab2:
    if hay_datos and len(partidos_actuales) >= 2:
        st.write("### COTEJO Y PESOS")
        col1, col2 = st.columns(2)
        nom_torneo = col1.text_input("Nombre del Torneo:", "DERBY DE GALLOS")
        fec_torneo = col2.date_input("Fecha:", datetime.now())

        # El anillo se genera automático [2026-01-14]
        html_cotejo = f"<html><head><style>@page {{ size: letter; margin: 10mm; }} body {{ font-family: Arial, sans-serif; }} .t-titulo {{ text-align: center; font-size: 20px; font-weight: bold; }} .t-fecha {{ text-align: center; margin-bottom: 15px; border-bottom: 2px solid #000; }} table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }} th {{ background: #333; color: white; border: 1px solid #000; padding: 6px; font-size: 11px; }} td {{ border: 1px solid #000; text-align: center; padding: 5px; font-size: 11px; }} .rojo {{ border-left: 12px solid #d32f2f; font-weight: bold; }} .verde {{ border-right: 12px solid #388e3c; font-weight: bold; }} .det {{ background: #f9f9f9; font-size: 9px; font-weight: bold; }} .box {{ width: 14px; height: 14px; border: 2px solid #000; margin: auto; }}</style></head><body>"
        html_cotejo += f"<div class='t-titulo'>{nom_torneo}</div><div class='t-fecha'>FECHA: {fec_torneo.strftime('%d/%m/%Y')}</div>"

        contador_a = 1
        pesos_cols = [f"Peso {i+1}" for i in range(gallos_en_archivo)]
        
        for r_idx, r_col in enumerate(pesos_cols):
            st.markdown(f"*RONDA {r_idx+1}*")
            html_cotejo += f"<div style='background:#eee; font-weight:bold; padding:5px; border:1px solid #000; text-align:center;'>RONDA {r_idx+1}</div>"
            html_cotejo += "<table><tr><th>G</th><th>ROJO</th><th>An.</th><th>DETALLE</th><th>An.</th><th>VERDE</th><th>G</th></tr>"
            
            lista = partidos_actuales.copy()
            p_n = 1
            while len(lista) >= 2:
                r, v = lista.pop(0), lista.pop(0)
                pr, pv = r.get(r_col, 0.0), v.get(r_col, 0.0)
                an1, an2 = f"{contador_a:03}", f"{contador_a+1:03}"
                contador_a += 2
                html_cotejo += f"<tr><td><div class='box'></div></td><td class='rojo'>{r['PARTIDO']}<br>{pr:.3f}</td><td><b>{an1}</b></td><td class='det'>P{p_n}<br>DIF: {abs(pr-pv):.3f}</td><td><b>{an2}</b></td><td class='verde'>{v['PARTIDO']}<br>{pv:.3f}</td><td><div class='box'></div></td></tr>"
                st.write(f"P{p_n}: {r['PARTIDO']} vs {v['PARTIDO']} (DIF: {abs(pr-pv):.3f})")
                p_n += 1
            html_cotejo += "</table>"

        html_cotejo += "</body></html>"
        
        if st.button("IMPRIMIR COTEJO COMPLETO"):
            js_print = f"<script>var w=window.open('','_blank');w.document.write({json.dumps(html_cotejo)});w.document.close();setTimeout(function(){{w.print();}},500);</script>"
            st.components.v1.html(js_print, height=0)
    else:
        st.info("Registre al menos 2 partidos para generar el cotejo.")

st.markdown('<p style="text-align:center; font-size:10px; color:#aaa; margin-top:50px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
