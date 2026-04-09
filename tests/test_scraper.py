import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraping.scraper import optimizar_url_segun_config, SITE_CONFIGS

class TestScraper(unittest.TestCase):

    def test_optimizar_url_segun_config_decathlon(self):
        url = "https://www.decathlon.es/es/p/zapatillas-running-adidas-runblaze-hombre-negro/361354/c1m8929086"
        config = SITE_CONFIGS["decathlon.es"]
        optimized_url = optimizar_url_segun_config(url, config)
        self.assertEqual(optimized_url, "https://www.decathlon.es/es/r/zapatillas-running-adidas-runblaze-hombre-negro/361354/c1m8929086")

    def test_optimizar_url_segun_config_pccomponentes(self):
        url = "https://www.pccomponentes.com/tarjeta-grafica-asus-prime-geforce-rtx-5060-oc-edition-8gb-gddr7"
        config = SITE_CONFIGS["pccomponentes.com"]
        optimized_url = optimizar_url_segun_config(url, config)
        # En PCComponentes inserta "opiniones/" después de "pccomponentes.com/"
        self.assertEqual(optimized_url, "https://www.pccomponentes.com/opiniones/tarjeta-grafica-asus-prime-geforce-rtx-5060-oc-edition-8gb-gddr7")

    def test_optimizar_url_no_config(self):
        url = "https://example.com/product"
        config = {}
        optimized_url = optimizar_url_segun_config(url, config)
        self.assertEqual(optimized_url, url)

    @patch('undetected_chromedriver.Chrome')
    @patch('scraping.scraper_utils.paginar')
    @patch('scraping.scraper_utils.get_domain')
    def test_scrape_opiniones_mock(self, mock_get_domain, mock_paginar, mock_chrome):
        # Configuración de mocks
        mock_get_domain.return_value = "mediamarkt.es"
        mock_paginar.return_value = [{"rating": 5, "comentario": "Genial"}]
        
        # Simular el driver
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        from scraping.scraper import scrape_opiniones
        
        url = "https://www.mediamarkt.es/es/product/iphone-17.html"
        result = scrape_opiniones(url)
        
        # Verificaciones
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["rating"], 5)
        mock_chrome.assert_called_once()
        mock_driver.get.assert_called()
        mock_driver.quit.assert_called_once()

if __name__ == "__main__":
    unittest.main()
