import streamlit as st
import pandas as pd
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIGURACIÓN DE USUARIOS (Tu lista de clientes) ---
# Aquí puedes agregar o quitar usuarios para controlar quién paga.
USUARIOS = {
    "galpon_azteca": "clave123",
    "derby_nacional": "pavo2026",
    "homero_admin": "admin77"
}

TOLERANCIA = 0.080

# --- ESTILOS CSS PARA MÓVIL ---
st.markdown("""
    <style>
    .header-azul { 
        background-color: #2c3e50; color: white; padding: 8px; 
        text-align: center; font-weight: bold; border-radius: 5px;
        font-size: 12px; margin-bottom: 5px;
    }
    .tabla-final { width: 100%; border-collapse: collapse; background-color: white; table-layout: fixed; }
    .tabla-final td, .tabla-final th { border: 1px solid #bdc3c7; text-align: center; padding: 2px; height: 38px; }
    .nombre-partido { font-weight: bold; font-size: 10px; line-height: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; width: 100%; }
    .peso-texto { font-size: 10px; color: #2c3e50; display: block; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS ---
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
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2c3e50")), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(t); elements.append(Spacer(1, 20))
    doc.build(elements)
    return buffer.getvalue()

# --- CONTROL DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔑 DerbySystem PRO")
    user = st.text_input("Usuario (Gallera)").lower().strip()
    pw = st.text_input("Contraseña", type="password")
    if st.button("Entrar", use_container_width=True):
        if user in USUARIOS and USUARIOS[user] == pw:
            st.session_state.autenticado = True
            st.session_state.usuario_id = user
            st.rerun()
        else:
            st.error("Acceso denegado.")
else:
    # --- SESIÓN ACTIVA ---
    USER_DB = f"datos_{st.session_state.usuario_id}.txt"
    partidos, n_gallos = cargar(USER_DB)
    
    st.sidebar.title(f"👤 {st.session_state.usuario_id.upper()}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    st.title(f"🏆 Derby de: {st.session_state.usuario_id.upper()}")
    t_reg, t_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO"])

    with t_reg:
        # Aquí se mantiene tu lógica de registro cargando/guardando en USER_DB
        st.info(f"Los datos se guardan en: {USER_DB}")
        # (Aquí iría el formulario de registro que ya tienes)

    with t_cot:
        if len(partidos) >= 2:
            pdf_bytes = generar_pdf(partidos, n_gallos, st.session_state.usuario_id)
            st.download_button("📥 DESCARGAR PDF", pdf_bytes, f"cotejo_{st.session_state.usuario_id}.pdf", "application/pdf", use_container_width=True)
            # (Aquí iría la visualización de las tablas de rondas)
