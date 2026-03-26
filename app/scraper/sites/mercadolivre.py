"""Price scraper for Mercado Livre product pages."""

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
    """Scraper for Mercado Livre (mercadolivre.com.br) product pages.

    Separately extracts the integer and decimal parts of the displayed price
    to handle Mercado Livre's split price rendering pattern.
    """

    def scrape(self, url: str) -> Optional[float]:
        """Extract the current price from a Mercado Livre product page.

        Args:
            url: Full URL of the Mercado Livre product page.

        Returns:
            Price as a float in BRL, or None if extraction failed.
        """
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
                    "No selector matched a price on Mercado Livre for: %s", url
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
                logger.info("Price extracted from Mercado Livre: R$ %.2f", price)
            return price

        except requests.RequestException as exc:
            logger.error("Request error while accessing Mercado Livre: %s", exc)
            return None
