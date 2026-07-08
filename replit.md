# KanhaMusic

A professional Telegram Music Bot that streams audio/video in Telegram Voice Chats.

## Architecture

- **main.py** — Entry point. Validates config, starts Pyrogram clients, PyTgCalls, then idles.
- **KanhaMusic/config.py** — All configuration (read from environment variables / secrets).
- **KanhaMusic/__init__.py** — Creates `app` (bot), `assistant` (userbot), and `call_py` (PyTgCalls) instances.
- **KanhaMusic/plugins/** — All command handlers, one file per feature area.
- **KanhaMusic/utils/** — YouTube, Spotify, thumbnail generation, decorators.
- **KanhaMusic/database/** — In-memory database (queues, active chats, auth users, settings).
- **KanhaMusic/strings/** — All user-facing text strings.

## Running the Bot

1. Set all required secrets (see below)
2. Generate a STRING_SESSION: `python3 generate_session.py`
3. Start via the **KanhaMusic Bot** workflow

## Required Secrets (Environment Variables)

| Secret | Description |
|--------|-------------|
| `BOT_TOKEN` | From @BotFather |
| `API_ID` | From https://my.telegram.org |
| `API_HASH` | From https://my.telegram.org |
| `STRING_SESSION` | Assistant account session (run generate_session.py) |
| `OWNER_ID` | Your Telegram user ID |

## Optional Secrets

| Secret | Description |
|--------|-------------|
| `SPOTIFY_CLIENT_ID` | For Spotify support |
| `SPOTIFY_CLIENT_SECRET` | For Spotify support |
| `LOG_GROUP_ID` | Group/channel for startup logs |
| `SUPPORT_GROUP` | Your support group link |
| `SUPPORT_CHANNEL` | Your updates channel link |
| `DURATION_LIMIT` | Max stream duration in minutes (default: 180) |

## User preferences

- Bot brand: KanhaMusic
- Thumbnail URL: https://h.uguu.se/PEdxUfYu.jpg
- All secrets must go through config.py (never hardcoded)
- pytgcalls v2.x API is used (MediaStream, not AudioPiped)
