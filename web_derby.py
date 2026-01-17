import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO (MANTENIENDO TUS COLORES AZUL Y GRIS) ---
st.markdown("""
    <style>
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; margin-bottom: 25px; }
    .tabla-final th { background-color: #2c3e50; color: white; padding: 10px; border: 1px solid #000; text-align: center; }
    .tabla-final td { border: 1px solid #bdc3c7; text-align: center; padding: 10px; font-size: 14px; }
    .rojo-v { border-left: 8px solid #d32f2f !important; font-weight: bold; background-color: #f9f9f9; }
    .verde-v { border-right: 8px solid #27ae60 !important; font-weight: bold; background-color: #f9f9f9; }
    .header-azul { background-color: #2c3e50; color: white; padding: 8px; text-align: center; font-weight: bold; margin-top: 15px; }
    .dif-alerta { color: #ffffff; font-weight: bold; background-color: #e74c3c; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA_MAX = 0.080 # 80 gramos

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
                        except: d[f"G{i}"] = 2.200
                    partidos.append(d)
    return partidos, g_por_evento

def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            # Forzamos 3 decimales al guardar en el archivo
            pesos = [f"{float(v):.3f}" for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- INTERFAZ ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_act, n_gallos_act = cargar_datos()

t_reg, t_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with t_reg:
    col_n, col_g = st.columns([2, 1])
    # Selector que actualiza automáticamente 2, 3, 4, 5 o 6 gallos
    g_seleccionados = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=n_gallos_act-2 if n_gallos_act <= 6 else 0)
    
    with st.form("registro_preciso", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        st.write("Pesos permitidos (1.800 - 2.600 kg):")
        w_in = []
        cols = st.columns(g_seleccionados)
        for i in range(g_seleccionados):
            # Formato %.3f asegura que en la pantalla siempre veas 2.200
            w_in.append(cols[i].number_input(f"P{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f"))
        
        if st.form_submit_button("GUARDAR PARTIDO"):
            if len(nombre) < 2:
                st.error("Nombre de partido no válido.")
            else:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(w_in): nuevo[f"G{i+1}"] = w
                partidos_act.append(nuevo)
                guardar_datos(partidos_act)
                st.success(f"PARTIDO {nombre} GUARDADO CON ÉXITO")
                st.rerun()

    if partidos_act:
        st.subheader("Partidos Registrados")
        # Mostramos la tabla formateada con 3 decimales
        df_vis = pd.DataFrame(partidos_act)
        for col in df_vis.columns:
            if col != "PARTIDO":
                df_vis[col] = df_vis[col].map('{:.3f}'.format)
        st.table(df_vis) # Usamos table para mantener el formato fijo
        
        if st.button("LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with t_cot:
    if len(partidos_act) >= 2:
        # Generación automática de anillos
        anillo_cont = 1
        pelea_id = 1
        for r in range(1, g_seleccionados + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_p = f"G{r}"
            lista = sorted(partidos_act, key=lambda x: x.get(col_p, 0))
            
            html = "<table class='tabla-final'><tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>E[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"
            
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), 0)
                verde = lista.pop(v_idx)
                dif = abs(rojo[col_p] - verde[col_p])
                c_dif = "dif-alerta" if dif > TOLERANCIA_MAX else ""
                
                html += f"""<tr>
                    <td>{pelea_id}</td><td>□</td>
                    <td class='rojo-v'>{rojo['PARTIDO']}<br>{rojo[col_p]:.3f}</td><td>{anillo_cont:03}</td>
                    <td class='{c_dif}'>{dif:.3f}</td><td>□</td>
                    <td>{(anillo_cont+1):03}</td><td class='verde-v'>{verde['PARTIDO']}<br>{verde[col_p]:.3f}</td>
                    <td>□</td></tr>"""
                anillo_cont += 2
                pelea_id += 1
            st.markdown(html + "</table>", unsafe_allow_html=True)
    else:
        st.info("Registre al menos 2 partidos.")
