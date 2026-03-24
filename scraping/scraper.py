from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
import undetected_chromedriver as uc
import random
import scraper_utils as su
import os

# Configuración de rutas para importar desde n8n_workflows
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
workflows_path = os.path.join(project_root, "n8n_workflows")

if workflows_path not in sys.path:
    sys.path.append(workflows_path)

try:
    from datos_enviar import enviar_n8n
except ImportError:
    print("⚠️ No se pudo importar 'datos_enviar' desde n8n_workflows")
    def enviar_n8n(x): print("Simulación: enviando datos a n8n...")


# CONFIGURACIÓN DEL SITIO

SITE_CONFIGS = {
    "pccomponentes.com": {
        "scroll_speed": 1.2,
        "cookies_btn":    (By.XPATH,      "//button[contains(., 'Aceptar')]"),
        "bloque":         (By.CSS_SELECTOR, "[class*='commentDataContainer']"),
        "paginacion": {
            "tipo":        "boton",
            "selector":    (By.XPATH, "//button[contains(., 'Cargar más opiniones')]"),
            "max_paginas": None,
            "popup": False
        },
        "campos": {
            "rating": {
                "selector": (By.CSS_SELECTOR, "[data-testid='rating-bar-percent']"),
                "tipo": "rating_style",
            },
            "fecha": {
                "selector": (By.CSS_SELECTOR, "[class*='captionRegular']"),
                "tipo": "text",
            },
            "comentario": {
                "selector": (By.CSS_SELECTOR, "[class*='body2Regular']"),
                "tipo": "text",
            },
            "pros": {
                "selector": (By.CSS_SELECTOR, "[data-testid='pros'] li"),
                "tipo": "lista",
            },
            "contras": {
                "selector": (By.CSS_SELECTOR, "[data-testid='cons'] li"),
                "tipo": "lista",
            },
        },
        "filtros": None
    },
    "mediamarkt.es": {
        "scroll_speed": 3,
        "cookies_btn": (By.XPATH,       "//button[contains(., 'Aceptar')]"),
        "bloque":      (By.CSS_SELECTOR, "[data-test='single-review-card']"),
        "paginacion": {
            "tipo":        "numerada",
            "selector": None,
            "max_paginas": 5,
            "popup": False
        },
        "campos": {
            "rating": {
                "selector": (By.CSS_SELECTOR, "[data-test='mms-customer-rating-count']"),
                "tipo": "rating_slash",
            },
            "titulo": {
                "selector": (By.CSS_SELECTOR, "p.ixvBRV"),
                "tipo": "text",
            },
            "comentario": {
                "selector": (By.CSS_SELECTOR, "[data-test='mms-review-full'] span"),
                "tipo": "text",
            },
            "pros": {
                "selector": (By.CSS_SELECTOR, "[data-test='review-feedback-pro'] ~ ul li p"),
                "tipo": "lista",
            },
            "contras": {
                "selector": (By.CSS_SELECTOR, "[data-test='review-feedback-cons'] ~ ul li p"),
                "tipo": "lista",
            },
        },
        "filtros": None
    },
    "es.aliexpress.com": {
        "cookies_btn": (By.XPATH, "//button[contains(., 'Aceptar cookies')]"),
        "bloque":      (By.CSS_SELECTOR, "div.list--itemBox--je_KNzb"),
        "paginacion": {
            "tipo":        "boton",
            "selector": (By.XPATH, "//button[.//span[text()='Ver más']]"),
            "max_paginas": None,
            "popup": True,
            "popup_selector": (By.CSS_SELECTOR, ".comet-v2-modal-body")
        },
        "scroll_speed": 1.2,
        "campos": {
            "rating": {
                "selector": (By.CSS_SELECTOR, "span.comet-icon-starreviewfilled"), 
                "tipo": "rating_stars_count"
                },
            "comentario": {
                "selector": (By.CSS_SELECTOR, "div.list--itemReview--d9Z9Z5Z"),    
                "tipo": "text"
                },
            "fecha": {
                "selector": (By.CSS_SELECTOR, "div.list--itemInfo--VEcgSFh span"),
                "tipo": "fecha_pipe"
                },
            "variante": {
                "selector": (By.CSS_SELECTOR, "div.list--itemSku--idEQSGC"),
                "tipo": "text"
                },
        },
        "filtros": {
            "pais": { # ESP
                "activo": True,
                "selector": (By.XPATH, "//div[contains(@class, 'filterItem')] [span[contains(@class, 'ES')]]"),
                "click_padre": False
            }
        }
    },
}

def scrape_opiniones(url):
    domain = su.get_domain(url)
    config = SITE_CONFIGS.get(domain)

    if not config:
        raise ValueError(f"No hay configuración para: {domain}")

    # Iniciar driver
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless") # TODO COMENTARLO Y MANEJARLO CORRECTAMENTE AL TENER LAS PÁGINAS PULIDAS
    options.add_argument("--disable-gpu")
    driver = uc.Chrome(options=options, version_main=145)
    driver.get(url)


    # Cerrar cookies
    try:
        by, sel = config["cookies_btn"]
        driver.find_element(by, sel).click()
        print("✅ Cookies aceptadas")
        time.sleep(0.3)
    except:
        print("ℹ️ No hay banner de cookies")

    # Extracción
    print("\n📋 Extrayendo opiniones...\n")
    opiniones = su.paginar(driver, config)
    print(f"Total: {len(opiniones)}")
    
    
    if driver:
        driver.quit()

    return opiniones
    
# EJECUCIÓN DESDE APP.PY
def analizar_url(url):
    """
    Función unificada para ser llamada desde Streamlit.
    Realiza el scraping y envía los datos a n8n.
    """
    try:
        opiniones = scrape_opiniones(url)

        print("Opiniones extraidas:", opiniones)
        if opiniones:
            resultado = enviar_n8n(opiniones)
            return resultado
        else:
            return {"error": "No se encontraron opiniones para analizar."}
    except Exception as e:
        return {"error": str(e)}

#  EJECUCIÓN

if __name__ == "__main__":
    urlpcc = "https://www.pccomponentes.com/opiniones/krom-kertz-rgb-238-led-fullhd-200hz-g-sync-compatible"
    urlmm = "https://www.mediamarkt.es/es/product/_apple-iphone-17-azul-neblina-256-gb-5g-63-oled-super-retina-xdr-chip-a19-ios-1606127.html"
    urlax = "https://es.aliexpress.com/item/1005005952420757.html?spm=a2g0o.best.0.0.77b922aeMkiNt7&pdp_npi=6%40dis%21EUR%214%2C61%E2%82%AC%210%2C99%E2%82%AC%21%21%21%21%21%402103892f17736749760602052e01ac%2112000035000006810%21btfaff%21%21%21%211%210%21&afTraceInfo=1005005952420757__pc__pcBestMore2Love__oU6Kj8D__1773674976369&gatewayAdapt=glo2esp#nav-review"

    resultados = scrape_opiniones(urlax)

    if resultados:
        resultado_limpio = enviar_n8n(resultados)
        print(resultado_limpio)
    else:
        print("❌ No se obtuvieron resultados para enviar.")