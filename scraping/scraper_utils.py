import time
import random
from selenium.webdriver.common.by import By


def scroll_suave(driver, speed = 1):
    altura_actual = driver.execute_script("return window.scrollY")
    altura_total = driver.execute_script("return document.body.scrollHeight")
    
    while altura_actual < altura_total:
        # Incremento aleatorio entre 50 y 150px (más humano)
        incremento = random.randint(60, 250) * speed
        altura_actual += incremento
        driver.execute_script(f"window.scrollTo(0, {altura_actual});")
        
        # Pausa aleatoria entre 0.05 y 0.3 segundos
        time.sleep(random.uniform(0.05, 0.3))
        
        # De vez en cuando hace una pausa más larga, como si estuvieras leyendo
        if random.random() < 0.1:  # 10% de probabilidad
            time.sleep(random.uniform(0.5, 1.5))
        
        # Actualizar altura total por si el DOM ha crecido
        altura_total = driver.execute_script("return document.body.scrollHeight")

def extraer_campo(bloque, config_campo):
    by, selector = config_campo["selector"]
    tipo = config_campo["tipo"]

    try:
        if tipo == "lista":
            elementos = bloque.find_elements(by, selector)
            return [el.text for el in elementos]
        elif tipo == "rating_style":
            el = bloque.find_element(by, selector)
            style = el.get_attribute("style")
            porcentaje = float(style.replace("width:", "").replace("%;", "").strip())
            return round(porcentaje / 100 * 5, 1)
        else:
            el = bloque.find_element(by, selector)
            return el.text
    except:
        return [] if tipo == "lista" else None

def get_domain(url):
    from urllib.parse import urlparse
    return urlparse(url).netloc.replace("www.", "")

def paginar(driver, config):
    """Siempre devuelve una lista de opiniones, sin importar el tipo."""
    pag_cfg               = config["paginacion"]
    scroll_cfg            = config["scroll_speed"]
    by_bloque, sel_bloque = config["bloque"]

    ESTRATEGIAS = {
        "boton":    _paginar_boton,      # extrae AL FINAL (DOM acumulativo)
        "numerada": _paginar_numerada,   # extrae EN CADA PÁGINA (DOM se reemplaza)
    }

    estrategia = ESTRATEGIAS.get(pag_cfg["tipo"])
    if not estrategia:
        raise ValueError(f"Tipo de paginación desconocido: {pag_cfg['tipo']}")

    return estrategia(driver, pag_cfg, scroll_cfg, by_bloque, sel_bloque, config)


def _extraer_bloques(driver, by_bloque, sel_bloque, config):
    """Extracción reutilizable, la llaman ambas estrategias."""
    bloques = driver.find_elements(by_bloque, sel_bloque)
    return [
        {campo: extraer_campo(bloque, cfg) for campo, cfg in config["campos"].items()}
        for bloque in bloques
    ]


def _paginar_boton(driver, pag_cfg, scroll_cfg, by_bloque, sel_bloque, config):
    """PCComponentes: el DOM acumula → extrae solo al final."""
    by_boton, sel_boton = pag_cfg["selector"]

    while True:
        try:
            bloques_antes = len(driver.find_elements(by_bloque, sel_bloque))
            scroll_suave(driver, scroll_cfg)
            time.sleep(1)

            botones = driver.find_elements(by_boton, sel_boton)
            if not botones:
                print("✅ No hay más botón, fin")
                break

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", botones[0])
            time.sleep(2)
            driver.execute_script("arguments[0].click();", botones[0])
            print("⏳ Cargando más...")
            time.sleep(4)

            timeout = 20
            while timeout > 0:
                if len(driver.find_elements(by_bloque, sel_bloque)) > bloques_antes:
                    break
                time.sleep(1)
                timeout -= 1

            if timeout == 0:
                print("⚠️ Sin nuevas opiniones, saliendo...")
                break

        except Exception as e:
            print(f"Error: {e}")
            break

    # 👇 Extrae UNA VEZ al final
    opiniones = _extraer_bloques(driver, by_bloque, sel_bloque, config)
    print(f"✅ Total extraídas: {len(opiniones)}")
    return opiniones


def _paginar_numerada(driver, pag_cfg, scroll_cfg, by_bloque, sel_bloque, config):
    """MediaMarkt: el DOM se reemplaza → extrae en CADA página."""
    pagina_actual    = 1
    opiniones_totales = []
    max_paginas       = pag_cfg.get("max_paginas")

    while True:
        try:
            scroll_suave(driver, scroll_cfg)
            time.sleep(1)

            # 👇 Extrae ANTES de cambiar de página
            parcial = _extraer_bloques(driver, by_bloque, sel_bloque, config)
            opiniones_totales.extend(parcial)
            print(f"📄 Página {pagina_actual}: {len(parcial)} opiniones")

            if max_paginas and pagina_actual >= max_paginas:
                print(f"✅ Límite de páginas alcanzado ({max_paginas})")
                break

            pagina_siguiente = pagina_actual + 1
            boton = driver.find_element(
                By.XPATH,
                f"//button[@translate='no' and @data-ignore-a11y='true' and text()='{pagina_siguiente}']"
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", boton)
            print(f"⏳ Yendo a página {pagina_siguiente}...")
            time.sleep(3)
            pagina_actual += 1

        except:
            # No hay más páginas, extrae la última
            parcial = _extraer_bloques(driver, by_bloque, sel_bloque, config)
            opiniones_totales.extend(parcial)
            print(f"✅ Fin en página {pagina_actual}. Total: {len(opiniones_totales)}")
            break

    return opiniones_totales