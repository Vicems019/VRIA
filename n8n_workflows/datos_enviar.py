import requests

def enviar_n8n(resultados):
    if not resultados:
        print("No hay resultados para enviar.")
        return
        
    print("Resultados:", resultados)
    total_resenas = len(resultados)

    print("Total reseñas extraidas:", total_resenas)
    
    # Calcular promedio rating
    # TODO ERROR EN LOS RATINGS MIRARLO
    ratings_validos = []
    for r in resultados:
        print(r)
        # Algunos ratings vienen como string o no existen
        try:
            rating = r.get("rating")
            if rating is not None:
                ratings_validos.append(float(rating))
        except (ValueError, TypeError):
            continue
            
    rating_promedio = 0.0
    if ratings_validos:
        rating_promedio = round(sum(ratings_validos) / len(ratings_validos), 1)

    # Extraer comentarios
    comentarios = [r.get("comentario", "") for r in resultados if r.get("comentario")]

    print(comentarios)

    # Extraer pros y contras
    pros_mencionados = []
    contras_mencionados = []
    for r in resultados:
        pros = r.get("pros")
        if pros:
            if isinstance(pros, list):
                pros_mencionados.extend(pros)
            else:
                pros_mencionados.append(pros)
                
        contras = r.get("contras")
        if contras:
            if isinstance(contras, list):
                contras_mencionados.extend(contras)
            else:
                contras_mencionados.append(contras)

    print(pros_mencionados)
    print(contras_mencionados)

    datos = {
        "total_resenas": total_resenas,
        "rating_promedio": rating_promedio,
        "comentarios": comentarios,
        "pros_mencionados": pros_mencionados,
        "contras_mencionados": contras_mencionados
    }

    print(datos)

    print(f"Enviando {total_resenas} reseñas a n8n...")
    webhook_url = "http://localhost:5678/webhook/analizar-producto"
    webhook_url_test = "http://localhost:5678/webhook-test/analizar-producto"

    try:
        response = requests.post(webhook_url_test, json=datos)
        response.raise_for_status()
        print(f"✅ Datos enviados a n8n correctamente. Código: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar datos a n8n: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    pass
