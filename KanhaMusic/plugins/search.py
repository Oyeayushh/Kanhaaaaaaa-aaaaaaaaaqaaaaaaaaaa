"""
Search command: /search — Search YouTube and pick a result.
"""

import os

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from KanhaMusic.core.call import call_py
from KanhaMusic.database import db
from KanhaMusic.strings import get_string
from KanhaMusic.utils import (
    search_youtube, get_youtube_info, get_stream_url,
    get_thumb, stream_audio, check_blacklist,
)


@Client.on_message(filters.command(["search", "yts"]) & filters.group)
@check_blacklist
async def search_command(client: Client, message: Message):
    query = " ".join(message.command[1:]).strip()
    if not query:
        return await message.reply_text(
            "❌ Provide a search query.\n**Usage:** `/search [song name]`"
        )

    msg = await message.reply_text(f"🔍 Searching YouTube for: **{query[:50]}**...")
    results = await search_youtube(query, limit=7)
    if not results:
        return await msg.edit_text(get_string["no_result"])

    text = f"🔍 **Search Results for:** `{query[:40]}`\n\nPick a song below:\n\n"
    buttons = []
    for i, r in enumerate(results[:7], 1):
        text += f"**{i}.** {r['title'][:45]} — ⏱ {r['duration']}\n"
        buttons.append([
            InlineKeyboardButton(
                f"{'🎵' if i <= 5 else '🎬'} {i}. {r['title'][:32]}",
                callback_data=f"sr_{i-1}_{message.chat.id}_{message.from_user.id}"
            )
        ])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="sr_cancel")])

    db.update_setting(message.chat.id, f"search_{message.from_user.id}", results)
    await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex(r"^sr_(\d+)_(-?\d+)_(\d+)$"))
async def search_result_callback(client: Client, query: CallbackQuery):
    idx     = int(query.matches[0].group(1))
    chat_id = int(query.matches[0].group(2))
    user_id = int(query.matches[0].group(3))

    if query.from_user.id != user_id:
        return await query.answer("❌ This is not your search!", show_alert=True)

    results = db.get_settings(chat_id).get(f"search_{user_id}", [])
    if not results or idx >= len(results):
        return await query.answer("❌ Search results expired.", show_alert=True)

    chosen = results[idx]
    await query.message.delete()
    await query.answer("⏳ Loading track...")

    info = await get_youtube_info(chosen["url"])
    if not info:
        await client.send_message(chat_id, "❌ Could not fetch track info.")
        return

    # Queue if already streaming
    if db.is_active(chat_id):
        db.add_to_queue(chat_id, info)
        pos = len(db.get_queue(chat_id))
        await client.send_message(
            chat_id,
            f"📋 **Added to Queue** — Position #{pos}\n"
            f"🎵 **{info['title'][:50]}**\n"
            f"⏱ {info.get('duration', '?')} | 👤 {query.from_user.first_name}"
        )
        return

    # Start streaming
    stream_url = await get_stream_url(info["url"])
    if not stream_url:
        await client.send_message(chat_id, "❌ Could not get stream URL.")
        return

    db.add_active(chat_id, info)
    ok = await stream_audio(chat_id, stream_url)
    if not ok:
        db.remove_active(chat_id)
        await client.send_message(chat_id, "❌ Could not join voice chat.")
        return

    thumb = await get_thumb(
        info["title"], info.get("channel", "Unknown"),
        info.get("duration", ""), query.from_user.first_name,
        info.get("thumbnail"), info.get("id", "")
    )
    caption = (
        f"🎵 **Now Playing**\n\n"
        f"**{info['title'][:50]}**\n"
        f"🎤 {info.get('channel', 'Unknown')[:30]}\n"
        f"⏱ {info.get('duration', '?')} | 👤 {query.from_user.first_name}"
    )
    if thumb and os.path.exists(thumb):
        await client.send_photo(chat_id, thumb, caption=caption)
    else:
        await client.send_message(chat_id, caption)


@Client.on_callback_query(filters.regex(r"^sr_cancel$"))
async def search_cancel(client: Client, query: CallbackQuery):
    await query.message.delete()
    await query.answer("Cancelled ✅")
