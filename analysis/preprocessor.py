import re
import unicodedata

 # TEXTOS A ELIMINAR
STOP_WORDS = {
    # Artículos
    "el", "la", "los", "las", "lo", "un", "una", "unos", "unas",
    # Preposiciones
    "a", "al", "ante", "bajo", "con", "contra", "de", "del", "desde",
    "durante", "en", "entre", "hacia", "hasta", "mediante", "para",
    "por", "segun", "sin", "sobre", "tras", "via",
    # Pronombres / partículas
    "le", "me", "mi", "te", "se", "si", "su", "sus", "yo", "tu",
    "el", "ella", "ellos", "ellas", "nos", "vos",
    # Conjunciones
    "y", "e", "o", "u", "ni", "pero", "sino", "que", "aunque", "como",
    "cuando", "donde", "porque", "pues",
    # Verbos auxiliares comunes
    "es", "son", "fue", "ser", "esta", "este", "esto", "estan", "hay",
    # Adverbios genéricos
    "muy", "mas", "tan", "ya", "aun", "bien", "mal", "aqui", "alli",
    "tambien", "tampoco", "no", "si",
    # Otros
    "uno", "verso", "versus", "ante", "cabe", "segun", "fiambre",
    "nada", "ninguno", "ningun", "ninguna"
}

TEXTOS_INVALIDOS = {
    "ninguno", "ninguna", "ningun", "nada", "no hay", "sin contras",
    "todo bien", "todo perfecto", "todo correcto", "todo ok",
    "de momento nada", "por ahora nada", "no se me ocurre nada",
    "no tengo quejas", "sin quejas", "sin problemas",
    "ok", "normal",
} 

def clean_ratings(resultados):
    ratings_validos = []
    for r in resultados:
        rating = r.get("rating")
        
        if rating is None:
            continue
        try:
            if isinstance(rating, str) and "/" in rating:
                partes = rating.split("/")
                numerador = float(partes[0])
                denominador = float(partes[1])
                if denominador == 0:
                    continue
                valor_normalizado = (numerador / denominador) * 5
                ratings_validos.append(valor_normalizado)
            else:
                valor = float(rating)
                if valor > 5:
                    valor = (valor / 10) * 5
                ratings_validos.append(valor)
        except (ValueError, TypeError, ZeroDivisionError) as e:
            print(f"Error: {e}")
            continue
    
    if not ratings_validos:
        return 0.0
    return round(sum(ratings_validos) / len(ratings_validos), 1)

def remove_accents(text):
    if not text:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def clean_texts(text_list):
    if not text_list:
        return []

    cleaned_list = []
    seen = set()

    for text in text_list:
        if not text or not isinstance(text, str):
            continue

        # 1. Filtro de textos inútiles
        texto_check = remove_accents(text.lower().strip())
        if texto_check in TEXTOS_INVALIDOS:
            continue
        if any(invalido in texto_check for invalido in TEXTOS_INVALIDOS):
            continue

        # 2. Pasar a minúsculas
        t = remove_accents(text.lower().strip())

        # 3. Eliminar puntuación y guiones bajos
        t = re.sub(r'[^\w\s]', ' ', t)
        t = t.replace("_", "")

        # 4. Limpieza de espacios extras
        t = t.strip()

        if t in seen:
            continue

        seen.add(t)

        # 5. Filtrar stopwords y palabras cortas
        words = t.split()
        filtered_words = [
            w for w in words
            if w not in STOP_WORDS and len(w) > 2
        ]

        if not filtered_words:
            continue
        
        cleaned_text = " ".join(filtered_words)
        if cleaned_text.lower() not in seen:
            cleaned_list.append(cleaned_text)
            seen.add(cleaned_text.lower())

    return cleaned_list

def preprocess_data(resultados):
    if not resultados:
        return {
            "total_resenas": 0,
            "rating_promedio": 0.0,
            "comentarios": [],
            "pros_mencionados": [],
            "contras_mencionados": []
        }

    total_resenas = len(resultados)
    rating_promedio = clean_ratings(resultados)
    
    # Extraer comentarios
    comentarios = [r.get("comentario", "").strip() 
                    for r in resultados 
                    if r.get("comentario") and r.get("comentario").strip()
                    ]
    
    # Extraer y limpiar pros/contras
    raw_pros = []
    raw_contras = []
    
    for r in resultados:
        pros = r.get("pros")
        if pros:
            if isinstance(pros, list):
                raw_pros.extend(pros)
            else:
                raw_pros.append(pros)
                
        contras = r.get("contras")
        if contras:
            if isinstance(contras, list):
                raw_contras.extend(contras)
            else:
                raw_contras.append(contras)

    # Aplicar limpieza profunda
    pros_limpios = clean_texts(raw_pros)
    contras_limpios = clean_texts(raw_contras)
    
    # Eliminar elementos que aparezcan en ambos (si un pro y contra son idénticos después de limpiar)
    # según petición "si hay pros y contras que se parecen pues se eliminan"
    intersect = set(p.lower() for p in pros_limpios) & set(c.lower() for c in contras_limpios)
    
    pros_final = [p for p in pros_limpios if p.lower() not in intersect]
    contras_final = [c for c in contras_limpios if c.lower() not in intersect]

    return {
        "total_resenas": total_resenas,
        "rating_promedio": rating_promedio,
        "comentarios": comentarios,
        "pros_mencionados": pros_final,
        "contras_mencionados": contras_final
    }
