import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.preprocessor import clean_ratings, remove_accents, clean_texts, preprocess_data

class TestAnalysis(unittest.TestCase):

    def test_clean_ratings(self):
        # Caso 1: Ratings con "/"
        self.assertEqual(clean_ratings([{"rating": "4/5"}]), 4.0)
        self.assertEqual(clean_ratings([{"rating": "5/5"}]), 5.0)
        self.assertEqual(clean_ratings([{"rating": "0/5"}]), 0.0)
        
        # Caso 2: Ratings numéricos (0-5)
        self.assertEqual(clean_ratings([{"rating": 4.5}]), 4.5)
        self.assertEqual(clean_ratings([{"rating": "3"}]), 3.0)
        
        # Caso 3: Ratings numéricos (>5, asumiendo escala 10)
        self.assertEqual(clean_ratings([{"rating": 9}]), 4.5)
        self.assertEqual(clean_ratings([{"rating": "8.0"}]), 4.0)
        
        # Caso 4: Varios ratings (promedio)
        self.assertEqual(clean_ratings([{"rating": "4/5"}, {"rating": 5}, {"rating": 3}]), 4.0)
        
        # Caso 5: Casos inválidos
        self.assertEqual(clean_ratings([{"rating": None}]), 0.0)
        self.assertEqual(clean_ratings([{"rating": "invalid"}]), 0.0)
        self.assertEqual(clean_ratings([]), 0.0)

    def test_remove_accents(self):
        self.assertEqual(remove_accents("camión"), "camion")
        self.assertEqual(remove_accents("Árbol"), "Arbol")
        self.assertEqual(remove_accents("pingüino"), "pinguino")
        self.assertEqual(remove_accents(""), "")
        self.assertEqual(remove_accents(None), "")

    def test_clean_texts(self):
        # Caso 1: Stopwords y minúsculas
        texts = ["El producto es muy bueno"]
        self.assertEqual(clean_texts(texts), ["producto bueno"])
        
        # Caso 2: Textos inválidos
        texts = ["nada", "todo ok", "Buen producto"]
        self.assertEqual(clean_texts(texts), ["buen producto"])
        
        # Caso 3: Duplicados
        texts = ["Excelente", "Excelente", "muy bueno"]
        self.assertEqual(clean_texts(texts), ["excelente", "bueno"])
        
        # Caso 4: Puntuación
        texts = ["¡Increíble! ¿verdad?"]
        self.assertEqual(clean_texts(texts), ["increible verdad"])

    def test_preprocess_data(self):
        data = [
            {"rating": "4/5", "comentario": "Me gusta", "pros": ["Rápido"], "contras": ["Caro"]},
            {"rating": 5, "comentario": "Excelente", "pros": "Bonito", "contras": None},
            {"rating": None, "comentario": "", "pros": [], "contras": ["nada"]}
        ]
        result = preprocess_data(data)
        
        self.assertEqual(result["total_resenas"], 3)
        self.assertEqual(result["rating_promedio"], 4.5)
        self.assertEqual(len(result["comentarios"]), 2)
        self.assertIn("Me gusta", result["comentarios"])
        self.assertIn("rapido", result["pros_mencionados"])
        self.assertIn("bonito", result["pros_mencionados"])
        self.assertIn("caro", result["contras_mencionados"])
        # "nada" debería ser filtrado
        self.assertNotIn("nada", result["contras_mencionados"])

if __name__ == "__main__":
    unittest.main()
