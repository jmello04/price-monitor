from unittest.mock import MagicMock, patch

# BUG CORRIGIDO: 'pytest' estava importado mas nunca utilizado no arquivo.
# Import desnecessário removido.

from app.scraper.base import BaseScraper
from app.scraper.sites import get_scraper
from app.scraper.sites.amazon import AmazonScraper
from app.scraper.sites.mercadolivre import MercadoLivreScraper

AMAZON_HTML = b"""
<html><body>
  <span id="priceblock_ourprice">R$&#160;2.499,00</span>
</body></html>
"""

MERCADOLIVRE_HTML = b"""
<html><body>
  <span class="andes-money-amount__fraction">1899</span>
  <span class="andes-money-amount__cents">99</span>
</body></html>
"""

HTML_SEM_PRECO = b"<html><body><p>Produto indisponivel</p></body></html>"


def _mock_response(content: bytes) -> MagicMock:
    mock = MagicMock()
    mock.content = content
    mock.raise_for_status = MagicMock()
    return mock


class TestAmazonScraper:
    def test_extrai_preco_corretamente(self):
        scraper = AmazonScraper()
        with patch("requests.get", return_value=_mock_response(AMAZON_HTML)):
            price = scraper.scrape("https://www.amazon.com.br/dp/B08N5M7S6K")
        assert price == 2499.00

    def test_retorna_none_quando_sem_preco(self):
        scraper = AmazonScraper()
        with patch("requests.get", return_value=_mock_response(HTML_SEM_PRECO)):
            price = scraper.scrape("https://www.amazon.com.br/dp/invalido")
        assert price is None

    def test_retorna_none_em_erro_de_conexao(self):
        scraper = AmazonScraper()
        with patch("requests.get", side_effect=Exception("Timeout")):
            price = scraper.scrape("https://www.amazon.com.br/dp/qualquer")
        assert price is None


class TestMercadoLivreScraper:
    def test_extrai_preco_corretamente(self):
        scraper = MercadoLivreScraper()
        with patch("requests.get", return_value=_mock_response(MERCADOLIVRE_HTML)):
            price = scraper.scrape("https://www.mercadolivre.com.br/produto/123")
        assert price == 1899.99

    def test_retorna_none_quando_sem_preco(self):
        scraper = MercadoLivreScraper()
        with patch("requests.get", return_value=_mock_response(HTML_SEM_PRECO)):
            price = scraper.scrape("https://www.mercadolivre.com.br/produto/456")
        assert price is None

    def test_retorna_none_em_erro_de_conexao(self):
        scraper = MercadoLivreScraper()
        with patch("requests.get", side_effect=Exception("Timeout")):
            price = scraper.scrape("https://www.mercadolivre.com.br/produto/qualquer")
        assert price is None


class TestGetScraper:
    def test_retorna_amazon_scraper(self):
        assert isinstance(
            get_scraper("https://www.amazon.com.br/dp/B08N5M7S6K"), AmazonScraper
        )

    def test_retorna_amazon_scraper_para_amazon_us(self):
        assert isinstance(
            get_scraper("https://www.amazon.com/dp/B08N5M7S6K"), AmazonScraper
        )

    def test_retorna_mercadolivre_scraper(self):
        assert isinstance(
            get_scraper("https://produto.mercadolivre.com.br/MLB-123"),
            MercadoLivreScraper,
        )

    def test_retorna_none_para_site_desconhecido(self):
        assert get_scraper("https://www.loja-generica.com.br/produto") is None


class TestBaseScraper:
    def setup_method(self):
        class ScraperConcreto(BaseScraper):
            def scrape(self, url):
                return None

        self.scraper = ScraperConcreto()

    def test_clean_price_formato_brasileiro(self):
        assert self.scraper.clean_price("R$ 1.234,56") == 1234.56

    def test_clean_price_sem_centavos(self):
        assert self.scraper.clean_price("2.499,00") == 2499.00

    def test_clean_price_com_espaco_nao_separavel(self):
        assert self.scraper.clean_price("R$\xa02.499,00") == 2499.00

    def test_clean_price_valor_simples(self):
        assert self.scraper.clean_price("99,90") == 99.90

    def test_clean_price_texto_invalido_retorna_none(self):
        assert self.scraper.clean_price("Indisponivel") is None

    def test_clean_price_string_vazia_retorna_none(self):
        assert self.scraper.clean_price("") is None
