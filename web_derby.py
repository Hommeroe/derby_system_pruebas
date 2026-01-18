import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")

# --- ESTILOS (ACTUALIZADOS PARA TABLA DE COTEJO) ---
st.markdown("""
    <style>
    .caja-anillo {
        background-color: #2c3e50; color: white; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #34495e;
        font-size: 0.9em;
    }
    .header-azul { 
        background-color: #2c3e50; color: white; padding: 10px; 
        text-align: center; font-weight: bold; border-radius: 5px;
    }
    /* Estilos para que la tabla quepa en el celular */
    .tabla-final { 
        width: 100%; 
        border-collapse: collapse; 
        background-color: white; 
        font-size: 11px; /* Letra más pequeña para que quepa todo */
    }
    .tabla-final td, .tabla-final th { 
        border: 1px solid #bdc3c7; 
        text-align: center; 
        padding: 4px; /* Menos espacio interno */
    }
    .nombre-partido { font-weight: bold; font-size: 10px; }
    div[data-testid="stNumberInput"] { margin-bottom: 0px; }
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

st.title("🏆 PRUEBAS")
t_reg, t_cot = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO Y ANILLOS"])

with t_reg:
    # --- ESTA SECCIÓN NO SE TOCÓ, SE MANTIENE COMO TE GUSTA ---
    anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
    col_n, col_g = st.columns([2,1])
    g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, 
                            disabled=len(st.session_state.partidos)>0)
    st.session_state.n_gallos = g_sel

    with st.form("f_nuevo", clear_on_submit=True):
        st.subheader(f"Añadir Partido # {len(st.session_state.partidos) + 1}")
        nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
        for i in range(g_sel):
            p_val = st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
            st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True)
            st.write("") 
        
        if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
            if nombre:
                nuevo = {"PARTIDO": nombre}
                for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                st.session_state.partidos.append(nuevo)
                guardar(st.session_state.partidos)
                st.rerun()

    if st.session_state.partidos:
        st.markdown("### ✏️ Tabla de Edición")
        display_data = []
        cont_anillo = 1
        for p in st.session_state.partidos:
            item = {"❌": False, "PARTIDO": p["PARTIDO"]}
            for i in range(1, st.session_state.n_gallos + 1):
                item[f"G{i}"] = p[f"G{i}"]; item[f"Anillo {i}"] = f"{cont_anillo:03}"
                cont_anillo += 1
            display_data.append(item)
        
        df = pd.DataFrame(display_data)
        config = {"❌": st.column_config.CheckboxColumn("B", default=False), "PARTIDO": st.column_config.TextColumn("Partido")}
        for i in range(1, st.session_state.n_gallos + 1):
            config[f"G{i}"] = st.column_config.NumberColumn(f"G{i}", format="%.3f")
            config[f"Anillo {i}"] = st.column_config.TextColumn(f"A{i}", disabled=True)

        res = st.data_editor(df, column_config=config, use_container_width=True, num_rows="fixed", hide_index=True)

        if not res.equals(df):
            nuevos = []
            for _, r in res.iterrows():
                if not r["❌"]:
                    p_upd = {"PARTIDO": str(r["PARTIDO"]).upper()}
                    for i in range(1, st.session_state.n_gallos + 1): p_upd[f"G{i}"] = float(r[f"G{i}"])
                    nuevos.append(p_upd)
            st.session_state.partidos = nuevos; guardar(nuevos); st.rerun()

        if st.button("🚨 LIMPIAR TODO EL EVENTO"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.partidos = []; st.rerun()

with t_cot:
    # --- SECCIÓN DE COTEJO OPTIMIZADA ---
    if len(st.session_state.partidos) >= 2:
        for r in range(1, st.session_state.n_gallos + 1):
            st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
            col_g = f"G{r}"
            # Lógica de emparejamiento por peso
            lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
            
            html = """<table class='tabla-final'>
                        <tr>
                            <th>#</th><th>ROJO</th><th>AN.</th><th>DIF.</th><th>AN.</th><th>VERDE</th>
                        </tr>"""
            pelea_n = 1
            while len(lista) >= 2:
                rojo = lista.pop(0)
                v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                if v_idx is not None:
                    verde = lista.pop(v_idx)
                    d = abs(rojo[col_g] - verde[col_g])
                    c = "style='background:#e74c3c;color:white;'" if d > TOLERANCIA else ""
                    
                    # Calcular anillos automáticos [cite: 2026-01-14]
                    idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                    idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                    an_r = (idx_r * st.session_state.n_gallos) + r
                    an_v = (idx_v * st.session_state.n_gallos) + r
                    
                    html += f"""
                    <tr>
                        <td>{pelea_n}</td>
                        <td style='border-left:4px solid red'><span class='nombre-partido'>{rojo['PARTIDO']}</span><br>{rojo[col_g]:.3f}</td>
                        <td>{an_r:03}</td>
                        <td {c}>{d:.3f}</td>
                        <td>{an_v:03}</td>
                        <td style='border-right:4px solid green'><span class='nombre-partido'>{verde['PARTIDO']}</span><br>{verde[col_g]:.3f}</td>
                    </tr>"""
                    pelea_n += 1
                else: break
            st.markdown(html + "</table><br>", unsafe_allow_html=True)
