import re
from typing import Dict, List, Tuple
from . import cleaning


class ValidationResult:
    def __init__(self):
        self.valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, msg: str):
        self.errors.append(msg)
        self.valid = False

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def to_dict(self):
        return {"valid": self.valid, "errors": self.errors, "warnings": self.warnings}


def validate_record(record: dict) -> ValidationResult:
    result = ValidationResult()
    source = record.get("source", "").strip()
    title = record.get("name_or_title", "").strip()
    url = record.get("source_url", "").strip()

    if not source:
        result.add_warning("Missing source")

    if not title:
        result.add_error("Missing name_or_title")

    if not url:
        result.add_error("Missing source_url")
    else:
        if not re.match(r"^https?://", url):
            result.add_error("source_url does not look like a valid URL")

    price = record.get("price", "")
    if price:
        if not cleaning.parse_price_numeric(price):
            result.add_warning("Price present but not numeric: {}".format(price))

    rating = record.get("rating", "")
    if rating:
        try:
            r = int(rating)
            if r < 1 or r > 5:
                result.add_warning("Rating out of expected range 1-5: {}".format(rating))
        except (ValueError, TypeError):
            result.add_warning("Rating is not an integer: {}".format(rating))

    return result


def validate_dataset(records: List[dict]) -> Tuple[List[dict], List[dict], Dict]:
    valid_records: List[dict] = []
    rejected_records: List[dict] = []
    summary = {"total": len(records), "valid": 0, "rejected": 0}

    for record in records:
        result = validate_record(record)
        record["_validation"] = result.to_dict()
        if result.valid:
            valid_records.append(record)
        else:
            rejected_records.append(record)

    summary["valid"] = len(valid_records)
    summary["rejected"] = len(rejected_records)
    return valid_records, rejected_records, summary
