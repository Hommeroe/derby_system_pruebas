import streamlit as st
import random
import string
import os

# --- FUNCIÓN PARA GENERAR CÓDIGO ÚNICO ---
def generar_codigo_nuevo():
    # Genera algo como DERBY-8293
    letras = ''.join(random.choices(string.ascii_uppercase, k=2))
    numeros = ''.join(random.choices(string.digits, k=4))
    return f"DERBY-{letras}{numeros}"

# --- PANTALLA DE ENTRADA ACTUALIZADA ---
if st.session_state.id_usuario == "":
    # (Tus estilos CSS se mantienen iguales)
    st.markdown("""<style>...</style>""", unsafe_allow_html=True) 

    col_1, col_center, col_3 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="main-title">DerbySystem</div>', unsafe_allow_html=True)
        
        tab_entrar, tab_nuevo = st.tabs(["🔑 ENTRAR CON CÓDIGO", "➕ CREAR NUEVO EVENTO"])
        
        with tab_entrar:
            codigo = st.text_input("ESCRIBE TU CÓDIGO DE ACCESO", placeholder="EJ: DERBY-XJ42").upper().strip()
            if st.button("ACCEDER", use_container_width=True):
                if codigo:
                    if os.path.exists(f"datos_{codigo}.txt"):
                        st.session_state.id_usuario = codigo
                        st.rerun()
                    else:
                        st.error("Ese código no existe. Verifica o crea uno nuevo.")
                else:
                    st.warning("Escribe un código.")

        with tab_nuevo:
            st.write("Si es un evento nuevo, genera una llave de acceso única.")
            if st.button("GENERAR MI LLAVE DE ACCESO", use_container_width=True):
                nuevo_cod = generar_codigo_nuevo()
                # Nos aseguramos que no exista ya por azar
                while os.path.exists(f"datos_{nuevo_cod}.txt"):
                    nuevo_cod = generar_codigo_nuevo()
                
                st.session_state.id_usuario = nuevo_cod
                # Creamos el archivo vacío para apartar el nombre
                with open(f"datos_{nuevo_cod}.txt", "w") as f: f.write("")
                st.success(f"¡Código generado! Tu llave es: **{nuevo_cod}**")
                st.info("⚠️ ANOTA TU LLAVE. La necesitarás para volver a entrar.")
                if st.button("ENTRAR AHORA"): st.rerun()

        st.markdown('<div class="login-footer">© 2026 DerbySystem PRO | Seguridad por Llaves</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
