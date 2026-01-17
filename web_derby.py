import streamlit as st
import pandas as pd
import os

# -------------------------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------------------------
st.set_page_config(
    page_title="DerbySystem PRO",
    layout="wide"
)

# -------------------------------------------------
# ESTILOS
# -------------------------------------------------
st.markdown("""
<style>
.tabla-final {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
    margin-bottom: 25px;
}
.tabla-final th {
    background-color: #2c3e50;
    color: white;
    padding: 10px;
    border: 1px solid #000;
}
.tabla-final td {
    border: 1px solid #bdc3c7;
    text-align: center;
    padding: 12px;
}
.rojo-v {
    border-left: 10px solid #d32f2f !important;
    font-weight: bold;
}
.verde-v {
    border-right: 10px solid #27ae60 !important;
    font-weight: bold;
}
.alerta {
    color: #e74c3c;
    font-weight: bold;
    background-color: #fdeaea;
}
.header-azul {
    background-color: #2c3e50;
    color: white;
    padding: 10px;
    text-align: center;
    font-weight: bold;
    margin-top: 20px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# CONSTANTES
# -------------------------------------------------
DB_FILE = "datos_derby.txt"
TOLERANCIA = 0.080  # 80 gramos

# -------------------------------------------------
# FUNCIONES
# -------------------------------------------------
def cargar_datos():
    partidos = []
    g_evento = 2

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 2:
                    g_evento = len(p) - 1
                    d = {"PARTIDO": p[0]}
                    for i in range(1, g_evento + 1):
                        try:
                            d[f"Gallo {i}"] = float(p[i])
                        except:
                            d[f"Gallo {i}"] = 2.000
                    partidos.append(d)

    return partidos, g_evento


def guardar_datos(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for p in lista:
            pesos = [str(v) for k, v in p.items() if k != "PARTIDO"]
            f.write(f"{p['PARTIDO']}|{'|'.join(pesos)}\n")

# -------------------------------------------------
# APP
# -------------------------------------------------
st.title("DERBYSYSTEM PRUEBAS")

partidos_act, n_gallos_act = cargar_datos()

tab_reg, tab_cot = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

# -------------------------------------------------
# TAB REGISTRO
# -------------------------------------------------
with tab_reg:

    with st.form("registro_gallos", clear_on_submit=True):

        c1, c2 = st.columns([2, 1])
        nombre = c1.text_input("NOMBRE DEL PARTIDO").upper()

        g_tipo = c2.selectbox(
            "GALLOS POR PARTIDO:",
            [2, 3, 4, 5, 6],
            index=0
        )

        st.write("Introduzca los pesos:")
        pesos_in = []
        cols = st.columns(g_tipo)

        for i in range(g_tipo):
            peso = cols[i].number_input(
                f"Gallo {i+1}",
                min_value=1.000,
                max_value=5.000,
                value=2.100,
                step=0.001,
                format="%.3f"
            )
            pesos_in.append(peso)

        submit = st.form_submit_button("GUARDAR PARTIDO")

    # ---------- FUERA DEL FORM ----------
    if submit:

        if nombre == "":
            st.error("Debe escribir el nombre del partido")
            st.stop()

        if partidos_act:
            gallos_evento = len([k for k in partidos_act[0].keys() if k != "PARTIDO"])
            if g_tipo != gallos_evento:
                st.error(f"Este evento ya es de {gallos_evento} gallos por partido")
                st.stop()

        nuevo = {"PARTIDO": nombre}
        for i, w in enumerate(pesos_in):
            nuevo[f"Gallo {i+1}"] = w

        partidos_act.append(nuevo)
        guardar_datos(partidos_act)
        st.success(f"PARTIDO {nombre} GUARDADO CON {g_tipo} GALLOS")
        st.rerun()

    if partidos_act:
        st.subheader("Partidos en este evento")
        st.dataframe(pd.DataFrame(partidos_act), use_container_width=True)

        if st.button("BORRAR EVENTO"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            st.rerun()

# -------------------------------------------------
# TAB COTEJO
# -------------------------------------------------
with tab_cot:

    if len(partidos_act) >= 2:
        st.info("Cotejo listo para generarse.")
        st.write("Aquí puedes agregar la lógica de emparejamiento y anillos.")
    else:
        st.warning("Registre al menos 2 partidos para generar el cotejo.")
