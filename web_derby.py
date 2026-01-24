import streamlit as st
import os
import random
import string

# --- 1. INICIALIZACIÓN (Evita el AttributeError) ---
if "id_usuario" not in st.session_state:
    st.session_state.id_usuario = ""
if "temp_llave" not in st.session_state:
    st.session_state.temp_llave = None

# --- PANTALLA DE ENTRADA CORREGIDA ---
if st.session_state.id_usuario == "":
    st.markdown("""
        <style>
        .stApp { margin-top: -60px !important; }
        .login-card {
            max-width: 480px; margin: 0 auto; background: #ffffff;
            padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-top: 5px solid #E67E22;
        }
        .main-title { font-size: 2.4rem; font-weight: 800; color: #E67E22; text-align: center; }
        .llave-grande { 
            font-size: 2rem; color: #1a1a1a; background: #f0f2f6; 
            padding: 10px; border-radius: 8px; text-align: center; 
            border: 2px dashed #E67E22; margin: 15px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    col_1, col_center, col_3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="main-title">DerbySystem</div>', unsafe_allow_html=True)
        
        # Si no estamos en proceso de generar una llave, mostramos las pestañas normales
        if not st.session_state.temp_llave:
            tab_entrar, tab_nuevo = st.tabs(["🔑 ENTRAR", "✨ NUEVO EVENTO"])
            
            with tab_entrar:
                llave_input = st.text_input("Introduce tu llave:", placeholder="EJ: DERBY-XJ429").upper().strip()
                if st.button("ACCEDER AL SISTEMA", use_container_width=True):
                    if os.path.exists(f"datos_{llave_input}.txt"):
                        st.session_state.id_usuario = llave_input
                        st.rerun()
                    else:
                        st.error("Esa llave no existe.")
            
            with tab_nuevo:
                st.write("Crea un identificador único para tu torneo.")
                if st.button("GENERAR NUEVA LLAVE", use_container_width=True):
                    chars = string.ascii_uppercase + string.digits
                    st.session_state.temp_llave = "DERBY-" + "".join(random.choices(chars, k=5))
                    st.rerun()
        
        # Si ya se generó la llave, mostramos la confirmación y el botón de entrar/volver
        else:
            st.markdown(f"### ¡Tu llave ha sido generada!")
            st.markdown(f'<div class="llave-grande">{st.session_state.temp_llave}</div>', unsafe_allow_html=True)
            st.warning("⚠️ IMPORTANTE: Anota esta llave ahora. La necesitarás para volver a entrar a tus datos.")
            
            if st.button("✅ YA LA ANOTÉ, ENTRAR AL SISTEMA", use_container_width=True):
                # Creamos el archivo y entramos
                with open(f"datos_{st.session_state.temp_llave}.txt", "w", encoding="utf-8") as f: pass
                st.session_state.id_usuario = st.session_state.temp_llave
                st.session_state.temp_llave = None # Limpiamos la temporal
                st.rerun()
            
            if st.button("⬅️ VOLVER / CANCELAR", use_container_width=True):
                st.session_state.temp_llave = None
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- EL RESTO DE TU CÓDIGO (Lógica, Cotejo, Anillos) ---
# Recuerda que el anillo se genera automático [cite: 2026-01-14]
# No mover nada de la lógica de tablas e impresiones.
