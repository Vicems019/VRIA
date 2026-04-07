# 🤖 VRIA: Virtual Review Intelligence Analyzer

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=Selenium&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-FF6D5A?style=for-the-badge&logo=n8n&logoColor=white)

> **VRIA** transforma URLs de productos complejas en análisis estratégicos. Olvídate de leer cientos de comentarios; obtén una radiografía completa del producto en segundos.

---

## 🌟 Características Principales

* 🔍 **Scraping Avanzado:** Extracción de datos en crudo mediante Selenium y Undetected Chromedriver para evitar bloqueos.
* 🧠 **Análisis de Sentimiento:** Clasificación inteligente de la opinión de los usuarios.
* 📊 **Puntuación Dinámica:** Generación de un score basado en el contenido real de las reseñas.
* 📝 **Resumen Ejecutivo:** Síntesis de los puntos clave, pros y contras.
* 🚀 **Backend de IA:** Procesamiento ultra-rápido utilizando la API de Groq a través de flujos de trabajo en n8n.

---

## 🏗️ Arquitectura del Sistema

El flujo de trabajo de VRIA está diseñado para separar la captura de datos de la lógica de procesamiento:

1.  **Frontend (Streamlit):** El usuario introduce la URL.
2.  **Captura (Selenium):** Se navega al sitio, se extraen los datos (HTML/Text) y se limpian mínimamente.
3.  **Puente (Webhooks):** Los datos se envían a una instancia de **n8n**.
4.  **Cerebro (IA):** n8n procesa la información, consulta a **Groq (Llama 3* / Mixtral)** para el análisis semántico.
5.  **Entrega:** El JSON procesado vuelve a la interfaz para mostrarse de forma elegante.

---

## 🛠️ Stack Tecnológico y Versiones

| Tecnología | Versión | Uso |
| :--- | :--- | :--- |
| **Python** | 3.x | Lenguaje base |
| **Streamlit** | 1.55.0 | Interfaz de usuario |
| **Selenium** | 4.41.0 | Scraping y automatización |
| **Undetected Chromedriver** | 3.5.5 | Evasión de bloqueos de bots |
| **n8n** | Cloud/Self-hosted* | Orquestación de nodos |
| **Groq API** | Llama 3* / Mixtral | Procesamiento de lenguaje natural |

---

## 📂 Estructura del Proyecto

```text
VRIA/
├── analysis/               # Carpeta para analizar los datos en crudo
│   └── preprocessor.py     # Limpieza de palabras (tíldes, monosílabos, palabras poco relevantes)
├── n8n_workflows/
│   └── workflow.json       # Estructura de nodos para n8n
│   └── datos_enviar.py     # Enviar datos crudos a n8n
├── scraping/
│   └── scraper_utils.py    # Funciones para elaborar el scraping
│   └── scraper.py          # Acceso salida del scraping
├── streamlit_app/
│   └── app.py              # Aplicación principal
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación
```
---
## Creado por Vicente Marín Suazo
