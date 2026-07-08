from pyrogram import Client

from KanhaMusic.config import Config

app = Client(
    name="KanhaMusic",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="KanhaMusic/plugins"),
    sleep_threshold=30,
)
