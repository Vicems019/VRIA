from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import undetected_chromedriver as uc
import random
import scraper_utils as su

# CONFIGURACIÓN DEL SITIO

SITE_CONFIGS = {
    "pccomponentes.com": {
        "scroll_speed": 1.2,
        "cookies_btn":    (By.XPATH,      "//button[contains(., 'Aceptar')]"),
        "bloque":         (By.CSS_SELECTOR, "[class*='commentDataContainer']"),
        "paginacion": {
            "tipo":        "boton",   # 👈 "boton" | "numerada"
            "selector":    (By.XPATH, "//button[contains(., 'Cargar más opiniones')]"),
            "max_paginas": None,
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
        }
    },
    "mediamarkt.es": {
        "scroll_speed": 2.2,
        "cookies_btn": (By.XPATH,       "//button[contains(., 'Aceptar')]"),
        "bloque":      (By.CSS_SELECTOR, "[data-test='single-review-card']"),
        "paginacion": {
            "tipo":        "numerada",  # 👈 paginación por números
            "selector":    None,
            "max_paginas": 5,
        },
        "campos": {
            "rating": {
                "selector": (By.CSS_SELECTOR, "[data-test='mms-customer-rating-count']"),
                "tipo": "rating_slash",   # viene como "5 / 5", nuevo tipo necesario
            },
            "titulo": {
                "selector": (By.CSS_SELECTOR, "p.ixvBRV"),   # ⚠️ clase generada, puede cambiar
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
        }
    },
    "amazon.es": {
        "scroll_speed": 2.2,
        "cookies_btn": (By.XPATH,       "//button[contains(., 'Aceptar')]"),
        "bloque":      (By.CSS_SELECTOR, "[data-test='single-review-card']"),
        "paginacion": {
            "tipo":        "numerada",  # 👈 paginación por números
            "selector":    None,
            "max_paginas": 5,
        },
        "campos": {
            "rating": {
                "selector": (By.CSS_SELECTOR, "[data-test='mms-customer-rating-count']"),
                "tipo": "rating_slash",   # viene como "5 / 5", nuevo tipo necesario
            },
            "titulo": {
                "selector": (By.CSS_SELECTOR, "p.ixvBRV"),   # ⚠️ clase generada, puede cambiar
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
        }
    },
}

def scrape_opiniones(url):
    domain = su.get_domain(url)
    config = SITE_CONFIGS.get(domain)

    if not config:
        raise ValueError(f"❌ No hay configuración para: {domain}")

    # — Iniciar driver —
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options, version_main=145)
    driver.get(url)
    time.sleep(2.2)

    # — Cerrar cookies —
    try:
        by, sel = config["cookies_btn"]
        driver.find_element(by, sel).click()
        print("✅ Cookies aceptadas")
        time.sleep(1)
    except:
        print("ℹ️ No hay banner de cookies")

    # — Paginación —
    su.paginar(driver, config)

    # — Extracción —
    print("\n📋 Extrayendo opiniones...\n")
    opiniones = su.paginar(driver, config)
    print(f"Total: {len(opiniones)}")
    
    driver.quit()
    return opiniones

#  EJECUCIÓN

if __name__ == "__main__":
    urlpcc = "https://www.pccomponentes.com/opiniones/krom-kertz-rgb-238-led-fullhd-200hz-g-sync-compatible"
    urlmm = "https://www.mediamarkt.es/es/product/_apple-iphone-17-azul-neblina-256-gb-5g-63-oled-super-retina-xdr-chip-a19-ios-1606127.html"
    urlamz = "https://www.amazon.es/product-reviews/B0FHQFFDJ6/ref=cm_cr_dp_d_show_all_btm?ie=UTF8"
    resultados = scrape_opiniones(urlamz)
    print(resultados)