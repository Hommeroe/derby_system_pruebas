import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; text-align: center; font-size: 12px; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 8px; vertical-align: middle; }
    
    .rojo-v { border-left: 10px solid #d32f2f !important; background-color: #fdfdfd; }
    .verde-v { border-right: 10px solid #27ae60 !important; background-color: #fdfdfd; }
    
    /* Rectángulos de datos */
    .caja-dato { 
        display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 5px;
    }
    .rect-peso { 
        background-color: #f0f3f4; border: 1px solid #d5dbdb; border-radius: 4px;
        padding: 2px 10px; font-weight: bold; color: #2c3e50; font-size: 15px; width: 70px;
    }
    .rect-anillo { 
        background-color: #2c3e50; color: white; border-radius: 4px;
        padding: 2px 10px; font-weight: bold; font-size: 13px; width: 70px;
    }
    
    .check-box { font-size: 18px; color: #7f8c8d; cursor: pointer; }
    .header-azul { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; }
    .dif-alerta { background-color: #e74c3c; color: white; font-weight: bold; border-radius: 4px; padding: 2px 5px; }
    </style>
""", unsafe_allow_html=True)

# (Funciones cargar/guardar se mantienen igual)
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

# --- PESTAÑA COTEJO MEJORADA ---
with t_cot:
    if len(st.session_state.partidos) >= 2:
        anillo_dinamico = 1
        pelea_id = 1
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_p = f"G{r}"
            lista = sorted(st.session_state.partidos, key=lambda x: x.get(col_p, 0))
            
            # Tabla con columnas específicas para G y E
            html = """<table class='tabla-final'>
                <tr>
                    <th>#</th><th>GAN.</th><th>LADO ROJO (PARTIDO / PESO / ANILLO)</th>
                    <th>DIF.</th><th>EMP.</th>
                    <th>LADO VERDE (PARTIDO / PESO / ANILLO)</th><th>GAN.</th>
                </tr>"""
            
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    dif = abs(rojo[col_p] - verde[col_p])
                    c_dif = "class='dif-alerta'" if dif > TOLERANCIA_MAX else ""
                    
                    html += f"""
                    <tr>
                        <td style='font-weight:bold;'>{pelea_id}</td>
                        <td class='check-box'>□</td>
                        <td class='rojo-v'>
                            <div class='caja-dato'>
                                <b>{rojo['PARTIDO']}</b>
                                <div class='rect-peso'>{rojo[col_p]:.3f}</div>
                                <div class='rect-anillo'>{anillo_dinamico:03}</div>
                            </div>
                        </td>
                        <td><span {c_dif}>{dif:.3f}</span></td>
                        <td class='check-box'>□</td>
                        <td class='verde-v'>
                            <div class='caja-dato'>
                                <b>{verde['PARTIDO']}</b>
                                <div class='rect-peso'>{verde[col_p]:.3f}</div>
                                <div class='rect-anillo'>{(anillo_dinamico+1):03}</div>
                            </div>
                        </td>
                        <td class='check-box'>□</td>
                    </tr>"""
                    anillo_dinamico += 2
                    pelea_id += 1
                else:
                    html += f"<tr><td colspan='7' style='color:grey italic'>Pendiente de Oponente: {rojo['PARTIDO']}</td></tr>"
                    break
            st.markdown(html + "</table>", unsafe_allow_html=True)
    else:
        st.info("Ingrese partidos en la pestaña de Registro.")
