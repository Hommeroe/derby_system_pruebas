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
    
    /* Estilos para la tabla en pantalla */
    .tabla-juez { 
        width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; 
        background-color: white; color: black; font-size: 11px; table-layout: fixed;
    }
    .tabla-juez th { background-color: #333; color: white; padding: 5px; border: 1px solid #000; }
    .tabla-juez td { border: 1px solid #000; padding: 6px 2px; text-align: center; vertical-align: middle; }
    .col-gan { width: 25px; }
    .col-an { width: 35px; }
    .col-detalle { width: 65px; background-color: #f0f0f0; font-weight: bold; }
    .border-rojo { border-left: 6px solid #d32f2f !important; }
    .border-verde { border-right: 6px solid #388e3c !important; }
    .casilla { width: 16px; height: 16px; border: 1px solid #000; margin: auto; background: white; }
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
    if "edit_index" not in st.session_state: st.session_state.edit_index = None
    col1, col2 = st.columns([1, 1.5])
    with col1:
        tipo_derby = st.radio("Gallos:", [2, 3, 4], horizontal=True)
        default_name = ""
        default_weights = [1.800] * tipo_derby
        if st.session_state.edit_index is not None:
            p_edit = partidos[st.session_state.edit_index]
            default_name = p_edit["PARTIDO"]
            for i in range(tipo_derby): default_weights[i] = p_edit.get(f"Peso {i+1}", 1.800)

        with st.form("registro_form", clear_on_submit=True):
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
            st.dataframe(df, use_container_width=True)
            if st.button("🗑️ LIMPIAR TODO"): 
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()

with tab2:
    partidos = cargar_datos()
    col_a, col_b = st.columns(2)
    nombre_t = col_a.text_input("Nombre del Torneo:", "DERBY DE GALLOS")
    fecha_t = col_b.date_input("Fecha:", datetime.now())

    if len(partidos) >= 2:
        peleas = generar_cotejo_justo(partidos)
        pesos_keys = [c for c in partidos[0].keys() if "Peso" in c]
        
        # PREPARAR HTML PARA LA NUEVA VENTANA
        html_impresion = f"""
        <html><head><title>Imprimir Cotejo</title>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            .t-titulo {{ text-align: center; font-size: 24px; font-weight: bold; margin: 0; }}
            .t-fecha {{ text-align: center; font-size: 14px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; table-layout: fixed; }}
            th {{ background: #333; color: white; border: 1px solid #000; padding: 5px; font-size: 12px; }}
            td {{ border: 1px solid #000; text-align: center; padding: 8px 2px; font-size: 12px; }}
            .ronda-header {{ background: #eee; font-weight: bold; padding: 10px; border: 1px solid #000; text-align: center; font-size: 16px; }}
            .rojo {{ border-left: 8px solid #d32f2f !important; font-weight: bold; }}
            .verde {{ border-right: 8px solid #388e3c !important; font-weight: bold; }}
            .detalle {{ background: #f9f9f9; font-size: 11px; font-weight: bold; }}
            .casilla {{ width: 18px; height: 18px; border: 1px solid #000; margin: auto; }}
        </style></head><body>
        <div class='t-titulo'>{nombre_t}</div>
        <div class='t-fecha'>Fecha: {fecha_t.strftime('%d/%m/%Y')}</div>
        """

        contador_anillos = 1
        for r_idx, r_col in enumerate(pesos_keys):
            st.markdown(f'<div class="titulo-ronda">RONDA {r_idx + 1}</div>', unsafe_allow_html=True)
            html_impresion += f"<div class='ronda-header'>RONDA {r_idx+1}</div>"
            html_impresion += "<table><tr><th>G</th><th>ROJO</th><th>An.</th><th>DETALLE</th><th>An.</th><th>VERDE</th><th>G</th></tr>"
            
            # Tabla para visualización en web
            html_web = '<table class="tabla-juez"><tr><th class="col-gan">G</th><th>ROJO</th><th class="col-an">An.</th><th class="col-detalle">DETALLE</th><th class="col-an">An.</th><th>VERDE</th><th class="col-gan">G</th></tr>'
            
            for i, (roj, ver) in enumerate(peleas):
                p_rojo, p_verde = roj.get(r_col, 0), ver.get(r_col, 0)
                dif = abs(p_rojo - p_verde)
                an1, an2 = f"{contador_anillos:03}", f"{contador_anillos + 1:03}"
                contador_anillos += 2
                
                fila = f"""
                <tr>
                    <td class="col-gan"><div class="casilla"></div></td>
                    <td class="border-rojo"><b>{roj['PARTIDO']}</b><br>{p_rojo:.3f}</td>
                    <td><b>{an1}</b></td>
                    <td class="col-detalle">P{i+1}<br>DIF: {dif:.3f}<br>E [ ]</td>
                    <td><b>{an2}</b></td>
                    <td class="border-verde"><b>{ver['PARTIDO']}</b><br>{p_verde:.3f}</td>
                    <td class="col-gan"><div class="casilla"></div></td>
                </tr>"""
                html_web += fila
                html_impresion += fila.replace('border-rojo', 'rojo').replace('border-verde', 'verde').replace('col-detalle', 'detalle')
            
            html_web += "</table>"
            html_impresion += "</table>"
            st.markdown(html_web, unsafe_allow_html=True)

        html_impresion += "<p style='text-align:center; font-size:10px;'>Creado por HommerDesigns’s</p></body></html>"

        # BOTÓN MAGICO QUE ABRE VENTANA NUEVA
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
