# 🎵 KanhaMusic

> A professional, feature-rich Telegram Music Bot that streams audio/video directly in Telegram Voice Chats — powered by YouTube, Spotify & more.

<p align="center">
  <img src="https://h.uguu.se/PEdxUfYu.jpg" width="400" alt="KanhaMusic Banner"/>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎵 **Audio Streaming** | Stream music in Telegram Voice Chats via assistant account |
| 🎬 **Video Streaming** | Stream video in Voice Chats (`/vplay`) |
| 🔍 **YouTube Search** | Search by name or paste a URL directly |
| 🟢 **Spotify Support** | Play Spotify tracks, playlists & albums |
| 🎨 **Custom Thumbnails** | Beautiful per-song image cards with artist & duration |
| 📋 **Queue System** | Add, skip, remove, shuffle songs |
| 🔁 **Loop Modes** | Single-song loop or full queue loop |
| 🔊 **Volume Control** | 1–200% volume per group |
| 🔄 **Smart Autoplay** | Auto-plays similar songs when queue ends |
| 🛡 **Auth System** | Per-group authorized users |
| 🚫 **Global Ban** | Block users across all groups |
| 📊 **Stats & Ping** | System stats, CPU, RAM usage |
| 📡 **Broadcast** | Send messages to all active chats |
| ⚙️ **Group Settings** | Per-group configuration panel |

---

## 🗂 Project Structure

```
KanhaMusic/
├── core/
│   ├── bot.py         ← Pyrogram Bot Client (app)
│   ├── userbot.py     ← Pyrogram Assistant Client
│   └── call.py        ← PyTgCalls instance (call_py)
├── plugins/
│   ├── start.py       ← /start, /help
│   ├── play.py        ← /play, /vplay, /playforce, /song, /video
│   ├── controls.py    ← /pause, /resume, /skip, /stop, /volume, /loop
│   ├── queue.py       ← /queue, /clearqueue, /queueskip, /remove
│   ├── search.py      ← /search
│   ├── autoplay.py    ← /autoplay on/off
│   ├── assistant.py   ← /joinvc, /leavevc, /vcstatus
│   ├── admin.py       ← /auth, /unauth, /gban, /ungban
│   └── misc.py        ← /ping, /stats, /broadcast, /settings
├── utils/
│   ├── stream/
│   │   ├── audio.py   ← stream_audio(), change_audio()
│   │   └── video.py   ← stream_video(), change_video()
│   ├── youtube.py     ← yt-dlp search/download/stream
│   ├── spotify.py     ← Spotify API integration
│   ├── thumbnails.py  ← Pillow thumbnail generation
│   ├── autoplay.py    ← Related song finder
│   └── decorators.py  ← owner_only, admin_or_auth, check_blacklist
├── database/
│   └── memorydatabase.py  ← In-memory DB (queues, settings, auth)
├── strings/
│   └── en.py          ← All user-facing text
└── config.py          ← All config read from environment variables
main.py                ← Entry point + stream-end handler
generate_session.py    ← String session generator
```

---

## 📦 Requirements

- Python **3.9+**
- **FFmpeg** installed
- A Telegram **Bot Token** (from [@BotFather](https://t.me/BotFather))
- A Telegram **API ID & Hash** (from [my.telegram.org](https://my.telegram.org))
- A **second Telegram account** for the assistant (generates `STRING_SESSION`)

---

## 🚀 Setup

### 1. Clone & Install

```bash
git clone https://github.com/Oyeayushh/Kanhaaaaaaa-aaaaaaaaaqaaaaaaaaaa
cd Kanhaaaaaaa-aaaaaaaaaqaaaaaaaaaa
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Bot token from [@BotFather](https://t.me/BotFather) |
| `API_ID` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `STRING_SESSION` | ✅ | Assistant account session (run `generate_session.py`) |
| `OWNER_ID` | ✅ | Your Telegram numeric user ID |
| `SPOTIFY_CLIENT_ID` | ⭕ | For Spotify support |
| `SPOTIFY_CLIENT_SECRET` | ⭕ | For Spotify support |
| `LOG_GROUP_ID` | ⭕ | Group/channel ID for bot logs |
| `SUPPORT_GROUP` | ⭕ | Your support group link |
| `SUPPORT_CHANNEL` | ⭕ | Your updates channel link |
| `DURATION_LIMIT` | ⭕ | Max stream duration in minutes (default: 180) |

### 3. Generate String Session

Run this **once** using your **second** Telegram account:

```bash
python generate_session.py
```

Enter your API ID, API Hash, and phone number of the 2nd account. Copy the output and set it as `STRING_SESSION`.

### 4. Run

```bash
python main.py
```

---

## 📋 Commands

### 🎵 Music
| Command | Description |
|---------|-------------|
| `/play [song/URL]` | Play audio in voice chat |
| `/vplay [song/URL]` | Play video in voice chat |
| `/playforce [song]` | Force play, skip current song |
| `/search [query]` | Search YouTube and pick a result |
| `/song [name]` | Download & send audio file |
| `/video [name]` | Download & send video file |

### ⏯ Playback Controls
| Command | Description |
|---------|-------------|
| `/pause` | Pause music |
| `/resume` | Resume music |
| `/skip` | Skip to next song |
| `/stop` | Stop music & leave VC |
| `/volume [1-200]` | Set volume |
| `/mute` | Mute assistant |
| `/unmute` | Unmute assistant |
| `/loop` | Toggle single-song loop |
| `/loopqueue` | Toggle full queue loop |
| `/shuffle` | Shuffle the queue |

### 📋 Queue
| Command | Description |
|---------|-------------|
| `/queue` | View current queue |
| `/clearqueue` | Clear entire queue |
| `/queueskip [pos]` | Skip to specific queue position |
| `/remove [pos]` | Remove a song from queue |

### 🔄 Autoplay
| Command | Description |
|---------|-------------|
| `/autoplay on` | Enable smart autoplay |
| `/autoplay off` | Disable autoplay |
| `/autoplay` | Check/toggle autoplay status |

### 🎙 Assistant / VC
| Command | Description |
|---------|-------------|
| `/joinvc` | Make assistant join voice chat |
| `/leavevc` | Make assistant leave voice chat |
| `/vcstatus` | Show current VC status |

### 🛡 Admin
| Command | Description |
|---------|-------------|
| `/auth [reply/ID]` | Authorize a user |
| `/unauth [reply/ID]` | Unauthorize a user |
| `/authlist` | List authorized users |
| `/gban [reply/ID]` | Global ban (Owner only) |
| `/ungban [reply/ID]` | Global unban (Owner only) |
| `/gbanlist` | List globally banned users |

### ⚙️ Settings & Other
| Command | Description |
|---------|-------------|
| `/settings` | Group settings panel |
| `/ping` | Check bot latency |
| `/stats` | Bot statistics |
| `/broadcast [msg]` | Broadcast to active chats (Owner only) |
| `/help` | Show help menu |

---

## 🔄 How Smart Autoplay Works

When a song ends, the bot follows this priority chain automatically:

```
Song ends
   ├─ 🔁 Loop ON?      → Replay same song
   ├─ 📋 Queue?        → Play next queued song
   ├─ 🔄 Autoplay ON?  → Search YouTube for similar songs
   │      └─ Picks random from top results based on artist/title
   └─ ⏹  Nothing      → Leave voice chat
```

---

## 🎙 How Voice Chat Streaming Works

```
User: /play Kesariya
        │
        ▼
🤖 Bot (BOT_TOKEN)              👤 Assistant (STRING_SESSION)
   Searches YouTube                Joins Group Voice Chat
   Downloads/streams URL    →      Streams audio LIVE
   Sends "Now Playing" card        Everyone in VC hears it!
```

> **Why two accounts?** Telegram only allows **user accounts** (not bots) to join Voice Chats. The assistant userbot joins VC invisibly and streams the audio.

---

## ⚡ Tech Stack

| Library | Purpose |
|---------|---------|
| [Pyrogram](https://pyrogram.org/) | Telegram MTProto client |
| [PyTgCalls](https://pytgcalls.github.io/) | Voice Chat streaming engine |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube download & stream URLs |
| [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) | YouTube search |
| [Spotipy](https://spotipy.readthedocs.io/) | Spotify API |
| [Pillow](https://pillow.readthedocs.io/) | Thumbnail generation |
| [FFmpeg](https://ffmpeg.org/) | Audio/video processing |

---

## 📞 Support

- 💬 [Support Group](https://t.me/KanhaMusicSupport)
- 📢 [Updates Channel](https://t.me/KanhaMusicUpdates)

---

*Made with ❤️ — KanhaMusic*
