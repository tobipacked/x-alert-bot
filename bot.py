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


def save_seen_ids(seen
