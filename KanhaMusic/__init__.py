"""
KanhaMusic — Main package init.
Imports are served from KanhaMusic.core so plugins can do:
    from KanhaMusic import app, assistant, call_py
"""

import logging
import os
import sys

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

from KanhaMusic.core.bot import app
from KanhaMusic.core.userbot import assistant
from KanhaMusic.core.call import call_py

__all__ = ["app", "assistant", "call_py"]
