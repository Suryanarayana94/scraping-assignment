# AI_USAGE.md

## AI Tools Used
- ChatGPT (free web interface)

## Usage Breakdown
- **Understanding page structure:** ChatGPT helped me inspect the HTML structure of `books.toscrape.com` and `quotes.toscrape.com` and identify stable CSS selectors.
- **Initial code scaffolding:** ChatGPT generated the initial `dataclass` definitions and scraper method stubs.
- **Pagination logic:** ChatGPT suggested following the `li.next a` link as a robust pagination approach.
- **Debugging selector issues:** ChatGPT helped fix a few broken selectors after verifying against the live sites.
- **Reviewing deduplication logic:** ChatGPT reviewed my deduplication strategy and confirmed the tuple-based approach.
- **README and documentation:** ChatGPT assisted in drafting the README sections.

## Representative Prompts
1. "What CSS selectors should I use to extract book titles and prices from books.toscrape.com?"
2. "How can I detect pagination on quotes.toscrape.com?"
3. "Is a tuple-based deduplication strategy on (source, title, author, url) sufficient for this assignment?"
4. "How should I structure a Python project for a web scraping assignment with scrapers and processing modules?"

## AI-Assisted Code Parts
- CSS selectors in `books_scraper.py` and `quotes_scraper.py`
- Pagination loop structure
- Deduplication key tuple design

## Important Changes After Reviewing AI Output
- Fixed an incorrect author extraction selector on `books.toscrape.com` product pages by inspecting the actual HTML.
- Removed an over-engineered retry mechanism to keep the code simple and focused on assignment requirements.
- Changed initial duplicate-detection plan (which used only title) to the more robust (source, title, author, url) tuple.

## Incorrect or Incomplete AI Suggestions
- ChatGPT initially suggested using `response.encoding = "utf-8"` after fetching, which is unnecessary here because `requests` detects encoding well for these sites.
- An early AI suggestion proposed using Scrapy; I switched to Requests + BeautifulSoup to match the simpler requirements and ease of reproducibility.

## Testing & Verification
- Ran the full pipeline locally against both live sites.
- Verified pagination by checking that all 50 pages of quotes were traversed.
- Manually spot-checked several records in `output/final_dataset.csv`.
- Ran `python -m unittest` and confirmed all cleaning tests pass.
