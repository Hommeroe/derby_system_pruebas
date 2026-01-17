import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO (RECTÁNGULOS DOBLES LADO A LADO) ---
st.markdown("""
    <style>
    .tabla-registro { width: 100%; border-collapse: collapse; margin-top: 10px; background-color: white; }
    .tabla-registro th { background-color: #2c3e50; color: white; border: 1px solid #000; padding: 10px; text-align: center; }
    .tabla-registro td { border: 1px solid #bdc3c7; padding: 10px; text-align: center; vertical-align: middle; }
    
    .contenedor-gallo {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 4px;
    }

    /* Rectángulo de Peso */
    .caja-peso {
        background-color: #f4f6f7;
        border: 1px solid #d5dbdb;
        border-radius: 4px;
        padding: 3px 8px;
        min-width: 70px;
    }

    /* Rectángulo de Anillo */
    .caja-anillo {
        background-color: #2c3e50;
        border: 1px solid #2c3e50;
        border-radius: 4px;
        padding: 3px 8px;
        min-width: 60px;
    }

    .etiqueta-mini {
        font-size: 9px;
        font-weight: bold;
        display: block;
        margin-bottom: -2px;
    }
    
    .peso-texto { color: #2c3e50; font-weight: bold; font-size: 14px; }
    .anillo-texto { color: #ffffff; font-weight: bold; font-size: 14px; }
    
    .num-partido { color: #d32f2f; font-weight: bold; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"

def cargar_datos():
    partidos = []
    g_por_evento = 2
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    g_por_evento = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, g_por_evento + 1):
                        try: d[f"G{i}"] = float(p[i])
                        except: d[f"G{i}"] = 2.200
                    partidos.append(d)
    return partidos, g_por_evento

def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [f"{float(v):.3f}" for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar_datos()

st.title("DERBYSYSTEM PRUEBAS")
t_reg, t_cot = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO Y ANILLOS"])

with t_reg:
    with st.container(border=True):
        col_n, col_g = st.columns([2, 1])
        hay_datos = len(st.session_state.partidos) > 0
        g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], 
                                index=st.session_state.n_gallos-2 if st.session_state.n_gallos <= 6 else 0,
                                disabled=hay_datos)
        st.session_state.n_gallos = g_sel

        with st.form("nuevo_p", clear_on_submit=True):
            nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
            cols = st.columns(g_sel)
            w_in = [cols[i].number_input(f"P{i+1}", 1.8, 2.6, 2.200, 0.001, format="%.3f") for i in range(g_sel)]
            if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
                if nombre:
                    nuevo = {"PARTIDO": nombre}
                    for i, w in enumerate(w_in): nuevo[f"G{i+1}"] = w
                    st.session_state.partidos.append(nuevo)
                    guardar_datos(st.session_state.partidos)
                    st.rerun()

    if st.session_state.partidos:
        st.markdown(f"### 📋 Listado de Partidos ({len(st.session_state.partidos)})")
        
        html_reg = f"""<table class='tabla-registro'>
            <tr>
                <th>#</th>
                <th>PARTIDO</th>"""
        for i in range(st.session_state.n_gallos):
            html_reg += f"<th>GALLO {i+1}</th>"
        html_reg += "</tr>"
        
        anillo_global = 1
        for idx, p in enumerate(st.session_state.partidos):
            html_reg += f"<tr>"
            html_reg += f"<td><span class='num-partido'>{idx+1}</span></td>"
            html_reg += f"<td><b>{p['PARTIDO']}</b></td>"
            
            for i in range(1, st.session_state.n_gallos + 1):
                peso_val = f"{p[f'G{i}']:.3f}"
                html_reg += f"""
                <td>
                    <div class='contenedor-gallo'>
                        <div class='caja-peso'>
                            <span class='etiqueta-mini' style='color:#7f8c8d'>PESO</span>
                            <span class='peso-texto'>{peso_val}</span>
                        </div>
                        <div class='caja-anillo'>
                            <span class='etiqueta-mini' style='color:#bdc3c7'>ANILLO</span>
                            <span class='anillo-texto'>{anillo_global:03}</span>
                        </div>
                    </div>
                </td>"""
                anillo_global += 1
            html_reg += f"</tr>"
            
        st.markdown(html_reg + "</table>", unsafe_allow_html=True)

        if st.button("🗑️ LIMPIAR TODO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []
            st.rerun()

# (La pestaña de cotejo permanece igual para no cambiar el diseño funcional)
