import streamlit as st

# --- Título y descripción ---
st.set_page_config(page_title="Demo Análisis de Producto", layout="centered")
st.title("Demo: Análisis de Opiniones de Productos")
st.write("""
Esta demo recibe una URL de producto y simula un análisis de sentimiento,
mostrando resultados de ejemplo como descripción, pros y contras.
""")

# --- Entrada del usuario ---
url = st.text_input("Introduce la URL del producto")

# TODO AQUÍ HAY QUE PASARLO AL N8N

# --- Botón para iniciar análisis ---
if st.button("Analizar"):
    if url:
        # Simulación de procesamiento
        with st.spinner("Analizando..."):
            import time
            time.sleep(2)  # Simula tiempo de análisis

        

        # Resultados simulados
        st.subheader("Resultados del Análisis")
        st.write(f"URL analizada: {url}")
        st.markdown("**Sentimiento general:** ✅ Positivo")
        st.markdown("**Pros:**")
        st.write("- Buen diseño\n- Alta durabilidad\n- Fácil de usar")
        st.markdown("**Contras:**")
        st.write("- Precio algo elevado\n- Disponibilidad limitada")
        st.markdown("**Descripción resumida:**")
        st.write("Producto muy bien valorado por los usuarios, destaca en calidad y facilidad de uso.")
    else:
        st.error("Por favor introduce una URL")