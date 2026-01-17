import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; text-align: center; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 10px; font-size: 14px; }
    .rojo-v { border-left: 8px solid #d32f2f !important; font-weight: bold; background-color: #f9f9f9; }
    .verde-v { border-right: 8px solid #27ae60 !important; font-weight: bold; background-color: #f9f9f9; }
    
    /* Estilo para los rectángulos de la hoja de cotejo */
    .caja-peso { background-color: #ecf0f1; border: 1px solid #bdc3c7; padding: 4px 8px; border-radius: 4px; font-weight: bold; display: inline-block; min-width: 60px; }
    .caja-anillo { background-color: #2c3e50; color: white; border: 1px solid #000; padding: 4px 8px; border-radius: 4px; font-weight: bold; display: inline-block; margin-left: 5px; }
    
    .header-azul { background-color: #2c3e50; color: white; padding: 8px; text-align: center; font-weight: bold; margin-top: 15px; }
    .dif-alerta { color: #ffffff; font-weight: bold; background-color: #e74c3c; }
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
    col_n, col_g = st.columns([2, 1])
    hay_datos = len(st.session_state.partidos) > 0
    g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=st.session_state.n_gallos-2 if st.session_state.n_gallos <= 6 else 0, disabled=hay_datos)
    st.session_state.n_gallos = g_sel

    # Calcular el siguiente número de anillo basado en registros actuales
    proximo_anillo = (len(st.session_state.partidos) * g_sel) + 1

    with st.form("nuevo_p", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        
        # Grid para Pesos y Anillos
        for i in range(g_sel):
            c_p, c_a = st.columns([2, 1])
            w_val = c_p.number_input(f"Peso Gallo {i+1}", 1.8, 2.6, 2.200, 0.001, format="%.3f", key=f"w_{i}")
            c_a.markdown(f"<br><div style='padding:8px; background:#2c3e50; color:white; border-radius:5px; text-align:center;'>Anillo: {proximo_anillo + i:03}</div>", unsafe_allow_html=True)
        
        if st.form_submit_button("GUARDAR PARTIDO"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"w_{i}"]
                st.session_state.partidos.append(nuevo)
                guardar_datos(st.session_state.partidos)
                st.rerun()

    if st.session_state.partidos:
        st.markdown("### ✏️ Tabla de Edición")
        df_ed = pd.DataFrame(st.session_state.partidos)
        config_columnas = {f"G{i+1}": st.column_config.NumberColumn(f"G{i+1}", format="%.3f") for i in range(st.session_state.n_gallos)}
        res_ed = st.data_editor(df_ed, use_container_width=True, num_rows="dynamic", column_config=config_columnas)
        if not res_ed.equals(df_ed):
            st.session_state.partidos = res_ed.to_dict('records')
            guardar_datos(st.session_state.partidos)
            st.rerun()
        if st.button("🗑️ LIMPIAR TODO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []
            st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        # Re-calculamos anillos dinámicamente según el orden de peso del cotejo
        # Para que el anillo 001 siempre sea de la Pelea 1
        anillo_dinamico = 1
        pelea_id = 1
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_p = f"G{r}"
            lista = sorted(st.session_state.partidos, key=lambda x: x.get(col_p, 0))
            html = "<table class='tabla-final'><tr><th>#</th><th>G</th><th>ROJO</th><th>DIF.</th><th>VERDE</th><th>G</th></tr>"
            
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    dif = abs(rojo[col_p] - verde[col_p])
                    c_dif = "dif-alerta" if dif > TOLERANCIA_MAX else ""
                    
                    html += f"""
                    <tr>
                        <td>{pelea_id}</td>
                        <td>□</td>
                        <td class='rojo-v'>
                            <b>{rojo['PARTIDO']}</b><br>
                            <div class='caja-peso'>{rojo[col_p]:.3f}</div><div class='caja-anillo'>{anillo_dinamico:03}</div>
                        </td>
                        <td class='{c_dif}'>{dif:.3f}</td>
                        <td class='verde-v'>
                            <b>{verde['PARTIDO']}</b><br>
                            <div class='caja-peso'>{verde[col_p]:.3f}</div><div class='caja-anillo'>{(anillo_dinamico+1):03}</div>
                        </td>
                        <td>□</td>
                    </tr>"""
                    anillo_dinamico += 2
                    pelea_id += 1
                else:
                    html += f"<tr><td colspan='6' style='color:grey'>Esperando oponente para {rojo['PARTIDO']}...</td></tr>"
                    break
            st.markdown(html + "</table>", unsafe_allow_html=True)
