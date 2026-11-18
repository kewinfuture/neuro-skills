---
name: neuro-trials
description: Neuro Trials tests versions of a video through Instagram Trial Reels for any business. Each round changes only one thing (first the hook and opening shot, then music, editing, visuals); it evaluates the numbers and publishes the winner only after approval. Use for hook tests, trial reels, or "which version of this video is better".
---

# Neuro Trials

Turns one video into several versions that always differ in just one thing. After the person approves, they are published as Trial Reels (shown first only to non-followers). After 48 to 72 hours the numbers are evaluated and, after approval, the winner is shared with all followers. Business-specific rules (style, account, audience) belong in the business's own notes file, not here.

## When
Trial reels, hook test, which version of a video is better, test this video.

## Shared rules
- **Hooks and scripts:** use the person's script or hook skill if they have one; otherwise write 3 hook options yourself.
- **Caption:** use the person's caption skill if they have one.
- **Video versions:** do one clean edit; voice, retouching and colour are done once. Only the intro and first shot, the on-screen text and the music change, depending on the round.
- **Music** is baked into the video file (the API cannot add music from Instagram's library). Use only music the business is licensed to use.
- **GPU work:** if generating, editing and transcription run on the same machine, don't run them at the same time. Check before starting.
- **Nothing is published without a yes.** The person gives one yes for the whole batch of versions (table + previews). Nothing is published automatically, not even daily.

## Steps
1. **Load the business's notes:** voice, editing style, Instagram account, audience.
2. **Input:** a video (filmed, AI or 3D) and a script with hooks. If there are no hooks, write them first.
3. **Round 1 – hook and first shot (3 versions).** Versions differ only in:
   - the hook: the first sentence and the on-screen text in the first 2 seconds,
   - the first shot (product close-up, face, result, surprise).
   Music, editing, subtitles and visuals in the rest of the video are identical in all versions.
4. **Later rounds – one thing at a time:** on the winner, change only one thing per round (e.g. round 2 music, round 3 editing pace, round 4 visuals or subtitles), so it's clear why a version won.
5. **Check before publishing:** 9:16, 1080x1920, MP4, at most 90 seconds, caption ready.
6. **Approval:** show the person a table (version, hook, first shot, what changes in this round) and previews. After one yes for the whole batch, set `"approved": true` in the batch file. Without it the program publishes nothing.
7. **Publishing** is done by the program `scripts/trials.py` (see below), not by the AI.
8. **Evaluation after 48 h and 72 h** (see Evaluation).
9. **Winner:** propose it to the person. After their yes, the winner is shared with all followers. The API can't do this for a trial reel, so give the person exact instructions on where to tap in the Instagram app.
10. **Record it:** see Log and patterns.

## Evaluation
- **Minimum views:** every version needs at least 500 views (1000 is better). If any has fewer, the result is "undecided, keep going" – wait another day, don't declare a winner.
- **Metrics (always as ratios, never absolute numbers):**
  - average watch time as % of video length (average time ÷ length × 100),
  - skip rate in the first 3 s, if Instagram provides it (lower is better); completion rate if available,
  - shares per 1000 views,
  - saves per 1000 views.
  Absolute views are only used to check the minimum and are not mixed into the comparison.
- **Ranking:** first watch time %, then shares + saves per 1000. The winner must be at least 20% better than the runner-up on the main metric; otherwise it's undecided and another round runs.
- The AI only reads the CSV from the program and writes the conclusion: winner, by how much, and why (what changed in this round).

## Log and patterns
- **Test log:** a separate file `neuro-trials-log.md` in the business's folder: date, round, what changed, versions, numbers, track (title, link, licence), winner, why.
- **Into the business's notes** write only 3 to 5 proven patterns (held in at least two tests), e.g. "a question hook holds attention longer than a number hook". Use them in the next content plan.

## The trials.py program (runs without the AI)
Run it from a scheduled task or by hand. Needs only Python 3.

1. **Access token** – keep it outside the skill: environment variable `NEURO_TRIALS_TOKEN` or the file `~/.neuro-trials/token.txt` (another path via `NEURO_TRIALS_TOKEN_FILE`). Never in the skill or in the chat.
2. **Batch file** (`batch.json`), prepared by the AI:
   ```json
   {
     "ig_user_id": "123...",
     "round": 1,
     "duration_s": 30,
     "approved": false,
     "graduation_strategy": "MANUAL",
     "versions": [
       {"id": "A", "hook": "...", "video_url": "https://public-link/A.mp4", "caption": "..."}
     ]
   }
   ```
   The video must have a public URL. `"approved": true` is set only after the person says yes.
3. **Publish:** `python scripts/trials.py publish batch.json` – uploads the approved versions as Trial Reels (REELS container, then media_publish) and writes `media_id` into the batch. Already published versions are skipped.
4. **Stats:** `python scripts/trials.py stats batch.json` – saves a CSV and JSON next to the batch with each version's metrics (including "undecided, keep going" when views are too low).
5. The AI then only evaluates the CSV and updates the log.

Trial Reels parameters and metric names are in the code with links to the Meta documentation. Check them before first use (the Meta API changes).

## One-time Meta app setup
Meta for Developers → new app → Instagram API with Instagram Login → publishing and insights permissions → connect the business's account (business or creator) → save the access token on the machine as in point 1 above. Using it for other businesses' accounts will require Meta app review. The limit is roughly 20 trial reels per day per account.

## Automation
A scheduled task runs only `trials.py stats` for tests older than 48 h and 72 h. Publishing runs only after the person approves the batch. The AI is involved only when there's a new CSV to evaluate.
