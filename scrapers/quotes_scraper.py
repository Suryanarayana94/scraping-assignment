import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin
from dataclasses import dataclass, field, asdict
from typing import List, Optional

logger = logging.getLogger(__name__)

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class QuoteRecord:
    source: str = "Quotes to Scrape"
    source_url: str = ""
    name_or_title: str = ""
    category: str = ""
    price: str = ""
    rating: str = ""
    author: str = ""
    tags: str = ""
    description: str = ""
    scraped_at: str = ""


class QuotesScraper:
    def __init__(self, delay: float = 1.0, timeout: int = 15):
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; Scraper/1.0; +https://example.com)"
        })

    def _get(self, url: str) -> Optional[BeautifulSoup]:
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as e:
            logger.error("Failed to fetch %s: %s", url, e)
            return None

    def _parse_quote(self, div, page_url: str) -> Optional[QuoteRecord]:
        try:
            text_span = div.select_one(".text")
            title = text_span.get_text(strip=True) if text_span else ""

            author_tag = div.select_one(".author")
            author = author_tag.get_text(strip=True) if author_tag else ""

            tag_elements = div.select(".tags .tag")
            tags = ", ".join(t.get_text(strip=True) for t in tag_elements)

            source_url = page_url

            return QuoteRecord(
                source_url=source_url,
                name_or_title=title,
                author=author,
                tags=tags,
                scraped_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception as e:
            logger.error("Error parsing quote on %s: %s", page_url, e)
            return None

    def scrape_page(self, page_url: str) -> List[QuoteRecord]:
        logger.info("Scraping page: %s", page_url)
        soup = self._get(page_url)
        if not soup:
            return []
        time.sleep(self.delay)

        records = []
        quote_divs = soup.select(".quote")
        if not quote_divs:
            logger.warning("No quotes found on %s", page_url)
            return []

        for div in quote_divs:
            record = self._parse_quote(div, page_url)
            if record:
                records.append(record)

        return records

    def scrape(self, max_pages: Optional[int] = None) -> List[QuoteRecord]:
        all_records: List[QuoteRecord] = []
        current_url = BASE_URL
        page_num = 1

        while current_url:
            if max_pages and page_num > max_pages:
                break

            records = self.scrape_page(current_url)
            all_records.extend(records)
            logger.info("Page %d: collected %d quotes", page_num, len(records))

            soup = self._get(current_url)
            if not soup:
                break
            time.sleep(self.delay)

            next_link = soup.select_one("li.next a")
            if next_link and next_link.get("href"):
                next_href = next_link.get("href")
                current_url = urljoin(current_url, next_href)
                page_num += 1
            else:
                break

        logger.info("Quotes scraping complete. Total: %d", len(all_records))
        return all_records

    def to_dicts(self, records: List[QuoteRecord]) -> List[dict]:
        return [asdict(r) for r in records]
