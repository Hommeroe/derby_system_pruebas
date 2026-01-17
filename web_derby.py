import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO VISUAL (ENCABEZADOS AZULES) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 12px; }
    .rojo-v { border-left: 10px solid #d32f2f !important; font-weight: bold; }
    .verde-v { border-right: 10px solid #27ae60 !important; font-weight: bold; }
    .alerta-w { color: #e74c3c; font-weight: bold; background-color: #fdeaea; }
    .header-ronda { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA = 0.080 # 80 gramos

# --- FUNCIONES DE DATOS ---
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
                        try: d[f"Gallo {i}"] = float(p[i])
                        except: d[f"Gallo {i}"] = 2.000
                    partidos.append(d)
    return partidos, g_por_evento

def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos_str = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos_str)}\n")

# --- LÓGICA DE COTEJO ---
def generar_cotejo(partidos, n_gallos):
    an_cont, p_cont = 1, 1
    res = {}
    for r in range(1, n_gallos + 1):
        col_p = f"Gallo {r}"
        lista = sorted(partidos, key=lambda x: x.get(col_p, 0))
        peleas_r = []
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), 0)
            verde = lista.pop(v_idx)
            dif = abs(rojo[col_p] - verde[col_p])
            peleas_r.append({
                "id": p_cont, "n_r": rojo["PARTIDO"], "w_r": rojo[col_p], "an_r": f"{an_cont:03}",
                "n_v": verde["PARTIDO"], "w_v": verde[col_p], "an_v": f"{(an_cont+1):03}", "dif": dif
            })
            an_cont += 2
            p_cont += 1
        res[f"RONDA {r}"] = peleas_r
    return res

# --- INTERFAZ ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_act, n_gallos_act = cargar_datos()

tab_reg, tab_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with tab_reg:
    with st.form("registro_p", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        nombre = c1.text_input("NOMBRE DEL PARTIDO:").upper()
        g_tipo = c2.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=n_gallos_act-2 if n_gallos_act <= 6 else 0)
        
        st.write("Pesos:")
        w_in = []
        cols = st.columns(g_tipo)
        for i in range(g_tipo):
            w_in.append(cols[i].number_input(f"G{i+1}", 1.0, 5.0, 2.100, 0.001, format="%.3f"))
        
        if st.form_submit_button("GUARDAR PARTIDO"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(w_in): nuevo[f"Gallo {i+1}"] = w
                partidos_act.append(nuevo)
                guardar_datos(partidos_act)
                st.success(f"PARTIDO {nombre} GUARDADO")
                st.rerun()

    if partidos_act:
        st.subheader("Partidos Registrados")
        st.dataframe(pd.DataFrame(partidos_act), use_container_width=True)
        if st.button("BORRAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with tab_cot:
    if len(partidos_act) >= 2:
        res = generar_cotejo(partidos_act, n_gallos_act)
        for r_nom, peleas in res.items():
            st.markdown(f"<div class='header-ronda'>{r_nom}</div>", unsafe_allow_html=True)
            html = "<table class='tabla-final'><tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"
            for p in peleas:
                c_dif = "alerta-w" if p['dif'] > TOLERANCIA else ""
                html += f"<tr><td>{p['id']}</td><td>□</td><td class='rojo-v'>{p['n_r']}<br>{p['w_r']:.3f}</td><td>{p['an_r']}</td><td class='{c_dif}'>{p['dif']:.3f}</td><td>□</td><td>{p['an_v']}</td><td class='verde-v'>{p['n_v']}<br>{p['w_v']:.3f}</td><td>□</td></tr>"
            st.markdown(html + "</table>", unsafe_allow_html=True)
