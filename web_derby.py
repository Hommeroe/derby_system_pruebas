import streamlit as st
import pandas as pd
import os
import json

# ==========================================
# BLOQUE 1: REGLAS FIJAS (LÓGICA BLINDADA)
# ==========================================
# [2026-01-14] El anillo se genera automático y vincula peso-partido-pelea.
TOLERANCIA_MAX = 0.080 

def generar_cotejo_anti_fraude(partidos, num_gallos):
    """
    Función Maestra: 
    1. Separa equipos iguales (Anti-choque).
    2. Respeta los 80g de tolerancia.
    3. Asigna anillos únicos y correlativos.
    """
    anillo_secuencia = 1
    pelea_secuencia = 1
    resultado_cotejo = {}

    for ronda in range(1, num_gallos + 1):
        col_p = f"Peso {ronda}"
        # Ordenar por peso para justicia deportiva
        lista_disp = sorted(partidos, key=lambda x: x.get(col_p, 0))
        peleas_ronda = []

        while len(lista_disp) >= 2:
            rojo = lista_disp.pop(0)
            
            # LÓGICA ANTI-CHOQUE: Buscar oponente de distinto partido
            verde_idx = -1
            for i in range(len(lista_disp)):
                if lista_disp[i]["PARTIDO"] != rojo["PARTIDO"]:
                    verde_idx = i
                    break
            
            # Si solo quedan del mismo partido al final (caso forzado)
            if verde_idx == -1: verde_idx = 0 
            
            verde = lista_disp.pop(verde_idx)

            # ASIGNACIÓN DE ANILLOS REAL (Seguridad)
            anillo_r = f"{anillo_secuencia:03}"
            anillo_v = f"{(anillo_secuencia + 1):03}"
            
            dif = abs(rojo[col_p] - verde[col_p])
            
            peleas_ronda.append({
                "pelea": pelea_secuencia,
                "partido_r": rojo["PARTIDO"],
                "peso_r": rojo[col_p],
                "an_r": anillo_r,
                "partido_v": verde["PARTIDO"],
                "peso_v": verde[col_p],
                "an_v": anillo_v,
                "dif": dif
            })
            
            anillo_secuencia += 2
            pelea_secuencia += 1
            
        resultado_cotejo[f"RONDA {ronda}"] = peleas_ronda
    
    return resultado_cotejo

# ==========================================
# BLOQUE 2: INTERFAZ Y ESTILOS (PROFESIONAL)
# ==========================================
st.set_page_config(page_title="DerbySystem PRUEBAS", layout="wide")

st.markdown("""
    <style>
    .software-brand { color: #555; font-size: 14px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .tabla-cotejo { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    .tabla-cotejo th { background: #000; color: #fff; border: 1px solid #000; padding: 6px; font-size: 11px; }
    .tabla-cotejo td { border: 1px solid #000; text-align: center; padding: 10px; font-size: 13px; }
    .celda-roja { border-left: 12px solid #d32f2f !important; font-weight: bold; }
    .celda-verde { border-right: 12px solid #388e3c !important; font-weight: bold; }
    .alerta-peso { background-color: #ffebee; color: red; font-weight: bold; }
    .box-check { width: 18px; height: 18px; border: 2px solid #000; margin: auto; }
    </style>
""", unsafe_allow_html=True)

# ... (Aquí van las funciones cargar_datos y guardar_todos que ya tienes) ...

st.markdown('<p class="software-brand">DERBYSYSTEM PRUEBAS</p>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📝 REGISTRO", "🏆 COTEJO Y ANILLOS"])

with tab2:
    partidos_lista, total_gallos = cargar_datos()
    if len(partidos_lista) >= 2:
        # Generar los datos usando la lógica blindada
        rondas_finales = generar_cotejo_anti_fraude(partidos_lista, total_gallos)
        
        for nombre_ronda, peleas in rondas_finales.items():
            st.markdown(f"<div style='background:#f0f0f0; border:2px solid #000; padding:8px; text-align:center; font-weight:bold;'>{nombre_ronda}</div>", unsafe_allow_html=True)
            
            tabla_html = """<table class='tabla-cotejo'>
                <tr>
                    <th># PELEA</th>
                    <th>G</th>
                    <th>PARTIDO ROJO</th>
                    <th>ANILLO</th>
                    <th>DIF.</th>
                    <th>E [ ]</th>
                    <th>ANILLO</th>
                    <th>PARTIDO VERDE</th>
                    <th>G</th>
                </tr>"""
            
            for p in peleas:
                clase_dif = "alerta-peso" if p['dif'] > TOLERANCIA_MAX else ""
                
                tabla_html += f"""
                <tr>
                    <td><b>{p['pelea']}</b></td>
                    <td><div class='box-check'></div></td>
                    <td class='celda-roja'>{p['partido_r']}<br>{p['peso_r']:.3f}</td>
                    <td><small>ID:</small><br><b>{p['an_r']}</b></td>
                    <td class='{clase_dif}'>{p['dif']:.3f}</td>
                    <td><div class='box-check'></div></td>
                    <td><small>ID:</small><br><b>{p['an_v']}</b></td>
                    <td class='celda-verde'>{p['partido_v']}<br>{p['peso_v']:.3f}</td>
                    <td><div class='box-check'></div></td>
                </tr>
                """
            tabla_html += "</table>"
            st.markdown(tabla_html, unsafe_allow_html=True)
            
        if st.button("📄 GENERAR IMPRESIÓN OFICIAL"):
            st.info("Generando reporte con trazabilidad de anillos...")
    else:
        st.info("Registre al menos 2 partidos para asignar anillos y generar peleas.")

st.markdown('<p style="text-align:center; font-size:10px; color:#aaa; margin-top:50px;">Creado por HommerDesigns’s</p>', unsafe_allow_html=True)
