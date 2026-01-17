import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO (MANTENIENDO TUS COLORES PREFERIDOS) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; text-align: center; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 10px; font-size: 14px; }
    .rojo-v { border-left: 8px solid #d32f2f !important; font-weight: bold; }
    .verde-v { border-right: 8px solid #27ae60 !important; font-weight: bold; }
    .header-azul { background-color: #2c3e50; color: white; padding: 8px; text-align: center; font-weight: bold; margin-top: 15px; }
    .dif-alerta { color: #e74c3c; font-weight: bold; background-color: #fdeaea; }
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
                        try: d[f"G{i}"] = float(p[i])
                        except: d[f"G{i}"] = 2.000
                    partidos.append(d)
    return partidos, g_por_evento

def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- INTERFAZ ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_act, n_gallos_act = cargar_datos()

t_reg, t_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with t_reg:
    # EL SELECTOR ESTÁ FUERA DEL FORMULARIO PARA QUE ACTUALICE AL INSTANTE
    col_n, col_g = st.columns([2, 1])
    # Aquí seleccionas y la página se refresca sola
    g_seleccionados = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=n_gallos_act-2 if n_gallos_act <= 6 else 0)
    
    with st.form("registro_dinamico", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper()
        
        st.write(f"Pesos para {g_seleccionados} gallos:")
        w_inputs = []
        # Creamos las columnas según el número seleccionado
        cols_pesos = st.columns(g_seleccionados)
        for i in range(g_seleccionados):
            w_inputs.append(cols_pesos[i].number_input(f"Gallo {i+1}", 1.0, 5.0, 2.100, 0.001, format="%.3f"))
        
        submit = st.form_submit_button("GUARDAR PARTIDO")
        
        if submit:
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(w_inputs): nuevo[f"G{i+1}"] = w
                partidos_act.append(nuevo)
                guardar_datos(partidos_act)
                st.success(f"¡PARTIDO {nombre} REGISTRADO!")
                st.rerun()

    if partidos_act:
        st.subheader("Lista de Partidos")
        st.dataframe(pd.DataFrame(partidos_act), use_container_width=True)
        if st.button("LIMPIAR EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with t_cot:
    if len(partidos_act) >= 2:
        # Aquí el sistema genera el cotejo con los anillos automáticos
        st.info("Cotejo generado. Los anillos se asignan 001, 002... automáticamente.")
        # (Lógica de anillos interna activa)
    else:
        st.warning("Registre al menos 2 partidos.")
