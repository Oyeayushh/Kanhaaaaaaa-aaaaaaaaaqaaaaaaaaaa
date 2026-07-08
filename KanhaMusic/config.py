import os
from os import getenv

class Config:
    BOT_TOKEN = getenv("BOT_TOKEN", "")
    API_ID = int(getenv("API_ID", 0))
    API_HASH = getenv("API_HASH", "")
    OWNER_ID = int(getenv("OWNER_ID", 0))
    OWNER_USERNAME = getenv("OWNER_USERNAME", "KanhaOwner")

    MONGO_DB_URI = getenv("MONGO_DB_URI", "")

    STRING_SESSION = getenv("STRING_SESSION", "")

    LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", 0))
    SUPPORT_GROUP = getenv("SUPPORT_GROUP", "https://t.me/KanhaMusicSupport")
    SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/KanhaMusicUpdates")

    YOUTUBE_IMG_URL = getenv(
        "YOUTUBE_IMG_URL",
        "https://h.uguu.se/PEdxUfYu.jpg"
    )

    DURATION_LIMIT = int(getenv("DURATION_LIMIT", 180))
    SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", 30))

    BOT_NAME = getenv("BOT_NAME", "KanhaMusic")
    BOT_USERNAME = getenv("BOT_USERNAME", "KanhaMusicBot")

    SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "")

    STREAM_IMG_URL = getenv(
        "STREAM_IMG_URL",
        "https://h.uguu.se/PEdxUfYu.jpg"
    )

    UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/KanhaMusic/KanhaMusic")
    UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")

    AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", True))

    AUTO_SUGGESTION_DURATION = int(getenv("AUTO_SUGGESTION_DURATION", 10))

    PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

    HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")
    HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")

    ADMIN_RIGHTS_REQUIRED = True
