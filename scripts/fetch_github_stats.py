"""
Fetches public GitHub stats for the configured handle straight from the GitHub API
and writes them to data/cache/stats.json. No third-party stats-card service involved,
so there's nothing external that can go down.

Usage:
    python3 scripts/fetch_github_stats.py

Optional: set GITHUB_TOKEN in the environment (or a .env file) to raise the rate
limit from 60/hr to 5000/hr. A fine-grained PAT with no special scopes is enough
since this only reads public data. Without a token this still works, it's just
easier to hit the rate limit if you re-run it a lot.
"""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "cache" / "stats.json"
HANDLE = "rbwkai"

TOKEN = os.environ.get("GITHUB_TOKEN")


def gh_get(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch():
    user = gh_get(f"/users/{HANDLE}")
    repos, page = [], 1
    while True:
        batch = gh_get(f"/users/{HANDLE}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        repos.extend(batch)
        page += 1
        time.sleep(0.2)

    total_stars = sum(r["stargazers_count"] for r in repos)
    lang_bytes = {}
    for r in repos:
        if r.get("fork"):
            continue
        try:
            langs = gh_get(f"/repos/{HANDLE}/{r['name']}/languages")
        except urllib.error.HTTPError:
            continue
        for lang, n in langs.items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + n
        time.sleep(0.15)

    top_langs = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)[:6]

    return {
        "handle": HANDLE,
        "public_repos": user.get("public_repos", len(repos)),
        "followers": user.get("followers", 0),
        "total_stars": total_stars,
        "top_languages": [{"name": n, "bytes": b} for n, b in top_langs],
        "fetched_at": time.strftime("%Y-%m-%d"),
    }


def main():
    try:
        stats = fetch()
    except urllib.error.HTTPError as e:
        print(f"GitHub API error ({e.code}): {e.reason}")
        if CACHE.exists():
            print("Keeping previous cached stats.")
            return
        print("No cache to fall back on — writing zeros so the build doesn't crash.")
        stats = {"handle": HANDLE, "public_repos": 0, "followers": 0,
                  "total_stars": 0, "top_languages": [], "fetched_at": time.strftime("%Y-%m-%d")}

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(stats, indent=2))
    print(f"wrote {CACHE}: {stats['public_repos']} repos, {stats['total_stars']} stars")


if __name__ == "__main__":
    main()
