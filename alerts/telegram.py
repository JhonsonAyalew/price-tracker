import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(text: str):
    """Send a plain text message to the configured chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured. Skipping alert.")
        return
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"Telegram error: {e} - response: {getattr(r, 'text', None)}")

def notify_drop(product: dict, old_price: float, new_price: float, drop_pct: float):
    """Send a price drop notification."""
    message = (
        f"📉 Price Drop Alert!\n\n"
        f"🛒 {product['name']}\n"
        f"💰 {old_price:.2f} → {new_price:.2f}  (-{drop_pct:.1f}%)\n\n"
        f"🔗 {product['url']}"
    )
    send_message(message)
