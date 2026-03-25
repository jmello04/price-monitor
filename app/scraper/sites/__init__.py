from typing import Optional

from app.scraper.base import BaseScraper
from app.scraper.sites.amazon import AmazonScraper
from app.scraper.sites.mercadolivre import MercadoLivreScraper

_AMAZON_DOMAINS = ("amazon.com.br", "amazon.com")
_MERCADOLIVRE_DOMAINS = ("mercadolivre.com.br", "mercadolibre.com")


def get_scraper(url: str) -> Optional[BaseScraper]:
    url_lower = url.lower()

    if any(domain in url_lower for domain in _AMAZON_DOMAINS):
        return AmazonScraper()

    if any(domain in url_lower for domain in _MERCADOLIVRE_DOMAINS):
        return MercadoLivreScraper()

    return None
