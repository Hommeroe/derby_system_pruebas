import streamlit as st
import pandas as pd
import os

# ==========================================
# BLOQUE 1: REGLAS Y LOGICA (BLINDADO)
# ==========================================
TOLERANCIA_MAX = 0.080  # 80 gramos [cite: 2026-01-14]

def cargar_datos():
    partidos = []
    gallos = 2
    if os.path.exists("datos_derby.txt"):
        with open("datos_derby.txt", "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    gallos = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, gallos + 1):
                        try:
                            d[f"Peso {i}"] = float(p[i])
                        except:
                            d[f"Peso {i}"] = 0.0
                    partidos.append(d)
    return partidos, gallos

def generar_cotejo_profesional(partidos, num_gallos):
    anillo_seq = 1
    pelea_seq = 1
    rondas_res = {}
    
    for r_idx in range(1, num_gallos + 1):
        col_p = f"Peso {r_idx}"
        lista = sorted(partidos, key=lambda x: x.get(col_p, 0))
        peleas_data = []
        
        while len(lista) >= 2:
            rojo = lista.pop(0)
            # ANTI-CHOQUE: No pelea contra si mismo
            v_idx = -1
            for i in range(len(lista)):
                if lista[i]["PARTIDO"] != rojo["PARTIDO"]:
                    v_idx = i
                    break
            
            if v_idx == -1: v_idx = 0 
            verde = lista.pop(v_idx)
            
            # ANILLOS REALES (TRAZABILIDAD) [cite: 2026-01-14]
            an_r = f"{anillo_seq:03}"
            an_v = f"{(anillo_seq + 1):03}"
            dif = abs(rojo[col_p] - verde[col_p])
            
            peleas_data.append({
                "id": pelea_seq,
                "n_rojo": rojo["PARTIDO"], "w_rojo": rojo[col_p], "an_rojo": an_r,
                "n_verde": verde["PARTIDO"], "w_verde": verde[col_p], "an_verde": an_v,
                "dif": dif
            })
            anillo_seq += 2
            pelea_seq += 1
        rondas_res[f"RONDA {r_idx}"] = peleas_data
    return rondas_res

# ==========================================
# BLOQUE 2: INTERFAZ VISUAL
# ==========================================
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    .tabla-final th { background: #1a1a1a; color: white; padding: 10px; border: 1px solid #000; font-size: 12px; }
    .tabla-final td { border: 1px solid #000; text-align: center; padding: 12px; font-size: 14px; }
    .borde-rojo { border-left: 12px solid #d32f2f !important; font-weight: bold; }
    .borde-verde { border-right: 12px solid #388e3c !important; font-weight: bold; }
    .fuera-peso { background-color: #ffebee; color: red; font-weight: bold; }
    .check-box { width: 20px; height: 20px; border: 2px solid #000; margin: auto; }
    </style>
""", unsafe_allow_html=True)

st.title("DERBYSYSTEM PRUEBAS")
t1, t2 = st.tabs(["REGISTRO", "COTEJO Y ANILLOS"])

with t2:
    lista_p, n_g = cargar_datos()
    if len(lista_p) >= 2:
        st.subheader("CONTROL DE PELEAS Y ANILLOS")
        data_final = generar_cotejo_profesional(lista_p, n_g)
        
        for r_nombre, peleas in data_final.items():
            st.markdown(f"<div style='background:#333; color:white; padding:10px; text-align:center; font-weight:bold;'>{r_nombre}</div>", unsafe_allow_html=True)
            
            html_table = "<table class='tabla-final'><tr><th>#</th><th>G</th><th>ROJO / ANILLO</th><th>PESO</th><th>DIF.</th><th>E [ ]</th><th>PESO</th><th>VERDE / ANILLO</th><th>G</th></tr>"
            
            for p in peleas:
                estilo_dif = "fuera-peso" if p['dif'] > TOLERANCIA_MAX else ""
                html_table += f"""<tr>
                    <td>{p['id']}</td>
                    <td><div class='check-box'></div></td>
                    <td class='borde-rojo'>{p['n_rojo']}<br><small>ANILLO: {p['an_rojo']}</small></td>
                    <td>{p['w_rojo']:.3f}</td>
                    <td class='{estilo_dif}'>{p['dif']:.3f}</td>
                    <td><div class='check-box'></div></td>
                    <td>{p['w_verde']:.3f}</td>
                    <td class='borde-verde'>{p['n_verde']}<br><small>ANILLO: {p['an_verde']}</small></td>
                    <td><div class='check-box'></div></td>
                </tr>"""
            html_table += "</table>"
            st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.info("Registre al menos 2 partidos para generar anillos.")
