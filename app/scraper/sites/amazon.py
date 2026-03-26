"""Price scraper for Amazon Brasil product pages."""

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
    """Scraper for Amazon Brasil (amazon.com.br) product pages.

    Iterates through a prioritised list of CSS selectors to locate the
    displayed price, handling layout variations across different product types.
    """

    def scrape(self, url: str) -> Optional[float]:
        """Extract the current price from an Amazon product page.

        Args:
            url: Full URL of the Amazon product page.

        Returns:
            Price as a float in BRL, or None if extraction failed.
        """
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
                            "Price extracted from Amazon: R$ %.2f (selector: %s)",
                            price,
                            selector,
                        )
                        return price

            logger.warning("No selector matched a price on Amazon for: %s", url)
            return None

        except requests.RequestException as exc:
            logger.error("Request error while accessing Amazon: %s", exc)
            return None
