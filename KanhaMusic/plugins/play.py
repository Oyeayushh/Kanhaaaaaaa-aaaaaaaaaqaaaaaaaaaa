"""
Play commands: /play, /vplay, /playforce, /song, /video
Uses pytgcalls old API (AudioPiped / VideoAudioPiped).
"""

import os

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from KanhaMusic.config import Config
from KanhaMusic.database import db
from KanhaMusic.strings import get_string
from KanhaMusic.utils import (
    get_youtube_info, download_audio, download_video,
    get_stream_url, is_spotify_url, get_spotify_url_type,
    get_spotify_track, get_thumb,
    admin_or_auth, check_blacklist,
)

os.makedirs("downloads", exist_ok=True)


def _keyboard(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{chat_id}"),
            InlineKeyboardButton("▶️ Resume", callback_data=f"resume_{chat_id}"),
            InlineKeyboardButton("⏭ Skip", callback_data=f"skip_{chat_id}"),
        ],
        [
            InlineKeyboardButton("🔁 Loop", callback_data=f"loop_{chat_id}"),
            InlineKeyboardButton("🔀 Shuffle", callback_data=f"shuffle_{chat_id}"),
            InlineKeyboardButton("⏹ Stop", callback_data=f"stop_{chat_id}"),
        ],
        [
            InlineKeyboardButton("📋 Queue", callback_data=f"queue_{chat_id}"),
            InlineKeyboardButton("🔊 Volume", callback_data=f"volume_{chat_id}"),
            InlineKeyboardButton("❌ Close", callback_data=f"close_{chat_id}"),
        ],
    ])


async def _resolve_query(query: str):
    if is_spotify_url(query):
        kind = get_spotify_url_type(query)
        if kind == "track":
            info = await get_spotify_track(query)
            if info:
                yt = await get_youtube_info(info["query"])
                if yt:
                    yt["thumbnail"] = info.get("thumbnail") or yt.get("thumbnail")
                    return yt
        return None
    return await get_youtube_info(query)


async def _send_now_playing(client: Client, message: Message, info: dict, is_video: bool = False):
    requester = message.from_user.first_name if message.from_user else "Someone"
    thumb_path = await get_thumb(
        song_title=info.get("title", "Unknown"),
        artist=info.get("channel", "Unknown"),
        duration=info.get("duration", "0:00"),
        requested_by=requester,
        song_thumb_url=info.get("thumbnail"),
        video_id=info.get("id", ""),
    )
    caption = (
        f"🎵 **Now Playing**\n\n"
        f"**Title:** {info.get('title', 'Unknown')[:50]}\n"
        f"**Artist:** {info.get('channel', 'Unknown')[:30]}\n"
        f"**Duration:** {info.get('duration', '0:00')}\n"
        f"**Requested by:** {requester}\n"
        f"**Platform:** {'🎬 YouTube Video' if is_video else '🎵 YouTube Audio'}"
    )
    chat_id = message.chat.id
    if thumb_path and os.path.exists(thumb_path):
        return await client.send_photo(
            chat_id=chat_id, photo=thumb_path,
            caption=caption, reply_markup=_keyboard(chat_id),
        )
    return await message.reply_text(caption, reply_markup=_keyboard(chat_id))


async def _do_stream(client: Client, message: Message, info: dict, force: bool = False):
    chat_id = message.chat.id
    if db.is_active(chat_id) and not force:
        db.add_to_queue(chat_id, info)
        pos = len(db.get_queue(chat_id))
        await message.reply_text(
            f"📋 **Added to Queue** — Position #{pos}\n"
            f"🎵 **{info.get('title', 'Unknown')[:50]}**\n"
            f"⏱ Duration: {info.get('duration', '0:00')}"
        )
        return

    loading_msg = await message.reply_text("⬇️ Preparing stream, please wait...")
    try:
        from pytgcalls.types.input_stream import AudioPiped
        from KanhaMusic import call_py

        stream_url = await get_stream_url(info["url"])
        if not stream_url:
            await loading_msg.edit_text("❌ Could not fetch stream URL.")
            return

        db.add_active(chat_id, info)
        db.set_pause(chat_id, False)
        await call_py.join_group_call(chat_id, AudioPiped(stream_url), stream_type=None)
        await loading_msg.delete()
        await _send_now_playing(client, message, info)
    except Exception as e:
        await loading_msg.edit_text(f"❌ Stream error: {e}")
        db.remove_active(chat_id)


@Client.on_message(filters.command(["play", "p"]) & filters.group)
@check_blacklist
@admin_or_auth
async def play_command(client: Client, message: Message):
    query = " ".join(message.command[1:]).strip()
    if not query and message.reply_to_message and message.reply_to_message.text:
        query = message.reply_to_message.text.strip()
    if not query:
        await message.reply_text(
            "❌ Please provide a song name or URL.\n\n**Usage:** `/play [song name or URL]`"
        )
        return

    searching_msg = await message.reply_text(f"🔍 Searching for: **{query[:50]}**...")
    info = await _resolve_query(query)
    if not info:
        await searching_msg.edit_text(get_string["no_result"])
        return

    if info.get("duration_sec", 0) > Config.DURATION_LIMIT * 60:
        await searching_msg.edit_text(
            get_string["duration_limit"].format(Config.DURATION_LIMIT)
        )
        return

    await searching_msg.delete()
    await _do_stream(client, message, info)


@Client.on_message(filters.command(["playforce", "pf"]) & filters.group)
@check_blacklist
@admin_or_auth
async def playforce_command(client: Client, message: Message):
    query = " ".join(message.command[1:]).strip()
    if not query:
        await message.reply_text("❌ Please provide a song name or URL.")
        return

    msg = await message.reply_text(f"🔍 Force searching: **{query[:50]}**...")
    info = await _resolve_query(query)
    if not info:
        await msg.edit_text(get_string["no_result"])
        return
    await msg.delete()

    chat_id = message.chat.id
    try:
        from pytgcalls.types.input_stream import AudioPiped
        from KanhaMusic import call_py
        stream_url = await get_stream_url(info["url"])
        if stream_url:
            await call_py.change_stream(chat_id, AudioPiped(stream_url))
            db.add_active(chat_id, info)
            db.set_pause(chat_id, False)
            await _send_now_playing(client, message, info)
    except Exception:
        await _do_stream(client, message, info, force=True)


@Client.on_message(filters.command(["vplay", "vp"]) & filters.group)
@check_blacklist
@admin_or_auth
async def vplay_command(client: Client, message: Message):
    query = " ".join(message.command[1:]).strip()
    if not query:
        await message.reply_text("❌ Please provide a video name or URL.")
        return

    msg = await message.reply_text(f"🔍 Searching video: **{query[:50]}**...")
    info = await get_youtube_info(query)
    if not info:
        await msg.edit_text(get_string["no_result"])
        return

    await msg.edit_text("⬇️ Preparing video stream...")
    chat_id = message.chat.id
    try:
        from pytgcalls.types.input_stream import AudioVideoPiped
        from KanhaMusic import call_py
        stream_url = await get_stream_url(info["url"])
        if not stream_url:
            await msg.edit_text("❌ Could not fetch video stream.")
            return
        db.add_active(chat_id, info)
        await call_py.join_group_call(chat_id, AudioVideoPiped(stream_url), stream_type=None)
        await msg.delete()
        await _send_now_playing(client, message, info, is_video=True)
    except Exception as e:
        await msg.edit_text(f"❌ Video stream error: {e}")
        db.remove_active(chat_id)


@Client.on_message(filters.command(["song", "jsong"]) & filters.group)
@check_blacklist
async def song_command(client: Client, message: Message):
    query = " ".join(message.command[1:]).strip()
    if not query:
        await message.reply_text("❌ Provide a song name.\n**Usage:** `/song [name]`")
        return

    msg = await message.reply_text(f"🔍 Fetching: **{query[:50]}**...")
    info = await get_youtube_info(query)
    if not info:
        await msg.edit_text(get_string["no_result"])
        return

    dur_limit = Config.SONG_DOWNLOAD_DURATION_LIMIT
    if info.get("duration_sec", 0) > dur_limit * 60:
        await msg.edit_text(f"❌ Song too long! Max download limit is **{dur_limit} minutes**.")
        return

    await msg.edit_text("⬇️ Downloading audio...")
    path = await download_audio(info["url"])
    if not path or not os.path.exists(path):
        await msg.edit_text("❌ Download failed. Try again.")
        return

    await msg.delete()
    await client.send_audio(
        chat_id=message.chat.id, audio=path,
        caption=f"🎵 **{info['title']}**\n⏱ Duration: {info['duration']}\n\n✨ Powered by **KanhaMusic**",
        title=info["title"], performer=info.get("channel", "Unknown"),
    )
    try:
        os.remove(path)
    except Exception:
        pass


@Client.on_message(filters.command(["video", "jvideo"]) & filters.group)
@check_blacklist
async def video_command(client: Client, message: Message):
    query = " ".join(message.command[1:]).strip()
    if not query:
        await message.reply_text("❌ Provide a video name.\n**Usage:** `/video [name]`")
        return

    msg = await message.reply_text(f"🔍 Fetching video: **{query[:50]}**...")
    info = await get_youtube_info(query)
    if not info:
        await msg.edit_text(get_string["no_result"])
        return

    if info.get("duration_sec", 0) > 15 * 60:
        await msg.edit_text("❌ Video too long! Max download limit is **15 minutes**.")
        return

    await msg.edit_text("⬇️ Downloading video...")
    path = await download_video(info["url"])
    if not path or not os.path.exists(path):
        await msg.edit_text("❌ Download failed. Try again.")
        return

    await msg.delete()
    await client.send_video(
        chat_id=message.chat.id, video=path,
        caption=f"🎬 **{info['title']}**\n⏱ Duration: {info['duration']}\n\n✨ Powered by **KanhaMusic**",
    )
    try:
        os.remove(path)
    except Exception:
        pass
