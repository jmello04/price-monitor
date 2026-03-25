import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

from app.scraper.base import BaseScraper

logger = logging.getLogger(__name__)

PRICE_SELECTORS = [
    "#priceblock_ourprice",
    "#priceblock_dealprice",
    "#apex_offerDisplay_desktop .a-price .a-offscreen",
    ".reinventPricePriceToPayMargin .a-offscreen",
    "#corePrice_feature_div .a-offscreen",
    ".a-price .a-offscreen",
    ".a-price-whole",
]


class AmazonScraper(BaseScraper):
    def scrape(self, url: str) -> Optional[float]:
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")

            for selector in PRICE_SELECTORS:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True)
                    price = self.clean_price(price_text)
                    if price:
                        logger.info(
                            "Preço extraído da Amazon: R$ %.2f (seletor: %s)",
                            price,
                            selector,
                        )
                        return price

            logger.warning("Nenhum seletor encontrou o preço na Amazon para: %s", url)
            return None

        except requests.RequestException as exc:
            logger.error("Erro de requisição ao acessar Amazon: %s", exc)
            return None
        except Exception as exc:
            logger.error("Erro inesperado ao fazer scraping da Amazon: %s", exc)
            return None
