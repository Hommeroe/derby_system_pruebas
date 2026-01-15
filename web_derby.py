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
# Usamos iconos de texto más seguros
tab1, tab2 = st.tabs(["📝 REGISTRO", "📊 COTEJO"])

with tab1:
    tipo_derby = st.radio("Gallos:", [2, 3, 4], horizontal=True)
    partidos = cargar_datos(tipo_derby)
    
    if "edit_idx" not in st.session_state: st.session_state.edit_idx = None
    
    col_reg, col_list = st.columns([1.2, 2.5])
    
    with col_reg:
        st.write("### DATOS")
        v_nombre = ""
        v_pesos = [1.800] * tipo_derby
        
        if st.session_state.edit_idx is not None:
            idx = st.session_state.edit_idx
            if idx < len(partidos):
                p_edit = partidos[idx]
                v_nombre = p_edit["PARTIDO"]
                for i in range(tipo_derby):
                    v_pesos[i] = p_edit.get(f"Peso {i+1}", 1.800)
            st.info(f"Modificando # {idx + 1}")

        with st.form("form_registro", clear_on_submit=True):
            n = st.text_input("NOMBRE DEL PARTIDO:", value=v_nombre).upper()
            pesos_in = [st.number_input(f"Peso G{i+1}", 1.000, 4.000, v_pesos[i], 0.001, format="%.3f") for i in range(tipo_derby)]
            
            label_boton = "💾 ACTUALIZAR" if st.session_state.edit_idx is not None else "💾 GUARDAR"
            if st.form_submit_button(label_boton):
                if n:
                    nuevo = {"PARTIDO": n}
                    for i, v in enumerate(pesos_in): nuevo[f"Peso {i+1}"] = v
                    if st.session_state.edit_idx is not None:
                        partidos[st.session_state.edit_idx] = nuevo
                        st.session_state.edit_idx = None
                    else:
                        partidos.append(nuevo)
                    guardar_todos(partidos); st.rerun()
        
        if st.session_state.edit_idx is not None:
            if st.button("❌ CANCELAR"):
                st.session_state.edit_idx = None
                st.rerun()

    with col_list:
        if partidos:
            st.write("### LISTA DE PARTIDOS")
            df = pd.DataFrame(partidos)
            df.index = range(1, len(df) + 1)
            for c in df.columns:
                if "Peso" in c: df[c] = df[c].map('{:,.3f}'.format)
            
            # TU TABLA DE CELDAS PREFERIDA
            st.table(df)
            
            st.write("*ACCIONES:*")
            for i in range(len(partidos)):
                c1, c2, _ = st.columns([1, 1, 4])
                # Usamos iconos y texto para asegurar que se vea bien
                if c1.button(f"✏️ {i+1}", key=f"e{i}"):
                    st.session_state.edit_idx = i
                    st.rerun()
                if c2.button(f"🗑️ {i+1}", key=f"b{i}"):
                    partidos.pop(i)
                    guardar_todos(partidos)
                    st.rerun()
            
            st.write("---")
            if st.button("🗑️ LIMPIAR TODO"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_idx = None
                st.rerun()

with tab2:
    partidos = cargar_datos(tipo_derby)
    c_t, c_f = st.columns(2)
    nombre_torneo = c_t.text_input("Torneo:", "DERBY DE GALLOS")
    fecha_torneo = c_f.date_input("Fecha:", datetime.now())

    if len(partidos) >= 2:
        peleas = generar_cotejo_justo(partidos)
        pesos_k = [f"Peso {i+1}" for i in range(tipo_derby)]
        
        # Diseño de impresión con el anillo automático
        html_doc = f"<html><head><style>@page {{ size: letter; margin: 10mm; }} body {{ font-family: Arial; }} .t-titulo {{ text-align: center; font-size: 22px; font-weight: bold; }} .t-fecha {{ text-align: center; margin-bottom: 20px; border-bottom: 2px solid #000; }} table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 20px; }} th {{ background: #222; color: white; border: 1px solid #000; padding: 8px; font-size: 12px; }} td {{ border: 1px solid #000; text-align: center; padding: 6px 2px; font-size: 12px; }} .ronda-h {{ background: #eee; font-weight: bold; padding: 8px; border: 1px solid #000; text-align: center; }} .rojo {{ border-left: 10px solid #d32f2f; font-weight: bold; }} .verde {{ border-right: 10px solid #388e3c; font-weight: bold; }} .det {{ background: #f2f2f2; font-size: 10px; font-weight: bold; }} .box {{ width: 18px; height: 18px; border: 2px solid #000; margin: auto; }}</style></head><body><div class='t-titulo'>{nombre_torneo}</div><div class='t-fecha'>FECHA: {fecha_torneo.strftime('%d/%m/%Y')}</div>"

        contador_a = 1
        for r_idx, r_col in enumerate(pesos_k):
            st.markdown(f'<div style="background:#ddd; padding:8px; border:1px solid #000; font-weight:bold; text-align:center;">RONDA {r_idx+1}</div>', unsafe_allow_html=True)
            html_doc += f"<div class='ronda-h'>RONDA {r_idx+1}</div>"
            html_doc += "<table><tr><th style='width:7%;'>G</th><th style='width:30%;'>ROJO</th><th style='width:8%;'>An.</th><th style='width:10%;'>DETALLE</th><th style='width:8%;'>An.</th><th style='width:30%;'>VERDE</th><th style='width:7%;'>G</th></tr>"
            
            for i, (roj, ver) in enumerate(peleas):
                p_r, p_v = roj.get(r_col, 0.0), ver.get(r_col, 0.0)
                dif = abs(p_r - p_v)
                an1, an2 = f"{contador_a:03}", f"{contador_a + 1:03}"
                contador_a += 2
                
                fila = f"<tr><td><div class='box'></div></td><td class='rojo'><b>{roj['PARTIDO']}</b><br>{p_r:.3f}</td><td><b>{an1}</b></td><td class='det'>P{i+1}<br>DIF: {dif:.3f}<br>E [ ]</td><td><b>{an2}</b></td><td class='verde'><b>{ver['PARTIDO']}</b><br>{p_v:.3f}</td><td><div class='box'></div></td></tr>"
                html_doc += fila
                st.write(f"Pelea {i+1}: {roj['PARTIDO']} vs {ver['PARTIDO']} (Anillos {an1}-{an2})")
            
            html_doc += "</table>"

        html_doc += "</body></html>"
        if st.button("📄 GENERAR HOJA DE IMPRESIÓN"):
            js = f"<script>var win = window.open('', '_blank'); win.document.write({json.dumps(html_doc)}); win.document.close(); win.focus(); setTimeout(function(){{ win.print(); }}, 500);</script>"
            st.components.v1.html(js, height=0)

    st.markdown('<p style="text-align:center; font-size:10px; margin-top:20px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
