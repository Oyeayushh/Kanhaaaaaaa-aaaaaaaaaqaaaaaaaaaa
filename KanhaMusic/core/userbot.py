from pyrogram import Client

from KanhaMusic.config import Config

assistant = Client(
    name="KanhaAssistant",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.STRING_SESSION,
    sleep_threshold=30,
)
