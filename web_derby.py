import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Importamos reportlab (asegúrate de tenerlo en requirements.txt)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- 1. CONFIGURACIÓN DE USUARIOS (Tus Clientes) ---
USUARIOS = {
    "galpon_azteca": "clave123",
    "derby_nacional": "pavo2026",
    "homero_admin": "admin77"
}

# --- 2. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="DerbySystem PRO", layout="wide")
TOLERANCIA = 0.080

# Estilos CSS para nombres largos y diseño móvil
st.markdown("""
    <style>
    .caja-anillo {
        background-color: #2c3e50; color: white; padding: 2px;
        border-radius: 0px 0px 5px 5px; font-weight: bold; 
        text-align: center; margin-top: -15px; border: 1px solid #34495e;
        font-size: 0.8em;
    }
    .header-azul { 
        background-color: #2c3e50; color: white; padding: 8px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 12px; margin-bottom: 5px;
    }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; table-layout: fixed; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 2px; height: 38px; }
    .nombre-partido { font-weight: bold; font-size: 10px; line-height: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; width: 100%; }
    .peso-texto { font-size: 10px; color: #2c3e50; display: block; }
    .cuadro { font-size: 11px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DEL SISTEMA ---
def cargar(db_file):
    partidos = []
    n_gallos = 2
    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    n_gallos = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, n_gallos + 1): d[f"G{i}"] = float(p[i])
                    partidos.append(d)
    return partidos, n_gallos

def guardar(lista, db_file):
    with open(db_file, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [f"{v:.3f}" for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

def generar_pdf(partidos, n_gallos, usuario):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"<b>COTEJO OFICIAL: {usuario.upper()}</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    for r in range(1, n_gallos + 1):
        elements.append(Paragraph(f"<b>RONDA {r}</b>", styles['Heading2']))
        col_g = f"G{r}"
        lista = sorted([dict(p) for p in partidos], key=lambda x: x[col_g])
        data = [["#", "G", "ROJO", "AN.", "E", "DIF.", "AN.", "VERDE", "G"]]
        pelea_n = 1
        while len(lista) >= 2:
            rojo = lista.pop(0)
            v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
            if v_idx is not None:
                verde = lista.pop(v_idx)
                d = abs(rojo[col_g] - verde[col_g])
                idx_r = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                idx_v = next(i for i, p in enumerate(partidos) if p["PARTIDO"]==verde["PARTIDO"])
                an_r, an_v = (idx_r * n_gallos) + r, (idx_v * n_gallos) + r
                data.append([pelea_n, " ", f"{rojo['PARTIDO']}\n({rojo[col_g]:.3f})", f"{an_r:03}", " ", f"{d:.3f}", f"{an_v:03}", f"{verde['PARTIDO']}\n({verde[col_g]:.3f})", " "])
                pelea_n += 1
            else: break
        t = Table(data, colWidths=[20, 25, 140, 35, 25, 45, 35, 140, 25])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2c3e50")), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(t); elements.append(Spacer(1, 20))
    doc.build(elements)
    return buffer.getvalue()

# --- 4. CONTROL DE ACCESO (LOGIN) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🏆 DerbySystem PRO")
    user_input = st.text_input("Usuario (ID de Gallera)").lower().strip()
    pw_input = st.text_input("Contraseña", type="password")
    if st.button("Entrar al Sistema", use_container_width=True):
        if user_input in USUARIOS and USUARIOS[user_input] == pw_input:
            st.session_state.autenticado = True
            st.session_state.usuario_id = user_input
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos.")
else:
    # --- 5. PROGRAMA PRINCIPAL (Solo si está autenticado) ---
    USER_DB = f"datos_{st.session_state.usuario_id}.txt"
    
    # Cargar datos específicos del usuario
    if 'partidos' not in st.session_state:
        st.session_state.partidos, st.session_state.n_gallos = cargar(USER_DB)

    st.sidebar.title(f"👤 {st.session_state.usuario_id.upper()}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        if 'partidos' in st.session_state: del st.session_state.partidos
        st.rerun()

    st.title(f"📊 Panel: {st.session_state.usuario_id.upper()}")
    t_reg, t_cot = st.tabs(["📝 REGISTRO Y EDICIÓN", "🏆 COTEJO Y ANILLOS"])

    with t_reg:
        anillos_actuales = len(st.session_state.partidos) * st.session_state.n_gallos
        col_n, col_g = st.columns([2,1])
        g_sel = col_g.selectbox("GALLOS POR PARTIDO:", [2,3,4,5,6], index=st.session_state.n_gallos-2, 
                                disabled=len(st.session_state.partidos)>0)
        st.session_state.n_gallos = g_sel

        with st.form("f_nuevo", clear_on_submit=True):
            st.subheader(f"Añadir Partido # {len(st.session_state.partidos) + 1}")
            nombre = st.text_input("NOMBRE DEL PARTIDO:").upper().strip()
            for i in range(g_sel):
                st.number_input(f"Peso G{i+1}", 1.800, 2.600, 2.200, 0.001, format="%.3f", key=f"p_{i}")
                st.markdown(f"<div class='caja-anillo'>ANILLO: {(anillos_actuales + i + 1):03}</div>", unsafe_allow_html=True)
            
            if st.form_submit_button("💾 GUARDAR PARTIDO", use_container_width=True):
                if nombre:
                    nuevo = {"PARTIDO": nombre}
                    for i in range(g_sel): nuevo[f"G{i+1}"] = st.session_state[f"p_{i}"]
                    st.session_state.partidos.append(nuevo)
                    guardar(st.session_state.partidos, USER_DB)
                    st.rerun()

        if st.session_state.partidos:
            st.markdown("### ✏️ Tabla de Edición")
            df = pd.DataFrame(st.session_state.partidos)
            res = st.data_editor(df, use_container_width=True, hide_index=True)
            if not res.equals(df):
                st.session_state.partidos = res.to_dict('records')
                guardar(st.session_state.partidos, USER_DB)
                st.rerun()

            if st.button("🚨 LIMPIAR TODO EL EVENTO"):
                if os.path.exists(USER_DB): os.remove(USER_DB)
                st.session_state.partidos = []
                st.rerun()

    with t_cot:
        if len(st.session_state.partidos) >= 2:
            pdf_bytes = generar_pdf(st.session_state.partidos, st.session_state.n_gallos, st.session_state.usuario_id)
            st.download_button("📥 DESCARGAR PDF", pdf_bytes, f"cotejo_{st.session_state.usuario_id}.pdf", "application/pdf", use_container_width=True)
            
            st.divider()
            # Lógica visual de las rondas (HTML)
            for r in range(1, st.session_state.n_gallos + 1):
                st.markdown(f"<div class='header-azul'>RONDA {r}</div>", unsafe_allow_html=True)
                col_g = f"G{r}"
                lista = sorted([dict(p) for p in st.session_state.partidos], key=lambda x: x[col_g])
                html = "<table class='tabla-final'><thead><tr><th>#</th><th>G</th><th>ROJO</th><th>AN.</th><th>E</th><th>DIF.</th><th>AN.</th><th>VERDE</th><th>G</th></tr></thead><tbody>"
                pelea_n = 1
                while len(lista) >= 2:
                    rojo = lista.pop(0)
                    v_idx = next((i for i, x in enumerate(lista) if x["PARTIDO"] != rojo["PARTIDO"]), None)
                    if v_idx is not None:
                        verde = lista.pop(v_idx)
                        d = abs(rojo[col_g] - verde[col_g])
                        idx_r = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==rojo["PARTIDO"])
                        idx_v = next(i for i, p in enumerate(st.session_state.partidos) if p["PARTIDO"]==verde["PARTIDO"])
                        an_r, an_v = (idx_r * st.session_state.n_gallos) + r, (idx_v * st.session_state.n_gallos) + r
                        html += f"<tr><td>{pelea_n}</td><td>□</td><td>{rojo['PARTIDO']}<br>{rojo[col_g]:.3f}</td><td>{an_r:03}</td><td>□</td><td>{d:.3f}</td><td>{an_v:03}</td><td>{verde['PARTIDO']}<br>{verde[col_g]:.3f}</td><td>□</td></tr>"
                        pelea_n += 1
                    else: break
                st.markdown(html + "</tbody></table><br>", unsafe_allow_html=True)
