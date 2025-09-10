import sqlite3
from scrape.sites.demo_books import scrape_books
from config import DB_PATH, PRICE_DROP_THRESHOLD
from alerts.telegram import send_telegram_alert

def run_scrapers():
    # 1️⃣ Scrape demo books
    scrape_books()

    # 2️⃣ Check for price drops
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    products = cursor.fetchall()
    
    for product_id, name, price in products:
        # Simple example: check if price < threshold (for demo purposes)
        if price < PRICE_DROP_THRESHOLD:
            send_telegram_alert(f"📉 Price drop alert: {name} is now £{price}")

    conn.close()

if __name__ == "__main__":
    run_scrapers()
