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
    
    .tabla-juez { 
        width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; 
        background-color: white; color: black; font-size: 11px; table-layout: fixed;
    }
    .tabla-juez th { background-color: #333; color: white; padding: 8px; border: 1px solid #000; text-align: center; }
    .tabla-juez td { border: 1px solid #000; padding: 6px 2px; text-align: center; vertical-align: middle; }
    .col-gan { width: 30px; }
    .col-an { width: 45px; }
    .col-detalle { width: 95px; background-color: #f0f0f0; font-weight: bold; }
    .border-rojo { border-left: 8px solid #d32f2f !important; }
    .border-verde { border-right: 8px solid #388e3c !important; }
    .casilla { width: 18px; height: 18px; border: 1px solid #000; margin: auto; background: white; }
    .titulo-ronda { background-color: #ddd; padding: 8px; margin-top: 20px; border: 1px solid #000; font-weight: bold; text-align: center; color: black; }
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
    # Inicializar el índice de edición si no existe
    if "edit_index" not in st.session_state: 
        st.session_state.edit_index = None

    col1, col2 = st.columns([1, 1.8])
    
    with col1:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], horizontal=True)
        
        # Lógica para precargar datos si se está editando
        default_name = ""
        default_weights = [1.800] * tipo_derby
        
        if st.session_state.edit_index is not None:
            idx_e = st.session_state.edit_index
            if idx_e < len(partidos):
                p_edit = partidos[idx_e]
                default_name = p_edit["PARTIDO"]
                for i in range(tipo_derby):
                    default_weights[i] = p_edit.get(f"Peso {i+1}", 1.800)
            st.info(f"Editando: {default_name}")

        with st.form("registro_form", clear_on_submit=True):
            n = st.text_input("PARTIDO:", value=default_name).upper()
            pesos_input = [st.number_input(f"Peso G{i+1}", 1.000, 4.000, default_weights[i], 0.001, format="%.3f") for i in range(tipo_derby)]
            
            btn_label = "💾 ACTUALIZAR" if st.session_state.edit_index is not None else "💾 GUARDAR"
            if st.form_submit_button(btn_label):
                if n:
                    nuevo_p = {"PARTIDO": n}
                    for idx, val in enumerate(pesos_input): nuevo_p[f"Peso {idx+1}"] = val
                    
                    if st.session_state.edit_index is not None:
                        partidos[st.session_state.edit_index] = nuevo_p
                        st.session_state.edit_index = None
                    else:
                        partidos.append(nuevo_p)
                    
                    guardar_todos(partidos)
                    st.rerun()
        
        if st.session_state.edit_index is not None:
            if st.button("❌ CANCELAR EDICIÓN"):
                st.session_state.edit_index = None
                st.rerun()

    with col2:
        if partidos:
            st.write("### LISTA DE PARTIDOS")
            # Mostrar tabla con botones de acción
            for i, p in enumerate(partidos):
                c_p, c_btn = st.columns([3, 1])
                pesos_str = " | ".join([f"{v:.3f}" for k, v in p.items() if "Peso" in k])
                c_p.markdown(f"*{i+1}. {p['PARTIDO']}* ({pesos_str})")
                if c_btn.button("✏️", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.rerun()
            
            if st.button("🗑️ LIMPIAR TODO"): 
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_index = None
                st.rerun()

with tab2:
    partidos = cargar_datos()
    col_a, col_b = st.columns(2)
    nombre_t = col_a.text_input("Nombre del Torneo:", "DERBY DE GALLOS")
    fecha_t = col_b.date_input("Fecha:", datetime.now())

    if len(partidos) >= 2:
        peleas = generar_cotejo_justo(partidos)
        pesos_keys = [c for c in partidos[0].keys() if "Peso" in c]
        
        html_impresion = f"""
        <html><head><title>Imprimir Cotejo</title>
        <style>
            @page {{ size: letter; margin: 10mm; }}
            body {{ font-family: Arial, sans-serif; padding: 0; color: black; }}
            .t-titulo {{ text-align: center; font-size: 24px; font-weight: bold; margin: 0; text-transform: uppercase; }}
            .t-fecha {{ text-align: center; font-size: 14px; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; table-layout: fixed; }}
            th {{ background: #222 !important; color: white !important; border: 1px solid #000; padding: 8px; font-size: 12px; }}
            td {{ border: 1px solid #000; text-align: center; padding: 8px 2px; font-size: 12px; vertical-align: middle; }}
            .ronda-header {{ background: #ddd !important; font-weight: bold; padding: 10px; border: 1px solid #000; text-align: center; font-size: 16px; margin-top: 5px; }}
            .rojo-celda {{ border-left: 10px solid #d32f2f !important; font-weight: bold; }}
            .verde-celda {{ border-right: 10px solid #388e3c !important; font-weight: bold; }}
            .detalle-celda {{ background: #f2f2f2 !important; font-size: 10px; font-weight: bold; line-height: 1.3; }}
            .casilla {{ width: 20px; height: 20px; border: 2px solid #000; margin: auto; }}
        </style></head><body>
        <div class='t-titulo'>{nombre_t}</div>
        <div class='t-fecha'>Fecha: {fecha_t.strftime('%d/%m/%Y')}</div>
        """

        contador_anillos = 1
        for r_idx, r_col in enumerate(pesos_keys):
            html_impresion += f"<div class='ronda-header'>RONDA {r_idx+1}</div>"
            html_impresion += """<table>
                <tr>
                    <th style='width:7%;'>G</th>
                    <th style='width:30%;'>LADO ROJO</th>
                    <th style='width:8%;'>An.</th>
                    <th style='width:10%;'>DETALLE</th>
                    <th style='width:8%;'>An.</th>
                    <th style='width:30%;'>LADO VERDE</th>
                    <th style='width:7%;'>G</th>
                </tr>"""
            
            st.markdown(f'<div class="titulo-ronda">RONDA {r_idx + 1}</div>', unsafe_allow_html=True)
            html_web = f'<table class="tabla-juez"><tr><th class="col-gan">G</th><th>LADO ROJO</th><th class="col-an">An.</th><th class="col-detalle">DETALLE</th><th class="col-an">An.</th><th>LADO VERDE</th><th class="col-gan">G</th></tr>'
            
            for i, (roj, ver) in enumerate(peleas):
                p_rojo, p_verde = roj.get(r_col, 0), ver.get(r_col, 0)
                dif = abs(p_rojo - p_verde)
                an1, an2 = f"{contador_anillos:03}", f"{contador_anillos + 1:03}"
                contador_anillos += 2
                
                num_pelea = i + 1
                
                fila_base = f"""
                <tr>
                    <td><div class="casilla"></div></td>
                    <td class="CLASS_ROJO"><b>{roj['PARTIDO']}</b><br>{p_rojo:.3f}</td>
                    <td><b>{an1}</b></td>
                    <td class="CLASS_DETALLE">P{num_pelea}<br>DIF: {dif:.3f}<br>E [ ]</td>
                    <td><b>{an2}</b></td>
                    <td class="CLASS_VERDE"><b>{ver['PARTIDO']}</b><br>{p_verde:.3f}</td>
                    <td><div class="casilla"></div></td>
                </tr>"""
                
                html_web += fila_base.replace("CLASS_ROJO", "border-rojo").replace("CLASS_VERDE", "border-verde").replace("CLASS_DETALLE", "col-detalle")
                html_impresion += fila_base.replace("CLASS_ROJO", "rojo-celda").replace("CLASS_VERDE", "verde-celda").replace("CLASS_DETALLE", "detalle-celda")
            
            html_web += "</table>"
            html_impresion += "</table>"
            st.markdown(html_web, unsafe_allow_html=True)

        html_impresion += "<p style='text-align:center; font-size:10px;'>Creado por HommerDesigns’s</p></body></html>"

        if st.button("📄 GENERAR HOJA DE IMPRESIÓN"):
            js = f"""
            <script>
                var win = window.open('', '_blank');
                win.document.write({json.dumps(html_impresion)});
                win.document.close();
                win.focus();
                setTimeout(function(){{ win.print(); }}, 500);
            </script>
            """
            st.components.v1.html(js, height=0)

    st.markdown('<p style="text-align:center; font-size:10px; margin-top:20px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
