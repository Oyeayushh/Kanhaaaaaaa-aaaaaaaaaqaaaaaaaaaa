"""
Queue management: /queue, /clearqueue, /queueskip
"""

from pyrogram import Client, filters
from pyrogram.types import Message

from KanhaMusic.database import db
from KanhaMusic.strings import get_string
from KanhaMusic.utils.decorators import admin_or_auth, check_blacklist


@Client.on_message(filters.command(["queue", "q"]) & filters.group)
@check_blacklist
async def queue_command(client: Client, message: Message):
    chat_id = message.chat.id
    queue = db.get_queue(chat_id)
    active = db.get_active(chat_id)

    if not active and not queue:
        return await message.reply_text(get_string["queue_empty"])

    text = "🎵 **KanhaMusic — Queue**\n\n"
    if active:
        text += (
            f"**▶️ Now Playing:**\n"
            f"┌ {active.get('title', 'Unknown')[:50]}\n"
            f"└ ⏱ {active.get('duration', '0:00')}\n\n"
        )
    if queue:
        text += f"**📋 Up Next ({len(queue)} tracks):**\n"
        for i, item in enumerate(queue[:15], 1):
            text += f"{i}. {item.get('title', 'Unknown')[:45]} — {item.get('duration', '?')}\n"
        if len(queue) > 15:
            text += f"\n_...and {len(queue) - 15} more tracks_"
    else:
        text += "📭 **Queue is empty after this song.**"

    await message.reply_text(text)


@Client.on_message(filters.command(["clearqueue", "cq"]) & filters.group)
@check_blacklist
@admin_or_auth
async def clearqueue_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not db.get_queue(chat_id):
        return await message.reply_text(get_string["queue_empty"])
    db.clear_queue(chat_id)
    await message.reply_text(get_string["queue_cleared"])


@Client.on_message(filters.command(["queueskip", "qs"]) & filters.group)
@check_blacklist
@admin_or_auth
async def queueskip_command(client: Client, message: Message):
    chat_id = message.chat.id
    queue = db.get_queue(chat_id)
    if not queue:
        return await message.reply_text(get_string["queue_empty"])

    args = message.command[1:]
    if not args:
        return await message.reply_text(
            "❌ Provide the queue position.\n**Usage:** `/queueskip [number]`"
        )
    try:
        pos = int(args[0]) - 1
        if not 0 <= pos < len(queue):
            raise ValueError
    except ValueError:
        return await message.reply_text(f"❌ Invalid position. Queue has **{len(queue)}** songs.")

    next_track = queue[pos]
    db.queues[chat_id] = queue[pos + 1:]

    try:
        from pytgcalls.types.input_stream import AudioPiped
        from KanhaMusic.utils import get_stream_url
        from KanhaMusic import call_py

        stream_url = await get_stream_url(next_track["url"])
        if stream_url:
            await call_py.change_stream(chat_id, AudioPiped(stream_url))
            db.add_active(chat_id, next_track)
            await message.reply_text(
                f"⏭ Skipped **{pos + 1}** track(s)!\n\n"
                f"🎵 **Now Playing:** {next_track.get('title', 'Unknown')[:50]}\n"
                f"⏱ Duration: {next_track.get('duration', '0:00')}"
            )
        else:
            await message.reply_text("❌ Could not load the track.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
