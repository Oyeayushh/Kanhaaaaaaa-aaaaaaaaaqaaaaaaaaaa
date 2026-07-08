"""
Start, help, and about commands for KanhaMusic.
"""

import os

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from KanhaMusic.config import Config
from KanhaMusic.strings import get_string
from KanhaMusic.utils.decorators import check_blacklist


START_IMG = Config.STREAM_IMG_URL

START_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("➕ Add Me to Group", url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true"),
    ],
    [
        InlineKeyboardButton("📖 Help", callback_data="help_main"),
        InlineKeyboardButton("ℹ️ About", callback_data="about_me"),
    ],
    [
        InlineKeyboardButton("💬 Support", url=Config.SUPPORT_GROUP),
        InlineKeyboardButton("📢 Updates", url=Config.SUPPORT_CHANNEL),
    ],
])


ABOUT_TEXT = (
    f"🎵 **KanhaMusic**\n\n"
    f"A powerful Telegram Music Bot that streams music "
    f"directly in your Voice Chats.\n\n"
    f"**Features:**\n"
    f"├ YouTube, Spotify, Apple Music & Resso support\n"
    f"├ High quality audio & video streaming\n"
    f"├ Beautiful custom thumbnails\n"
    f"├ Queue management system\n"
    f"├ Loop, shuffle & volume controls\n"
    f"└ Professional admin controls\n\n"
    f"**Owner:** [KanhaOwner](tg://user?id={Config.OWNER_ID})\n"
    f"**Version:** v1.0 | **Language:** Python"
)


@Client.on_message(filters.command(["start"]))
@check_blacklist
async def start_command(client: Client, message: Message):
    if message.chat.type.name == "PRIVATE":
        name = message.from_user.first_name if message.from_user else "User"
        try:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=START_IMG,
                caption=get_string["start_pm"].format(name),
                reply_markup=START_KEYBOARD,
            )
        except Exception:
            await message.reply_text(
                get_string["start_pm"].format(name),
                reply_markup=START_KEYBOARD,
            )
    else:
        await message.reply_text(get_string["start_group"])


@Client.on_message(filters.command(["help"]))
@check_blacklist
async def help_command(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Music",    callback_data="help_music"),
            InlineKeyboardButton("⏯ Controls", callback_data="help_controls"),
        ],
        [
            InlineKeyboardButton("📋 Queue",    callback_data="help_queue"),
            InlineKeyboardButton("📥 Download", callback_data="help_download"),
        ],
        [
            InlineKeyboardButton("🔄 Autoplay", callback_data="help_autoplay"),
            InlineKeyboardButton("🛡 Admin",    callback_data="help_admin"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="help_settings"),
            InlineKeyboardButton("ℹ️ About",    callback_data="about_me"),
        ],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")],
    ])

    try:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=START_IMG,
            caption=(
                "🎵 **KanhaMusic — Help Menu**\n\n"
                "Select a category below to see available commands:"
            ),
            reply_markup=keyboard,
        )
    except Exception:
        await message.reply_text(
            "🎵 **KanhaMusic — Help Menu**\n\nSelect a category:",
            reply_markup=keyboard,
        )


HELP_SECTIONS = {
    "music": (
        "🎵 **Music Commands**\n\n"
        "/play [song] — Play audio in voice chat\n"
        "/vplay [song] — Play video in voice chat\n"
        "/playforce [song] — Force play (skip current)\n"
        "/search [query] — Search and pick a song\n"
        "/song [name] — Download & send audio file\n"
        "/video [name] — Download & send video file"
    ),
    "controls": (
        "⏯ **Playback Controls**\n\n"
        "/pause — Pause the current song\n"
        "/resume — Resume playback\n"
        "/skip — Skip to next song in queue\n"
        "/stop — Stop music and leave VC\n"
        "/end — End the stream\n"
        "/mute — Mute the assistant\n"
        "/unmute — Unmute the assistant\n"
        "/volume [1-200] — Set volume\n"
        "/loop — Toggle single-song loop\n"
        "/loopqueue — Loop entire queue\n"
        "/shuffle — Shuffle the queue"
    ),
    "queue": (
        "📋 **Queue Commands**\n\n"
        "/queue — View current song queue\n"
        "/clearqueue — Clear the entire queue\n"
        "/queueskip [num] — Skip to specific queue position"
    ),
    "download": (
        "📥 **Download Commands**\n\n"
        "/song [name] — Download audio (max 30 min)\n"
        "/video [name] — Download video (max 15 min)"
    ),
    "admin": (
        "🛡 **Admin Commands**\n\n"
        "/auth [reply/id] — Authorize a user\n"
        "/unauth [reply/id] — Unauthorize a user\n"
        "/authlist — List authorized users\n"
        "/gban [reply/id] — Global ban (Owner only)\n"
        "/ungban [reply/id] — Remove global ban\n"
        "/broadcast [msg] — Broadcast to active chats"
    ),
    "settings": (
        "⚙️ **Settings & Autoplay**\n\n"
        "/autoplay on — Enable smart autoplay 🔄\n"
        "/autoplay off — Disable autoplay\n"
        "/autoplay — Check autoplay status\n\n"
        "/settings — Open group settings panel\n"
        "/playmode — Toggle play mode\n"
        "/ping — Check bot latency\n"
        "/stats — Bot statistics"
    ),
    "autoplay": (
        "🔄 **Autoplay System**\n\n"
        "When autoplay is **ON**, KanhaMusic automatically "
        "finds and plays a similar song when the current one ends.\n\n"
        "**Commands:**\n"
        "/autoplay on — Enable autoplay\n"
        "/autoplay off — Disable autoplay\n"
        "/autoplay — Toggle / check status\n\n"
        "**How it works:**\n"
        "├ Song ends → checks queue first\n"
        "├ Queue empty + autoplay ON → searches YouTube\n"
        "│   for songs similar to what just played\n"
        "└ Picks a random match from top results\n\n"
        "**Priority order:**\n"
        "1. 🔁 Loop (if enabled)\n"
        "2. 📋 Queue (plays next queued song)\n"
        "3. 🔄 Autoplay (finds related song)\n"
        "4. ⏹ Stop (if nothing else matches)"
    ),
}


@Client.on_callback_query(filters.regex(r"^help_(music|controls|queue|download|admin|settings|autoplay)$"))
async def help_section_callback(client: Client, query: CallbackQuery):
    section = query.matches[0].group(1)
    text = HELP_SECTIONS.get(section, "❌ Section not found.")
    back_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("◀️ Back", callback_data="help_main"),
        InlineKeyboardButton("❌ Close", callback_data="help_close"),
    ]])
    await query.message.edit_caption(caption=text, reply_markup=back_btn)
    await query.answer()


@Client.on_callback_query(filters.regex(r"^help_main$"))
async def help_main_callback(client: Client, query: CallbackQuery):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Music",    callback_data="help_music"),
            InlineKeyboardButton("⏯ Controls", callback_data="help_controls"),
        ],
        [
            InlineKeyboardButton("📋 Queue",    callback_data="help_queue"),
            InlineKeyboardButton("📥 Download", callback_data="help_download"),
        ],
        [
            InlineKeyboardButton("🔄 Autoplay", callback_data="help_autoplay"),
            InlineKeyboardButton("🛡 Admin",    callback_data="help_admin"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="help_settings"),
            InlineKeyboardButton("ℹ️ About",    callback_data="about_me"),
        ],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")],
    ])
    try:
        await query.message.edit_caption(
            caption=(
                "🎵 **KanhaMusic — Help Menu**\n\n"
                "Select a category below:"
            ),
            reply_markup=keyboard,
        )
    except Exception:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^about_me$"))
async def about_callback(client: Client, query: CallbackQuery):
    back_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("◀️ Back", callback_data="help_main"),
        InlineKeyboardButton("❌ Close", callback_data="help_close"),
    ]])
    try:
        await query.message.edit_caption(caption=ABOUT_TEXT, reply_markup=back_btn)
    except Exception:
        await query.message.reply_text(ABOUT_TEXT)
    await query.answer()


@Client.on_callback_query(filters.regex(r"^help_close$"))
async def help_close_callback(client: Client, query: CallbackQuery):
    await query.message.delete()
    await query.answer("Closed ✅")
