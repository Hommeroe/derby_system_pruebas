import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO (MANTENIENDO AZUL Y GRIS) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; text-align: center; font-size: 14px; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 10px; vertical-align: middle; }
    
    .rojo-v { border-left: 10px solid #d32f2f !important; }
    .verde-v { border-right: 10px solid #27ae60 !important; }
    
    /* Rectángulos verticales solicitados */
    .contenedor-datos { display: flex; flex-direction: column; align-items: center; gap: 5px; }
    .rect-peso { background-color: #f4f6f7; border: 1px solid #d5dbdb; border-radius: 4px; padding: 2px 12px; font-weight: bold; color: #2c3e50; font-size: 16px; min-width: 80px; }
    .rect-anillo { background-color: #2c3e50; color: white; border-radius: 4px; padding: 2px 12px; font-weight: bold; font-size: 14px; min-width: 80px; }
    
    .check-v { font-size: 20px; color: #95a5a6; font-weight: bold; }
    .header-azul { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; }
    .dif-alerta { background-color: #e74c3c; color: white; font-weight: bold; border-radius: 3px; padding: 2px 6px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
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

# --- REGISTRO ---
with t_reg:
    col_n, col_g = st.columns([2, 1])
    hay_datos = len(st.session_state.partidos) > 0
    g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=st.session_state.n_gallos-2 if st.session_state.n_gallos <= 6 else 0, disabled=hay_datos)
    st.session_state.n_gallos = g_sel

    with st.form("nuevo_p", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        cols_w = st.columns(g_sel)
        pesos_f = [cols_w[i].number_input(f"P{i+1}", 1.8, 2.6, 2.200, 0.001, format="%.3f") for i in range(g_sel)]
        if st.form_submit_button("GUARDAR PARTIDO"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(pesos_f): nuevo[f"G{i+1}"] = w
                st.session_state.partidos.append(nuevo)
                guardar_datos(st.session_state.partidos)
                st.rerun()

    if st.session_state.partidos:
        df_ed = pd.DataFrame(st.session_state.partidos)
        config_c = {f"G{i+1}": st.column_config.NumberColumn(format="%.3f") for i in range(st.session_state.n_gallos)}
        res_ed = st.data_editor(df_ed, use_container_width=True, num_rows="dynamic", column_config=config_c)
        if not res_ed.equals(df_ed):
            st.session_state.partidos = res_ed.to_dict('records')
            guardar_datos(st.session_state.partidos)
            st.rerun()
        if st.button("🗑️ LIMPIAR TODO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []
            st.rerun()

# --- COTEJO (RESTAURADO Y MEJORADO) ---
with t_cot:
    if len(st.session_state.partidos) >= 2:
        anillo_idx = 1
        pelea_id = 1
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_p = f"G{r}"
            lista = sorted(st.session_state.partidos, key=lambda x: x.get(col_p, 0))
            
            html = """<table class='tabla-final'>
                <tr>
                    <th width='5%'>#</th>
                    <th width='5%'>G</th>
                    <th width='35%'>LADO ROJO</th>
                    <th width='10%'>DIF.</th>
                    <th width='5%'>E</th>
                    <th width='35%'>LADO VERDE</th>
                    <th width='5%'>G</th>
                </tr>"""
            
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    dif = abs(rojo[col_p] - verde[col_p])
                    c_dif = f"class='dif-alerta'" if dif > TOLERANCIA_MAX else ""
                    
                    html += f"""
                    <tr>
                        <td><b>{pelea_id}</b></td>
                        <td class='check-v'>□</td>
                        <td class='rojo-v'>
                            <div class='contenedor-datos'>
                                <b>{rojo['PARTIDO']}</b>
                                <div class='rect-peso'>{rojo[col_p]:.3f}</div>
                                <div class='rect-anillo'>{anillo_idx:03}</div>
                            </div>
                        </td>
                        <td><span {c_dif}>{dif:.3f}</span></td>
                        <td class='check-v'>□</td>
                        <td class='verde-v'>
                            <div class='contenedor-datos'>
                                <b>{verde['PARTIDO']}</b>
                                <div class='rect-peso'>{verde[col_p]:.3f}</div>
                                <div class='rect-anillo'>{(anillo_idx+1):03}</div>
                            </div>
                        </td>
                        <td class='check-v'>□</td>
                    </tr>"""
                    anillo_idx += 2
                    pelea_id += 1
                else:
                    html += f"<tr><td colspan='7' style='color:grey'>Esperando oponente para {rojo['PARTIDO']}...</td></tr>"
                    break
            st.markdown(html + "</table>", unsafe_allow_html=True)
