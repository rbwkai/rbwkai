"""
Fetches rated contest history for the configured AtCoder handle from
https://atcoder.jp/users/{handle}/history/json — an unofficial but long-stable
endpoint (same one used by most community AtCoder tools). Caches the result
so render_atcoder_chart.py doesn't need network access to redraw the chart.
"""
import json
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "cache" / "atcoder_history.json"
HANDLE = "rbwkai"  # update if your AtCoder handle differs


def main():
    url = f"https://atcoder.jp/users/{HANDLE}/history/json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; rbwkai-profile-bot/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            history = json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"Couldn't reach AtCoder ({e}). Keeping existing cache if present.")
        if not CACHE.exists():
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps([]))
        return

    rated = [h for h in history if h.get("IsRated")]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(rated, indent=2))
    print(f"wrote {CACHE}: {len(rated)} rated contests")


if __name__ == "__main__":
    main()
