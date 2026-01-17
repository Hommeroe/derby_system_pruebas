import streamlit as st
import pandas as pd
import os

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- ESTILOS CSS (PARA QUE SE VEA PROFESIONAL) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; }
    .tabla-final th { background: #000; color: #fff; padding: 10px; border: 1px solid #000; }
    .tabla-final td { border: 1px solid #000; text-align: center; padding: 10px; }
    .rojo { border-left: 12px solid #d32f2f !important; font-weight: bold; }
    .verde { border-right: 12px solid #388e3c !important; font-weight: bold; }
    .alerta { background-color: #ffebee; color: red; font-weight: bold; }
    .box { width: 18px; height: 18px; border: 2px solid #000; margin: auto; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA = 0.080 # 80 gramos [cite: 2026-01-14]

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
                        except: d[f"Peso {i}"] = 0.0
                    partidos.append(d)
    return partidos, gallos

def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- LOGICA DE COTEJO (ANTI-CHOQUE Y ANILLOS) ---
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
            # ANTI-CHOQUE: No pelean contra si mismos
            v_idx = -1
            for i in range(len(lista)):
                if lista[i]["PARTIDO"] != rojo["PARTIDO"]:
                    v_idx = i
                    break
            if v_idx == -1: v_idx = 0 
            verde = lista.pop(v_idx)
            
            # ANILLOS AUTOMATICOS [cite: 2026-01-14]
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

# --- INTERFAZ DE USUARIO ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_act, n_gallos_act = cargar_datos()

tab1, tab2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with tab1:
    st.subheader("REGISTRO DE PARTIDOS")
    with st.form("form_reg", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("NOMBRE DEL PARTIDO:").upper()
        g_tipo = col2.selectbox("GALLOS POR PARTIDO:", [2, 3, 4], index=n_gallos_act-2)
        
        pesos = []
        cols_pesos = st.columns(g_tipo)
        for i in range(g_tipo):
            pesos.append(cols_pesos[i].number_input(f"PESO G{i+1}:", 1.000, 4.000, 2.000, 0.001, format="%.3f"))
        
        if st.form_submit_button("GUARDAR PARTIDO"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(pesos): nuevo[f"Peso {i+1}"] = w
                partidos_act.append(nuevo)
                guardar_datos(partidos_act)
                st.success(f"PARTIDO {nombre} GUARDADO")
                st.rerun()

    if partidos_act:
        st.write("### LISTA ACTUAL")
        st.table(pd.DataFrame(partidos_act))
        if st.button("BORRAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with tab2:
    if len(partidos_act) >= 2:
        res = generar_cotejo(partidos_act, n_gallos_act)
        for ronda, peleas in res.items():
            st.markdown(f"<div style='background:#333; color:white; padding:10px; text-align:center;'>{ronda}</div>", unsafe_allow_html=True)
            html = "<table class='tabla-final'><tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"
            for p in peleas:
                c_dif = "alerta" if p['dif'] > TOLERANCIA else ""
                html += f"""<tr>
                    <td>{p['id']}</td><td><div class='box'></div></td>
                    <td class='rojo'>{p['n_r']}<br>{p['w_r']:.3f}</td><td>{p['an_r']}</td>
                    <td class='{c_dif}'>{p['dif']:.3f}</td><td><div class='box'></div></td>
                    <td>{p['an_v']}</td><td class='verde'>{p['n_v']}<br>{p['w_v']:.3f}</td>
                    <td><div class='box'></div></td></tr>"""
            html += "</table><br>"
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("REGISTRE AL MENOS 2 PARTIDOS PARA VER EL COTEJO.")
