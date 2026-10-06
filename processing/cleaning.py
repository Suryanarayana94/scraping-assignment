import re
from decimal import Decimal, InvalidOperation


def clean_text(value: str) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_text(value: str) -> str:
    return clean_text(value).lower()


def clean_price(value: str) -> str:
    if value is None:
        return ""
    value = clean_text(value)
    match = re.search(r"[\d]+(?:\.[\d]+)?", value.replace(",", ""))
    if match:
        return match.group(0)
    return ""


def parse_price_numeric(value: str):
    cleaned = clean_price(value)
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except (ValueError, InvalidOperation):
        return None


RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def standardize_rating(value: str) -> str:
    if value is None:
        return ""
    value = clean_text(value).lower()
    return str(RATING_MAP.get(value, ""))


def clean_tags(value: str) -> str:
    if value is None:
        return ""
    tags = [t.strip() for t in str(value).split(",") if t.strip()]
    return ", ".join(tags)


def clean_url(value: str) -> str:
    if value is None:
        return ""
    return clean_text(value)


def normalize_missing(value: str) -> str:
    if value is None:
        return ""
    return value


def clean_record(record: dict) -> dict:
    cleaned = {}
    cleaned["source"] = normalize_missing(record.get("source", ""))
    cleaned["source_url"] = clean_url(record.get("source_url", ""))
    cleaned["name_or_title"] = clean_text(record.get("name_or_title", ""))
    cleaned["category"] = clean_text(record.get("category", ""))
    cleaned["price"] = clean_price(record.get("price", ""))
    cleaned["rating"] = standardize_rating(record.get("rating", ""))
    cleaned["author"] = clean_text(record.get("author", ""))
    cleaned["tags"] = clean_tags(record.get("tags", ""))
    cleaned["description"] = clean_text(record.get("description", ""))
    cleaned["scraped_at"] = clean_text(record.get("scraped_at", ""))
    return cleaned
