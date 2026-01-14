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
    
    /* EL DISEÑO BONITO QUE TE GUSTÓ */
    .tabla-ui { 
        width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; 
        background-color: white; color: black; font-size: 14px;
    }
    .tabla-ui th { background-color: #f8f9fa; color: #333; padding: 12px; border: 1px solid #dee2e6; text-align: center; }
    .tabla-ui td { border: 1px solid #dee2e6; padding: 10px; text-align: center; vertical-align: middle; }
    
    .titulo-ronda { background-color: #ddd; padding: 8px; margin-top: 20px; border: 1px solid #000; font-weight: bold; text-align: center; color: black; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"

def cargar_datos(num_gallos_actual):
    partidos = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                p = linea.strip().split("|")
                if len(p) >= 2:
                    d = {"PARTIDO": p[0]}
                    for i in range(1, num_gallos_actual + 1):
                        try:
                            val = float(p[i]) if i < len(p) else 0.0
                            d[f"Peso {i}"] = val
                        except:
                            d[f"Peso {i}"] = 0.0
                    partidos.append(d)
    return partidos

def guardar_todos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

def generar_cotejo_justo(lista_original):
    lista = lista_original.copy()
    cotejo = []
    while len(lista) >= 2:
        rojo = lista.pop(0)
        encontrado = False
        for i in range(len(lista)):
            if lista[i]['PARTIDO'] != rojo['PARTIDO']:
                verde = lista.pop(i); cotejo.append((rojo, verde)); encontrado = True; break
        if not encontrado:
            verde = lista.pop(0); cotejo.append((rojo, verde))
    return cotejo

# --- INTERFAZ ---
st.markdown('<p class="software-brand">DerbySystem PRUEBAS</p>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO"])

with tab1:
    tipo_derby = st.radio("Gallos:", [2, 3, 4], horizontal=True)
    partidos = cargar_datos(tipo_derby)
    
    if "edit_index" not in st.session_state: st.session_state.edit_index = None
    
    col_input, col_tabla = st.columns([1.2, 2.5])
    
    with col_input:
        st.write("### DATOS")
        default_name = ""
        default_weights = [1.800] * tipo_derby
        
        if st.session_state.edit_index is not None:
            idx = st.session_state.edit_index
            if idx < len(partidos):
                p_edit = partidos[idx]
                default_name = p_edit["PARTIDO"]
                for i in range(tipo_derby): 
                    default_weights[i] = p_edit.get(f"Peso {i+1}", 1.800)
            st.info(f"Editando: {default_name}")

        with st.form("registro_form", clear_on_submit=True):
            n = st.text_input("NOMBRE DEL PARTIDO:", value=default_name).upper()
            pesos_input = [st.number_input(f"Peso G{i+1}", 1.000, 4.000, default_weights[i], 0.001, format="%.3f") for i in range(tipo_derby)]
            if st.form_submit_button("💾 GUARDAR"):
                if n:
                    nuevo_p = {"PARTIDO": n}
                    for idx_p, val in enumerate(pesos_input): nuevo_p[f"Peso {idx_p+1}"] = val
                    if st.session_state.edit_index is not None:
                        partidos[st.session_state.edit_index] = nuevo_p
                        st.session_state.edit_index = None
                    else: partidos.append(nuevo_p)
                    guardar_todos(partidos); st.rerun()
        
        if st.session_state.edit_index is not None:
            if st.button("❌ CANCELAR"): st.session_state.edit_index = None; st.rerun()

    with col_tabla:
        if partidos:
            st.write("### LISTA DE PARTIDOS")
            
            # Formatear el DataFrame para que se vea como la tabla sencilla
            df = pd.DataFrame(partidos)
            df.index = range(1, len(df) + 1)
            for col in df.columns:
                if "Peso" in col: df[col] = df[col].map('{:,.3f}'.format)
            
            # Mostramos la tabla bonita de Streamlit
            st.table(df)

            # Botones de Acción debajo de la tabla para no romper la estética
            st.write("*ACCIONES:*")
            cols_accion = st.columns(😎
            for i in range(len(partidos)):
                with cols_accion[i % 8]:
                    # Botón doble: Editar y luego Eliminar
                    if st.button(f"✏️{i+1}", key=f"e_{i}"):
                        st.session_state.edit_index = i
                        st.rerun()
                    if st.button(f"🗑️{i+1}", key=f"d_{i}"):
                        partidos.pop(i)
                        guardar_todos(partidos)
                        st.rerun()
            
            st.write("---")
            if st.button("🧨 LIMPIAR TODO"): 
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_index = None
                st.rerun()

with tab2:
    # El cotejo usa el anillo automático [2026-01-14]
    partidos = cargar_datos(tipo_derby)
    col_a, col_b = st.columns(2)
    nombre_t = col_a.text_input("Torneo:", "DERBY DE GALLOS")
    fecha_t = col_b.date_input("Fecha:", datetime.now())

    if len(partidos) >= 2:
        peleas = generar_cotejo_justo(partidos)
        pesos_keys = [f"Peso {i+1}" for i in range(tipo_derby)]
        
        # HTML de Impresión (Mismo diseño de tus fotos)
        html_impresion = f"<html><head><style>@page {{ size: letter; margin: 10mm; }} body {{ font-family: Arial; }} .t-titulo {{ text-align: center; font-size: 22px; font-weight: bold; }} .t-fecha {{ text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; }} table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 20px; }} th {{ background: #222; color: white; border: 1px solid #000; padding: 8px; font-size: 12px; }} td {{ border: 1px solid #000; text-align: center; padding: 6px 2px; font-size: 12px; }} .ronda-header {{ background: #eee; font-weight: bold; padding: 8px; border: 1px solid #000; text-align: center; }} .rojo-celda {{ border-left: 10px solid #d32f2f; font-weight: bold; }} .verde-celda {{ border-right: 10px solid #388e3c; font-weight: bold; }} .detalle-celda {{ background: #f2f2f2; font-size: 10px; font-weight: bold; }}</style></head><body><div class='t-titulo'>{nombre_t}</div><div class='t-fecha'>FECHA: {fecha_t.strftime('%d/%m/%Y')}</div>"

        contador_anillos = 1
        for r_idx, r_col in enumerate(pesos_keys):
            html_impresion += f"<div class='ronda-header'>RONDA {r_idx+1}</div>"
            header = "<table><tr><th style='width:7%;'>G</th><th style='width:30%;'>ROJO</th><th style='width:8%;'>An.</th><th style='width:10%;'>DETALLE</th><th style='width:8%;'>An.</th><th style='width:30%;'>VERDE</th><th style='width:7%;'>G</th></tr>"
            html_impresion += header
            
            st.markdown(f'<div class="titulo-ronda">RONDA {r_idx + 1}</div>', unsafe_allow_html=True)
            
            for i, (roj, ver) in enumerate(peleas):
                p_rojo, p_verde = roj.get(r_col, 0.0), ver.get(r_col, 0.0)
                dif = abs(p_rojo - p_verde)
                an1, an2 = f"{contador_anillos:03}", f"{contador_anillos + 1:03}"
                contador_anillos += 2
                
                fila = f"<tr><td>[ ]</td><td class='rojo-celda'><b>{roj['PARTIDO']}</b><br>{p_rojo:.3f}</td><td><b>{an1}</b></td><td class='detalle-celda'>P{i+1}<br>DIF: {dif:.3f}<br>E [ ]</td><td><b>{an2}</b></td><td class='verde-celda'><b>{ver['PARTIDO']}</b><br>{p_verde:.3f}</td><td>[ ]</td></tr>"
                html_impresion += fila
                
                # Vista previa en web sencilla
                st.write(f"Pelea {i+1}: {roj['PARTIDO']} ({p_rojo:.3f}) vs {ver['PARTIDO']} ({p_verde:.3f}) | Anillos: {an1}-{an2}")
            
            html_impresion += "</table>"

        html_impresion += "</body></html>"
        if st.button("📄 GENERAR HOJA DE IMPRESIÓN"):
            js = f"<script>var win = window.open('', '_blank'); win.document.write({json.dumps(html_impresion)}); win.document.close(); win.focus(); setTimeout(function(){{ win.print(); }}, 500);</script>"
            st.components.v1.html(js, height=0)

    st.markdown('<p style="text-align:center; font-size:10px; margin-top:20px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
