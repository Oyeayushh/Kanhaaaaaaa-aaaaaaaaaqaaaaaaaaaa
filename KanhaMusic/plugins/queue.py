"""
Queue management: /queue, /clearqueue, /queueskip, /remove
"""

from pyrogram import Client, filters
from pyrogram.types import Message

from KanhaMusic.core.call import call_py
from KanhaMusic.database import db
from KanhaMusic.strings import get_string
from KanhaMusic.utils import get_stream_url, change_audio, admin_or_auth, check_blacklist


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
            text += f"`{i}.` {item.get('title', 'Unknown')[:40]} — ⏱ {item.get('duration', '?')}\n"
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

    stream_url = await get_stream_url(next_track["url"])
    if not stream_url:
        return await message.reply_text("❌ Could not fetch stream URL.")

    ok = await change_audio(chat_id, stream_url)
    if ok:
        db.add_active(chat_id, next_track)
        db.set_pause(chat_id, False)
        await message.reply_text(
            f"⏭ Skipped to position **#{pos + 1}**!\n\n"
            f"🎵 **Now Playing:** {next_track.get('title', 'Unknown')[:50]}\n"
            f"⏱ Duration: {next_track.get('duration', '0:00')}"
        )
    else:
        await message.reply_text("❌ Could not switch track. Try again.")


@Client.on_message(filters.command(["remove", "rm"]) & filters.group)
@check_blacklist
@admin_or_auth
async def remove_command(client: Client, message: Message):
    """Remove a specific song from queue by position."""
    chat_id = message.chat.id
    queue = db.get_queue(chat_id)
    if not queue:
        return await message.reply_text(get_string["queue_empty"])

    args = message.command[1:]
    if not args:
        return await message.reply_text(
            "❌ Provide the position to remove.\n**Usage:** `/remove [number]`"
        )
    try:
        pos = int(args[0]) - 1
        if not 0 <= pos < len(queue):
            raise ValueError
    except ValueError:
        return await message.reply_text(f"❌ Invalid position. Queue has **{len(queue)}** songs.")

    removed = queue.pop(pos)
    db.queues[chat_id] = queue
    await message.reply_text(
        f"🗑 **Removed from queue:**\n"
        f"🎵 {removed.get('title', 'Unknown')[:50]}\n"
        f"⏱ {removed.get('duration', '?')}"
    )
