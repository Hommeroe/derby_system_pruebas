import streamlit as st
import pandas as pd
import random
import os

# Configuración de la página (Diseño Ancho)
st.set_page_config(page_title="SISTEMA DERBY V28 - ONLINE", layout="wide")

# Archivo de datos (El mismo que ya usas)
ARCHIVO_DATOS = "datos_derby.txt"
TOLERANCIA = 0.080
PESO_MIN = 1.800
PESO_MAX = 2.680

# Estilo personalizado para que se vea como tu programa
st.markdown("""
    <style>
    .main { background-color: #1e272e; color: white; }
    .stButton>button { background-color: #27ae60; color: white; font-weight: bold; }
    .stTable { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def cargar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        return []
    lista = []
    with open(ARCHIVO_DATOS, "r") as f:
        for linea in f:
            d = linea.strip().split("|")
            lista.append(d)
    return lista

st.title("SISTEMA DERBY V28 - REGISTRO OFICIAL")

# --- BARRA LATERAL PARA REGISTRO ---
with st.sidebar:
    st.header("REGISTRO DE PARTIDO")
    nom_partido = st.text_input("NOMBRE DEL PARTIDO:").upper()
    
    col1, col2 = st.columns(2)
    with col1:
        peso1 = st.number_input("P1", min_value=0.0, max_value=3.0, format="%.3f", step=0.001)
        peso2 = st.number_input("P2", min_value=0.0, max_value=3.0, format="%.3f", step=0.001)
    with col2:
        peso3 = st.number_input("P3", min_value=0.0, max_value=3.0, format="%.3f", step=0.001)
        peso4 = st.number_input("P4", min_value=0.0, max_value=3.0, format="%.3f", step=0.001)

    if st.button("REGISTRAR PARTIDO"):
        pesos_ingresados = [p for p in [peso1, peso2, peso3, peso4] if p > 0]
        # Validar rango 1.800 - 2.680
        error_rango = [p for p in pesos_ingresados if p < PESO_MIN or p > PESO_MAX]
        
        if not nom_partido:
            st.error("Escribe el nombre del partido")
        elif error_rango:
            st.error(f"Pesos fuera de rango: {error_rango}")
        else:
            # Calcular anillos (total de gallos registrados)
            datos_previos = cargar_datos()
            total_gallos = sum(len(fila)-1 for fila in datos_previos)
            
            nueva_linea = [nom_partido]
            for p in pesos_ingresados:
                total_gallos += 1
                anillo = str(total_gallos).zfill(3)
                nueva_linea.append(f"{p}:{anillo}")
            
            with open(ARCHIVO_DATOS, "a") as f:
                f.write("|".join(nueva_linea) + "\n")
            
            st.success("¡Registrado!")
            st.rerun()

# --- TABLA PRINCIPAL ---
datos = cargar_datos()
if datos:
    st.subheader("PARTIDOS REGISTRADOS")
    tabla_visual = []
    for idx, d in enumerate(datos, 1):
        fila = {"#": idx, "PARTIDO": d[0]}
        # Extraer solo el peso (sin el anillo) para la tabla
        for i in range(1, 5):
            if i < len(d):
                fila[f"G{i}"] = d[i].split(":")[0]
            else:
                fila[f"G{i}"] = "-"
        tabla_visual.append(fila)
    
    # Usamos un formato más sencillo para evitar el error de DLL
    st.write("### Lista de Partidos")
    for p in tabla_visual:
        st.write(f"*{p['#']}. {p['PARTIDO']}* | P1: {p['G1']} | P2: {p['G2']} | P3: {p['G3']} | P4: {p['G4']}")

    if st.button("🗑️ BORRAR TODO EL DERBY"):
        if os.path.exists(ARCHIVO_DATOS):
            os.remove(ARCHIVO_DATOS)
            st.rerun()
# --- BOTÓN DE REPORTE Y COTEJO ---
st.divider()
if st.button("🟢 GENERAR COTEJO E IMPRIMIR REPORTE", type="primary"):
    if not datos:
        st.error("No hay partidos registrados para cotejar.")
    else:
        # 1. Organizar por Rondas
        rondas = {1: [], 2: [], 3: [], 4: []}
        for d in datos:
            partido = d[0]
            for i in range(1, len(d)):
                # Separar peso y anillo
                peso, anillo = d[i].split(":")
                rondas[i].append({"p": partido, "w": float(peso), "a": anillo})

        # 2. Diseño del Reporte (HTML)
        html = """
        <html><head><style>
            body { font-family: 'Courier New', Courier, monospace; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
            th, td { border: 1px solid black; padding: 6px; text-align: center; font-size: 14px; }
            .rojo { background-color: #ffcccc; font-weight: bold; }
            .verde { background-color: #ccffcc; font-weight: bold; }
            .header { background-color: #333; color: white; }
            .box { width: 20px; height: 20px; border: 2px solid black; margin: auto; }
        </style></head><body>
        <h1 style='text-align:center;'>COTEJO OFICIAL - SISTEMA DERBY V28</h1>
        """

        cotejo_n = 1
        for num_r, gallos in rondas.items():
            if not gallos: continue
            random.shuffle(gallos)
            html += f"<table><tr class='header'><td colspan='9'>RONDA # {num_r}</td></tr>"
            html += "<tr><td>#</td><td>GAN</td><td class='rojo'>PARTIDO ROJO</td><td>ANILLO</td><td>VS</td><td>ANILLO</td><td class='verde'>PARTIDO VERDE</td><td>GAN</td><td>DIF</td></tr>"
            
            while len(gallos) >= 2:
                g1 = gallos.pop(0)
                match_idx = -1
                for i in range(len(gallos)):
                    # Regla: No pelea contra sí mismo y entra en tolerancia de 0.080kg
                    if gallos[i]["p"] != g1["p"] and abs(gallos[i]["w"] - g1["w"]) <= 0.080:
                        match_idx = i
                        break
                
                if match_idx != -1:
                    g2 = gallos.pop(match_idx)
                    dif = abs(g1["w"] - g2["w"])
                    html += f"<tr><td>{cotejo_n}</td><td><div class='box'></div></td>"
                    html += f"<td class='rojo'>{g1['p']}<br>{g1['w']:.3f}</td><td>{g1['a']}</td>"
                    html += f"<td>VS</td><td>{g2['a']}</td>"
                    html += f"<td class='verde'>{g2['p']}<br>{g2['w']:.3f}</td><td><div class='box'></div></td>"
                    html += f"<td>{dif:.3f}</td></tr>"
                    cotejo_n += 1
            html += "</table>"
        
        html += "<p style='text-align:right;'>Impreso desde Sistema Derby Online</p></body></html>"

        # 3. Mostrar botón para descargar y ver
        st.download_button("📥 DESCARGAR HOJA DE COTEJO", html, file_name="cotejos_derby.html", mime="text/html")
        st.components.v1.html(html, height=800, scrolling=True)


        # 2. Crear HTML del Reporte
        html = """
        <html><head><style>
            body { font-family: Arial; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; font-size: 12px; }
            th, td { border: 1px solid black; padding: 4px; text-align: center; }
            .header { background: #1a252f; color: white; font-weight: bold; }
            .box { width: 15px; height: 15px; border: 1px solid black; margin: auto; }
        </style></head><body>
        <h2 style='text-align:center;'>REPORTE DE COTEJOS OFICIAL</h2>
        """

        cotejo_n = 1
        for r_num, lista in rondas.items():
            random.shuffle(lista)
            if not lista: continue
            html += f"<table><tr class='header'><td colspan='9'>RONDA {r_num}</td></tr>"
            html += "<tr><td>#</td><td>GAN</td><td>ROJO</td><td>ANILLO</td><td>EMP</td><td>ANILLO</td><td>VERDE</td><td>GAN</td><td>DIF</td></tr>"
            
            while len(lista) >= 2:
                g1 = lista.pop(0)
                match_idx = -1
                for i in range(len(lista)):
                    if lista[i]["p"] != g1["p"] and abs(lista[i]["w"] - g1["w"]) <= TOLERANCIA:
                        match_idx = i
                        break
                
                if match_idx != -1:
                    g2 = lista.pop(match_idx)
                    html += f"<tr><td>{cotejo_n}</td><td><div class='box'></div></td>"
                    html += f"<td>{g1['p']}<br>{g1['w']:.3f}</td><td>{g1['a']}</td>"
                    html += f"<td><div class='box'></div></td><td>{g2['a']}</td>"
                    html += f"<td>{g2['p']}<br>{g2['w']:.3f}</td><td><div class='box'></div></td>"
                    html += f"<td>{abs(g1['w']-g2['w']):.3f}</td></tr>"
                    cotejo_n += 1
            html += "</table>"
        
        html += "</body></html>"

        # 3. Mostrar botón de descarga y vista previa
        st.download_button("📥 DESCARGAR HOJA PARA IMPRIMIR", html, file_name="cotejos_online.html", mime="text/html")
        st.components.v1.html(html, height=600, scrolling=True)
