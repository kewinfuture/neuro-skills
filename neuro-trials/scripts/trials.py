#!/usr/bin/env python3
"""Neuro Trials - publish versions as Instagram Trial Reels and fetch their stats.

Runs without an AI (e.g. from a scheduled task). Python standard library only.

Usage:
    python trials.py publish batch.json
    python trials.py stats batch.json

Access token (never inside the skill):
    - environment variable NEURO_TRIALS_TOKEN, or
    - a file given by the environment variable NEURO_TRIALS_TOKEN_FILE, or
    - the file ~/.neuro-trials/token.txt

Sources (VERIFY BEFORE FIRST USE, the Meta API changes):
    - trial_params (graduation_strategy MANUAL / SS_PERFORMANCE), only with media_type=REELS:
      https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media.md
    - changelog entry "Supporting Trial Reels in the Content Publishing API":
      https://developers.facebook.com/docs/instagram-platform/changelog
    - reel insights (views, reach, saved, shares, ig_reels_avg_watch_time, reels_skip_rate):
      https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights
    Notes: the API cannot graduate a trial reel to all followers; that is done in the app.
    ig_reels_avg_watch_time is treated as milliseconds - verify on your first reel.
    The limit of about 20 trial reels per day per account comes from unofficial sources.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# Instagram API with Instagram Login -> graph.instagram.com
# (with Facebook Login it would be graph.facebook.com). Verify before first use.
HOST = os.environ.get("NEURO_TRIALS_HOST", "https://graph.instagram.com")
API_VERSION = os.environ.get("NEURO_TRIALS_API_VERSION", "v27.0")
DAILY_LIMIT = 20
MIN_VIEWS = int(os.environ.get("NEURO_TRIALS_MIN_VIEWS", "500"))
METRICS = "views,reach,saved,shares,likes,comments,total_interactions,ig_reels_avg_watch_time,reels_skip_rate"


def load_token():
    token = os.environ.get("NEURO_TRIALS_TOKEN")
    if token:
        return token.strip()
    path = os.environ.get("NEURO_TRIALS_TOKEN_FILE") or str(Path.home() / ".neuro-trials" / "token.txt")
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except OSError:
        sys.exit("Error: access token missing (NEURO_TRIALS_TOKEN or a token file outside the skill).")


def call(method, path, params, token):
    params = dict(params, access_token=token)
    url = f"{HOST}/{API_VERSION}/{path}"
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        text = e.read().decode(errors="replace")
        text = text.replace(token, "***")
        raise RuntimeError(f"API error {e.code}: {text}") from None


def load_batch(file):
    return json.loads(Path(file).read_text(encoding="utf-8"))


def save_batch(file, batch):
    Path(file).write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")


def publish(file):
    batch = load_batch(file)
    if batch.get("approved") is not True:
        sys.exit('Not published: the batch is missing "approved": true (the person has not approved it yet).')
    ig = batch["ig_user_id"]
    versions = [v for v in batch["versions"] if not v.get("media_id")]
    if len(versions) > DAILY_LIMIT:
        sys.exit(f"Too many versions ({len(versions)}); the limit is about {DAILY_LIMIT} per day.")
    token = load_token()
    strategy = batch.get("graduation_strategy", "MANUAL")
    for v in versions:
        print(f"Version {v['id']}: creating container...")
        cont = call("POST", f"{ig}/media", {
            "media_type": "REELS",
            "video_url": v["video_url"],
            "caption": v.get("caption", ""),
            "trial_params": json.dumps({"graduation_strategy": strategy}),
        }, token)
        cid = cont["id"]
        v["container_id"] = cid
        status = ""
        for _ in range(60):  # at most 10 minutes
            status = call("GET", cid, {"fields": "status_code"}, token).get("status_code", "")
            if status in ("FINISHED", "ERROR", "EXPIRED"):
                break
            time.sleep(10)
        if status != "FINISHED":
            v["error"] = f"container ended in status {status or 'unknown'}"
            print(f"  {v['error']}, skipping.")
            save_batch(file, batch)
            continue
        pub = call("POST", f"{ig}/media_publish", {"creation_id": cid}, token)
        v["media_id"] = pub["id"]
        v["published"] = datetime.now().isoformat(timespec="minutes")
        v.pop("error", None)
        save_batch(file, batch)
        print(f"  published, media_id {pub['id']}")
    print("Done.")


def stats(file):
    batch = load_batch(file)
    token = load_token()
    duration = float(batch.get("duration_s") or 0)
    rows = []
    for v in batch["versions"]:
        mid = v.get("media_id")
        if not mid:
            continue
        data = call("GET", f"{mid}/insights", {"metric": METRICS}, token).get("data", [])
        m = {d["name"]: (d.get("values") or [{}])[0].get("value", d.get("total_value", {}).get("value")) for d in data}
        views = m.get("views") or 0
        avg_s = (m.get("ig_reels_avg_watch_time") or 0) / 1000  # assumption: milliseconds
        rows.append({
            "version": v["id"],
            "hook": v.get("hook", ""),
            "views": views,
            "reach": m.get("reach"),
            "avg_watch_s": round(avg_s, 1),
            "avg_watch_pct_of_length": round(avg_s / duration * 100, 1) if duration else None,
            "skip_rate_3s_pct": m.get("reels_skip_rate"),
            "shares_per_1000": round(m.get("shares", 0) / views * 1000, 1) if views else None,
            "saves_per_1000": round(m.get("saved", 0) / views * 1000, 1) if views else None,
            "status": "ok" if views >= MIN_VIEWS else "undecided, keep going",
        })
    base = Path(file).with_suffix("")
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    csv_path = Path(f"{base}-stats-{stamp}.csv")
    json_path = Path(f"{base}-stats-{stamp}.json")
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {csv_path} and {json_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("publish", "stats"):
        sys.exit(__doc__)
    try:
        {"publish": publish, "stats": stats}[sys.argv[1]](sys.argv[2])
    except RuntimeError as e:
        sys.exit(str(e))
