from __future__ import annotations
import random
import time
import requests
from bs4 import BeautifulSoup
from config import USER_AGENTS, DEFAULT_TIMEOUT, PROXY
from scrape.parsers import parse_price

BASE = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"

def fetch_products() -> list[dict]:
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    proxies = {"http": PROXY, "https": PROXY} if PROXY else None
    resp = requests.get(BASE, headers=headers, timeout=DEFAULT_TIMEOUT, proxies=proxies)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    products: list[dict] = []
    for card in soup.select("div.thumbnail"):
        title_el = card.select_one("a.title")
        if not title_el:
            continue
        name = title_el.get_text(strip=True)
        url = "https://webscraper.io" + title_el.get("href")
        price_text = card.select_one("h4.pull-right.price").get_text(strip=True)
        price, currency = parse_price(price_text)
        desc = card.select_one("p.description").get_text(strip=True) if card.select_one("p.description") else ""
        products.append({
            "name": name,
            "price": price,
            "currency": currency,
            "url": url,
            "in_stock": True,
            "source": "webscraper_laptops",
            "description": desc,
        })
    time.sleep(1.0)
    return products
