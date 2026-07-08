"""
KanhaMusic — Main bot initialization.
Uses pytgcalls old API (AudioPiped).
"""

import logging
import os
import sys

from pyrogram import Client
from pytgcalls import PyTgCalls

from KanhaMusic.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("KanhaMusic")

for name in ("pyrogram", "pytgcalls", "asyncio"):
    logging.getLogger(name).setLevel(logging.WARNING)

os.makedirs("downloads", exist_ok=True)
os.makedirs("cache/thumbs", exist_ok=True)
os.makedirs("assets", exist_ok=True)

app = Client(
    name="KanhaMusic",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="KanhaMusic/plugins"),
    sleep_threshold=30,
)

assistant = Client(
    name="KanhaAssistant",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.STRING_SESSION,
    sleep_threshold=30,
)

call_py = PyTgCalls(assistant)
