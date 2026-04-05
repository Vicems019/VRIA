import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# popup

def scroll_suave(driver, speed = 1, stop_before = 300):
    altura_actual = driver.execute_script("return window.scrollY")
    altura_total = driver.execute_script("return document.body.scrollHeight")
    
    while altura_actual < altura_total - stop_before:
        incremento = random.randint(300, 350) * speed
        altura_actual += incremento
        driver.execute_script(f"window.scrollTo(0, {altura_actual});")
        
        time.sleep(random.uniform(0.05, 0.3))
        
        altura_total = driver.execute_script("return document.body.scrollHeight")
        stop_before = altura_total*0.13

def extraer_campo(bloque, config_campo):
    by, selector = config_campo["selector"]
    tipo = config_campo["tipo"]

    try:
        if tipo == "lista":
            elementos = bloque.find_elements(by, selector)
            return [el.text for el in elementos]
        elif tipo == "rating_stars_count":
            estrellas = bloque.find_elements(by, selector)
            return len(estrellas)
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
    pag_cfg               = config["paginacion"]
    scroll_cfg            = config["scroll_speed"]
    by_bloque, sel_bloque = config["bloque"]
    
    ESTRATEGIAS = {
        "boton":    _paginar_boton,
        "numerada": _paginar_numerada,
    }

    estrategia = ESTRATEGIAS.get(pag_cfg["tipo"])
    if not estrategia:
        raise ValueError(f"Tipo de paginación desconocido: {pag_cfg['tipo']}")

    return estrategia(driver, pag_cfg, scroll_cfg, by_bloque, sel_bloque, config)


def _extraer_bloques(driver, by_bloque, sel_bloque, config):
    bloques = driver.find_elements(by_bloque, sel_bloque)
    return [
        {campo: extraer_campo(bloque, cfg) for campo, cfg in config["campos"].items()}
        for bloque in bloques
    ]

def _paginar_boton(driver, pag_cfg, scroll_cfg, by_bloque, sel_bloque, config):
    by_boton, sel_boton = pag_cfg["selector"]
    
    tiene_popup = pag_cfg.get("popup", False)
    popup_selector = pag_cfg.get("popup_selector")
    
    if tiene_popup:
        try:
            boton_ver_mas = driver.find_element(by_boton, sel_boton)
            driver.execute_script("arguments[0].click();", boton_ver_mas)
            print("🔲 Popup abierto")
            time.sleep(0.8)

            # Aplicar filtros
            aplicar_filtros(driver, config)
            popup_body = driver.find_element(By.CSS_SELECTOR, ".comet-v2-modal-body")
            scroll_popup(driver, popup_body, speed=1, stop_before=300)
            print("✅ Scroll del popup completado")

            # Extraer los datos
            opiniones = _extraer_bloques(driver, by_bloque, sel_bloque, config)
            print(f"✅ Total extraídas: {len(opiniones)}")
            return opiniones

        except Exception as e:
            print(f"⚠️ No se pudo abrir el popup: {e}")
        return []

    while True:
        try:
            bloques_antes = len(driver.find_elements(by_bloque, sel_bloque))
            scroll_suave(driver, scroll_cfg)
            time.sleep(1)

            botones = driver.find_elements(by_boton, sel_boton)
            if not botones:
                print("✅ No hay más botón, fin")
                break

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", botones[0])
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", botones[0])
            print("⏳ Cargando más...")

            timeout = 10
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

    opiniones = _extraer_bloques(driver, by_bloque, sel_bloque, config)
    print(f"✅ Total extraídas: {len(opiniones)}")
    return opiniones

def _paginar_numerada(driver, pag_cfg, scroll_cfg, by_bloque, sel_bloque, config):
    pagina_actual     = 1
    opiniones_totales = []
    max_paginas       = pag_cfg.get("max_paginas")

    aplicar_filtros(driver, config)

    while True:
        try:
            # Esperar a que los bloques estén cargados
            WebDriverWait(driver, 14).until(
                EC.presence_of_element_located((by_bloque, sel_bloque))
            )

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
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", boton)
            
            primer_bloque = driver.find_element(by_bloque, sel_bloque)
            driver.execute_script("arguments[0].click();", boton)
            print(f"⏳ Yendo a página {pagina_siguiente}...")
            WebDriverWait(driver, 14).until(
                EC.staleness_of(primer_bloque)
            )

            pagina_actual += 1

        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}")
            parcial = _extraer_bloques(driver, by_bloque, sel_bloque, config)
            opiniones_totales.extend(parcial)
            print(f"✅ Fin en página {pagina_actual}. Total: {len(opiniones_totales)}")
            break

    return opiniones_totales


def aplicar_filtros(driver, config):
    try:
        filtros = config.get("filtros", {})

        for nombre, cfg in filtros.items():
            if not cfg.get("activo", False):
                continue

            try:
                by, sel = cfg["selector"]
                el = driver.find_element(by, sel)

                if cfg.get("click_padre"):
                    el = el.find_element(By.XPATH, ".//..")

                driver.execute_script("arguments[0].click();", el)

                clase = el.get_attribute("class")
                time.sleep(0.8)
                if "active" in clase:
                    print(f"⏩ El filtro '{nombre}' ya está activo, saltando...")
                else:
                    try:
                        # Intento de click con ActionChains (simula ratón real)
                        actions = ActionChains(driver)
                        actions.move_to_element(el).click().perform()
                    except:
                        # Si falla, usamos el click de JS que ya tenías como plan B
                        driver.execute_script("arguments[0].click();", el)
                    
                    print(f"✅ Filtro '{nombre}' clickeado")

                print(f"✅ Filtro '{nombre}' aplicado")
            except Exception as e:
                print(f"Error al aplicar filtro '{nombre}': {e}")

    except:
        print("No se han agregado filtros")
        return
    
def scroll_popup(driver, popup_element, speed=1, stop_before=300, max_seconds=6):
    scroll_top = 0

    deadline = time.time() + max_seconds


    while time.time() < deadline:
        scroll_height = driver.execute_script("return arguments[0].scrollHeight", popup_element)

        if scroll_top >= scroll_height - stop_before:
            break

        incremento = random.randint(80, 300) * speed
        scroll_top = min(scroll_top + incremento, scroll_height)

        driver.execute_script("arguments[0].scrollTop = arguments[1];", popup_element, scroll_top)
        time.sleep(0.1)