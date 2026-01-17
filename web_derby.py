import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO VISUAL (FRANJA AZUL OSCURA Y TABLAS LIMPIAS) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; font-size: 12px; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 12px; font-size: 14px; }
    .rojo-banda { border-left: 10px solid #d32f2f !important; font-weight: bold; }
    .verde-banda { border-right: 10px solid #27ae60 !important; font-weight: bold; }
    .alerta-peso { color: #e74c3c; font-weight: bold; background-color: #fdeaea; }
    .casilla-e { width: 20px; height: 20px; border: 2px solid #34495e; margin: auto; }
    .header-ronda { background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; margin-top: 20px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

DB_ARCHIVO = "datos_derby.txt"
DIF_MAXIMA = 0.080 # Límite de 80 gramos

# --- FUNCIONES DE ALMACENAMIENTO ---
def leer_base_datos():
    lista = []
    total_g = 2
    if os.path.exists(DB_ARCHIVO):
        with open(DB_ARCHIVO, "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split("|")
                if len(datos) >= 2:
                    total_g = len(datos) - 1
                    item = {"PARTIDO": datos[0]}
                    for i in range(1, total_g + 1):
                        try: item[f"Peso {i}"] = float(datos[i])
                        except: item[f"Peso {i}"] = 2.000
                    lista.append(item)
    return lista, total_g

def escribir_base_datos(lista):
    with open(DB_ARCHIVO, "w", encoding="utf-8") as f:
        for p in lista:
            pesos_str = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos_str)}\n")

# --- LÓGICA DE EMPAREJAMIENTO (ANTI-CHOQUE Y ANILLOS) ---
def organizar_peleas(partidos, n_gallos):
    anillo_cont = 1
    pelea_cont = 1
    resultado_rondas = {}
    
    for r in range(1, n_gallos + 1):
        col_w = f"Peso {r}"
        disponibles = sorted(partidos, key=lambda x: x.get(col_w, 0))
        emparejamientos = []
        
        while len(disponibles) >= 2:
            rojo = disponibles.pop(0)
            # BUSCAR OPONENTE DIFERENTE (ANTI-CHOQUE)
            idx_v = -1
            for i in range(len(disponibles)):
                if disponibles[i]["PARTIDO"] != rojo["PARTIDO"]:
                    idx_v = i
                    break
            
            if idx_v == -1: idx_v = 0 # Si no hay más, pelean contra el que sigue
            verde = disponibles.pop(idx_v)
            
            an_r, an_v = f"{anillo_cont:03}", f"{(anillo_cont+1):03}"
            diferencia = abs(rojo[col_w] - verde[col_w])
            
            emparejamientos.append({
                "pelea": pelea_cont, "p_rojo": rojo["PARTIDO"], "w_rojo": rojo[col_w], "an_r": an_r,
                "p_verde": verde["PARTIDO"], "w_verde": verde[col_w], "an_v": an_v, "dif": diferencia
            })
            anillo_cont += 2
            pelea_cont += 1
        resultado_rondas[f"RONDA {r}"] = emparejamientos
    return resultado_rondas

# --- INTERFAZ ---
st.title("DERBYSYSTEM PRUEBAS")
datos_actuales, gallos_por_derby = leer_base_datos()

t_reg, t_cot = st.tabs(["📝 REGISTRO DE ENTRADAS", "🏆 COTEJO Y ANILLOS"])

with t_reg:
    st.subheader("Ingreso de Datos")
    # FORMULARIO REHECHO PARA EVITAR ERRORES
    with st.form("registro_gallos"):
        c1, c2 = st.columns([2, 1])
        nombre_equipo = c1.text_input("NOMBRE DEL PARTIDO:").upper()
        g_tipo = c2.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=gallos_por_derby-2)
        
        st.write("Introduzca los pesos:")
        pesos_inputs = []
        c_pesos = st.columns(g_tipo)
        for i in range(g_tipo):
            pesos_inputs.append(c_pesos[i].number_input(f"Gallo {i+1}", 1.0, 5.0, 2.0, 0.001, format="%.3f"))
        
        # Botón de envío obligatorio para Streamlit
        guardar = st.form_submit_button("GUARDAR PARTIDO")
        
        if guardar:
            if nombre_equipo:
                nuevo_partido = {"PARTIDO": nombre_equipo}
                for idx, peso in enumerate(pesos_inputs):
                    nuevo_partido[f"Peso {idx+1}"] = peso
                datos_actuales.append(nuevo_partido)
                escribir_base_datos(datos_actuales)
                st.success(f"PARTIDO {nombre_equipo} REGISTRADO CORRECTAMENTE")
                st.rerun()
            else:
                st.error("Por favor escriba el nombre del partido.")

    if datos_actuales:
        st.write("---")
        if st.button("LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_ARCHIVO): os.remove(DB_ARCHIVO)
            st.rerun()

with t_cot:
    if len(datos_actuales) >= 2:
        st.subheader("CONTROL DE PELEAS Y ANILLOS")
        peleo_log = organizar_peleas(datos_actuales, gallos_por_derby)
        
        for nombre_r, peleas in peleo_log.items():
            st.markdown(f"<div class='header-ronda'>{nombre_r}</div>", unsafe_allow_html=True)
            
            tabla_html = """<table class='tabla-final'>
                <tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"""
            
            for p in peleas:
                estilo_p = "alerta-peso" if p['dif'] > DIF_MAXIMA else ""
                tabla_html += f"""<tr>
                    <td>{p['pelea']}</td>
                    <td><div class='casilla-e'></div></td>
                    <td class='rojo-banda'>{p['p_rojo']}<br>{p['w_rojo']:.3f}</td>
                    <td>{p['an_r']}</td>
                    <td class='{estilo_p}'>{p['dif']:.3f}</td>
                    <td><div class='casilla-e'></div></td>
                    <td>{p['an_v']}</td>
                    <td class='verde-banda'>{p['p_verde']}<br>{p['w_verde']:.3f}</td>
                    <td><div class='casilla-e'></div></td>
                </tr>"""
            tabla_html += "</table>"
            st.markdown(tabla_html, unsafe_allow_html=True)
    else:
        st.info("Favor de registrar al menos 2 partidos para ver el cotejo oficial.")
