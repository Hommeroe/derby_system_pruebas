import streamlit as st
import pandas as pd
import os

# ==========================================
# BLOQUE 1: LÓGICA DE COTEJO (BLINDADA)
# ==========================================
TOLERANCIA_MAX = 0.080 # 80 gramos [cite: 2026-01-14]

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
                        try: d[f"Peso {i}"] = float(p[i])
                        except: d[f"Peso {i}"] = 0.0
                    partidos.append(d)
    return partidos, gallos

def generar_cotejo_anti_choque(partidos, num_gallos):
    """Separa entradas del mismo partido y asigna anillos reales"""
    anillo_seq = 1
    pelea_seq = 1
    rondas_finales = {}
    
    for r_idx in range(1, num_gallos + 1):
        col_p = f"Peso {r_idx}"
        lista = sorted(partidos, key=lambda x: x.get(col_p, 0))
        peleas_ronda = []
        
        while len(lista) >= 2:
            rojo = lista.pop(0)
            # BUSCAR OPONENTE QUE NO SEA EL MISMO PARTIDO
            v_idx = -1
            for i in range(len(lista)):
                if lista[i]["PARTIDO"] != rojo["PARTIDO"]:
                    v_idx = i
                    break
            
            if v_idx == -1: v_idx = 0 
            verde = lista.pop(v_idx)
            
            # ANILLO AUTOMATICO [cite: 2026-01-14]
            an_r = f"{anillo_seq:03}"
            an_v = f"{(anillo_seq + 1):03}"
            dif = abs(rojo[col_p] - verde[col_p])
            
            peleas_ronda.append({
                "pelea": pelea_seq,
                "n_rojo": rojo["PARTIDO"], "w_rojo": rojo[col_p], "an_r": an_r,
                "n_verde": verde["PARTIDO"], "w_verde": verde[col_p], "an_v": an_v,
                "dif": dif
            })
            anillo_seq += 2
            pelea_seq += 1
        rondas_finales[f"RONDA {r_idx}"] = peleas_ronda
    return rondas_finales

# ==========================================
# BLOQUE 2: INTERFAZ VISUAL (LIMPIA)
# ==========================================
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; }
    .tabla-final th { background: #000; color: #fff; padding: 10px; border: 1px solid #000; }
    .tabla-final td { border: 1px solid #000; text-align: center; padding: 10px; }
    .celda-roja { border-left: 10px solid #d32f2f !important; font-weight: bold; }
    .celda-verde { border-right: 10px solid #388e3c !important; font-weight: bold; }
    .alerta { background-color: #ffebee; color: red; font-weight: bold; }
    .box { width: 18px; height: 18px; border: 2px solid #000; margin: auto; }
    </style>
""", unsafe_allow_html=True)

st.title("DERBYSYSTEM PRUEBAS")
t1, t2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with t2:
    lista_p, n_g = cargar_datos()
    if len(lista_p) >= 2:
        st.subheader("CONTROL DE ANILLOS Y PELEAS")
        # LLAMADA A LA LOGICA
        resultado = generar_cotejo_anti_choque(lista_p, n_g)
        
        for r_nombre, peleas in resultado.items():
            st.markdown(f"<div style='background:#444; color:white; padding:8px; text-align:center;'>{r_nombre}</div>", unsafe_allow_html=True)
            
            html = "<table class='tabla-final'><tr><th>#</th><th>G</th><th>ROJO / ANILLO</th><th>PESO</th><th>DIF.</th><th>E[ ]</th><th>PESO</th><th>VERDE / ANILLO</th><th>G</th></tr>"
            
            for p in peleas:
                clase_dif = "alerta" if p['dif'] > TOLERANCIA_MAX else ""
                html += f"""<tr>
                    <td>{p['pelea']}</td>
                    <td><div class='box'></div></td>
                    <td class='celda-roja'>{p['n_rojo']}<br><small>ANILLO: {p['an_r']}</small></td>
                    <td>{p['w_rojo']:.3f}</td>
                    <td class='{clase_dif}'>{p['dif']:.3f}</td>
                    <td><div class='box'></div></td>
                    <td>{p['w_verde']:.3f}</td>
                    <td class='celda-verde'>{p['n_verde']}<br><small>ANILLO: {p['an_v']}</small></td>
                    <td><div class='box'></div></td>
                </tr>"""
            html += "</table><br>"
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.warning("No hay suficientes partidos registrados.")
