# 🎵 KanhaMusic

> A professional, feature-rich Telegram Music Bot — streams music directly in Voice Chats from YouTube, Spotify, Apple Music & Resso.

---

## ✨ Features

- 🎵 Stream audio/video in Telegram Voice Chats
- 🔍 YouTube search & direct URL support
- 🟢 Spotify playlist/album/track support
- 🎨 Beautiful custom thumbnails for every song
- 📋 Queue management (add, skip, shuffle, clear)
- 🔁 Loop & loop-queue modes
- 🔊 Volume control (1–200%)
- 🛡 Admin authorization system
- 🚫 Global ban system
- 📊 Bot statistics & ping
- 📡 Broadcast to active chats
- ⚙️ Per-group settings

---

## 📦 Requirements

- Python 3.9+
- FFmpeg installed on your system
- A Telegram Bot Token (from @BotFather)
- A Telegram API ID & Hash (from https://my.telegram.org)
- An Assistant account with a String Session

---

## 🚀 Setup

### 1. Clone & Install

```bash
git clone https://github.com/KanhaMusic/KanhaMusic
cd KanhaMusic
pip install -r requirements.txt
```

### 2. Configure

Copy `.env.example` to `.env` and fill in all required values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Bot token from @BotFather |
| `API_ID` | ✅ | From https://my.telegram.org |
| `API_HASH` | ✅ | From https://my.telegram.org |
| `STRING_SESSION` | ✅ | Assistant account session |
| `OWNER_ID` | ✅ | Your Telegram user ID |
| `SPOTIFY_CLIENT_ID` | ⭕ | For Spotify support |
| `SPOTIFY_CLIENT_SECRET` | ⭕ | For Spotify support |
| `LOG_GROUP_ID` | ⭕ | Group for bot logs |

### 3. Generate String Session

```bash
python generate_session.py
```

### 4. Run

```bash
python main.py
```

---

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/play [song]` | Play audio in voice chat |
| `/vplay [song]` | Play video in voice chat |
| `/playforce [song]` | Force play (skip current) |
| `/search [query]` | Search and pick a song |
| `/queue` | View song queue |
| `/skip` | Skip current song |
| `/pause` | Pause music |
| `/resume` | Resume music |
| `/stop` | Stop and leave VC |
| `/volume [1-200]` | Set volume |
| `/loop` | Toggle loop |
| `/shuffle` | Shuffle queue |
| `/song [name]` | Download audio file |
| `/video [name]` | Download video file |
| `/auth` | Authorize a user |
| `/unauth` | Unauthorize a user |
| `/ping` | Check latency |
| `/stats` | Bot statistics |

---

## 🎨 Thumbnail

Every song played generates a custom thumbnail overlay on the KanhaMusic brand image, showing:
- Song title & artist
- Duration
- Requested by
- KanhaMusic branding

---

## 📞 Support

- 💬 [Support Group](https://t.me/KanhaMusicSupport)
- 📢 [Updates Channel](https://t.me/KanhaMusicUpdates)

---

## ⚡ Powered by

- [Pyrogram](https://pyrogram.org/) — Telegram MTProto API
- [PyTgCalls](https://pytgcalls.github.io/) — Voice Chat streaming
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube downloading
- [Spotipy](https://spotipy.readthedocs.io/) — Spotify API
- [Pillow](https://pillow.readthedocs.io/) — Thumbnail generation

---

*Made with ❤️ for KanhaMusic*
