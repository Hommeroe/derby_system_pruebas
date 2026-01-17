import streamlit as st
import pandas as pd
import os

# --- CONFIGURACION ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- ESTILOS VISUALES (TU DISENO SOLICITADO) ---
st.markdown("""
    <style>
    .tabla-oficial { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-oficial th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; font-size: 12px; }
    .tabla-oficial td { border: 1px solid #bdc3c7; text-align: center; padding: 12px; font-size: 14px; }
    .franja-roja { border-left: 10px solid #d32f2f !important; font-weight: bold; }
    .franja-verde { border-right: 10px solid #27ae60 !important; font-weight: bold; }
    .peso-alerta { color: #e74c3c; font-weight: bold; background-color: #fdeaea; }
    .cuadro-e { width: 20px; height: 20px; border: 2px solid #34495e; margin: auto; }
    .ronda-header { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA = 0.080 # 80 gramos

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    partidos = []
    gallos = 2
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    gallos = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, gallos + 1):
                        try: d[f"Peso {i}"] = float(p[i])
                        except: d[f"Peso {i}"] = 2.000
                    partidos.append(d)
    return partidos, gallos

def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- LOGICA DE COTEJO ---
def generar_cotejo_oficial(partidos, n_gallos):
    anillo_seq = 1
    pelea_seq = 1
    rondas_res = {}
    for r in range(1, n_gallos + 1):
        col_p = f"Peso {r}"
        lista = sorted(partidos, key=lambda x: x.get(col_p, 0))
        peleas_ronda = []
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = -1
            for i in range(len(lista)):
                if lista[i]["PARTIDO"] != rojo["PARTIDO"]:
                    v_idx = i
                    break
            if v_idx == -1: v_idx = 0 
            verde = lista.pop(v_idx)
            an_r, an_v = f"{anillo_seq:03}", f"{(anillo_seq+1):03}"
            dif = abs(rojo[col_p] - verde[col_p])
            peleas_ronda.append({
                "id": pelea_seq, "n_r": rojo["PARTIDO"], "w_r": rojo[col_p], "an_r": an_r,
                "n_v": verde["PARTIDO"], "w_v": verde[col_p], "an_v": an_v, "dif": dif
            })
            anillo_seq += 2
            pelea_seq += 1
        rondas_res[f"RONDA {r}"] = peleas_ronda
    return rondas_res

# --- INTERFAZ DE USUARIO ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_act, n_gallos_act = cargar_datos()

tab1, tab2 = st.tabs(["REGISTRO", "COTEJO Y ANILLOS"])

with tab1:
    st.subheader("Ingreso de Datos")
    # Formulario corregido para evitar el error "Missing Submit Button"
    with st.form("form_registro"):
        col1, col2 = st.columns([2, 1])
        nombre_partido = col1.text_input("NOMBRE DEL PARTIDO:").upper()
        num_gallos = col2.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=n_gallos_act-2)
        
        st.write("Pesos:")
        cols_pesos = st.columns(num_gallos)
        nuevos_pesos = []
        for i in range(num_gallos):
            nuevos_pesos.append(cols_pesos[i].number_input(f"G{i+1}", 1.0, 5.0, 2.0, 0.001, format="%.3f"))
        
        btn_guardar = st.form_submit_button("GUARDAR PARTIDO")
        
        if btn_guardar:
            if nombre_partido:
                nuevo_p = {"PARTIDO": nombre_partido}
                for idx, w in enumerate(nuevos_pesos): nuevo_p[f"Peso {idx+1}"] = w
                partidos_act.append(nuevo_p)
                guardar_datos(partidos_act)
                st.success(f"PARTIDO {nombre_partido} REGISTRADO")
                st.rerun()

    if partidos_act:
        if st.button("LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with tab2:
    if len(partidos_act) >= 2:
        res = generar_cotejo_oficial(partidos_act, n_gallos_act)
        for ronda_nom, peleas in res.items():
            st.markdown(f"<div class='ronda-header'>{ronda_nom}</div>", unsafe_allow_html=True)
            html = """<table class='tabla-oficial'>
                <tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"""
            for p in peleas:
                est_dif = "peso-alerta" if p['dif'] > TOLERANCIA else ""
                html += f"""<tr>
                    <td>{p['id']}</td>
                    <td><div class='cuadro-e'></div></td>
                    <td class='franja-roja'>{p['n_r']}<br>{p['w_r']:.3f}</td>
                    <td>{p['an_r']}</td>
                    <td class='{est_dif}'>{p['dif']:.3f}</td>
                    <td><div class='cuadro-e'></div></td>
                    <td>{p['an_v']}</td>
                    <td class='franja-verde'>{p['n_v']}<br>{p['w_v']:.3f}</td>
                    <td><div class='cuadro-e'></div></td>
                </tr>"""
            html += "</table>"
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("No hay suficientes datos. Registre al menos 2 partidos.")
