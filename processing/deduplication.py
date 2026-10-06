from typing import List, Dict, Tuple, Set
from collections import defaultdict


def _dedup_key(record: dict) -> tuple:
    source = record.get("source", "").strip().lower()
    title = record.get("name_or_title", "").strip().lower()
    author = record.get("author", "").strip().lower()
    url = record.get("source_url", "").strip().lower()
    return (source, title, author, url)


def deduplicate(records: List[dict]) -> Tuple[List[dict], List[dict], Dict]:
    seen: Set[tuple] = set()
    unique: List[dict] = []
    duplicates: List[dict] = []
    stats: Dict = {"total": len(records), "duplicates_removed": 0}

    for record in records:
        key = _dedup_key(record)
        if key in seen:
            duplicates.append(record)
        else:
            seen.add(key)
            unique.append(record)

    stats["duplicates_removed"] = len(duplicates)
    return unique, duplicates, stats
