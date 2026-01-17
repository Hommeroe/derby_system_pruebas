import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO (AZUL OSCURO Y GRIS - NO CAMBIAR) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; text-align: center; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 10px; font-size: 14px; }
    .rojo-v { border-left: 8px solid #d32f2f !important; font-weight: bold; background-color: #f9f9f9; }
    .verde-v { border-right: 8px solid #27ae60 !important; font-weight: bold; background-color: #f9f9f9; }
    .header-azul { background-color: #2c3e50; color: white; padding: 8px; text-align: center; font-weight: bold; margin-top: 15px; }
    .dif-alerta { color: #e74c3c; font-weight: bold; background-color: #fdeaea; }
    .cuadrito { width: 18px; height: 18px; border: 1px solid #333; margin: auto; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA = 0.080 # 80 gramos

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
                        except: d[f"G{i}"] = 2.000
                    partidos.append(d)
    return partidos, g_por_partido

def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- LÓGICA DE COTEJO AUTOMÁTICO ---
def generar_cotejo_visual(partidos, n_gallos):
    anillo_cont = 1
    pelea_id = 1
    rondas_resultado = {}
    
    for r in range(1, n_gallos + 1):
        col_p = f"G{r}"
        # Ordenamos para emparejar pesos similares
        lista = sorted(partidos, key=lambda x: x.get(col_p, 0))
        combates = []
        
        while len(lista) >= 2:
            rojo = lista.pop(0)
            # Evitar pelea contra el mismo partido si es posible
            v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), 0)
            verde = lista.pop(v_idx)
            
            dif = abs(rojo[col_p] - verde[col_p])
            # Generación automática de anillos [cite: 2026-01-14]
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
    # Selector dinámico que actualiza la cantidad de gallos
    col_n, col_g = st.columns([2, 1])
    g_seleccionados = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=n_gallos_act-2 if n_gallos_act <= 6 else 0)
    
    with st.form("registro_form", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper()
        st.write(f"Pesos para {g_seleccionados} gallos:")
        w_in = []
        cols = st.columns(g_seleccionados)
        for i in range(g_seleccionados):
            w_in.append(cols[i].number_input(f"P{i+1}", 1.0, 5.0, 2.100, 0.001, format="%.3f"))
        
        if st.form_submit_button("GUARDAR PARTIDO"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(w_in): nuevo[f"G{i+1}"] = w
                partidos_act.append(nuevo)
                guardar_datos(partidos_act)
                st.success(f"PARTIDO {nombre} GUARDADO")
                st.rerun()

    if partidos_act:
        st.subheader("Partidos en Memoria")
        st.dataframe(pd.DataFrame(partidos_act), use_container_width=True)
        if st.button("LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with t_cot:
    if len(partidos_act) >= 2:
        # AQUÍ SE DIBUJA LA TABLA AUTOMÁTICAMENTE
        resultado = generar_cotejo_visual(partidos_act, n_gallos_act)
        for r_nombre, peleas in resultado.items():
            st.markdown(f"<div class='header-azul'>{r_nombre}</div>", unsafe_allow_html=True)
            html = """<table class='tabla-final'>
                <tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"""
            for p in peleas:
                c_dif = "dif-alerta" if p['dif'] > TOLERANCIA else ""
                html += f"""<tr>
                    <td>{p['id']}</td><td><div class='cuadrito'></div></td>
                    <td class='rojo-v'>{p['n_r']}<br>{p['w_r']:.3f}</td><td>{p['an_r']}</td>
                    <td class='{c_dif}'>{p['dif']:.3f}</td><td><div class='cuadrito'></div></td>
                    <td>{p['an_v']}</td><td class='verde-v'>{p['n_v']}<br>{p['w_v']:.3f}</td>
                    <td><div class='cuadrito'></div></td></tr>"""
            st.markdown(html + "</table>", unsafe_allow_html=True)
    else:
        st.info("Registre al menos 2 partidos para ver la tabla de cotejo.")
