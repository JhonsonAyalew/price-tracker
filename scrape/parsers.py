from __future__ import annotations
import re
from datetime import datetime, timezone

_CURRENCY_MAP = {
    "$": "USD",
    "£": "GBP",
    "€": "EUR",
}

PRICE_RE = re.compile(r"([£$€])\s*([0-9]+(?:\.[0-9]{1,2})?)")

def parse_price(text: str) -> tuple[float, str]:
    """Extract numeric price and ISO currency code from a string."""
    m = PRICE_RE.search(text)
    if not m:
        digits = re.findall(r"[0-9]+(?:\.[0-9]{1,2})?", text)
        if not digits:
            raise ValueError(f"Cannot parse price from: {text!r}")
        return float(digits[0]), "USD"
    symbol, amount = m.groups()
    return float(amount), _CURRENCY_MAP.get(symbol, "USD")

def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
