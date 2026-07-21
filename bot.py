import json
import os
import sys

import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
HASHTAG_URL = "https://x.com/search?q=%23buyingcontent&f=live"
SEEN_IDS_FILE = "seen_ids.json"
MAX_SEEN_IDS = 500  # cap file size so it doesn't grow forever


def load_seen_ids():
    if os.path.exists(SEEN_IDS_FILE):
        try:
            with open(SEEN_IDS_FILE, "r") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARNING] Could not read {SEEN_IDS_FILE}: {e}")
    return set()


def save_seen_ids(seen_ids):
    trimmed = list(seen_ids)[-MAX_SEEN_IDS:]
    with open(SEEN_IDS_FILE, "w") as f:
        json.dump(trimmed, f)


def send_telegram_alert(tweet_url):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID env vars.")
        return
    message = f"New #buyingcontent Post!\n\nTap to open in X app:\n{tweet_url}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code != 200:
            print(f"[ERROR] Telegram API returned {resp.status_code}: {resp.text}")
    except requests.RequestException as e:
        print(f"[ERROR] Telegram request failed: {e}")


def run_check():
    print("Checking for new #buyingcontent posts...")
    seen_ids = load_seen_ids()
    is_first_ever_run = len(seen_ids) == 0
    new_ids = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            page.goto(HASHTAG_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
        except Exception as e:
            print(f"[WARNING] Could not load results this run: {e}")
            try:
                page.screenshot(path="debug_screenshot.png")
                print(f"[DEBUG] Page title was: {page.title()}")
                print(f"[DEBUG] Current URL was: {page.url}")
            except Exception as debug_e:
                print(f"[DEBUG] Could not capture debug info: {debug_e}")
            browser.close()
            return

        tweets = page.query_selector_all('article[data-testid="tweet"]')
        for tweet in tweets[:10]:
            link_element = tweet.query_selector('a[href*="/status/"]')
            if not link_element:
                continue
            href = link_element.get_attribute('href')
            if not href:
                continue
            tweet_id = href.split('/status/')[-1].split('?')[0]

            if tweet_id in seen_ids:
                continue

            full_url = f"https://x.com{href.split('?')[0]}"

            if not is_first_ever_run:
                send_telegram_alert(full_url)
                print(f"[ALERT] {full_url}")

            seen_ids.add(tweet_id)
            new_ids.append(tweet_id)

        browser.close()

    if new_ids:
        save_seen_ids(seen_ids)
        print(f"[INFO] Recorded {len(new_ids)} new tweet ID(s).")
    else:
        print("[INFO] No new posts this run.")


if __name__ == "__main__":
    try:
        run_check()
    except Exception as e:
        print(f"[ERROR] Unhandled error: {e}")
        sys.exit(1)
