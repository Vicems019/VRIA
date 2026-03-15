from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import undetected_chromedriver as uc
import random

def scroll_suave(driver):
    altura_actual = driver.execute_script("return window.scrollY")
    altura_total = driver.execute_script("return document.body.scrollHeight")
    
    while altura_actual < altura_total:
        # Incremento aleatorio entre 50 y 150px (más humano)
        incremento = random.randint(60, 250)
        altura_actual += incremento
        driver.execute_script(f"window.scrollTo(0, {altura_actual});")
        
        # Pausa aleatoria entre 0.05 y 0.3 segundos
        time.sleep(random.uniform(0.05, 0.3))
        
        # De vez en cuando hace una pausa más larga, como si estuvieras leyendo
        if random.random() < 0.1:  # 10% de probabilidad
            time.sleep(random.uniform(0.5, 1.5))
        
        # Actualizar altura total por si el DOM ha crecido
        altura_total = driver.execute_script("return document.body.scrollHeight")

options = uc.ChromeOptions()
options.add_argument("--start-maximized")

driver = uc.Chrome(options=options, version_main=145)  # 👈 Reemplaza al Chrome normal

url = "https://www.pccomponentes.com/opiniones/pccom-ready-v2-amd-ryzen-7-5800x-32gb-1tb-ssd-rtx-5060-ti-16gb"
url2 = "https://www.pccomponentes.com/opiniones/krom-kertz-rgb-238-led-fullhd-200hz-g-sync-compatible"
driver.get(url2)
time.sleep(3) # 5

# Cerrar cookies
try:
    cookies_btn = driver.find_element(By.XPATH, "//button[contains(., 'Aceptar')]")
    cookies_btn.click()
    print("✅ Cookies aceptadas")
    time.sleep(1)
except:
    print("No hay banner de cookies")

# ---- BUCLE CARGAR MÁS ----
while True:
    try:
        # 👇 Cambiado a commentDataContainer
        bloques_antes = len(driver.find_elements(By.CSS_SELECTOR, "[class*='commentDataContainer']"))
        print(f"Opiniones actuales: {bloques_antes}")

        scroll_suave(driver)
        time.sleep(1)

        botones = driver.find_elements(By.XPATH, "//button[contains(., 'Cargar más opiniones')]")
        
        if not botones:
            print("✅ No hay más botón, fin")
            break
        
        boton = botones[0]
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", boton)
        print("⏳ Click hecho, esperando nuevas opiniones...")
        time.sleep(4)

        scroll_suave(driver)
        time.sleep(2)

        timeout = 20
        while timeout > 0:
            # 👇 Cambiado a commentDataContainer
            bloques_despues = len(driver.find_elements(By.CSS_SELECTOR, "[class*='commentDataContainer']"))
            if bloques_despues > bloques_antes:
                print(f"✅ Cargadas {bloques_despues - bloques_antes} nuevas opiniones")
                break
            time.sleep(1)
            timeout -= 1
        
        if timeout == 0:
            print("⚠️ No cargó nuevas opiniones, saliendo...")
            break

    except Exception as e:
        print(f"Error: {e}")
        break

# ---- EXTRACCIÓN COMPLETA ----
print("\n📋 Extrayendo opiniones...\n")
bloques = driver.find_elements(By.CSS_SELECTOR, "[class*='commentDataContainer']")
print(f"Total de opiniones encontradas: {len(bloques)}\n")

opiniones = []

for i, bloque in enumerate(bloques):
    opinion = {}

    # Rating
    try:
        rating_el = bloque.find_element(By.CSS_SELECTOR, "[data-testid='rating-bar-percent']")
        style = rating_el.get_attribute("style")  # "width: 90%;"
        porcentaje = float(style.replace("width:", "").replace("%;", "").strip())
        opinion["rating"] = round(porcentaje / 100 * 5, 1)
    except:
        opinion["rating"] = None

    # Fecha
    try:
        fecha = bloque.find_element(By.CSS_SELECTOR, "[class*='captionRegular']")
        opinion["fecha"] = fecha.text
    except:
        opinion["fecha"] = None

    # Comentario
    try:
        comentario = bloque.find_element(By.CSS_SELECTOR, "[class*='body2Regular']")
        opinion["comentario"] = comentario.text
    except:
        opinion["comentario"] = None

    # Pros
    try:
        pros = bloque.find_elements(By.CSS_SELECTOR, "[data-testid='pros'] li")
        opinion["pros"] = [p.text for p in pros]
    except:
        opinion["pros"] = []

    # Contras
    try:
        cons = bloque.find_elements(By.CSS_SELECTOR, "[data-testid='cons'] li")
        opinion["contras"] = [c.text for c in cons]
    except:
        opinion["contras"] = []

    opiniones.append(opinion)

    print(f"--- Opinión {i+1} ---")
    print(f"⭐ Rating:     {opinion['rating']} / 5")
    print(f"📅 Fecha:      {opinion['fecha']}")
    print(f"💬 Comentario: {opinion['comentario']}")
    print(f"✅ Pros:       {opinion['pros']}")
    print(f"❌ Contras:    {opinion['contras']}")
    print()

driver.quit()