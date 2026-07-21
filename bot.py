import time
import requests
from playwright.sync_api import sync_playwright
import os

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8881051610:AAFWDhPVM-ESVu1_w7IgP18sPdeIs2RfAOs')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '7905985567')
HASHTAG_URL = "https://x.com/search?q=%23buyingcontent&f=live"
CHECK_INTERVAL_SECONDS = 30 
seen_tweet_ids = set()

def send_telegram_alert(tweet_url):
    message = f"🚨 **New #buyingcontent Post!**\n\nTap to open in X app:\n{tweet_url}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[ERROR] Telegram error: {e}")

def run_monitor():
    print("🤖 Starting Cloud X Monitor...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Run for a few loops or a fixed window in CI before timing out
        for _ in range(5):
            try:
                print("\n[INFO] Checking for new posts...")
                page.goto(HASHTAG_URL, wait_until="domcontentloaded")
                page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)

                tweets = page.query_selector_all('article[data-testid="tweet"]')
                for tweet in tweets[:5]:
                    link_element = tweet.query_selector('a[href*="/status/"]')
                    if link_element:
                        href = link_element.get_attribute('href')
                        tweet_id = href.split('/status/')[-1].split('?')[0]
                        
                        if tweet_id not in seen_tweet_ids:
                            full_url = f"https://x.com{href.split('?')[0]}"
                            if len(seen_tweet_ids) > 0: 
                                send_telegram_alert(full_url)
                            seen_tweet_ids.add(tweet_id)

            except Exception as e:
                print(f"[WARNING] Error: {e}")

            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_monitor()
