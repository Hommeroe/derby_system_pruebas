import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO MEJORADO: CAJAS COMPACTAS VERTICALES ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; text-align: center; font-size: 14px; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 5px; vertical-align: middle; }
    
    /* Contenedor vertical para apilar cajas */
    .contenedor-vertical {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3px;
        padding: 5px 0;
    }

    /* Caja de Peso más pequeña */
    .caja-peso-mini { 
        background-color: #f4f6f7; 
        border: 1px solid #d5dbdb; 
        border-radius: 3px; 
        padding: 1px 8px; 
        font-weight: bold; 
        color: #2c3e50; 
        font-size: 14px; 
        width: 70px;
    }
    
    /* Caja de Anillo automática */
    .caja-anillo-mini { 
        background-color: #2c3e50; 
        color: white; 
        border-radius: 3px; 
        padding: 1px 8px; 
        font-weight: bold; 
        font-size: 12px; 
        width: 70px;
    }
    
    .rojo-v { border-left: 10px solid #d32f2f !important; }
    .verde-v { border-right: 10px solid #27ae60 !important; }
    .header-azul { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; }
    .dif-alerta { background-color: #e74c3c; color: white; font-weight: bold; border-radius: 3px; padding: 2px 5px; }
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
t_reg, t_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

# (Sección de Registro omitida por brevedad, se mantiene igual)

with t_cot:
    if len(st.session_state.partidos) >= 2:
        anillo_auto = 1
        pelea_num = 1
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
                    
                    html += f"""
                    <tr>
                        <td><b>{pelea_num}</b></td>
                        <td>□</td>
                        <td class='rojo-v'>
                            <div class='contenedor-vertical'>
                                <b>{rojo['PARTIDO']}</b>
                                <div class='caja-peso-mini'>{rojo[col_p]:.3f}</div>
                                <div class='caja-anillo-mini'>{anillo_auto:03}</div>
                            </div>
                        </td>
                        <td><span {c_dif}>{dif:.3f}</span></td>
                        <td>□</td>
                        <td class='verde-v'>
                            <div class='contenedor-vertical'>
                                <b>{verde['PARTIDO']}</b>
                                <div class='caja-peso-mini'>{verde[col_p]:.3f}</div>
                                <div class='caja-anillo-mini'>{(anillo_auto+1):03}</div>
                            </div>
                        </td>
                        <td>□</td>
                    </tr>"""
                    anillo_auto += 2
                    pelea_num += 1
                else:
                    break
            st.markdown(html + "</table>", unsafe_allow_html=True)
