import streamlit as st
import pandas as pd
import os

# --- 1. SEGURIDAD ---
if "autenticado" not in st.session_state:
    st.title("Acceso Privado")
    password = st.text_input("Clave de Acceso:", type="password")
    if st.button("Entrar"):
        if password == "2026":
            st.session_state["autenticado"] = True
            st.rerun()
    st.stop()

# --- 2. CONFIGURACION ---
st.set_page_config(page_title="DerbySystem PRUEBAS", layout="wide")

st.markdown("""
    <style>
    .software-brand { color: #555; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 12px; letter-spacing: 5px; text-align: center; text-transform: uppercase; margin-top: -10px; margin-bottom: 10px; }
    .footer-hommer { text-align: center; color: #666; font-size: 11px; font-family: 'Courier New', Courier, monospace; margin-top: 50px; padding-top: 20px; border-top: 1px solid #333; letter-spacing: 2px; }
    
    @media print {
        .no-print, header, footer, .stTabs, .stSelectbox, .stButton { display: none !important; }
        .report-container { background-color: white !important; color: black !important; }
        body { background-color: white !important; }
    }
    .tabla-juez { 
        width: 100%; 
        border-collapse: collapse; 
        font-family: Arial, sans-serif; 
        background: white; 
        color: black;
        font-size: 12px;
    }
    .tabla-juez th { background-color: #333; color: white; padding: 4px; text-align: center; border: 1px solid #000; }
    .tabla-juez td { border: 1px solid #000; padding: 5px; text-align: center; }
    .casilla { width: 16px; height: 16px; border: 2px solid #000; margin: auto; }
    .nombre-partido { font-weight: bold; font-size: 13px; }
    .titulo-ronda { background: #eee; padding: 8px; margin-top: 15px; border: 1px solid #000; font-weight: bold; text-align: center; color: black; }
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
                    for i in range(1, len(p)):
                        d[f"Peso {i}"] = float(p[i])
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

# --- 3. INTERFAZ ---
st.markdown('<p class="software-brand">DerbySystem PRUEBAS</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO E IMPRESIÓN"])

with tab1:
    st.subheader("Panel de Registro")
    tipo_derby = st.radio("Gallo por Partido:", [2, 3, 4], horizontal=True)
    partidos = cargar_datos()
    
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None

    col1, col2 = st.columns([1, 2])
    with col1:
        default_name = ""
        default_weights = [1.800] * tipo_derby
        
        if st.session_state.edit_index is not None and st.session_state.edit_index < len(partidos):
            p_edit = partidos[st.session_state.edit_index]
            default_name = p_edit["PARTIDO"]
            for i in range(tipo_derby):
                default_weights[i] = p_edit.get(f"Peso {i+1}", 1.800)

        with st.form("registro_form", clear_on_submit=(st.session_state.edit_index is None)):
            label_modo = "🟠 EDITANDO" if st.session_state.edit_index is not None else "🟢 NUEVO"
            st.markdown(f"*{label_modo}*")
            n = st.text_input("NOMBRE DEL PARTIDO:", value=default_name).upper()
            pesos_input = []
            for i in range(1, tipo_derby + 1):
                p = st.number_input(f"Peso Gallo {i}", 1.800, 2.680, default_weights[i-1], 0.001, format="%.3f")
                pesos_input.append(p)
            
            if st.form_submit_button("💾 GUARDAR"):
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

    with col2:
        if partidos:
            df = pd.DataFrame(partidos)
            df.index = df.index + 1
            st.dataframe(df, use_container_width=True)
            idx_to_edit = st.selectbox("Seleccionar para editar:", range(1, len(partidos) + 1), format_func=lambda x: f"Partido: {partidos[x-1]['PARTIDO']}")
            if st.button("✏️ EDITAR SELECCIONADO", use_container_width=True):
                st.session_state.edit_index = idx_to_edit - 1
                st.rerun()
            if st.button("🗑️ LIMPIAR TODO", use_container_width=True):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_index = None
                st.rerun()

with tab2:
    partidos = cargar_datos()
    if len(partidos) >= 2:
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        opciones_print = ["VER TODO EL EVENTO"] + [p["PARTIDO"] for p in partidos]
        seleccion_print = st.selectbox("🖨️ Filtrar Hoja de Partido:", opciones_print)
        
        if st.button("📄 ACTIVAR IMPRESIÓN"):
            st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        peleas = generar_cotejo_justo(partidos)
        pesos_keys = [c for c in partidos[0].keys() if "Peso" in c]

        for r_idx, r_col in enumerate(pesos_keys):
            st.markdown(f'<div class="titulo-ronda">RONDA {r_idx + 1}</div>', unsafe_allow_html=True)
            html_tabla = """<table class="tabla-juez">
                <tr><th colspan="3">LADO ROJO</th><th colspan="3">DETALLES DEL COTEJO</th><th colspan="3">LADO VERDE</th></tr>
                <tr><th>Gan.</th><th>Partido</th><th>Peso</th><th>Anillo</th><th>VS</th><th>Anillo</th><th>Peso</th><th>Partido</th><th>Gan.</th></tr>"""
            
            for i, (roj, ver) in enumerate(peleas):
                if seleccion_print != "VER TODO EL EVENTO" and roj["PARTIDO"] != seleccion_print and ver["PARTIDO"] != seleccion_print:
                    continue
                p_rojo, p_verde = roj.get(r_col, 0), ver.get(r_col, 0)
                # Generación automática de anillos (Ej: 001, 002...)
                anillo_rojo = f"{(i*2)+1:03}"
                anillo_verde = f"{(i*2)+2:03}"
                
                html_tabla += f"""
                <tr>
                    <td><div class="casilla"></div></td>
                    <td class="nombre-partido">{roj["PARTIDO"]}</td>
                    <td>{p_rojo:.3f}</td>
                    <td><b>{anillo_rojo}</b></td>
                    <td><b>Cot. {i+1}</b><br><small>Empate [ ]</small></td>
                    <td><b>{anillo_verde}</b></td>
                    <td>{p_verde:.3f}</td>
                    <td class="nombre-partido">{ver["PARTIDO"]}</td>
                    <td><div class="casilla"></div></td>
                </tr>"""
            html_tabla += "</table>"
            st.markdown(html_tabla, unsafe_allow_html=True)
            
    st.markdown('<p class="footer-hommer">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
