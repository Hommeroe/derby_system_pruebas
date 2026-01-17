import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO (AZUL OSCURO Y GRIS - FIJO POR SOLICITUD) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; text-align: center; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 10px; font-size: 14px; }
    .rojo-v { border-left: 8px solid #d32f2f !important; font-weight: bold; background-color: #f9f9f9; }
    .verde-v { border-right: 8px solid #27ae60 !important; font-weight: bold; background-color: #f9f9f9; }
    .header-azul { background-color: #2c3e50; color: white; padding: 8px; text-align: center; font-weight: bold; margin-top: 15px; }
    .dif-alerta { color: #ffffff; font-weight: bold; background-color: #e74c3c; } /* Alerta roja para tolerancia excedida */
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA_MAX = 0.080 # 80 gramos exactos

# --- FUNCIONES DE DATOS ---
def cargar_datos():
    partidos = []
    g_por_partido = 2
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    g_por_partido = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, g_por_partido + 1):
                        try: d[f"G{i}"] = float(p[i])
                        except: d[f"G{i}"] = 2.100
                    partidos.append(d)
    return partidos, g_por_partido

def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- LÓGICA DE COTEJO ---
def generar_cotejo_visual(partidos, n_gallos):
    anillo_cont = 1
    pelea_id = 1
    rondas_resultado = {}
    for r in range(1, n_gallos + 1):
        col_p = f"G{r}"
        lista = sorted(partidos, key=lambda x: x.get(col_p, 0))
        combates = []
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), 0)
            verde = lista.pop(v_idx)
            dif = abs(rojo[col_p] - verde[col_p])
            combates.append({
                "id": pelea_id, "n_r": rojo["PARTIDO"], "w_r": rojo[col_p], "an_r": f"{anillo_cont:03}",
                "n_v": verde["PARTIDO"], "w_v": verde[col_p], "an_v": f"{(anillo_cont+1):03}", "dif": dif
            })
            anillo_cont += 2
            pelea_id += 1
        rondas_resultado[f"RONDA {r}"] = combates
    return rondas_resultado

# --- INTERFAZ ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_act, n_gallos_act = cargar_datos()

t_reg, t_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with t_reg:
    col_n, col_g = st.columns([2, 1])
    g_seleccionados = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=n_gallos_act-2 if n_gallos_act <= 6 else 0)
    
    with st.form("registro_ajustado", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        st.write(f"Rango de peso permitido: 1.800 - 2.600 kg")
        w_in = []
        cols = st.columns(g_seleccionados)
        for i in range(g_seleccionados):
            # AJUSTE: Nuevo rango de peso solicitado
            w_in.append(cols[i].number_input(f"P{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f"))
        
        if st.form_submit_button("GUARDAR PARTIDO"):
            if len(nombre) < 2:
                st.error("Por favor, ingrese un nombre de partido válido.")
            else:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(w_in): nuevo[f"G{i+1}"] = w
                partidos_act.append(nuevo)
                guardar_datos(partidos_act)
                st.success(f"PARTIDO {nombre} GUARDADO")
                st.rerun()

    if partidos_act:
        st.subheader("Partidos Registrados")
        st.dataframe(pd.DataFrame(partidos_act), use_container_width=True)
        if st.button("LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with t_cot:
    if len(partidos_act) >= 2:
        resultado = generar_cotejo_visual(partidos_act, n_gallos_act)
        for r_nombre, peleas in resultado.items():
            st.markdown(f"<div class='header-azul'>{r_nombre}</div>", unsafe_allow_html=True)
            html = """<table class='tabla-final'>
                <tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"""
            for p in peleas:
                # AJUSTE: Alerta si la diferencia es mayor a 80 gramos (0.080)
                c_dif = "dif-alerta" if p['dif'] > TOLERANCIA_MAX else ""
                html += f"""<tr>
                    <td>{p['id']}</td><td>□</td>
                    <td class='rojo-v'>{p['n_r']}<br>{p['w_r']:.3f}</td><td>{p['an_r']}</td>
                    <td class='{c_dif}'>{p['dif']:.3f}</td><td>□</td>
                    <td>{p['an_v']}</td><td class='verde-v'>{p['n_v']}<br>{p['w_v']:.3f}</td>
                    <td>□</td></tr>"""
            st.markdown(html + "</table>", unsafe_allow_html=True)
    else:
        st.info("Registre al menos 2 partidos para generar el cotejo.")
