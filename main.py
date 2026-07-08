"""
KanhaMusic — Entry point.
Registers the stream-end handler (autoplay / queue / loop logic lives here).
"""

import asyncio
import logging
import os
import sys

from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

BANNER = f"""
{Fore.CYAN}╔════════════════════════════════════════════╗
{Fore.CYAN}║       {Fore.YELLOW}🎵  K A N H A M U S I C  🎵       {Fore.CYAN}║
{Fore.CYAN}║  {Fore.WHITE}Telegram Music Bot — Professional Edition  {Fore.CYAN}║
{Fore.CYAN}╚════════════════════════════════════════════╝{Style.RESET_ALL}
"""

logger = logging.getLogger("KanhaMusic.main")


def check_config():
    from KanhaMusic.config import Config
    missing = []
    if not Config.BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not Config.API_ID:
        missing.append("API_ID")
    if not Config.API_HASH:
        missing.append("API_HASH")
    if not Config.STRING_SESSION:
        missing.append("STRING_SESSION")
    if missing:
        print(
            f"{Fore.RED}❌ Missing required config values:{Style.RESET_ALL}\n"
            + "\n".join(f"  • {m}" for m in missing)
            + f"\n\n{Fore.YELLOW}Please set them in your config.py or as environment variables.{Style.RESET_ALL}"
        )
        sys.exit(1)


# ─── Stream-End Handler ──────────────────────────────────────────────────────
# Registered here (after call_py is created) so it has access to app, call_py.
# Order of operations when a song ends:
#   1. Loop mode = 1  → replay same song
#   2. Queue not empty → play next queued song
#   3. Loop mode = 2  → re-add last song to queue end and repeat from step 2
#   4. Autoplay = on  → fetch a related song and play it
#   5. Otherwise      → clean up and leave VC

async def _handle_stream_end(chat_id: int):
    from KanhaMusic import app, call_py
    from KanhaMusic.database import db
    from KanhaMusic.utils.youtube import get_stream_url
    from KanhaMusic.utils.thumbnails import get_thumb
    from pytgcalls.types.input_stream import AudioPiped

    current = db.get_active(chat_id)
    queue   = db.get_queue(chat_id)
    loop    = db.get_loop(chat_id)

    async def _play_track(info: dict, label: str = ""):
        """Stream a track and send a now-playing card."""
        stream_url = await get_stream_url(info["url"])
        if not stream_url:
            logger.warning(f"[StreamEnd] Could not get stream URL for {info.get('title')}")
            return False
        try:
            await call_py.change_stream(chat_id, AudioPiped(stream_url))
            db.add_active(chat_id, info)
            db.set_pause(chat_id, False)

            thumb = await get_thumb(
                song_title=info.get("title", "Unknown"),
                artist=info.get("channel", "Unknown"),
                duration=info.get("duration", "0:00"),
                requested_by="Autoplay 🔄" if not label else label,
                song_thumb_url=info.get("thumbnail"),
                video_id=info.get("id", ""),
            )
            caption = (
                f"{'🔄 **Autoplay**' if not label else label}\n\n"
                f"🎵 **{info.get('title', 'Unknown')[:50]}**\n"
                f"🎤 {info.get('channel', 'Unknown')[:30]}\n"
                f"⏱ {info.get('duration', '0:00')}"
            )
            if thumb and os.path.exists(thumb):
                await app.send_photo(chat_id, thumb, caption=caption)
            else:
                await app.send_message(chat_id, caption)
            return True
        except Exception as e:
            logger.error(f"[StreamEnd] Play error: {e}")
            return False

    async def _stop():
        try:
            await call_py.leave_group_call(chat_id)
        except Exception:
            pass
        db.remove_active(chat_id)
        db.clear_queue(chat_id)

    # ── 1. Single-song loop ──────────────────────────────────────────────────
    if loop == 1 and current:
        logger.info(f"[StreamEnd] Loop mode — replaying: {current.get('title')}")
        ok = await _play_track(current, "🔁 **Loop**")
        if ok:
            return

    # ── 2. Play from queue ───────────────────────────────────────────────────
    if queue:
        next_track = queue.pop(0)
        db.queues[chat_id] = queue

        # Queue-loop: push the finished song back to the end
        if loop == 2 and current:
            db.add_to_queue(chat_id, current)

        logger.info(f"[StreamEnd] Queue → playing: {next_track.get('title')}")
        ok = await _play_track(next_track, "📋 **Queue**")
        if ok:
            return

    # ── 3. Queue-loop with no remaining queue (re-add last song) ────────────
    if loop == 2 and current and not queue:
        logger.info("[StreamEnd] Queue-loop restart")
        ok = await _play_track(current, "🔁 **Queue Loop**")
        if ok:
            return

    # ── 4. Autoplay ──────────────────────────────────────────────────────────
    from KanhaMusic.plugins.autoplay import is_autoplay_on
    if is_autoplay_on(chat_id) and current:
        logger.info(f"[StreamEnd] Autoplay fetching related song for: {current.get('title')}")
        try:
            from KanhaMusic.utils.autoplay import get_related_track
            related = await get_related_track(
                title=current.get("title", ""),
                artist=current.get("channel", ""),
                current_url=current.get("url", ""),
            )
            if related:
                logger.info(f"[StreamEnd] Autoplay → {related.get('title')}")
                ok = await _play_track(related, "🔄 **Autoplay**")
                if ok:
                    return
        except Exception as e:
            logger.error(f"[StreamEnd] Autoplay error: {e}")

    # ── 5. Nothing left — leave VC ───────────────────────────────────────────
    logger.info(f"[StreamEnd] Stream ended in {chat_id}, leaving VC.")
    await _stop()


async def start_bot():
    from KanhaMusic import app, assistant, call_py
    from KanhaMusic.config import Config
    from KanhaMusic.utils.thumbnails import ensure_brand_thumb
    from pytgcalls import PyTgCalls

    print(BANNER)
    logger.info("Starting KanhaMusic...")

    await ensure_brand_thumb()

    # ── Register stream-end event ────────────────────────────────────────────
    @call_py.on_stream_end()
    async def stream_end_handler(client: PyTgCalls, update):
        """Fired by pytgcalls when a stream finishes."""
        try:
            chat_id = update.chat_id
            await _handle_stream_end(chat_id)
        except Exception as e:
            logger.error(f"[StreamEnd] Unhandled error: {e}")

    # ── Start services ───────────────────────────────────────────────────────
    logger.info("Starting assistant client...")
    await assistant.start()
    me_assistant = await assistant.get_me()
    logger.info(f"Assistant ready: @{me_assistant.username}")

    logger.info("Starting PyTgCalls...")
    await call_py.start()

    logger.info("Starting main bot...")
    await app.start()
    me = await app.get_me()

    print(
        f"\n{Fore.GREEN}✅ KanhaMusic is now running!{Style.RESET_ALL}\n"
        f"{Fore.CYAN}🤖 Bot:{Style.RESET_ALL} @{me.username}\n"
        f"{Fore.CYAN}🎙 Assistant:{Style.RESET_ALL} @{me_assistant.username}\n"
        f"{Fore.CYAN}👑 Owner ID:{Style.RESET_ALL} {Config.OWNER_ID}\n"
        f"{Fore.CYAN}🔄 Autoplay:{Style.RESET_ALL} Enabled (per-group toggle)\n"
    )

    if Config.LOG_GROUP_ID:
        try:
            await app.send_message(
                Config.LOG_GROUP_ID,
                f"✅ **KanhaMusic Started!**\n\n"
                f"🤖 **Bot:** @{me.username}\n"
                f"🎙 **Assistant:** @{me_assistant.username}\n"
                f"🔄 **Autoplay:** Ready\n"
                f"⚡ All systems operational!"
            )
        except Exception as e:
            logger.warning(f"Could not send log message: {e}")

    await asyncio.Event().wait()


async def stop_bot():
    logger.info("Stopping KanhaMusic...")
    from KanhaMusic import app, assistant, call_py
    for obj in (call_py, assistant, app):
        try:
            await obj.stop()
        except Exception:
            pass
    logger.info("KanhaMusic stopped.")


if __name__ == "__main__":
    check_config()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        loop.run_until_complete(stop_bot())
