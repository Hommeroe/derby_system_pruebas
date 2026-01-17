import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO (TU ESTILO SOLICITADO) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 12px; }
    .rojo-v { border-left: 10px solid #d32f2f !important; font-weight: bold; }
    .verde-v { border-right: 10px solid #27ae60 !important; font-weight: bold; }
    .alerta { color: #e74c3c; font-weight: bold; background-color: #fdeaea; }
    .cuadrado { width: 20px; height: 20px; border: 2px solid #34495e; margin: auto; }
    .header-azul { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA = 0.080 # 80 gramos

# --- BASE DE DATOS ---
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

# --- LÓGICA DE PELEAS ---
def generar_cotejo(partidos, n_gallos):
    anillo_seq = 1
    pelea_seq = 1
    rondas = {}
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
        rondas[f"RONDA {r}"] = peleas_ronda
    return rondas

# --- INTERFAZ ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_act, n_gallos_act = cargar_datos()

t1, t2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with t1:
    st.subheader("Ingreso de Datos")
    # FORMULARIO REPARADO PARA QUE EL BOTÓN FUNCIONE
    with st.form("form_nuevo_partido"):
        c1, c2 = st.columns([2, 1])
        nombre = c1.text_input("NOMBRE DEL PARTIDO:").upper()
        # El selector ahora permite cambiar de 2 a 6 gallos
        g_tipo = c2.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=0)
        
        st.write("Introduzca los pesos:")
        pesos_inputs = []
        c_pesos = st.columns(g_tipo)
        for i in range(g_tipo):
            pesos_inputs.append(c_pesos[i].number_input(f"Gallo {i+1}", 1.0, 5.0, 2.0, 0.001, format="%.3f"))
        
        # EL BOTÓN DEBE ESTAR AQUÍ ADENTRO PARA QUE GUARDE
        enviar = st.form_submit_button("GUARDAR PARTIDO")
        
        if enviar:
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for idx, w in enumerate(pesos_inputs):
                    nuevo[f"Peso {idx+1}"] = w
                partidos_act.append(nuevo)
                guardar_datos(partidos_act)
                st.success(f"PARTIDO {nombre} GUARDADO")
                st.rerun()
            else:
                st.error("Falta el nombre del partido")

    if partidos_act:
        st.write("---")
        if st.button("LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with t2:
    if len(partidos_act) >= 2:
        res = generar_cotejo(partidos_act, n_gallos_act)
        for r_nom, peleas in res.items():
            st.markdown(f"<div class='header-azul'>{r_nom}</div>", unsafe_allow_html=True)
            html = """<table class='tabla-final'>
                <tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"""
            for p in peleas:
                c_dif = "alerta" if p['dif'] > TOLERANCIA else ""
                html += f"""<tr>
                    <td>{p['id']}</td>
                    <td><div class='cuadrado'></div></td>
                    <td class='rojo-v'>{p['n_r']}<br>{p['w_r']:.3f}</td>
                    <td>{p['an_r']}</td>
                    <td class='{c_dif}'>{p['dif']:.3f}</td>
                    <td><div class='cuadrado'></div></td>
                    <td>{p['an_v']}</td>
                    <td class='verde-v'>{p['n_v']}<br>{p['w_v']:.3f}</td>
                    <td><div class='cuadrado'></div></td>
                </tr>"""
            html += "</table>"
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("Registre al menos 2 partidos para ver el cotejo.")
