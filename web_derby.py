import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO FINAL SOLICITADO ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 12px; }
    .banda-roja { border-left: 10px solid #d32f2f !important; font-weight: bold; }
    .banda-verde { border-right: 10px solid #27ae60 !important; font-weight: bold; }
    .alerta-w { color: #e74c3c; font-weight: bold; background-color: #fdeaea; }
    .cuadro-check { width: 20px; height: 20px; border: 2px solid #34495e; margin: auto; }
    .ronda-blue { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
DIF_MAX = 0.080 # Límite de 80 gramos

# --- FUNCIONES DE DATOS ---
def cargar_db():
    lista = []
    g_derby = 2
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    g_derby = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, g_derby + 1):
                        try: d[f"Peso {i}"] = float(p[i])
                        except: d[f"Peso {i}"] = 2.000
                    lista.append(d)
    return lista, g_derby

def guardar_db(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- LÓGICA DE COTEJO (ANTI-CHOQUE) ---
def generar_combates(partidos, n_gallos):
    an_seq = 1
    p_seq = 1
    res = {}
    for r in range(1, n_gallos + 1):
        col_w = f"Peso {r}"
        lista = sorted(partidos, key=lambda x: x.get(col_w, 0))
        pelea_r = []
        while len(lista) >= 2:
            rojo = lista.pop(0)
            # ANTI-CHOQUE: No pelea contra su propio nombre
            v_idx = -1
            for i in range(len(lista)):
                if lista[i]["PARTIDO"] != rojo["PARTIDO"]:
                    v_idx = i
                    break
            if v_idx == -1: v_idx = 0 
            verde = lista.pop(v_idx)
            
            an_r, an_v = f"{an_seq:03}", f"{(an_seq+1):03}"
            dif = abs(rojo[col_w] - verde[col_w])
            pelea_r.append({
                "id": p_seq, "n_r": rojo["PARTIDO"], "w_r": rojo[col_w], "an_r": an_r,
                "n_v": verde["PARTIDO"], "w_v": verde[col_w], "an_v": an_v, "dif": dif
            })
            an_seq += 2
            p_seq += 1
        res[f"RONDA {r}"] = pelea_r
    return res

# --- INTERFAZ ---
st.title("DERBYSYSTEM PRUEBAS")
datos_act, gallos_act = cargar_db()

tab1, tab2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with tab1:
    st.subheader("Ingreso de Datos")
    # FORMULARIO CORREGIDO (Elimina el error de "Missing Submit Button")
    with st.form("registro_partidos", clear_on_submit=True):
        col_n, col_g = st.columns([2, 1])
        nombre_p = col_n.text_input("NOMBRE DEL PARTIDO:").upper()
        g_tipo = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=0)
        
        st.write("Pesos de los gallos:")
        w_inputs = []
        c_pesos = st.columns(g_tipo)
        for i in range(g_tipo):
            w_inputs.append(c_pesos[i].number_input(f"G{i+1}", 1.0, 5.0, 2.0, 0.001, format="%.3f"))
        
        # EL BOTÓN DEBE ESTAR AQUÍ DENTRO
        btn_save = st.form_submit_button("GUARDAR PARTIDO")
        
        if btn_save:
            if nombre_p:
                nuevo = {"PARTIDO": nombre_p}
                for idx, val in enumerate(w_inputs): nuevo[f"Peso {idx+1}"] = val
                datos_act.append(nuevo)
                guardar_db(datos_act)
                st.success(f"PARTIDO {nombre_p} GUARDADO CORRECTAMENTE")
                st.rerun()
            else:
                st.error("Por favor, ingrese el nombre del partido.")

    if datos_act:
        st.write("---")
        if st.button("LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with tab2:
    if len(datos_act) >= 2:
        combates_data = generar_combates(datos_act, gallos_act)
        for ronda_n, peleas in combates_data.items():
            st.markdown(f"<div class='ronda-blue'>{ronda_n}</div>", unsafe_allow_html=True)
            html = """<table class='tabla-final'>
                <tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"""
            for p in peleas:
                c_dif = "alerta-w" if p['dif'] > DIF_MAX else ""
                html += f"""<tr>
                    <td>{p['id']}</td><td><div class='cuadro-check'></div></td>
                    <td class='banda-roja'>{p['n_r']}<br>{p['w_r']:.3f}</td><td>{p['an_r']}</td>
                    <td class='{c_dif}'>{p['dif']:.3f}</td><td><div class='cuadro-check'></div></td>
                    <td>{p['an_v']}</td><td class='banda-verde'>{p['n_v']}<br>{p['w_v']:.3f}</td>
                    <td><div class='cuadro-check'></div></td></tr>"""
            html += "</table>"
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("Favor de registrar al menos 2 partidos para ver el cotejo.")
