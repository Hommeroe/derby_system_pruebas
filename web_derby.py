 import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .caja-anillo {
        background-color: #2c3e50; color: white; padding: 5px;
        border-radius: 5px; font-weight: bold; text-align: center;
        margin-top: 30px; border: 1px solid #34495e;
    }
    .header-ronda { 
        background-color: #2c3e50; color: white; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px;
    }
    .tabla-cotejo { width: 100%; border-collapse: collapse; background-color: white; }
    .tabla-cotejo td, .tabla-cotejo th { 
        border: 1px solid #bdc3c7; text-align: center; padding: 10px; 
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "datos_derby.txt"
TOLERANCIA = 0.080

def cargar():
    partidos = []
    n_gallos = 2
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    n_gallos = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, n_gallos + 1):
                        d[f"G{i}"] = float(p[i])
                    partidos.append(d)
    return partidos, n_gallos

def guardar(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [f"{v:.3f}" for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

if 'partidos' not in st.session_state:
    st.session_state.partidos, st.session_state.n_gallos = cargar()

st.title("🏆 DERBYSYSTEM PRUEBAS")
t_reg, t_cot = st.tabs(["📝 REGISTRO", "📊 COTEJO"])

with t_reg:
    # --- FORMULARIO DE REGISTRO ---
    anillos_totales = len(st.session_state.partidos) * st.session_state.n_gallos
    
    col_a, col_b = st.columns([2,1])
    n_sel = col_b.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, 
                            disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = n_sel

    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Registrar Partido # {len(st.session_state.partidos) + 1}")
        nom = st.text_input("NOMBRE DEL PARTIDO:").upper()
        pesos_temp = []
        
        for i in range(n_sel):
            c1, c2 = st.columns([4, 1])
            with c1:
                v = st.number_input(f"Peso Gallo {i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"in_{i}")
                pesos_temp.append(v)
            with c2:
                # El anillo se genera automático aquí [cite: 2026-01-14]
                st.markdown(f"<div class='caja-anillo'>{(anillos_totales + i + 1):03}</div>", unsafe_allow_html=True)
        
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nom:
                nuevo = {"PARTIDO": nom}
                for i, w in enumerate(pesos_temp): nuevo[f"G{i+1}"] = w
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()

    # --- TABLA DE EDICIÓN SEGURA (SIN AGREGAR FILAS) ---
    if st.session_state.partidos:
        st.divider()
        st.subheader("✏️ Tabla de Edición")
        
        datos_ed = []
        anillo_cnt = 1
        for p in st.session_state.partidos:
            d = {"PARTIDO": p["PARTIDO"]}
            for i in range(1, st.session_state.n_gallos + 1):
                d[f"G{i} Peso"] = p[f"G{i}"]
                # Mostramos el anillo en la celda de edición [cite: 2026-01-14]
                d[f"Anillo {i}"] = f"{anillo_cnt:03}"
                anillo_cnt += 1
            datos_ed.append(d)
        
        df = pd.DataFrame(datos_ed)
        
        # Bloqueamos columnas de anillos y el número de filas [cite: 2026-01-17]
        config = {"PARTIDO": st.column_config.TextColumn("Partido", width="medium")}
        for i in range(1, st.session_state.n_gallos + 1):
            config[f"Anillo {i}"] = st.column_config.TextColumn(f"💍 A{i}", disabled=True)
            config[f"G{i} Peso"] = st.column_config.NumberColumn(f"⚖️ G{i}", format="%.3f")

        res = st.data_editor(df, column_config=config, use_container_width=True, 
                             num_rows="fixed", hide_index=True)

        if not res.equals(df):
            actualizados = []
            for _, row in res.iterrows():
                p_upd = {"PARTIDO": row["PARTIDO"]}
                for i in range(1, st.session_state.n_gallos + 1):
                    p_upd[f"G{i}"] = float(row[f"G{i} Peso"])
                actualizados.append(p_upd)
            st.session_state.partidos = actualizados
            guardar(actualizados)
            st.rerun()

        if st.button("🗑️ LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []
            st.rerun()

# --- PESTAÑA COTEJO ---
with t_cot:
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-ronda'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            
            html = "<table class='tabla-cotejo'><tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>[ ]</th><th>AN.</th><th>VERDE</th><th>G</th></tr>"
            pelea = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    d = abs(rojo[col_g] - verde[col_g])
                    c = "style='background:#e74c3c;color:white;'" if d > TOLERANCIA else ""
                    
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r = (idx_r * st.session_state.n_gallos) + r
                    an_v = (idx_v * st.session_state.n_gallos) + r
                    
                    html += f"<tr><td>{pelea}</td><td>□</td><td style='border-left:5px solid red'>{rojo['PARTIDO']}<br>{rojo[col_g]:.3f}</td><td>{an_r:03}</td><td {c}>{d:.3f}</td><td>□</td><td>{an_v:03}</td><td style='border-right:5px solid green'>{verde['PARTIDO']}<br>{verde[col_g]:.3f}</td><td>□</td></tr>"
                    pelea += 1
                else: break
            st.markdown(html + "</table><br>", unsafe_allow_html=True)
