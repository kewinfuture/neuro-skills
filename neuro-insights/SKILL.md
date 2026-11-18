---
name: neuro-insights
description: Pulls the key advice (hooks, sales techniques, strategies, numbers) out of a YouTube video, a whole channel, a playlist or a podcast and saves it to a knowledge folder, so it can be used to improve skills and marketing. Use when someone shares a YouTube or podcast link and says "extract the insights", "what does this person recommend", "go through this channel", "transcribe this podcast" or "learn from this".
---

# Neuro Insights

The person using this skill may not be a programmer. Write in plain language, keep it short, avoid jargon.
The **knowledge folder** (where insights are saved) and the **skills folder** (where the person's skills live) come from the person's own settings. If they are not set, ask where to save.

## Tools (free)
- `yt-dlp` – list videos, download subtitles and audio
- A speech-to-text tool for audio without subtitles, for example `mlx_whisper` on Apple Silicon (`--model mlx-community/whisper-large-v3-turbo`) or `whisper` / `faster-whisper` elsewhere
- `python3 <this skill>/scripts/clean_subtitles.py file.vtt` – turns a .vtt subtitle file into clean text
- Optional: a knowledge-graph tool to connect all insights at the end (only on request)

Put working files (subtitles, audio) in a temporary folder, not on the desktop.

## Steps

### 1. What came in
- **One video** → go straight to step 3.
- **Channel or playlist** → step 2.
- **Podcast** → an Apple Podcasts link, an RSS feed or the YouTube version of the podcast works. Spotify does not (it is locked); find the same episode on YouTube or Apple Podcasts instead.

### 2. Pick the videos (saves tokens)
Never process a whole channel. List the most viewed ones:
```
yt-dlp --flat-playlist --print "%(view_count)s	%(id)s	%(duration_string)s	%(title)s" "CHANNEL_URL/videos" | sort -t$'\t' -k1 -nr | head -20
```
(Add `/videos` for a channel, not for a playlist. Short videos are under `/shorts`.)
Show the top 10 (title, views, length) and ask whether to process them or pick others. Default: 10 videos.

### 3. Transcript
Subtitles first (fast and free). Use this script, because downloading subtitles directly with yt-dlp sometimes fails with "Failed to connect":
```
python3 <this skill>/scripts/get_subtitles.py VIDEO_ID en > VIDEO_ID.txt
```
(Language code: `en`, `de`, `es`, …) It returns clean text.
- Wait at least 5 seconds between videos. On "429 Too Many Requests" YouTube is blocking you for a while (up to an hour). Continue with the next steps and retry the blocked videos later, or use audio and speech-to-text.

If there are no subtitles, download the audio and transcribe it:
```
yt-dlp -x --audio-format mp3 -o "%(id)s.%(ext)s" "URL"
mlx_whisper ID.mp3 --model mlx-community/whisper-large-v3-turbo --output-format txt
```
(Add `--language xx` when you know the language, otherwise let it detect automatically.)

Save the clean transcript to `[knowledge folder]/<Author>/transcripts/<video-name>.txt`.

### 4. Extract the advice
Read the transcripts **one at a time** and write notes from each right away. Do not read them all at once.
For each video create `[knowledge folder]/<Author>/<video-name>.md`:
- **Main idea** – 2 sentences
- **Key advice** – concrete, usable steps (not generalities)
- **Hooks and phrasing** – opening lines the author recommends or uses (short quotes only)
- **Numbers and facts** – percentages, times, frequencies
- **What it means for us** – which of our skills or strategies this would improve, and how

Skip filler, ads and greetings. This is for internal learning: summarise in your own words, keep quotes short.

### 5. Summary per author
After all videos, create `[knowledge folder]/<Author>/SUMMARY.md`:
- The author's 10 most important pieces of advice (the ones repeated across videos are the strongest)
- The best hooks to adopt

Files in the knowledge folder contain knowledge only, not proposed changes to skills.

### 6. Add to the per-skill overview
Add new findings to `[knowledge folder]/BY-SKILL.md` under the skill they fit, with the date and the author's name in brackets. Do not add what is already there; just add the author as another source to that point.

### 7. Ask the person directly
After each analysis, **ask the person in the chat** what they want to add to which skill. Use a multiple-choice question: for each skill, offer the 2 to 4 strongest concrete sentences, plus a "nothing" option.
- Do not write proposals into files; ask in the chat.
- Write into a skill only what the person picks.
- If the change affects an AI agent's instructions, show the new instructions first and write them only after the person says yes.

### 8. Finish
Say briefly what was created and where. If the knowledge folder contains several authors, offer to connect everything into one knowledge graph so the person can ask questions across all of them.
Delete temporary files (audio, .vtt).
