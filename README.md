# VRIA — Valoraciones y Reseñas con Inteligencia Artificial

> ⚠️ **README temporal.** Este documento se actualizará cuando la aplicación esté completamente desarrollada.

## ¿Qué es VRIA?

VRIA es una aplicación web local que analiza las reseñas de un producto de Amazon y genera un informe estructurado con sus cualidades y defectos, usando web scraping e inteligencia artificial.

El usuario introduce una URL de Amazon, la aplicación extrae automáticamente las reseñas y un modelo LLM local (Ollama) las analiza para devolver un informe en español.

---

## Estado actual del proyecto

| Módulo | Estado |
|---|---|
| Scraper (BeautifulSoup + Playwright) | 🟡 En desarrollo |
| Preprocesado de datos | ⬜ Pendiente |
| Análisis con Ollama | ⬜ Pendiente |
| Interfaz Streamlit | ⬜ Pendiente |
| Workflows n8n | ⬜ Pendiente |

---

## Estructura del proyecto

```
VRIA/
├── data/
│   ├── raw/                  # Reseñas en crudo (JSON)
│   └── processed/            # Reseñas limpias y estructuradas
├── scraping/
│   ├── scraper.py            # Scraper con fallback BS4 → Playwright
│   ├── playwright_config.py
│   └── parsers/              # Un parser por cada web soportada
│       └── amazon.py
├── analysis/
│   ├── sentiment.py          # Conexión y llamadas a Ollama
│   ├── preprocessor.py       # Limpieza del texto
│   └── report_builder.py     # Construcción del informe final
├── streamlit_app/
│   ├── app.py
│   ├── utils.py
│   └── pages/
├── n8n_workflows/
│   ├── scraping_workflow.json
│   └── procesamiento.json
├── tests/
│   ├── test_scraper.py
│   └── test_analysis.py
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Páginas soportadas

Por el momento la aplicación solo funciona con:

- ✅ PCComponentes.es
- ✅ Mediamarkt.es

> Otras páginas se irán añadiendo progresivamente.

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python |
| Interfaz web | Streamlit |
| Scraping | BeautifulSoup / Playwright (fallback) |
| Modelo LLM | Ollama |
| Automatización | n8n |

---

## Instalación y uso

> Pendiente de documentar cuando la aplicación esté funcional.

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd VRIA

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run streamlit_app/app.py
```

---

## Limitaciones conocidas

- La aplicación **no funciona con todos los enlaces**, solo con las páginas específicamente soportadas.
- No hay base de datos. Los datos se almacenan localmente en formato JSON.
- La aplicación **no está desplegada en cloud**, solo funciona en local.
- Amazon puede bloquear el scraping en determinadas circunstancias.

---

## Autor

Desarrollado como proyecto académico.
