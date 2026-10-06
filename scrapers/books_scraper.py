import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import re

logger = logging.getLogger(__name__)

BASE_URL = "https://books.toscrape.com/"


@dataclass
class BookRecord:
    source: str = "Books to Scrape"
    source_url: str = ""
    name_or_title: str = ""
    category: str = ""
    price: str = ""
    rating: str = ""
    author: str = ""
    tags: str = ""
    description: str = ""
    scraped_at: str = ""


class BooksScraper:
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

    def _parse_book(self, article, page_url: str) -> Optional[BookRecord]:
        try:
            title_tag = article.select_one("h3 a")
            if not title_tag:
                return None
            title = title_tag.get_text(strip=True)
            relative_url = title_tag.get("href", "")
            product_url = urljoin(page_url, relative_url)

            price_text = ""
            price_tag = article.select_one(".price_color")
            if price_tag:
                price_text = price_tag.get_text(strip=True)

            rating = ""
            star_tag = article.select_one(".star-rating")
            if star_tag:
                classes = star_tag.get("class", [])
                rating_class = [c for c in classes if c != "star-rating"]
                if rating_class:
                    rating = rating_class[0]

            category = ""
            breadcrumb = article.select_one(".breadcrumb")
            if breadcrumb:
                links = breadcrumb.select("a")
                if len(links) >= 2:
                    category = links[-1].get_text(strip=True)

            description = ""
            product_page = self._get(product_url)
            if product_page:
                time.sleep(self.delay)
                desc_heading = product_page.find("h2", text="Product Description")
                if desc_heading:
                    desc_p = desc_heading.find_next("p")
                    if desc_p:
                        description = desc_p.get_text(strip=True)

                author_tag = product_page.select_one("#product_description ~ .product_main h2")
                author = ""
                for th in product_page.select("table tr th"):
                    if th.get_text(strip=True) == "Author":
                        author = th.find_next("td").get_text(strip=True) if th.find_next("td") else ""

            return BookRecord(
                source_url=product_url,
                name_or_title=title,
                category=category,
                price=price_text,
                rating=rating,
                author=author,
                description=description,
                scraped_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception as e:
            logger.error("Error parsing book on %s: %s", page_url, e)
            return None

    def scrape_page(self, page_url: str) -> List[BookRecord]:
        logger.info("Scraping page: %s", page_url)
        soup = self._get(page_url)
        if not soup:
            return []
        time.sleep(self.delay)

        records = []
        articles = soup.select("article.product_pod")
        if not articles:
            logger.warning("No books found on %s", page_url)
            return []

        for article in articles:
            record = self._parse_book(article, page_url)
            if record:
                records.append(record)

        return records

    def scrape(self, max_pages: Optional[int] = None) -> List[BookRecord]:
        all_records: List[BookRecord] = []
        current_url = BASE_URL
        page_num = 1

        while current_url:
            if max_pages and page_num > max_pages:
                break

            records = self.scrape_page(current_url)
            all_records.extend(records)
            logger.info("Page %d: collected %d books", page_num, len(records))

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

        logger.info("Books scraping complete. Total: %d", len(all_records))
        return all_records

    def to_dicts(self, records: List[BookRecord]) -> List[dict]:
        return [asdict(r) for r in records]
