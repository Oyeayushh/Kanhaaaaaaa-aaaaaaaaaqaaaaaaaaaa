"""
KanhaMusic — Entry point.
Stream-end handler uses kanhaCall (core/call.py).
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
    if not Config.BOT_TOKEN:      missing.append("BOT_TOKEN")
    if not Config.API_ID:         missing.append("API_ID")
    if not Config.API_HASH:       missing.append("API_HASH")
    if not Config.STRING_SESSION: missing.append("STRING_SESSION")
    if missing:
        print(
            f"{Fore.RED}❌ Missing required config values:{Style.RESET_ALL}\n"
            + "\n".join(f"  • {m}" for m in missing)
            + f"\n\n{Fore.YELLOW}Please set them as environment variables / Replit Secrets.{Style.RESET_ALL}"
        )
        sys.exit(1)


# ─── Stream-End Handler ───────────────────────────────────────────────────────
# Priority chain when a song ends:
#   1. Loop = 1  → replay same song
#   2. Queue     → play next queued song
#   3. Loop = 2  → queue-loop (re-add finished song, play next)
#   4. Autoplay  → fetch related song from YouTube
#   5. Stop      → leave VC

async def _handle_stream_end(chat_id: int):
    from KanhaMusic import app
    from KanhaMusic.core.call import kanhaCall
    from KanhaMusic.database import db
    from KanhaMusic.utils.youtube import get_stream_url
    from KanhaMusic.utils.thumbnails import get_thumb

    current = db.get_active(chat_id)
    queue   = db.get_queue(chat_id)
    loop    = db.get_loop(chat_id)

    async def _play_track(info: dict, label: str = "🎵") -> bool:
        """Get stream URL, change stream, send now-playing card."""
        stream_url = await get_stream_url(info["url"])
        if not stream_url:
            logger.warning(f"[StreamEnd] No URL for: {info.get('title')}")
            return False
        ok = await kanhaCall.change_stream(chat_id, stream_url)
        if not ok:
            return False
        db.add_active(chat_id, info)
        db.set_pause(chat_id, False)
        try:
            thumb = await get_thumb(
                song_title=info.get("title", "Unknown"),
                artist=info.get("channel", "Unknown"),
                duration=info.get("duration", "0:00"),
                requested_by="Autoplay 🔄",
                song_thumb_url=info.get("thumbnail"),
                video_id=info.get("id", ""),
            )
            caption = (
                f"{label}\n\n"
                f"🎵 **{info.get('title', 'Unknown')[:50]}**\n"
                f"🎤 {info.get('channel', 'Unknown')[:30]}\n"
                f"⏱ {info.get('duration', '0:00')}"
            )
            if thumb and os.path.exists(thumb):
                await app.send_photo(chat_id, thumb, caption=caption)
            else:
                await app.send_message(chat_id, caption)
        except Exception as e:
            logger.warning(f"[StreamEnd] Card send error: {e}")
        return True

    async def _stop():
        await kanhaCall.leave_call(chat_id)
        db.remove_active(chat_id)
        db.clear_queue(chat_id)

    # 1. Single-song loop
    if loop == 1 and current:
        logger.info(f"[StreamEnd] Loop — replaying: {current.get('title')}")
        if await _play_track(current, "🔁 **Loop**"):
            return

    # 2. Play next from queue
    if queue:
        next_track = queue.pop(0)
        db.queues[chat_id] = queue
        if loop == 2 and current:
            db.add_to_queue(chat_id, current)
        logger.info(f"[StreamEnd] Queue → {next_track.get('title')}")
        if await _play_track(next_track, "📋 **Queue**"):
            return

    # 3. Queue-loop restart (queue was empty, re-add last song)
    if loop == 2 and current and not queue:
        logger.info("[StreamEnd] Queue-loop restart")
        if await _play_track(current, "🔁 **Queue Loop**"):
            return

    # 4. Autoplay — find related song
    from KanhaMusic.plugins.autoplay import is_autoplay_on
    if is_autoplay_on(chat_id) and current:
        logger.info(f"[StreamEnd] Autoplay → searching for: {current.get('title')}")
        try:
            from KanhaMusic.utils.autoplay import get_related_track
            related = await get_related_track(
                title=current.get("title", ""),
                artist=current.get("channel", ""),
                current_url=current.get("url", ""),
            )
            if related:
                logger.info(f"[StreamEnd] Autoplay → {related.get('title')}")
                if await _play_track(related, "🔄 **Autoplay**"):
                    return
        except Exception as e:
            logger.error(f"[StreamEnd] Autoplay error: {e}")

    # 5. Nothing left — leave VC
    logger.info(f"[StreamEnd] Stream ended in {chat_id}, leaving VC.")
    await _stop()


async def start_bot():
    from KanhaMusic import app, assistant
    from KanhaMusic.core.call import call_py, kanhaCall
    from KanhaMusic.config import Config
    from KanhaMusic.utils.thumbnails import ensure_brand_thumb
    from pytgcalls import PyTgCalls

    print(BANNER)
    logger.info("Starting KanhaMusic...")

    await ensure_brand_thumb()

    # Register stream-end event on the raw PyTgCalls instance
    @call_py.on_stream_end()
    async def stream_end_handler(client: PyTgCalls, update):
        try:
            await _handle_stream_end(update.chat_id)
        except Exception as e:
            logger.error(f"[StreamEnd] Unhandled: {e}")

    logger.info("Starting assistant (userbot)...")
    await assistant.start()
    me_assistant = await assistant.get_me()
    logger.info(f"Assistant ready: @{me_assistant.username}")

    logger.info("Starting PyTgCalls (call engine)...")
    await call_py.start()

    logger.info("Starting main bot...")
    await app.start()
    me = await app.get_me()

    print(
        f"\n{Fore.GREEN}✅  KanhaMusic is LIVE!{Style.RESET_ALL}\n"
        f"\n"
        f"{Fore.CYAN}  🤖  Bot:{Style.RESET_ALL}       @{me.username}\n"
        f"{Fore.CYAN}  🎙  Assistant:{Style.RESET_ALL}  @{me_assistant.username}\n"
        f"{Fore.CYAN}  👑  Owner ID:{Style.RESET_ALL}   {Config.OWNER_ID}\n"
        f"\n"
        f"{Fore.YELLOW}  📞  call.py  →  KanhaMusic/core/call.py{Style.RESET_ALL}\n"
        f"{Fore.YELLOW}  🔧  kanhaCall → join | leave | change | pause | volume{Style.RESET_ALL}\n"
        f"{Fore.YELLOW}  🔄  Autoplay → per-group smart autoplay{Style.RESET_ALL}\n"
    )

    if Config.LOG_GROUP_ID:
        try:
            await app.send_message(
                Config.LOG_GROUP_ID,
                f"✅ **KanhaMusic Started!**\n\n"
                f"🤖 **Bot:** @{me.username}\n"
                f"🎙 **Assistant:** @{me_assistant.username}\n"
                f"📞 **Engine:** `KanhaMusic/core/call.py` → `kanhaCall`\n"
                f"⚡ All systems operational!"
            )
        except Exception as e:
            logger.warning(f"Log message failed: {e}")

    await asyncio.Event().wait()


async def stop_bot():
    logger.info("Stopping KanhaMusic...")
    from KanhaMusic import app, assistant
    from KanhaMusic.core.call import call_py
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
