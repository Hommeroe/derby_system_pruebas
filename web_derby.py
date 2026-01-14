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
    .tabla-ui { width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; background-color: white; color: black; font-size: 12px; table-layout: fixed; }
    .tabla-ui th { background-color: #333; color: white; padding: 10px; border: 1px solid #000; text-align: center; }
    .tabla-ui td { border: 1px solid #000; padding: 8px; text-align: center; vertical-align: middle; }
    .col-detalle { background-color: #f0f0f0; font-weight: bold; width: 95px; }
    .border-rojo { border-left: 8px solid #d32f2f !important; }
    .border-verde { border-right: 8px solid #388e3c !important; }
    .casilla { width: 18px; height: 18px; border: 1px solid #000; margin: auto; background: white; }
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
                    # Solo cargar hasta el número de gallos seleccionado actualmente
                    for i in range(1, num_gallos_actual + 1):
                        try:
                            # Si la línea tiene el peso lo ponemos, si no, 0.0
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
    partidos = cargar_datos(tipo_derby) # Pasamos el tipo de derby para limpiar la carga
    
    if "edit_index" not in st.session_state: st.session_state.edit_index = None
    
    col1, col2 = st.columns([1, 2])
    with col1:
        default_name = ""
        default_weights = [1.800] * tipo_derby
        
        if st.session_state.edit_index is not None:
            idx = st.session_state.edit_index
            if idx < len(partidos):
                p_edit = partidos[idx]
                default_name = p_edit["PARTIDO"]
                for i in range(tipo_derby): 
                    default_weights[i] = p_edit.get(f"Peso {i+1}", 1.800)
            st.info(f"Modificando: {default_name}")

        with st.form("registro_form", clear_on_submit=True):
            n = st.text_input("NOMBRE DEL PARTIDO:", value=default_name).upper()
            pesos_input = [st.number_input(f"Peso Gallo {i+1}", 1.000, 4.000, default_weights[i], 0.001, format="%.3f") for i in range(tipo_derby)]
            if st.form_submit_button("💾 GUARDAR DATOS"):
                if n:
                    nuevo_p = {"PARTIDO": n}
                    for idx_p, val in enumerate(pesos_input): nuevo_p[f"Peso {idx_p+1}"] = val
                    if st.session_state.edit_index is not None:
                        partidos[st.session_state.edit_index] = nuevo_p
                        st.session_state.edit_index = None
                    else: partidos.append(nuevo_p)
                    guardar_todos(partidos); st.rerun()
        
        if st.session_state.edit_index is not None:
            if st.button("❌ CANCELAR EDICIÓN"): st.session_state.edit_index = None; st.rerun()

    with col2:
        if partidos:
            st.write("### LISTA DE PARTIDOS")
            df_display = pd.DataFrame(partidos)
            df_display.index = range(1, len(df_display) + 1)
            
            # Formato de 3 decimales para que no se vea el "None"
            for col in df_display.columns:
                if "Peso" in col:
                    df_display[col] = df_display[col].map('{:,.3f}'.format)
            
            st.dataframe(df_display, use_container_width=True)
            
            st.write("Selecciona el número para corregir:")
            edit_cols = st.columns(10)
            for i in range(len(partidos)):
                with edit_cols[i % 10]:
                    if st.button(f"✏️{i+1}"):
                        st.session_state.edit_index = i
                        st.rerun()
            
            st.write("---")
            if st.button("🗑️ BORRAR TODA LA LISTA"): 
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_index = None
                st.rerun()

with tab2:
    # Se carga con el tipo de derby seleccionado para que el cotejo sea exacto
    partidos = cargar_datos(tipo_derby)
    col_a, col_b = st.columns(2)
    nombre_t = col_a.text_input("Torneo:", "DERBY DE GALLOS")
    fecha_t = col_b.date_input("Fecha del Evento:", datetime.now())

    if len(partidos) >= 2:
        peleas = generar_cotejo_justo(partidos)
        pesos_keys = [f"Peso {i+1}" for i in range(tipo_derby)]
        
        # HTML de Impresión (Diseño blindado igual a las fotos)
        html_impresion = f"<html><head><style>@page {{ size: letter; margin: 10mm; }} body {{ font-family: Arial; }} .t-titulo {{ text-align: center; font-size: 22px; font-weight: bold; }} .t-fecha {{ text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; }} table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 20px; }} th {{ background: #222; color: white; border: 1px solid #000; padding: 8px; font-size: 12px; }} td {{ border: 1px solid #000; text-align: center; padding: 6px 2px; font-size: 12px; }} .ronda-header {{ background: #eee; font-weight: bold; padding: 8px; border: 1px solid #000; text-align: center; }} .rojo-celda {{ border-left: 10px solid #d32f2f; font-weight: bold; }} .verde-celda {{ border-right: 10px solid #388e3c; font-weight: bold; }} .detalle-celda {{ background: #f2f2f2; font-size: 10px; font-weight: bold; }} .casilla {{ width: 18px; height: 18px; border: 2px solid #000; margin: auto; }}</style></head><body><div class='t-titulo'>{nombre_t}</div><div class='t-fecha'>FECHA: {fecha_t.strftime('%d/%m/%Y')}</div>"

        contador_anillos = 1
        for r_idx, r_col in enumerate(pesos_keys):
            html_impresion += f"<div class='ronda-header'>RONDA {r_idx+1}</div>"
            header = "<table><tr><th style='width:7%;'>G</th><th style='width:30%;'>ROJO</th><th style='width:8%;'>An.</th><th style='width:10%;'>DETALLE</th><th style='width:8%;'>An.</th><th style='width:30%;'>VERDE</th><th style='width:7%;'>G</th></tr>"
            html_impresion += header
            
            st.markdown(f'<div class="titulo-ronda">RONDA {r_idx + 1}</div>', unsafe_allow_html=True)
            html_web = f'<table class="tabla-ui"><tr><th style="width:35px">G</th><th>ROJO</th><th style="width:45px">An.</th><th class="col-detalle">DETALLE</th><th style="width:45px">An.</th><th>VERDE</th><th style="width:35px">G</th></tr>'
            
            for i, (roj, ver) in enumerate(peleas):
                p_rojo, p_verde = roj.get(r_col, 0.0), ver.get(r_col, 0.0)
                dif = abs(p_rojo - p_verde)
                an1, an2 = f"{contador_anillos:03}", f"{contador_anillos + 1:03}"
                contador_anillos += 2
                
                fila = f"<tr><td><div class='casilla'></div></td><td class='CLASS_ROJO'><b>{roj['PARTIDO']}</b><br>{p_rojo:.3f}</td><td><b>{an1}</b></td><td class='CLASS_DETALLE'>P{i+1}<br>DIF: {dif:.3f}<br>E [ ]</td><td><b>{an2}</b></td><td class='CLASS_VERDE'><b>{ver['PARTIDO']}</b><br>{p_verde:.3f}</td><td><div class='casilla'></div></td></tr>"
                html_web += fila.replace("CLASS_ROJO", "border-rojo").replace("CLASS_VERDE", "border-verde").replace("CLASS_DETALLE", "col-detalle")
                html_impresion += fila.replace("CLASS_ROJO", "rojo-celda").replace("CLASS_VERDE", "verde-celda").replace("CLASS_DETALLE", "detalle-celda")
            
            html_web += "</table>"
            html_impresion += "</table>"
            st.markdown(html_web, unsafe_allow_html=True)

        html_impresion += "</body></html>"
        if st.button("📄 GENERAR HOJA DE IMPRESIÓN"):
            js = f"<script>var win = window.open('', '_blank'); win.document.write({json.dumps(html_impresion)}); win.document.close(); win.focus(); setTimeout(function(){{ win.print(); }}, 500);</script>"
            st.components.v1.html(js, height=0)

    st.markdown('<p style="text-align:center; font-size:10px; margin-top:20px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
