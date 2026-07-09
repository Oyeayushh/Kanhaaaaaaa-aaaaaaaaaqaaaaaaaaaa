"""
Video stream helpers — join/change group call with audio+video stream.
Uses KanhaCall wrapper (core/call.py).
"""

from KanhaMusic.core.call import kanhaCall


async def stream_video(chat_id: int, url: str) -> bool:
    """Join a group voice chat and stream video+audio. Returns True on success."""
    return await kanhaCall.join_call(chat_id, url, video=True)


async def change_video(chat_id: int, url: str) -> bool:
    """Switch current stream to a new video+audio URL. Returns True on success."""
    return await kanhaCall.change_stream(chat_id, url, video=True)
