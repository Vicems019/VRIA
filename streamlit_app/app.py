import streamlit as st
import os
import sys

# EJECUTAR CON: python -m streamlit run .\streamlit_app\app.py

# --- Configuración de rutas ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
scraping_path = os.path.join(project_root, "scraping")

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scraping'))

if scraping_path not in sys.path:
    sys.path.append(scraping_path)

try:
    from scraper import analizar_url
except Exception as e:
    st.error(f"Error exacto: {type(e).__name__}: {e}")
    st.error("No se pudo importar el scraper. Verifica las rutas.")
    def analizar_url(url): return {"error": "Scraper no disponible"}

def limpiar_texto():
    st.session_state['url'] = ''


# --- Estilos Personalizados ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .stButton > button {
        border-radius: 10px;
        width: 100%;
    }
    .card {
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        height: 100%;
    }
    .pro-card {
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
    }
    .contra-card {
        background-color: #ffebee;
        border-left: 5px solid #c62828;
    }
    .summary-card {
        background-color: #e3f2fd;
        border-left: 5px solid #1565c0;
        width: 100%;
    }
    .card-title {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 10px;
        display: block;
    }
    .card-content {
        font-size: 0.95rem;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# --- Título y descripción ---
st.set_page_config(page_title="Análisis de sentimiento de Productos", layout="centered")
st.title("🛍️ Análisis de Sentimiento")
st.markdown("##### Analiza las opiniones de cualquier producto mediante su URL")

# --- Entrada del usuario ---
col1, col2 = st.columns([4,1])

with col1:
    url = st.text_input("Introduce la URL del producto", key="url", placeholder="https://ejemplo.com/producto...")

with col2:
    st.markdown('<div style="padding-top: 28px;"></div>', unsafe_allow_html=True)
    if st.button("Limpiar 🗑️"):
        st.session_state['url'] = ''
        st.rerun()

# --- Botón para iniciar análisis ---
if st.button("✨ Analizar Producto", type="primary"):
    if url:
        with st.spinner("Analizando opiniones... esto puede tardar unos segundos"):
            resultado = analizar_url(url)
        
        if "error" in resultado:
            st.error(f"❌ Error en el análisis: {resultado['error']}")
        else:
            # Resultados reales
            st.divider()
            st.subheader("📊 Resultados del Análisis")
            
            sentimiento = resultado.get("sentimiento_general", "No disponible").title()
            puntuacion_final = resultado.get("puntuacion_final", "N/A")
            pros = resultado.get("pros", "No disponible")
            contras = resultado.get("contras", "No disponible")
            resumen = resultado.get("resumen", "No disponible")

            c1, c2 = st.columns(2)
            with c1:
                st.metric("Sentimiento General", sentimiento)
            with c2:
                st.metric("Puntuación Final", f"{puntuacion_final}/10")
            
            st.markdown("<br>", unsafe_allow_html=True)

            # Pros y Contras en cards
            col_pros, col_contras = st.columns(2)
            
            with col_pros:
                st.markdown(f"""
                <div class="card pro-card">
                    <span class="card-title">✅ Pros</span>
                    <div class="card-content">{pros}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_contras:
                st.markdown(f"""
                <div class="card contra-card">
                    <span class="card-title">❌ Contras</span>
                    <div class="card-content">{contras}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Resumen en card ancha
            st.markdown(f"""
            <div class="card summary-card">
                <span class="card-title">📝 Resumen del Análisis</span>
                <div class="card-content">{resumen}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Por favor introduce una URL válida")

