"""
Video stream helpers — join/change group call with audio+video stream.
Uses pytgcalls v0.9.x API (AudioVideoPiped).
"""

from pytgcalls.types.input_stream import AudioVideoPiped

from KanhaMusic.core.call import call_py


async def stream_video(chat_id: int, url: str) -> bool:
    """Join a group voice chat and stream video+audio. Returns True on success."""
    try:
        await call_py.join_group_call(chat_id, AudioVideoPiped(url), stream_type=None)
        return True
    except Exception as e:
        from KanhaMusic import logger
        logger.error(f"[stream_video] chat={chat_id} error={e}")
        return False


async def change_video(chat_id: int, url: str) -> bool:
    """Change current stream to a new video+audio URL. Returns True on success."""
    try:
        await call_py.change_stream(chat_id, AudioVideoPiped(url))
        return True
    except Exception as e:
        from KanhaMusic import logger
        logger.error(f"[change_video] chat={chat_id} error={e}")
        return False
