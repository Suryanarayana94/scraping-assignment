# Multi-Source Web Scraping & Data Consolidation

## Assignment Overview
A Python-based pipeline that collects data from `books.toscrape.com` and `quotes.toscrape.com`, cleans and standardizes records, detects duplicates, validates data, and produces a consolidated CSV with a summary report.

## Python Version
Python 3.9+

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Dependencies
- requests
- beautifulsoup4

## How to Run
```bash
python main.py
```

### CLI Arguments (optional)
You can modify `max_pages` and `delay` directly in `main.py` or extend `main.py` with `argparse`.

## How Pagination Works
Each scraper follows the `li.next a` link on every page until no next page exists. This avoids hard-coding URLs and works even if the site grows.

## Data Model
All records are normalized to a common schema:

| Field | Description |
|---|---|
| source | Name of the source website |
| source_url | Original product/quote page URL |
| name_or_title | Book title or quote text |
| category | Book category (empty for quotes) |
| price | Book price as numeric string (empty for quotes) |
| rating | Numeric rating 1–5 (empty for quotes) |
| author | Author name |
| tags | Comma-separated tags (quotes) |
| description | Book product description (empty for quotes) |
| scraped_at | Timestamp of scrape |

## Cleaning Approach
- Strip leading/trailing whitespace from all text fields.
- Extract numeric price values using regex.
- Map word-based ratings (One–Five) to integers 1–5.
- Join and deduplicate tags.
- Normalize missing values to empty strings.

## Validation Approach
A record must have a non-empty `name_or_title` and a `source_url` that starts with `http://` or `https://`. Prices are warned if non-numeric; ratings are warned if outside 1–5.

## Deduplication Approach
Records are considered duplicates if their `(source, name_or_title, author, source_url)` tuple matches after lowercasing and trimming. This handles differences in whitespace, capitalization, and formatting.

## Error Handling & Logging
- HTTP errors and connection failures are caught per page; the scraper continues.
- Missing HTML elements are handled with `None` checks.
- All actions are logged to `logs/pipeline.log` and printed to stdout.

## Output
- `output/final_dataset.csv`
- `output/summary_report.json`

## Assumptions
- Both practice sites remain publicly accessible without authentication.
- Pagination uses the visible "next" link on each page.
- Author names on `books.toscrape.com` are extracted from the product page table when available.

## Known Limitations
- No retry/backoff implemented.
- No rate limiting beyond a fixed delay.
- No incremental scraping or checkpointing.
- Author extraction for books may be empty if the site markup changes.

## AI Usage Summary
See `AI_USAGE.md`.
