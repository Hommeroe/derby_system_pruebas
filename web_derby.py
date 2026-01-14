import streamlit as st
import pandas as pd
import os
from datetime import datetime

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
    
    /* ENCABEZADO DE IMPRESIÓN */
    .encabezado-impresion { display: none; text-align: center; margin-bottom: 10px; border-bottom: 2px solid #000; padding-bottom: 5px; }
    .torneo-titulo { font-size: 20px; font-weight: bold; text-transform: uppercase; margin: 0; color: black; }
    .torneo-fecha { font-size: 12px; color: black; margin: 5px 0; }

    /* TABLA PROFESIONAL */
    .tabla-juez { 
        width: 100% !important; 
        border-collapse: collapse !important; 
        font-family: Arial, sans-serif !important; 
        background-color: white !important; 
        color: black !important;
        font-size: 10px;
        table-layout: fixed;
    }
    .tabla-juez th { background-color: #333 !important; color: white !important; padding: 5px; text-align: center; border: 1px solid #000 !important; }
    .tabla-juez td { border: 1px solid #000 !important; padding: 6px 2px; text-align: center; vertical-align: middle; color: black !important; }
    
    /* COLUMNAS */
    .col-gan { width: 25px; }
    .col-an { width: 35px; }
    .col-detalle { width: 65px; background-color: #f9f9f9 !important; font-size: 9px; font-weight: bold; }
    .col-partido { width: auto; }

    /* BORDES DE COLOR */
    .border-rojo { border-left: 6px solid #d32f2f !important; }
    .border-verde { border-right: 6px solid #388e3c !important; }
    
    .casilla { width: 16px; height: 16px; border: 1px solid #000 !important; margin: auto; background-color: white !important; }
    .nombre-partido { font-weight: bold; font-size: 11px; display: block; }
    .peso-texto { font-weight: normal; font-size: 10px; color: black !important; }
    .titulo-ronda { background-color: #eee !important; padding: 8px; margin-top: 20px; border: 1px solid #000 !important; font-weight: bold; text-align: center; color: black !important; font-size: 14px; }

    /* CORRECCIÓN DE IMPRESIÓN */
    @media print {
        @page { size: auto; margin: 10mm; }
        body { background: white !important; }
        .no-print, header, footer, .stTabs, [data-testid="stSidebar"], .stSelectbox, .stButton, [data-testid="stForm"] { 
            display: none !important; 
        }
        .encabezado-impresion { display: block !important; visibility: visible !important; }
        .tabla-juez { visibility: visible !important; display: table !important; width: 100% !important; }
        .titulo-ronda { visibility: visible !important; display: block !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        .stMarkdown { display: block !important; }
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"

def cargar_datos():
    partidos = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                p = linea.strip().split("|")
                if len(p) >= 2:
                    d = {"PARTIDO": p[0]}
                    for i in range(1, len(p)): d[f"Peso {i}"] = float(p[i])
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
    partidos = cargar_datos()
    if "edit_index" not in st.session_state: st.session_state.edit_index = None
    col1, col2 = st.columns([1, 1.5])
    with col1:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], horizontal=True)
        default_name = ""
        default_weights = [1.800] * tipo_derby
        if st.session_state.edit_index is not None and st.session_state.edit_index < len(partidos):
            p_edit = partidos[st.session_state.edit_index]; default_name = p_edit["PARTIDO"]
            for i in range(tipo_derby): default_weights[i] = p_edit.get(f"Peso {i+1}", 1.800)

        with st.form("registro_form", clear_on_submit=(st.session_state.edit_index is None)):
            n = st.text_input("PARTIDO:", value=default_name).upper()
            pesos_input = [st.number_input(f"Peso G{i+1}", 1.000, 4.000, default_weights[i], 0.001, format="%.3f") for i in range(tipo_derby)]
            if st.form_submit_button("💾 GUARDAR"):
                if n:
                    nuevo_p = {"PARTIDO": n}
                    for idx, val in enumerate(pesos_input): nuevo_p[f"Peso {idx+1}"] = val
                    if st.session_state.edit_index is not None:
                        partidos[st.session_state.edit_index] = nuevo_p
                        st.session_state.edit_index = None
                    else: partidos.append(nuevo_p)
                    guardar_todos(partidos); st.rerun()

    with col2:
        if partidos:
            df = pd.DataFrame(partidos)
            df.index = df.index + 1
            config_columnas = {f"Peso {i+1}": st.column_config.NumberColumn(format="%.3f") for i in range(4)}
            st.dataframe(df, use_container_width=True, column_config=config_columnas)
            idx_to_edit = st.selectbox("Editar:", range(1, len(partidos) + 1), format_func=lambda x: f"{partidos[x-1]['PARTIDO']}")
            if st.button("✏️ EDITAR"): st.session_state.edit_index = idx_to_edit - 1; st.rerun()
            if st.button("🗑️ LIMPIAR"): 
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_index = None; st.rerun()

with tab2:
    partidos = cargar_datos()
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    nombre_torneo = col_a.text_input("Nombre del Torneo:", "DERBY DE GALLOS")
    fecha_torneo = col_b.date_input("Fecha del Evento:", datetime.now())
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="encabezado-impresion">
            <p class="torneo-titulo">{nombre_torneo}</p>
            <p class="torneo-fecha">Fecha: {fecha_torneo.strftime('%d/%m/%Y')}</p>
        </div>
    """, unsafe_allow_html=True)

    if len(partidos) >= 2:
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        opciones_print = ["TODOS"] + [p["PARTIDO"] for p in partidos]
        seleccion_print = st.selectbox("Filtrar por Partido:", opciones_print)
        if st.button("📄 IMPRIMIR HOJA"): 
            st.components.v1.html("<script>window.parent.print();</script>", height=0)
        st.markdown('</div>', unsafe_allow_html=True)

        peleas = generar_cotejo_justo(partidos)
        pesos_keys = [c for c in partidos[0].keys() if "Peso" in c]
        contador_anillos = 1

        for r_idx, r_col in enumerate(pesos_keys):
            st.markdown(f'<div class="titulo-ronda">RONDA {r_idx + 1}</div>', unsafe_allow_html=True)
            html_tabla = """<table class="tabla-juez">
                <tr><th class="col-gan">G</th><th class="col-partido">ROJO</th><th class="col-an">An.</th><th class="col-detalle">DETALLE</th><th class="col-an">An.</th><th class="col-partido">VERDE</th><th class="col-gan">G</th></tr>"""
            
            for i, (roj, ver) in enumerate(peleas):
                if seleccion_print != "TODOS" and roj["PARTIDO"] != seleccion_print and ver["PARTIDO"] != seleccion_print:
                    continue
                p_rojo, p_verde = roj.get(r_col, 0), ver.get(r_col, 0)
                diferencia = abs(p_rojo - p_verde)
                an_rojo, an_verde = f"{contador_anillos:03}", f"{contador_anillos + 1:03}"
                contador_anillos += 2
                
                html_tabla += f"""
                <tr>
                    <td class="col-gan"><div class="casilla"></div></td>
                    <td class="col-partido border-rojo"><span class="nombre-partido">{roj["PARTIDO"]}</span><br><span class="peso-texto">{p_rojo:.3f}</span></td>
                    <td class="col-an"><b>{an_rojo}</b></td>
                    <td class="col-detalle"><b>P{i+1}</b><br>DIF: {diferencia:.3f}<br>E [ ]</td>
                    <td class="col-an"><b>{an_verde}</b></td>
                    <td class="col-partido border-verde"><span class="nombre-partido">{ver["PARTIDO"]}</span><br><span class="peso-texto">{p_verde:.3f}</span></td>
                    <td class="col-gan"><div class="casilla"></div></td>
                </tr>"""
            html_tabla += "</table>"
            st.markdown(html_tabla, unsafe_allow_html=True)
            
    st.markdown('<p style="text-align:center; font-size:10px; margin-top:20px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
