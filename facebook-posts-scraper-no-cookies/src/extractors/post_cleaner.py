thonimport re
from typing import Any, Dict

def normalize_whitespace(text: str) -> str:
    """
    Collapse all runs of whitespace into a single space and trim.
    """
    return re.sub(r"\s+", " ", text or "").strip()

def clean_post_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform lightweight normalization and sanitization on a scraped post record.
    """
    cleaned: Dict[str, Any] = dict(raw)

    # Normalize text fields
    for key in ("pageName", "text", "link", "url", "facebookUrl", "time"):
        if key in cleaned and isinstance(cleaned[key], str):
            cleaned[key] = normalize_whitespace(cleaned[key])

    # Coerce numeric fields if they look like numbers
    for key in ("likes", "comments", "shares", "timestamp"):
        value = cleaned.get(key)
        if value is None:
            continue
        if isinstance(value, (int, float)):
            continue
        if isinstance(value, str):
            num = _parse_int_safely(value)
            cleaned[key] = num

    # Ensure likes/comments/shares are either int or None
    for key in ("likes", "comments", "shares"):
        value = cleaned.get(key)
        if not isinstance(value, int):
            cleaned[key] = None

    return cleaned

def _parse_int_safely(value: str) -> int:
    value = value.replace(",", "").strip()
    # Handle formats like "1.2K" or "3.4M"
    suffix_multiplier = 1
    if value.lower().endswith("k"):
        suffix_multiplier = 1_000
        value = value[:-1]
    elif value.lower().endswith("m"):
        suffix_multiplier = 1_000_000
        value = value[:-1]

    try:
        return int(float(value) * suffix_multiplier)
    except ValueError:
        return 0