"""
Miscellaneous commands: /ping, /stats, /broadcast, /settings, /playmode
"""

import asyncio
import time

import psutil
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from KanhaMusic.config import Config
from KanhaMusic.database import db
from KanhaMusic.strings import get_string
from KanhaMusic.utils.decorators import owner_only, check_blacklist


@Client.on_message(filters.command(["ping"]))
@check_blacklist
async def ping_command(client: Client, message: Message):
    start = time.time()
    msg = await message.reply_text("🏓 Pinging...")
    latency = round((time.time() - start) * 1000)

    api_start = time.time()
    await client.get_me()
    api_ping = round((time.time() - api_start) * 1000)

    await msg.edit_text(
        f"🏓 **Pong!**\n\n"
        f"├ **Bot Latency:** `{latency}ms`\n"
        f"└ **API Ping:** `{api_ping}ms`"
    )


@Client.on_message(filters.command(["stats"]))
@check_blacklist
async def stats_command(client: Client, message: Message):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    active_chats = len(db.get_all_active())

    me = await client.get_me()

    text = (
        f"📊 **KanhaMusic Statistics**\n\n"
        f"🤖 **Bot:** {me.first_name}\n"
        f"👤 **Username:** @{me.username}\n\n"
        f"🎵 **Active Chats:** `{active_chats}`\n\n"
        f"💻 **System:**\n"
        f"├ **CPU:** `{cpu}%`\n"
        f"├ **RAM:** `{ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB`\n"
        f"└ **Disk:** `{disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB`\n\n"
        f"✨ **Powered by KanhaMusic**"
    )
    await message.reply_text(text)


@Client.on_message(filters.command(["broadcast"]) & filters.private)
@owner_only
async def broadcast_command(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "❌ Provide a message to broadcast.\n**Usage:** `/broadcast [message]`"
        )
        return

    broadcast_text = (
        " ".join(message.command[1:])
        if len(message.command) > 1
        else message.reply_to_message.text
    )
    if not broadcast_text:
        await message.reply_text("❌ No text to broadcast.")
        return

    msg = await message.reply_text("📡 Broadcasting...")

    sent = 0
    failed = 0
    active_chats = db.get_all_active()

    if not active_chats:
        await msg.edit_text("📭 No active chats to broadcast to.")
        return

    for chat_id in list(active_chats.keys()):
        try:
            await client.send_message(
                chat_id,
                f"📢 **Broadcast from KanhaMusic**\n\n{broadcast_text}"
            )
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.1)

    await msg.edit_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"├ **Sent:** `{sent}`\n"
        f"└ **Failed:** `{failed}`"
    )


@Client.on_message(filters.command(["settings"]) & filters.group)
@check_blacklist
async def settings_command(client: Client, message: Message):
    chat_id = message.chat.id
    settings = db.get_settings(chat_id)
    playmode = settings.get("playmode", "direct")

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"🎵 Play Mode: {playmode.title()}",
                callback_data=f"setting_playmode_{chat_id}"
            )
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data=f"close_{chat_id}")
        ]
    ])

    await message.reply_text(
        f"⚙️ **KanhaMusic Settings**\n\n"
        f"**Group:** {message.chat.title}\n"
        f"**Play Mode:** `{playmode}`\n\n"
        f"Adjust settings below:",
        reply_markup=buttons,
    )


@Client.on_callback_query(filters.regex(r"^setting_playmode_(-?\d+)$"))
async def cb_playmode(client: Client, query: CallbackQuery):
    chat_id = int(query.matches[0].group(1))
    settings = db.get_settings(chat_id)
    current = settings.get("playmode", "direct")
    new_mode = "inline" if current == "direct" else "direct"
    db.update_setting(chat_id, "playmode", new_mode)
    await query.answer(f"Play mode changed to: {new_mode.title()}", show_alert=False)

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"🎵 Play Mode: {new_mode.title()}",
                callback_data=f"setting_playmode_{chat_id}"
            )
        ],
        [InlineKeyboardButton("❌ Close", callback_data=f"close_{chat_id}")]
    ])
    await query.message.edit_reply_markup(buttons)


@Client.on_message(filters.command(["playmode"]) & filters.group)
@check_blacklist
async def playmode_command(client: Client, message: Message):
    await settings_command(client, message)
