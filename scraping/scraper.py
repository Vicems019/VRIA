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
        "url_mod": {
            "tipo": "insertar",
            "ancla": "pccomponentes.com/",
            "nuevo": "opiniones/",
        }
    },
    "mediamarkt.es": {
        "scroll_speed": 3,
        "cookies_btn": (By.XPATH,       "//button[contains(., 'Aceptar')]"),
        "bloque":      (By.CSS_SELECTOR, "[data-test='single-review-card']"),
        "paginacion": {
            "tipo":        "numerada",
            "selector": (By.XPATH, "//button[@translate='no' and @data-ignore-a11y='true' and text()='{}']"),
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
    "decathlon.es": {
    "scroll_speed": 1.5,
    "cookies_btn": (By.ID, "didomi-notice-agree-button"),
    "bloque": (By.CSS_SELECTOR, "div.review-card"),
    "paginacion": {
        "tipo": "numerada",
        "selector": (By.CSS_SELECTOR, "[data-part='button'][aria-label*='siguiente']"),
        "max_paginas": 5,
        "popup": False
    },
    "campos": {
        "rating": {
            "selector": (By.CSS_SELECTOR, ".vp-star-rating"),
            "tipo": "rating_aria",
        },
        "titulo": {
            "selector": (By.CSS_SELECTOR, ".review-card__title h3"),
            "tipo": "text",
        },
        "comentario": {
            "selector": (By.CSS_SELECTOR, "blockquote.review-card__review--long-content"),
            "tipo": "text",
        },
        "fecha": {
            "selector": (By.XPATH, ".//span[contains(@class, 'reviewer-info__item') and contains(., 'Hace')]"),
            "tipo": "text",
        },
    },
    "filtros": None,
    "url_mod": {
        "tipo": "reemplazar",
        "ancla": "/p/",
        "nuevo": "/r/"
    }
    }

}

prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.fonts": 2,
    "profile.default_content_setting_values.notifications": 2
}

def optimizar_url_segun_config(url, config):
    mod = config.get("url_mod")
    
    if not mod:
        return url

    tipo = mod.get("tipo")
    ancla = mod.get("ancla")
    nuevo = mod.get("nuevo")

    if tipo == "insertar":
        # Divide en el ancla e inserta justo después
        if ancla in url:
            partes = url.split(ancla, 1)
            suffix = mod.get("suffix", "")
            return f"{partes[0]}{ancla}{nuevo}{partes[1]}{suffix}"
            
    elif tipo == "reemplazar":
        return url.replace(ancla, nuevo, 1)

    return url

def scrape_opiniones(url):
    domain = su.get_domain(url)
    config = SITE_CONFIGS.get(domain)

    if not config:
        raise ValueError(f"No hay configuración para: {domain}")


    url_final = optimizar_url_segun_config(url, config)

    options = uc.ChromeOptions()

    options.add_experimental_option("prefs", prefs)  

    # Iniciar driver
    
    # options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")


    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options, version_main=145)

    wait = WebDriverWait(driver, 10)
    
    try: 

        driver.get(url_final)

        # Cerrar cookies
        try:
            by, sel = config["cookies_btn"]
            wait.until(EC.element_to_be_clickable((by, sel))).click()
            print("✅ Cookies aceptadas")
            time.sleep(0.3)
        except:
            print("ℹ️ No hay banner de cookies")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.65);")

        wait.until(
            EC.presence_of_element_located(config["bloque"])
        )

        opiniones = su.paginar(driver, config)

        print(f"Total: {len(opiniones)}")

        return opiniones

    except Exception as e:
        print(f"❌ Error en scrape_opiniones: {type(e).__name__}: {e}")
        return []
    finally:
        driver.quit()
    
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
    
    urlmm = "https://www.mediamarkt.es/es/product/_apple-iphone-17-azul-neblina-256-gb-5g-63-oled-super-retina-xdr-chip-a19-ios-1606127.html"
    urlax = "https://es.aliexpress.com/item/1005005952420757.html?spm=a2g0o.best.0.0.77b922aeMkiNt7&pdp_npi=6%40dis%21EUR%214%2C61%E2%82%AC%210%2C99%E2%82%AC%21%21%21%21%21%402103892f17736749760602052e01ac%2112000035000006810%21btfaff%21%21%21%211%210%21&afTraceInfo=1005005952420757__pc__pcBestMore2Love__oU6Kj8D__1773674976369&gatewayAdapt=glo2esp#nav-review"
    urldec = "https://www.decathlon.es/es/p/zapatillas-running-adidas-runblaze-hombre-negro/361354/c1m8929086"
    urlpcc = "https://www.pccomponentes.com/tarjeta-grafica-asus-prime-geforce-rtx-5060-oc-edition-8gb-gddr7-reflex-2-rtx-ai-dlss4"

    resultados = scrape_opiniones(urlmm)

    print(resultados)

    if resultados:
        resultado_limpio = enviar_n8n(resultados)
        print(resultado_limpio)
    else:
        print("❌ No se obtuvieron resultados para enviar.")