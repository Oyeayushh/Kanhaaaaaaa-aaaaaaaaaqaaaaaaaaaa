"""
Playback controls: pause, resume, skip, stop, mute, unmute, volume, loop, shuffle
Uses kanhaCall (core/call.py) for all VC operations.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from KanhaMusic.core.call import kanhaCall
from KanhaMusic.database import db
from KanhaMusic.strings import get_string
from KanhaMusic.utils import get_stream_url, change_audio, admin_or_auth, check_blacklist


@Client.on_message(filters.command(["pause"]) & filters.group)
@check_blacklist
@admin_or_auth
async def pause_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not db.is_active(chat_id):
        return await message.reply_text(get_string["not_in_vc"])
    if db.is_paused(chat_id):
        return await message.reply_text(get_string["already_paused"])
    ok = await kanhaCall.pause_call(chat_id)
    if ok:
        db.set_pause(chat_id, True)
        await message.reply_text(get_string["music_paused"])
    else:
        await message.reply_text("❌ Could not pause. Try again.")


@Client.on_message(filters.command(["resume"]) & filters.group)
@check_blacklist
@admin_or_auth
async def resume_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not db.is_active(chat_id):
        return await message.reply_text(get_string["not_in_vc"])
    if not db.is_paused(chat_id):
        return await message.reply_text(get_string["already_playing"])
    ok = await kanhaCall.resume_call(chat_id)
    if ok:
        db.set_pause(chat_id, False)
        await message.reply_text(get_string["music_resumed"])
    else:
        await message.reply_text("❌ Could not resume. Try again.")


@Client.on_message(filters.command(["skip", "s"]) & filters.group)
@check_blacklist
@admin_or_auth
async def skip_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not db.is_active(chat_id):
        return await message.reply_text(get_string["not_in_vc"])

    queue = db.get_queue(chat_id)
    if not queue:
        await kanhaCall.leave_call(chat_id)
        db.remove_active(chat_id)
        db.clear_queue(chat_id)
        return await message.reply_text("⏹ No more songs in queue. Left voice chat.")

    next_track = queue.pop(0)
    db.queues[chat_id] = queue
    stream_url = await get_stream_url(next_track["url"])
    if not stream_url:
        return await message.reply_text("❌ Could not fetch stream URL for next track.")

    ok = await kanhaCall.change_stream(chat_id, stream_url)
    if ok:
        db.add_active(chat_id, next_track)
        db.set_pause(chat_id, False)
        await message.reply_text(
            f"⏭ **Skipped!**\n\n"
            f"🎵 **Now Playing:** {next_track.get('title', 'Unknown')[:50]}\n"
            f"⏱ Duration: {next_track.get('duration', '0:00')}"
        )
    else:
        await message.reply_text("❌ Skip error. Try again.")


@Client.on_message(filters.command(["stop", "end"]) & filters.group)
@check_blacklist
@admin_or_auth
async def stop_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not db.is_active(chat_id):
        return await message.reply_text(get_string["not_in_vc"])
    await kanhaCall.leave_call(chat_id)
    db.remove_active(chat_id)
    db.clear_queue(chat_id)
    db.set_pause(chat_id, False)
    await message.reply_text(get_string["music_stopped"])


@Client.on_message(filters.command(["mute"]) & filters.group)
@check_blacklist
@admin_or_auth
async def mute_command(client: Client, message: Message):
    chat_id = message.chat.id
    ok = await kanhaCall.mute_call(chat_id)
    if ok:
        db.set_mute(chat_id, True)
        await message.reply_text("🔇 Assistant has been **muted**.")
    else:
        await message.reply_text("❌ Could not mute. Is assistant in VC?")


@Client.on_message(filters.command(["unmute"]) & filters.group)
@check_blacklist
@admin_or_auth
async def unmute_command(client: Client, message: Message):
    chat_id = message.chat.id
    ok = await kanhaCall.unmute_call(chat_id)
    if ok:
        db.set_mute(chat_id, False)
        await message.reply_text("🔊 Assistant has been **unmuted**.")
    else:
        await message.reply_text("❌ Could not unmute. Is assistant in VC?")


@Client.on_message(filters.command(["volume", "vol", "v"]) & filters.group)
@check_blacklist
@admin_or_auth
async def volume_command(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.command[1:]
    if not args:
        current = db.get_volume(chat_id)
        return await message.reply_text(
            f"🔊 Current volume: **{current}%**\n\nUsage: `/volume [1-200]`"
        )
    try:
        vol = int(args[0])
        if not 1 <= vol <= 200:
            raise ValueError
    except ValueError:
        return await message.reply_text("❌ Volume must be between **1 and 200**.")

    await kanhaCall.volume_call(chat_id, vol)
    db.set_volume(chat_id, vol)
    await message.reply_text(get_string["volume_changed"].format(vol))


@Client.on_message(filters.command(["loop"]) & filters.group)
@check_blacklist
@admin_or_auth
async def loop_command(client: Client, message: Message):
    chat_id = message.chat.id
    new_mode = 0 if db.get_loop(chat_id) == 1 else 1
    db.set_loop(chat_id, new_mode)
    status = "**Enabled** 🔁" if new_mode == 1 else "**Disabled** ✅"
    await message.reply_text(get_string["looped"].format(status))


@Client.on_message(filters.command(["loopqueue", "lq"]) & filters.group)
@check_blacklist
@admin_or_auth
async def loopqueue_command(client: Client, message: Message):
    chat_id = message.chat.id
    new_mode = 0 if db.get_loop(chat_id) == 2 else 2
    db.set_loop(chat_id, new_mode)
    status = "**Queue Loop Enabled** 🔁" if new_mode == 2 else "**Queue Loop Disabled** ✅"
    await message.reply_text(get_string["looped"].format(status))


@Client.on_message(filters.command(["shuffle"]) & filters.group)
@check_blacklist
@admin_or_auth
async def shuffle_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not db.get_queue(chat_id):
        return await message.reply_text(get_string["queue_empty"])
    db.shuffle_queue(chat_id)
    await message.reply_text(get_string["shuffled"])


# ── Inline button callbacks ──────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r"^pause_(-?\d+)$"))
async def cb_pause(client: Client, query: CallbackQuery):
    chat_id = int(query.matches[0].group(1))
    ok = await kanhaCall.pause_call(chat_id)
    if ok:
        db.set_pause(chat_id, True)
    await query.answer("⏸ Paused!" if ok else "❌ Error", show_alert=False)


@Client.on_callback_query(filters.regex(r"^resume_(-?\d+)$"))
async def cb_resume(client: Client, query: CallbackQuery):
    chat_id = int(query.matches[0].group(1))
    ok = await kanhaCall.resume_call(chat_id)
    if ok:
        db.set_pause(chat_id, False)
    await query.answer("▶️ Resumed!" if ok else "❌ Error", show_alert=False)


@Client.on_callback_query(filters.regex(r"^skip_(-?\d+)$"))
async def cb_skip(client: Client, query: CallbackQuery):
    chat_id = int(query.matches[0].group(1))
    queue = db.get_queue(chat_id)
    if queue:
        try:
            next_track = queue.pop(0)
            db.queues[chat_id] = queue
            stream_url = await get_stream_url(next_track["url"])
            if stream_url:
                ok = await kanhaCall.change_stream(chat_id, stream_url)
                if ok:
                    db.add_active(chat_id, next_track)
                    db.set_pause(chat_id, False)
        except Exception:
            pass
    await query.answer("⏭ Skipped!", show_alert=False)


@Client.on_callback_query(filters.regex(r"^stop_(-?\d+)$"))
async def cb_stop(client: Client, query: CallbackQuery):
    chat_id = int(query.matches[0].group(1))
    await kanhaCall.leave_call(chat_id)
    db.remove_active(chat_id)
    db.clear_queue(chat_id)
    await query.answer("⏹ Stopped!", show_alert=False)
    try:
        await query.message.edit_caption("⏹ **Music stopped.**")
    except Exception:
        pass


@Client.on_callback_query(filters.regex(r"^loop_(-?\d+)$"))
async def cb_loop(client: Client, query: CallbackQuery):
    chat_id = int(query.matches[0].group(1))
    new_mode = 0 if db.get_loop(chat_id) == 1 else 1
    db.set_loop(chat_id, new_mode)
    await query.answer(f"Loop {'Enabled 🔁' if new_mode else 'Disabled ✅'}", show_alert=False)


@Client.on_callback_query(filters.regex(r"^shuffle_(-?\d+)$"))
async def cb_shuffle(client: Client, query: CallbackQuery):
    chat_id = int(query.matches[0].group(1))
    db.shuffle_queue(chat_id)
    await query.answer("🔀 Queue shuffled!", show_alert=False)


@Client.on_callback_query(filters.regex(r"^queue_(-?\d+)$"))
async def cb_queue(client: Client, query: CallbackQuery):
    chat_id = int(query.matches[0].group(1))
    queue = db.get_queue(chat_id)
    if not queue:
        return await query.answer("📭 Queue is empty!", show_alert=True)
    text = "📋 Queue:\n" + "".join(
        f"{i}. {item.get('title','?')[:35]}\n" for i, item in enumerate(queue[:10], 1)
    )
    if len(queue) > 10:
        text += f"...+{len(queue)-10} more"
    await query.answer(text[:200], show_alert=True)


@Client.on_callback_query(filters.regex(r"^volume_(-?\d+)$"))
async def cb_volume(client: Client, query: CallbackQuery):
    chat_id = int(query.matches[0].group(1))
    await query.answer(
        f"🔊 Volume: {db.get_volume(chat_id)}% — Use /volume [1-200]", show_alert=True
    )


@Client.on_callback_query(filters.regex(r"^close_(-?\d+)$"))
async def cb_close(client: Client, query: CallbackQuery):
    await query.message.delete()
    await query.answer("Closed ✅")
