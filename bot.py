import os
import json
import requests

# 1. Safely create storage_state.json from GitHub Secret
storage_secret = os.getenv("X_STORAGE_STATE")
if storage_secret:
    with open("storage_state.json", "w", encoding="utf-8") as f:
        f.write(storage_secret)

# 2. Safely read seen_ids.json (prevents JSON crashes)
seen_ids = set()
if os.path.exists("seen_ids.json") and os.path.getsize("seen_ids.json") > 0:
    try:
        with open("seen_ids.json", "r", encoding="utf-8") as f:
            seen_ids = set(json.load(f))
    except json.JSONDecodeError:
        print("[WARNING] seen_ids.json was corrupted. Starting fresh.")

# 3. Main Bot Logic (Replace this comment with your original script logic if needed)
print("Bot starting...")
print(f"Loaded {len(seen_ids)} previously seen items.")

# Save seen_ids before finishing
with open("seen_ids.json", "w", encoding="utf-8") as f:
    json.dump(list(seen_ids), f)

print("Bot completed successfully!")
