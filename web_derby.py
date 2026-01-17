import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO (FUERZA PESO ARRIBA Y ANILLO ABAJO) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; text-align: center; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 10px; vertical-align: middle; }
    
    /* Contenedor que obliga a poner los datos uno debajo del otro */
    .celda-datos-vertical {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px; /* Espacio entre el nombre, el peso y el anillo */
    }

    .caja-peso { 
        background-color: #f4f6f7; border: 1px solid #d5dbdb; border-radius: 4px; 
        padding: 4px 12px; font-weight: bold; color: #2c3e50; font-size: 16px; min-width: 90px;
    }
    
    .caja-anillo { 
        background-color: #2c3e50; color: white; border-radius: 4px; 
        padding: 4px 12px; font-weight: bold; font-size: 14px; min-width: 90px;
    }
    
    .rojo-v { border-left: 10px solid #d32f2f !important; }
    .verde-v { border-right: 10px solid #27ae60 !important; }
    .header-azul { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; }
    .dif-alerta { background-color: #e74c3c; color: white; font-weight: bold; border-radius: 3px; padding: 2px 6px; }
    </style>
""", unsafe_allow_html=True)

# (Las funciones cargar_datos y guardar_datos se mantienen igual)
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
t_reg, t_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with t_reg:
    # (Código de registro igual para no afectar la edición)
    col_n, col_g = st.columns([2, 1])
    hay_datos = len(st.session_state.partidos) > 0
    g_sel = col_g.selectbox("GALLOS:", [2, 3, 4, 5, 6], index=st.session_state.n_gallos-2 if st.session_state.n_gallos <= 6 else 2, disabled=hay_datos)
    st.session_state.n_gallos = g_sel
    with st.form("nuevo_p", clear_on_submit=True):
        nombre = st.text_input("PARTIDO:").upper().strip()
        cols_w = st.columns(g_sel)
        pesos_f = [cols_w[i].number_input(f"P{i+1}", 1.8, 2.6, 2.200, 0.001, format="%.3f") for i in range(g_sel)]
        if st.form_submit_button("GUARDAR"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(pesos_f): nuevo[f"G{i+1}"] = w
                st.session_state.partidos.append(nuevo)
                guardar_datos(st.session_state.partidos)
                st.rerun()

with t_cot:
    if len(st.session_state.partidos) >= 2:
        anillo_cont = 1
        pelea_id = 1
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_p = f"G{r}"
            lista = sorted(st.session_state.partidos, key=lambda x: x.get(col_p, 0))
            
            html = """<table class='tabla-final'>
                <tr>
                    <th width='5%'>#</th><th width='5%'>G</th>
                    <th width='35%'>LADO ROJO</th><th width='10%'>DIF.</th>
                    <th width='5%'>E</th><th width='35%'>LADO VERDE</th>
                    <th width='5%'>G</th>
                </tr>"""
            
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    dif = abs(rojo[col_p] - verde[col_p])
                    c_dif = f"class='dif-alerta'" if dif > TOLERANCIA_MAX else ""
                    
                    # AQUÍ ESTÁ EL CAMBIO CLAVE: Caja vertical para Rojo y Verde
                    html += f"""
                    <tr>
                        <td><b>{pelea_id}</b></td>
                        <td>□</td>
                        <td class='rojo-v'>
                            <div class='celda-datos-vertical'>
                                <b>{rojo['PARTIDO']}</b>
                                <div class='caja-peso'>{rojo[col_p]:.3f}</div>
                                <div class='caja-anillo'>{anillo_cont:03}</div>
                            </div>
                        </td>
                        <td><span {c_dif}>{dif:.3f}</span></td>
                        <td>□</td>
                        <td class='verde-v'>
                            <div class='celda-datos-vertical'>
                                <b>{verde['PARTIDO']}</b>
                                <div class='caja-peso'>{verde[col_p]:.3f}</div>
                                <div class='caja-anillo'>{(anillo_cont+1):03}</div>
                            </div>
                        </td>
                        <td>□</td>
                    </tr>"""
                    anillo_cont += 2
                    pelea_id += 1
                else:
                    break
            st.markdown(html + "</table>", unsafe_allow_html=True)
