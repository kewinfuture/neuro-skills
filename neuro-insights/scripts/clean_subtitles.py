"""Turn a .vtt subtitle file into clean text without timestamps or repeated lines.
Usage: python3 clean_subtitles.py file.vtt > file.txt
"""
import re
import sys

lines = []
last = None
with open(sys.argv[1], encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line == "WEBVTT" or "-->" in line or line.startswith(("Kind:", "Language:", "NOTE")):
            continue
        if line.isdigit():
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and line != last:
            lines.append(line)
            last = line

text = " ".join(lines)
# group into paragraphs of ~8 sentences so it is readable
sentences = re.split(r"(?<=[.!?])\s+", text)
for i in range(0, len(sentences), 8):
    print(" ".join(sentences[i:i + 8]))
    print()
