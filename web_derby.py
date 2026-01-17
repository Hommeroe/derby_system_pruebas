import streamlit as st
import pandas as pd
import os

# --- CONFIGURACION DE LA PAGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- ESTILOS VISUALES (TU DISEÑO SOLICITADO) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 12px; }
    .franja-roja { border-left: 10px solid #d32f2f !important; font-weight: bold; }
    .franja-verde { border-right: 10px solid #27ae60 !important; font-weight: bold; }
    .header-azul { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; border-radius: 4px; }
    .alerta-peso { color: #e74c3c; font-weight: bold; background-color: #fdeaea; }
    .casilla-vacia { width: 20px; height: 20px; border: 2px solid #34495e; margin: auto; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA_GRAMOS = 0.080  # Límite de 80g

# --- GESTION DE DATOS ---
def cargar_archivo():
    partidos = []
    g_por_derby = 2
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                parts = linea.strip().split("|")
                if len(parts) >= 2:
                    g_por_derby = len(parts) - 1
                    item = {"PARTIDO": parts[0]}
                    for i in range(1, g_por_derby + 1):
                        try: item[f"Peso {i}"] = float(parts[i])
                        except: item[f"Peso {i}"] = 2.000
                    partidos.append(item)
    return partidos, g_por_derby

def guardar_archivo(lista_partidos):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista_partidos:
            nombres_pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(nombres_pesos)}\n")

# --- LOGICA DE EMPAREJAMIENTO ---
def crear_cotejo(partidos, n_gallos):
    anillo_idx = 1
    pelea_idx = 1
    rondas_resultado = {}
    
    for r in range(1, n_gallos + 1):
        col_w = f"Peso {r}"
        lista_ordenada = sorted(partidos, key=lambda x: x.get(col_w, 0))
        combates = []
        
        while len(lista_ordenada) >= 2:
            rojo = lista_ordenada.pop(0)
            # REGLA ANTI-CHOQUE: Buscar equipo diferente
            v_idx = -1
            for i in range(len(lista_ordenada)):
                if lista_ordenada[i]["PARTIDO"] != rojo["PARTIDO"]:
                    v_idx = i
                    break
            
            if v_idx == -1: v_idx = 0 
            verde = lista_ordenada.pop(v_idx)
            
            # ASIGNACION AUTOMATICA DE ANILLOS [cite: 2026-01-14]
            an_r, an_v = f"{anillo_idx:03}", f"{(anillo_idx+1):03}"
            diferencia = abs(rojo[col_w] - verde[col_w])
            
            combates.append({
                "id": pelea_idx, "rojo": rojo["PARTIDO"], "w_r": rojo[col_w], "an_r": an_r,
                "verde": verde["PARTIDO"], "w_v": verde[col_w], "an_v": an_v, "dif": diferencia
            })
            anillo_idx += 2
            pelea_idx += 1
        rondas_resultado[f"RONDA {r}"] = combates
    return rondas_resultado

# --- INTERFAZ DE USUARIO ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_actuales, gallos_config = cargar_archivo()

tab_reg, tab_cot = st.tabs(["📝 REGISTRO DE ENTRADAS", "🏆 COTEJO Y ANILLOS"])

with tab_reg:
    st.subheader("Ingreso de Datos")
    
    # FORMULARIO BLINDADO
    with st.form(key="registro_oficial"):
        c1, c2 = st.columns([2, 1])
        nombre_p = c1.text_input("NOMBRE DEL PARTIDO:").upper()
        # Selector de gallos corregido
        g_tipo = c2.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=0)
        
        st.write("Introduzca los pesos de los ejemplares:")
        pesos_temp = []
        cols_w = st.columns(g_tipo)
        for i in range(g_tipo):
            pesos_temp.append(cols_w[i].number_input(f"Gallo {i+1}", 1.0, 5.0, 2.100, 0.001, format="%.3f"))
        
        # EL BOTÓN DEBE ESTAR DENTRO DEL FORMULARIO
        submit_button = st.form_submit_button(label="GUARDAR PARTIDO")
        
        if submit_button:
            if nombre_p:
                nuevo_p = {"PARTIDO": nombre_p}
                for i, peso in enumerate(pesos_temp):
                    nuevo_p[f"Peso {i+1}"] = peso
                partidos_actuales.append(nuevo_p)
                guardar_archivo(partidos_actuales)
                st.success(f"¡PARTIDO {nombre_p} REGISTRADO!")
                st.rerun()
            else:
                st.error("Por favor, ingrese el nombre del partido.")

    if partidos_actuales:
        st.write("---")
        if st.button("LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with tab_cot:
    if len(partidos_actuales) >= 2:
        st.subheader("CONTROL DE PELEAS Y ANILLOS")
        data_cotejo = crear_cotejo(partidos_actuales, gallos_config)
        
        for r_nombre, peleas in data_cotejo.items():
            st.markdown(f"<div class='header-azul'>{r_nombre}</div>", unsafe_allow_html=True)
            
            # Tabla con el diseño solicitado
            html_t = """<table class='tabla-final'>
                <tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"""
            
            for p in peleas:
                clase_dif = "alerta-peso" if p['dif'] > TOLERANCIA_GRAMOS else ""
                html_t += f"""<tr>
                    <td>{p['id']}</td>
                    <td><div class='casilla-vacia'></div></td>
                    <td class='franja-roja'>{p['rojo']}<br>{p['w_r']:.3f}</td>
                    <td>{p['an_r']}</td>
                    <td class='{clase_dif}'>{p['dif']:.3f}</td>
                    <td><div class='casilla-vacia'></div></td>
                    <td>{p['an_v']}</td>
                    <td class='franja-verde'>{p['verde']}<br>{p['w_v']:.3f}</td>
                    <td><div class='casilla-vacia'></div></td>
                </tr>"""
            html_t += "</table>"
            st.markdown(html_t, unsafe_allow_html=True)
    else:
        st.info("Registre al menos 2 partidos para generar el cotejo oficial.")
