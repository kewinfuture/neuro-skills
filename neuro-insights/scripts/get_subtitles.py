"""Download a video's subtitles (English by default) and print clean text.
Works around a yt-dlp subtitle download error (curl: Failed to connect).
Usage: python3 get_subtitles.py VIDEO_ID [language] > output.txt
"""
import json
import re
import subprocess
import sys
import urllib.request

vid = sys.argv[1]
lang = sys.argv[2] if len(sys.argv) > 2 else "en"
info = json.loads(subprocess.check_output(
    ["yt-dlp", "-J", "--skip-download", f"https://www.youtube.com/watch?v={vid}"],
    stderr=subprocess.DEVNULL))

url = None
for source in ("subtitles", "automatic_captions"):
    tracks = info.get(source) or {}
    for key in (lang, f"{lang}-orig", f"{lang}-US", f"{lang}-GB"):
        for f in tracks.get(key, []):
            if f.get("ext") == "vtt":
                url = f["url"]
                break
        if url:
            break
    if url:
        break
if not url:
    sys.exit("NO SUBTITLES")

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
vtt = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

lines, last = [], None
for line in vtt.splitlines():
    line = line.strip()
    if not line or line == "WEBVTT" or "-->" in line or line.startswith(("Kind:", "Language:", "NOTE")) or line.isdigit():
        continue
    line = re.sub(r"<[^>]+>", "", line).strip()
    if line and line != last:
        lines.append(line)
        last = line
sentences = re.split(r"(?<=[.!?])\s+", " ".join(lines))
for i in range(0, len(sentences), 8):
    print(" ".join(sentences[i:i + 8]))
    print()
