# --- LOGICA PANEL ADMINISTRADOR ACTUALIZADA ---
if acceso == "28days":
    st.title("🛠️ Panel de Control Administrador")
    
    # Sección 1: Gestión de Usuarios
    st.subheader("👥 Usuarios Registrados")
    usuarios = cargar_usuarios()
    if usuarios:
        df_users = pd.DataFrame(list(usuarios.items()), columns=["Usuario", "Hash Contraseña"])
        st.table(df_users)
    else:
        st.info("No hay usuarios registrados aún.")
    
    st.divider()

    # Sección 2: Archivos de Datos
    st.subheader("📄 Archivos de Registros (.txt)")
    archivos = [f for f in os.listdir(".") if f.startswith("datos_") and f.endswith(".txt")]
    
    if archivos:
        for arch in archivos:
            with st.container():
                col_t, col_b = st.columns([5, 1])
                col_t.markdown(f"**Archivo:** `{arch}`")
                if col_b.button("🗑️ Eliminar", key=f"del_{arch}"):
                    os.remove(arch)
                    st.rerun()
                try:
                    # Cargamos el archivo para mostrar los datos internos
                    df_temp = pd.read_csv(arch, sep="|", header=None)
                    # Ponemos nombres de columnas genéricos según el contenido
                    columnas = ["PARTIDO"] + [f"G{i}" for i in range(1, len(df_temp.columns))]
                    df_temp.columns = columnas
                    st.dataframe(df_temp, use_container_width=True)
                except:
                    st.warning(f"El archivo {arch} está vacío o tiene un formato incompatible.")
                st.write("")
    else:
        st.info("No se encontraron archivos de datos generados.")

    if st.button("⬅️ VOLVER AL SISTEMA"): 
        st.rerun()
    st.stop()
