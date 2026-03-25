import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

from app.scraper.base import BaseScraper

logger = logging.getLogger(__name__)

FRACTION_SELECTORS = [
    ".ui-pdp-price__second-line .andes-money-amount__fraction",
    ".andes-money-amount__fraction",
    ".price-tag-fraction",
]

CENTS_SELECTORS = [
    ".andes-money-amount__cents",
    ".price-tag-cents",
]


class MercadoLivreScraper(BaseScraper):
    def scrape(self, url: str) -> Optional[float]:
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")

            fraction_text: Optional[str] = None
            for selector in FRACTION_SELECTORS:
                element = soup.select_one(selector)
                if element:
                    fraction_text = element.get_text(strip=True)
                    break

            if not fraction_text:
                logger.warning(
                    "Nenhum seletor encontrou o preço no Mercado Livre para: %s", url
                )
                return None

            cents_text = "00"
            for selector in CENTS_SELECTORS:
                element = soup.select_one(selector)
                if element:
                    cents_text = element.get_text(strip=True).zfill(2)
                    break

            price_text = f"{fraction_text},{cents_text}"
            price = self.clean_price(price_text)

            if price:
                logger.info("Preço extraído do Mercado Livre: R$ %.2f", price)
            return price

        except requests.RequestException as exc:
            logger.error("Erro de requisição ao acessar Mercado Livre: %s", exc)
            return None
        except Exception as exc:
            logger.error("Erro inesperado ao fazer scraping do Mercado Livre: %s", exc)
            return None
