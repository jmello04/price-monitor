import re
from abc import ABC, abstractmethod
from typing import Optional


class BaseScraper(ABC):
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    @abstractmethod
    def scrape(self, url: str) -> Optional[float]:
        raise NotImplementedError

    def clean_price(self, price_text: str) -> Optional[float]:
        cleaned = re.sub(r"[R$\s\xa0]", "", price_text)
        cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            value = float(cleaned)
            return value if value > 0 else None
        except (ValueError, AttributeError):
            return None
