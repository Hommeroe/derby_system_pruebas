import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO COMPACTO (PESO + ANILLO EN LÍNEA) ---
st.markdown("""
    <style>
    /* Contenedor que junta el peso y el anillo */
    .celda-registro {
        display: flex;
        align-items: center;
        gap: 8px;
        background-color: #f8f9f9;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #eaecee;
        margin-bottom: 10px;
    }
    
    .caja-anillo-v2 {
        background-color: #2c3e50;
        color: #f1c40f;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        min-width: 70px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }

    .etiqueta-v2 {
        font-size: 11px;
        color: #7f8c8d;
        font-weight: bold;
        margin-bottom: 2px;
    }

    .header-azul { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA_MAX = 0.080 

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
    # Contador para anillos automáticos
    anillo_actual = len(st.session_state.partidos) * st.session_state.n_gallos
    
    col_n, col_g = st.columns([2, 1])
    g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], 
                            index=st.session_state.n_gallos-2 if st.session_state.n_gallos <= 6 else 0,
                            disabled=len(st.session_state.partidos) > 0)
    st.session_state.n_gallos = g_sel

    with st.form("nuevo_p", clear_on_submit=True):
        st.markdown(f"### 🐓 Registrando Partido # {len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        
        w_in = []
        # Crear filas compactas para cada gallo
        for i in range(g_sel):
            num_anillo = anillo_actual + (i + 1)
            # Layout de dos columnas: una para el peso y otra para el anillo
            c1, c2 = st.columns([3, 1])
            with c1:
                p_val = st.number_input(f"Peso Gallo {i+1}", 1.8, 2.6, 2.200, 0.001, format="%.3f", key=f"p_{i}")
                w_in.append(p_val)
            with c2:
                st.markdown(f"""
                    <div style='margin-top: 28px;'>
                        <div class='caja-anillo-v2'>
                            <div style='font-size:9px; color:#bdc3c7;'>ANILLO</div>
                            {num_anillo:03}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for j, peso in enumerate(w_in): nuevo[f"G{j+1}"] = peso
                st.session_state.partidos.append(nuevo)
                guardar_datos(st.session_state.partidos)
                st.rerun()

    if st.session_state.partidos:
        st.markdown(f"### 📋 Listado de Partidos ({len(st.session_state.partidos)})")
        df_ed = pd.DataFrame(st.session_state.partidos)
        df_ed.index += 1 # Numeración de filas para saber cuántos hay
        st.data_editor(df_ed, use_container_width=True)

        if st.button("🗑️ LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []
            st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        anillo_cont = 1
        pelea_id = 1
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_p = f"G{r}"
            lista = sorted(st.session_state.partidos, key=lambda x: x.get(col_p, 0))
            html = "<table class='tabla-final'><tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"
            
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    dif = abs(rojo[col_p] - verde[col_p])
                    c_dif = "style='background-color:#e74c3c;color:white;font-weight:bold;'" if dif > TOLERANCIA_MAX else ""
                    html += f"<tr><td>{pelea_id}</td><td>□</td><td style='border-left:8px solid #d32f2f'>{rojo['PARTIDO']}<br>{rojo[col_p]:.3f}</td><td>{anillo_cont:03}</td><td {c_dif}>{dif:.3f}</td><td>□</td><td>{(anillo_cont+1):03}</td><td style='border-right:8px solid #27ae60'>{verde['PARTIDO']}<br>{verde[col_p]:.3f}</td><td>□</td></tr>"
                    anillo_cont += 2
                    pelea_id += 1
                else: break
            st.markdown(html + "</table>", unsafe_allow_html=True)
