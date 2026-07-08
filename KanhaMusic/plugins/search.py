"""
Search command: /search — Search YouTube and pick a result.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from KanhaMusic.database import db
from KanhaMusic.strings import get_string
from KanhaMusic.utils import search_youtube
from KanhaMusic.utils.decorators import check_blacklist


@Client.on_message(filters.command(["search"]) & filters.group)
@check_blacklist
async def search_command(client: Client, message: Message):
    query = " ".join(message.command[1:]).strip()
    if not query:
        return await message.reply_text(
            "❌ Provide a search query.\n**Usage:** `/search [song name]`"
        )

    msg = await message.reply_text(f"🔍 Searching YouTube for: **{query[:50]}**...")
    results = await search_youtube(query, limit=6)
    if not results:
        return await msg.edit_text(get_string["no_result"])

    text = f"🔍 **Search Results for:** `{query[:40]}`\n\nPick a song:\n\n"
    buttons = []
    for i, r in enumerate(results[:6], 1):
        text += f"**{i}.** {r['title'][:45]} — ⏱ {r['duration']}\n"
        buttons.append([
            InlineKeyboardButton(
                f"🎵 {i}. {r['title'][:30]}",
                callback_data=f"sr_{i-1}_{message.chat.id}_{message.from_user.id}"
            )
        ])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="sr_cancel")])

    db.update_setting(message.chat.id, f"search_{message.from_user.id}", results)
    await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex(r"^sr_(\d+)_(-?\d+)_(\d+)$"))
async def search_result_callback(client: Client, query: CallbackQuery):
    idx = int(query.matches[0].group(1))
    chat_id = int(query.matches[0].group(2))
    user_id = int(query.matches[0].group(3))

    if query.from_user.id != user_id:
        return await query.answer("❌ This is not your search!", show_alert=True)

    results = db.get_settings(chat_id).get(f"search_{user_id}", [])
    if not results or idx >= len(results):
        return await query.answer("❌ Search results expired.", show_alert=True)

    chosen = results[idx]
    await query.message.delete()

    from KanhaMusic.utils import get_youtube_info, get_stream_url
    info = await get_youtube_info(chosen["url"])
    if not info:
        await client.send_message(chat_id, "❌ Could not fetch track info.")
        return

    if db.is_active(chat_id):
        db.add_to_queue(chat_id, info)
        pos = len(db.get_queue(chat_id))
        await client.send_message(
            chat_id,
            f"📋 **Added to Queue** — Position #{pos}\n🎵 **{info['title'][:50]}**"
        )
        return await query.answer()

    try:
        from pytgcalls.types.input_stream import AudioPiped
        from KanhaMusic import call_py

        stream_url = await get_stream_url(info["url"])
        if not stream_url:
            await client.send_message(chat_id, "❌ Could not get stream URL.")
            return

        db.add_active(chat_id, info)
        await call_py.join_group_call(chat_id, AudioPiped(stream_url), stream_type=None)

        from KanhaMusic.utils.thumbnails import get_thumb
        import os
        thumb = await get_thumb(
            info["title"], info.get("channel", ""), info.get("duration", ""),
            query.from_user.first_name, info.get("thumbnail"), info.get("id", "")
        )
        cap = (
            f"🎵 **Now Playing**\n\n**{info['title'][:50]}**\n"
            f"⏱ {info.get('duration', '?')} | 👤 {query.from_user.first_name}"
        )
        if thumb and os.path.exists(thumb):
            await client.send_photo(chat_id, thumb, caption=cap)
        else:
            await client.send_message(chat_id, cap)
    except Exception as e:
        await client.send_message(chat_id, f"❌ Error: {e}")
        db.remove_active(chat_id)

    await query.answer()


@Client.on_callback_query(filters.regex(r"^sr_cancel$"))
async def search_cancel(client: Client, query: CallbackQuery):
    await query.message.delete()
    await query.answer("Cancelled ✅")
