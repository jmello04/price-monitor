"""Abstract base class for all e-commerce price scrapers."""

import re
from abc import ABC, abstractmethod
from typing import Optional


class BaseScraper(ABC):
    """Common interface and utilities shared by all site-specific scrapers.

    Subclasses must implement :meth:`scrape` to extract the current price
    from a given product page URL.

    Attributes:
        HEADERS: HTTP request headers that mimic a standard browser session
                 to reduce the likelihood of being blocked by anti-bot measures.
    """

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
        """Extract the current price from a product page.

        Args:
            url: Full URL of the product page to scrape.

        Returns:
            Parsed price as a float, or None if extraction failed.
        """
        raise NotImplementedError

    def clean_price(self, price_text: str) -> Optional[float]:
        """Normalise a raw price string into a float value.

        Removes currency symbols, whitespace and non-breaking spaces, then
        converts Brazilian decimal notation (comma as separator) to the
        standard floating-point representation.

        Args:
            price_text: Raw price string extracted from the HTML, e.g. "R$ 1.299,90".

        Returns:
            Positive float price value, or None if parsing fails.
        """
        cleaned = re.sub(r"[R$\s\xa0]", "", price_text)
        cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            value = float(cleaned)
            return value if value > 0 else None
        except (ValueError, AttributeError):
            return None
