import requests
import os
import sys

# Asegurar que la raíz del proyecto esté en el path para importar otros módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from analysis.preprocessor import preprocess_data
except ImportError:
    print("⚠️ No se pudo importar 'preprocess_data'. Se usará una versión mínima.")
    def preprocess_data(resultados):
        return {
            "total_resenas": len(resultados),
            "rating_promedio": 0.0,
            "comentarios": [r.get("comentario", "") for r in resultados if r.get("comentario")],
            "pros_mencionados": [],
            "contras_mencionados": []
        }

def enviar_n8n(resultados):
    if not resultados:
        print("No hay resultados para enviar.")
        return
        
    total_resenas = len(resultados)

    print("Total reseñas extraidas:", total_resenas)
    
    # Preprocesar datos (limpieza de ratings, pros, contras, etc.)
    datos = preprocess_data(resultados)

    total_resenas = datos["total_resenas"]
    rating_promedio = datos["rating_promedio"]
    comentarios = datos["comentarios"]
    pros_mencionados = datos["pros_mencionados"]
    contras_mencionados = datos["contras_mencionados"]

    print('Total Reseñas', total_resenas)
    print('Rating Promedio', rating_promedio)
    print('Comentarios', comentarios)
    print('Pros', pros_mencionados)
    print('Contras', contras_mencionados)

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
