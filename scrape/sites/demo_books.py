import sqlite3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

base_url = "http://books.toscrape.com/catalogue/"
page_url = base_url + "page-1.html"
response = requests.get(page_url)
soup = BeautifulSoup(response.text, "html.parser")

for book in soup.select(".product_pod"):
    name = book.h3.a["title"]
    price_text = book.select_one(".price_color").text
    price = float(price_text.replace("£", "").replace("Â", ""))
    created_at = datetime.now().isoformat()

    book_rel_url = book.h3.a["href"]
    book_url = base_url + book_rel_url

    # Insert new product or update existing
    cursor.execute("SELECT id FROM products WHERE url=?", (book_url,))
    row = cursor.fetchone()
    if row:
        product_id = row[0]
        cursor.execute(
            "UPDATE products SET price=?, created_at=? WHERE id=?",
            (price, created_at, product_id)
        )
    else:
        cursor.execute(
            "INSERT INTO products (name, url, source, price, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, book_url, "books.toscrape.com", price, created_at)
        )
        product_id = cursor.lastrowid

    # Insert into price_history
    cursor.execute(
        "INSERT INTO price_history (product_id, price) VALUES (?, ?)",
        (product_id, price)
    )

conn.commit()
conn.close()
print("Scraping complete, prices saved!")
