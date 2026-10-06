import time
import logging
import json
import csv
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict

from scrapers.books_scraper import BooksScraper, BASE_URL as BOOKS_BASE
from scrapers.quotes_scraper import QuotesScraper
from processing.cleaning import clean_record
from processing.validation import validate_dataset
from processing.deduplication import deduplicate


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"


def setup_logging():
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / "pipeline.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def write_csv(records, path: Path):
    if not records:
        return
    fieldnames = [
        "source",
        "source_url",
        "name_or_title",
        "category",
        "price",
        "rating",
        "author",
        "tags",
        "description",
        "scraped_at",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def write_summary(summary: dict, path: Path):
    with path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


def run(max_pages: int = None, delay: float = 1.0):
    start = time.time()
    setup_logging()
    logger = logging.getLogger("pipeline")

    OUTPUT_DIR.mkdir(exist_ok=True)
    summary = {
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sources": {},
        "cleaning": {},
        "validation": {},
        "deduplication": {},
        "final_count": 0,
        "elapsed_seconds": 0,
    }

    logger.info("Pipeline started")

    books_scraper = BooksScraper(delay=delay)
    quotes_scraper = QuotesScraper(delay=delay)

    raw_books = books_scraper.to_dicts(books_scraper.scrape(max_pages=max_pages))
    raw_quotes = quotes_scraper.to_dicts(quotes_scraper.scrape(max_pages=max_pages))

    summary["sources"] = {
        "books_raw": len(raw_books),
        "quotes_raw": len(raw_quotes),
        "total_raw": len(raw_books) + len(raw_quotes),
    }

    raw = raw_books + raw_quotes
    logger.info("Raw records: %d", len(raw))

    cleaned = [clean_record(r) for r in raw]
    summary["cleaning"] = {"records_after_cleaning": len(cleaned)}
    logger.info("Records after cleaning: %d", len(cleaned))

    valid, rejected, val_summary = validate_dataset(cleaned)
    summary["validation"] = val_summary
    logger.info("Valid: %d, Rejected: %d", val_summary["valid"], val_summary["rejected"])

    unique, duplicates, dedup_summary = deduplicate(valid)
    summary["deduplication"] = dedup_summary
    logger.info("Duplicates removed: %d", dedup_summary["duplicates_removed"])

    final_path = OUTPUT_DIR / "final_dataset.csv"
    write_csv(unique, final_path)

    summary["final_count"] = len(unique)
    summary["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    summary["elapsed_seconds"] = round(time.time() - start, 2)

    summary_path = OUTPUT_DIR / "summary_report.json"
    write_summary(summary, summary_path)

    logger.info("Pipeline complete. Final records: %d. Output: %s", len(unique), final_path)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Source Scraping Pipeline")
    parser.add_argument("--max-pages", type=int, default=None, help="Max pages to scrape per source")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")
    args = parser.parse_args()
    run(max_pages=args.max_pages, delay=args.delay)
