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
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

st.markdown("""
    <style>
    .software-brand { color: #555; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 12px; letter-spacing: 5px; text-align: center; text-transform: uppercase; margin-top: -10px; margin-bottom: 10px; }
    .footer-hommer { text-align: center; color: #666; font-size: 11px; font-family: 'Courier New', Courier, monospace; margin-top: 50px; padding-top: 20px; border-top: 1px solid #333; letter-spacing: 2px; }
    .pelea-card { background-color: #1e1e1e; border: 2px solid #444; border-radius: 10px; padding: 12px; margin-bottom: 20px; color: white; }
    .rojo-text { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .verde-text { color: #00c853; font-weight: bold; font-size: 16px; text-align: right; }
    .fila-principal { display: flex; justify-content: space-between; align-items: flex-start; }
    .lado { width: 42%; }
    .centro-vs { width: 16%; text-align: center; }
    .btn-check { border: 1px solid #777; padding: 2px 5px; border-radius: 3px; font-size: 11px; display: inline-block; margin-top: 5px; background: #222; }
    .info-sub { font-size: 12px; color: #bbb; margin-top: 2px; }
    .dif-normal { text-align: center; font-size: 11px; color: #888; border-top: 1px solid #333; margin-top: 10px; padding-top: 5px; }
    .dif-alerta { text-align: center; font-size: 12px; color: #ff4b4b; font-weight: bold; border-top: 2px solid #ff4b4b; margin-top: 10px; padding-top: 5px; }
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
st.markdown('<p class="software-brand">DerbySystem</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO"])

with tab1:
    st.subheader("Panel de Registro")
    tipo_derby = st.radio("Configuración del Derby:", [2, 3, 4], horizontal=True)
    
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
            label_modo = "🟠 EDITANDO PARTIDO" if st.session_state.edit_index is not None else "🟢 NUEVO REGISTRO"
            st.markdown(f"*{label_modo}*")
            n = st.text_input("NOMBRE DEL PARTIDO:", value=default_name).upper()
            pesos_input = []
            for i in range(1, tipo_derby + 1):
                p = st.number_input(f"Peso Gallo {i}", 1.800, 2.680, default_weights[i-1], 0.001, format="%.3f")
                pesos_input.append(p)
            
            btn_save = st.form_submit_button("💾 GUARDAR CAMBIOS" if st.session_state.edit_index is not None else "💾 GUARDAR EN LISTA")

            if btn_save and n:
                nuevo_p = {"PARTIDO": n}
                for idx, val in enumerate(pesos_input):
                    nuevo_p[f"Peso {idx+1}"] = val
                
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
            cols_peso = [c for c in df.columns if "Peso" in c]
            st.dataframe(df.style.format(subset=cols_peso, formatter="{:.3f}"), use_container_width=True)
            
            # Selector sin etiqueta arriba para que se vea más profesional
            idx_to_edit = st.selectbox("", range(1, len(partidos) + 1), 
                                        format_func=lambda x: f"Seleccionar: {partidos[x-1]['PARTIDO']}",
                                        label_visibility="collapsed")
            
            if st.button("✏️ EDITAR SELECCIONADO", use_container_width=True):
                st.session_state.edit_index = idx_to_edit - 1
                st.rerun()

            st.write("---")
            if st.button("🗑️ LIMPIAR TODO EL EVENTO", use_container_width=True):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.edit_index = None
                st.rerun()
    
    st.markdown('<p class="footer-hommer">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)

with tab2:
    partidos = cargar_datos()
    if len(partidos) >= 2:
        pesos_keys = [c for c in partidos[0].keys() if "Peso" in c]
        num_rondas = len(pesos_keys)
        peleas = generar_cotejo_justo(partidos)
        for r in range(1, num_rondas + 1):
            st.markdown(f"### RONDA {r}")
            col_p = f"Peso {r}"
            for i, (roj, ver) in enumerate(peleas):
                p_rojo = roj.get(col_p, 0)
                p_verde = ver.get(col_p, 0)
                dif = abs(p_rojo - p_verde)
                clase_dif = "dif-alerta" if dif > 0.060 else "dif-normal"
                st.markdown(f'<div class="pelea-card"><div style="text-align: center; font-size: 10px; color: #888; margin-bottom: 8px;">PELEA #{i+1}</div><div class="fila-principal"><div class="lado"><div class="rojo-text">{roj["PARTIDO"]}</div><div class="info-sub">P: {p_rojo:.3f} | A: {(i*2)+1:03}</div><div class="btn-check">G [ ]</div></div><div class="centro-vs"><div style="font-weight: bold; font-size: 14px;">VS</div><div class="btn-check" style="margin-top:10px;">E [ ]</div></div><div class="lado" style="text-align: right;"><div class="verde-text">{ver["PARTIDO"]}</div><div class="info-sub">P: {p_verde:.3f} | A: {(i*2)+2:03}</div><div class="btn-check">G [ ]</div></div></div><div class="{clase_dif}">DIFERENCIA DE PESO: {dif:.3f}</div></div>', unsafe_allow_html=True)
    st.markdown('<p class="footer-hommer">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)

