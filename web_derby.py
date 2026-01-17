import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- ESTILOS CSS (DISEÑO FINAL SOLICITADO) ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #eeeeee; border-radius: 4px 4px 0px 0px; gap: 1px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #d32f2f; color: white; }
    
    /* Diseño de la Tabla Oficial */
    .tabla-oficial { width: 100%; border-collapse: collapse; background-color: white; color: #333; margin-bottom: 30px; }
    .tabla-oficial th { background-color: #2c3e50; color: white; padding: 12px; border: 1px solid #1a252f; font-size: 13px; text-transform: uppercase; }
    .tabla-oficial td { border: 1px solid #bdc3c7; text-align: center; padding: 15px; font-size: 15px; }
    
    /* Franjas Rojas y Verdes */
    .franja-roja { border-left: 10px solid #d32f2f !important; font-weight: bold; background-color: #fff9f9; }
    .franja-verde { border-right: 10px solid #27ae60 !important; font-weight: bold; background-color: #f9fff9; }
    
    /* Alertas y Cuadros */
    .peso-alerta { color: #e74c3c; font-weight: bold; background-color: #fdeaea; }
    .cuadrante { width: 22px; height: 22px; border: 2px solid #34495e; margin: auto; border-radius: 3px; }
    .anillo-label { font-size: 12px; color: #7f8c8d; display: block; }
    .nombre-partido { font-size: 16px; display: block; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA = 0.080 # Límite de 80 gramos

# --- FUNCIONES DE DATOS ---
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

# --- LÓGICA DE COTEJO (ANTI-CHOQUE Y ANILLOS) ---
def generar_cotejo_oficial(partidos, n_gallos):
    anillo_seq = 1
    pelea_seq = 1
    rondas_finales = {}
    
    for r in range(1, n_gallos + 1):
        col_p = f"Peso {r}"
        # Ordenamos por peso para el emparejamiento más justo
        lista = sorted(partidos, key=lambda x: x.get(col_p, 0))
        peleas_ronda = []
        
        while len(lista) >= 2:
            rojo = lista.pop(0)
            
            # REGLA: No pelear contra uno mismo
            v_idx = -1
            for i in range(len(lista)):
                if lista[i]["PARTIDO"] != rojo["PARTIDO"]:
                    v_idx = i
                    break
            
            # Si no hay opción, se toma el siguiente (casos de empate de nombres)
            if v_idx == -1: v_idx = 0 
            verde = lista.pop(v_idx)
            
            # ANILLOS AUTOMÁTICOS
            an_r, an_v = f"{anillo_seq:03}", f"{(anillo_seq+1):03}"
            dif = abs(rojo[col_p] - verde[col_p])
            
            peleas_ronda.append({
                "id": pelea_seq, 
                "n_r": rojo["PARTIDO"], "w_r": rojo[col_p], "an_r": an_r,
                "n_v": verde["PARTIDO"], "w_v": verde[col_p], "an_v": an_v, 
                "dif": dif
            })
            anillo_seq += 2
            pelea_seq += 1
        rondas_finales[f"RONDA {r}"] = peleas_ronda
    return rondas_finales

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>DERBYSYSTEM PRUEBAS</h1>", unsafe_allow_html=True)
partidos_act, n_gallos_act = cargar_datos()

tab1, tab2 = st.tabs(["📝 REGISTRO DE ENTRADAS", "🏆 COTEJO Y ANILLOS"])

with tab1:
    st.subheader("Ingreso de Datos")
    with st.form("registro", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        nombre = col1.text_input("NOMBRE DEL PARTIDO:").upper()
        g_tipo = col2.selectbox("TIPO DE DERBY:", [2, 3, 4], index=n_gallos_act-2)
        
        st.write("Pesos de los ejemplares:")
        pesos = []
        cols = st.columns(g_tipo)
        for i in range(g_tipo):
            pesos.append(cols[i].number_input(f"Gallo {i+1}:", 1.000, 5.000, 2.000, 0.001, format="%.3f"))
            
        if st.form_submit_button("GUARDAR ENTRADA"):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(pesos): nuevo[f"Peso {i+1}"] = w
                partidos_act.append(nuevo)
                guardar_datos(partidos_act)
                st.rerun()

    if partidos_act:
        st.write("---")
        if st.button("LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with tab2:
    if len(partidos_act) >= 2:
        res = generar_cotejo_oficial(partidos_act, n_gallos_act)
        for ronda, peleas in res.items():
            st.markdown(f"<div style='background-color: #2c3e50; color: white; padding: 10px; text-align: center; font-weight: bold; font-size: 18px; border-radius: 4px; margin-bottom: 5px;'>{ronda}</div>", unsafe_allow_html=True)
            
            # Encabezado de la tabla según tu diseño solicitado
            html = """<table class='tabla-oficial'>
                <tr>
                    <th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E [ ]</th><th>AN.</th><th>VERDE</th><th>G</th>
                </tr>"""
            
            for p in peleas:
                estilo_dif = "peso-alerta" if p['dif'] > TOLERANCIA else ""
                html += f"""
                <tr>
                    <td style='width: 40px;'>{p['id']}</td>
                    <td style='width: 50px;'><div class='cuadrante'></div></td>
                    <td class='franja-roja'><span class='nombre-partido'>{p['n_r']}</span><br>{p['w_r']:.3f}</td>
                    <td style='width: 60px;'>{p['an_r']}</td>
                    <td class='{estilo_dif}' style='width: 80px;'>{p['dif']:.3f}</td>
                    <td style='width: 60px;'><div class='cuadrante'></div></td>
                    <td style='width: 60px;'>{p['an_v']}</td>
                    <td class='franja-verde'><span class='nombre-partido'>{p['n_v']}</span><br>{p['w_v']:.3f}</td>
                    <td style='width: 50px;'><div class='cuadrante'></div></td>
                </tr>"""
            html += "</table>"
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("Favor de registrar al menos 2 partidos para generar el cotejo oficial.")

st.markdown("<p style='text-align: center; color: #95a5a6; font-size: 12px;'>Diseño final por HommerDesigns's</p>", unsafe_allow_html=True)
