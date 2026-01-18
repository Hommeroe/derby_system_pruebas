import streamlit as st

# 1. Definimos usuarios y contraseñas (Esto después se pasa a una base de datos)
USUARIOS_VALIDOS = {
    "admin": "12345",
    "gallera_norte": "pavo99",
    "homero_pro": "derby2026"
}

def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.subheader("🔑 Acceso al Sistema")
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if user in USUARIOS_VALIDOS and USUARIOS_VALIDOS[user] == password:
                st.session_state.autenticado = True
                st.session_state.usuario_actual = user
                st.rerun()
            else:
                st.error("Usuario o clave incorrectos")
        return False
    return True

if login():
    st.sidebar.write(f"👤 Sesión: {st.session_state.usuario_actual}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    
    # AQUÍ VA TODO TU CÓDIGO DEL DERBY...
    st.title(f"Bienvenido al Derby de {st.session_state.usuario_actual}")
