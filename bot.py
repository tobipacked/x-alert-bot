import os
import json
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARNING] Telegram credentials missing, skipping alert.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")

def run():
    print("Checking for new #buyingcontent posts...")
    
    seen_ids = set()
    if os.path.exists("seen_ids.json") and os.path.getsize("seen_ids.json") > 0:
        try:
            with open("seen_ids.json", "r", encoding="utf-8") as f:
                seen_ids = set(json.load(f))
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context_kwargs = {}
        if os.path.exists("storage_state.json"):
            context_kwargs["storage_state"] = "storage_state.json"
        else:
            print("[WARNING] No storage_state.json found — running logged out.")

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        search_url = "https://x.com/search?q=%23buyingcontent&f=live"
        
        try:
            page.goto(search_url, wait_until="domcontentloaded")
            page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
            
            tweets = page.query_selector_all('article[data-testid="tweet"]')
            for tweet in tweets:
                # Extract and process tweet logic
                pass
                
        except Exception as e:
            print(f"[WARNING] Could not load results this run: {e}")
            print(f"[DEBUG] Page title was: {page.title()}")
            print(f"[DEBUG] Current URL was: {page.url()}")
            page.screenshot(path="debug_screenshot.png")
            
        browser.close()

if __name__ == "__main__":
    run()
