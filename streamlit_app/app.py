import streamlit as st
import os
import sys

# EJECUTAR CON: python -m streamlit run .\streamlit_app\app.py

# --- Configuración de rutas ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
scraping_path = os.path.join(project_root, "scraping")

if scraping_path not in sys.path:
    sys.path.append(scraping_path)

try:
    from scraper import analizar_url
except ImportError:
    st.error("No se pudo importar el scraper. Verifica las rutas.")
    def analizar_url(url): return {"error": "Scraper no disponible"}

# --- Título y descripción ---
st.set_page_config(page_title="Análisis de sentimiento de Productos", layout="centered")
st.title("Análisis de sentimiento de Productos")
st.write("""
Este programa recibe una URL de producto y realiza un análisis de sentimiento,
mostrando resultados como descripción, pros y contras.
""")

# --- Entrada del usuario ---
url = st.text_input("Introduce la URL del producto")

# --- Botón para iniciar análisis ---
if st.button("Analizar"):
    if url:
        with st.spinner("Analizando opiniones... esto puede tardar unos segundos"):
            resultado = analizar_url(url)
        
        if "error" in resultado:
            st.error(f"Error en el análisis: {resultado['error']}")
        else:
            # Resultados reales
            st.subheader("Resultados del Análisis")
            st.write(f"URL analizada: {url}")
            
            # Asumiendo que el n8n devuelve { "sentimiento": "...", "pros": "...", "contras": "...", "resumen": "..." }
            # O similar. Ajustamos según la respuesta esperada del webhook.
            
            sentimiento = resultado.get("sentimiento", "No disponible")
            pros = resultado.get("pros", "No disponible")
            contras = resultado.get("contras", "No disponible")
            resumen = resultado.get("resumen", "No disponible")

            st.markdown(f"**Sentimiento general:** {sentimiento}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Pros:**")
                st.write(pros)
            with col2:
                st.markdown("**Contras:**")
                st.write(contras)
                
            st.markdown("**Descripción resumida:**")
            st.write(resumen)
    else:
        st.error("Por favor introduce una URL")