import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO DE TABLAS (AZUL Y GRIS) ---
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

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    partidos = []
    g_por_partido = 5 # Valor por defecto
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

# --- LÓGICA DE EMPAREJAMIENTO AUTOMÁTICO ---
def generar_tabla_cotejo(partidos, n_gallos):
    anillo_cont = 1
    pelea_id = 1
    rondas_resultado = {}
    
    for r in range(1, n_gallos + 1):
        col_peso = f"G{r}"
        # Ordenar por peso para que las peleas sean parejas
        lista_ordenada = sorted(partidos, key=lambda x: x.get(col_peso, 0))
        peleas_de_ronda = []
        
        while len(lista_ordenada) >= 2:
            rojo = lista_ordenada.pop(0)
            # Buscar oponente que no sea del mismo partido
            v_idx = next((i for i, x in enumerate(lista_ordenada) if x["PARTIDO"] != rojo["PARTIDO"]), 0)
            verde = lista_ordenada.pop(v_idx)
            
            dif = abs(rojo[col_peso] - verde[col_peso])
            # Generación automática de anillos [cite: 2026-01-14]
            peleas_de_ronda.append({
                "id": pelea_id, "n_r": rojo["PARTIDO"], "w_r": rojo[col_peso], "an_r": f"{anillo_cont:03}",
                "n_v": verde["PARTIDO"], "w_v": verde[col_peso], "an_v": f"{(anillo_cont+1):03}", "dif": dif
            })
            anillo_cont += 2
            pelea_id += 1
        rondas_resultado[f"RONDA {r}"] = peleas_de_ronda
    return rondas_resultado

# --- INTERFAZ ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_actuales, gallos_config = cargar_datos()

t_reg, t_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with t_reg:
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        nombre = col1.text_input("NOMBRE DEL PARTIDO:").upper()
        g_num = col2.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=3) # Index 3 es para 5 gallos
        
        st.write("Pesos:")
        w_inputs = []
        cols_w = st.columns(g_num)
        for i in range(g_num):
            w_inputs.append(cols_w[i].number_input(f"P{i+1}", 1.0, 5.0, 2.100, 0.001, format="%.3f"))
        
        if st.form_submit_button("GUARDAR PARTIDO"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(w_inputs): nuevo[f"G{i+1}"] = w
                partidos_actuales.append(nuevo)
                guardar_datos(partidos_actuales)
                st.success(f"PARTIDO {nombre} GUARDADO")
                st.rerun()

    if partidos_actuales:
        st.subheader("Partidos Registrados")
        st.dataframe(pd.DataFrame(partidos_actuales), use_container_width=True)
        if st.button("BORRAR TODO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with t_cot:
    if len(partidos_actuales) >= 2:
        # AQUÍ SE GENERA LA TABLA AUTOMÁTICAMENTE
        resultado = generar_tabla_cotejo(partidos_actuales, gallos_config)
        
        for r_nombre, peleas in resultado.items():
            st.markdown(f"<div class='header-azul'>{r_nombre}</div>", unsafe_allow_html=True)
            
            html_tabla = """<table class='tabla-final'>
                <tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"""
            
            for p in peleas:
                clase_dif = "dif-alerta" if p['dif'] > TOLERANCIA else ""
                html_tabla += f"""
                <tr>
                    <td>{p['id']}</td>
                    <td><div class='cuadrito'></div></td>
                    <td class='rojo-v'>{p['n_r']}<br>{p['w_r']:.3f}</td>
                    <td>{p['an_r']}</td>
                    <td class='{clase_dif}'>{p['dif']:.3f}</td>
                    <td><div class='cuadrito'></div></td>
                    <td>{p['an_v']}</td>
                    <td class='verde-v'>{p['n_v']}<br>{p['w_v']:.3f}</td>
                    <td><div class='cuadrito'></div></td>
                </tr>"""
            st.markdown(html_tabla + "</table>", unsafe_allow_html=True)
    else:
        st.info("Registre al menos 2 partidos para ver el cotejo.")
