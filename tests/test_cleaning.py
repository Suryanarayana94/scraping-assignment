import unittest
from processing.cleaning import (
    clean_text,
    normalize_text,
    clean_price,
    parse_price_numeric,
    standardize_rating,
    clean_tags,
    clean_url,
    clean_record,
)


class TestCleaning(unittest.TestCase):
    def test_clean_text_strip(self):
        self.assertEqual(clean_text("  hello  "), "hello")

    def test_normalize_text_lower(self):
        self.assertEqual(normalize_text("HELLO World "), "hello world")

    def test_clean_price_extracts_number(self):
        self.assertEqual(clean_price("£51.77"), "51.77")

    def test_parse_price_numeric(self):
        self.assertAlmostEqual(parse_price_numeric("£51.77"), 51.77)

    def test_standardize_rating(self):
        self.assertEqual(standardize_rating("Three"), "3")

    def test_clean_tags_join(self):
        self.assertEqual(clean_tags("tag1, tag2"), "tag1, tag2")

    def test_clean_record_preserves_fields(self):
        rec = {
            "source": "Books to Scrape ",
            "source_url": " https://books.toscrape.com/catalogue/book_1/index.html ",
            "name_or_title": " A Light in the Attic ",
            "category": " Poetry ",
            "price": "£51.77 ",
            "rating": " Three ",
            "author": " Author Name ",
            "tags": "",
            "description": "  Description here  ",
            "scraped_at": "2025-01-01 00:00:00",
        }
        out = clean_record(rec)
        self.assertEqual(out["name_or_title"], "A Light in the Attic")
        self.assertEqual(out["price"], "51.77")
        self.assertEqual(out["rating"], "3")


if __name__ == "__main__":
    unittest.main()
