# Neuro Skills

Free, open-source [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for marketing and content work, from the **Future** project. Each skill is a folder with a `SKILL.md` and, where needed, small Python scripts (standard library only).

| Skill | What it does |
|---|---|
| [`neuro-insights`](neuro-insights/) | Pulls the key advice, hooks and numbers out of a YouTube video, channel, playlist or podcast and saves them to a knowledge folder. |
| [`neuro-playbook`](neuro-playbook/) | A working method for any multi-step task: plan, check the real state, review your own work, hand it over honestly. |
| [`neuro-trials`](neuro-trials/) | Tests versions of a video through Instagram Trial Reels, one change per round, and picks a winner from the numbers. |

## Install

**Claude Code:** copy a skill folder into `~/.claude/skills/` (personal) or `.claude/skills/` in your project.

```bash
git clone https://github.com/kewinfuture/neuro-skills.git
cp -r neuro-skills/neuro-playbook ~/.claude/skills/
```

**Claude apps:** zip a skill folder and upload it under Settings → Capabilities → Skills.

## Requirements

- `neuro-insights`: [`yt-dlp`](https://github.com/yt-dlp/yt-dlp); for videos without subtitles, a speech-to-text tool such as Whisper.
- `neuro-trials`: Python 3 and an Instagram API access token with publishing and insights permissions. Nothing is published without explicit approval.
- `neuro-playbook`: nothing.

## License

[MIT](LICENSE) © 2026 Kevin Ďurčík
