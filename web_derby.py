import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- DISEÑO (AZUL OSCURO Y GRIS - FIJO) ---
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
TOLERANCIA_MAX = 0.080 

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
                        except: d[f"G{i}"] = 2.200
                    partidos.append(d)
    return partidos, g_por_evento

def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [f"{float(v):.3f}" for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# --- INTERFAZ ---
st.title("DERBYSYSTEM PRUEBAS")
partidos_act, n_gallos_act = cargar_datos()

t_reg, t_cot = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO Y ANILLOS"])

with t_reg:
    # 1. FORMULARIO DE REGISTRO NUEVO
    col_n, col_g = st.columns([2, 1])
    g_seleccionados = col_g.selectbox("GALLOS POR PARTIDO:", [2, 3, 4, 5, 6], index=n_gallos_act-2 if n_gallos_act <= 6 else 0)
    
    with st.form("registro_rapido", clear_on_submit=True):
        nombre = st.text_input("NOMBRE DEL NUEVO PARTIDO:").upper().strip()
        w_in = []
        cols = st.columns(g_seleccionados)
        for i in range(g_seleccionados):
            w_in.append(cols[i].number_input(f"P{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f"))
        
        if st.form_submit_button("GUARDAR PARTIDO"):
            if len(nombre) >= 2:
                nuevo = {"PARTIDO": nombre}
                for i, w in enumerate(w_in): nuevo[f"G{i+1}"] = w
                partidos_act.append(nuevo)
                guardar_datos(partidos_act)
                st.rerun()

    # 2. TABLA EDITABLE (EDICIÓN DIRECTA)
    if partidos_act:
        st.markdown("### ✏️ Edición Directa (Haz clic para cambiar)")
        df_editable = pd.DataFrame(partidos_act)
        
        # Esta es la función mágica que permite editar haciendo clic
        edited_df = st.data_editor(
            df_editable,
            num_rows="dynamic", # Permite borrar filas también
            use_container_width=True,
            column_config={
                "PARTIDO": st.column_config.TextColumn("Nombre del Partido"),
                **{f"G{i+1}": st.column_config.NumberColumn(format="%.3f") for i in range(g_seleccionados)}
            }
        )
        
        # Si el usuario cambió algo en la tabla, guardamos
        if not edited_df.equals(df_editable):
            nuevos_datos = edited_df.to_dict('records')
            guardar_datos(nuevos_datos)
            st.toast("Cambios guardados automáticamente")

        if st.button("BORRAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

with t_cot:
    if len(partidos_act) >= 2:
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
                html += f"""<tr><td>{pelea_id}</td><td>□</td><td class='rojo-v'>{rojo['PARTIDO']}<br>{rojo[col_p]:.3f}</td><td>{anillo_cont:03}</td><td class='{c_dif}'>{dif:.3f}</td><td>□</td><td>{(anillo_cont+1):03}</td><td class='verde-v'>{verde['PARTIDO']}<br>{verde[col_p]:.3f}</td><td>□</td></tr>"""
                anillo_cont += 2
                pelea_id += 1
            st.markdown(html + "</table>", unsafe_allow_html=True)
