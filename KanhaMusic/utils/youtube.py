"""
YouTube search and download utilities for KanhaMusic.
Uses yt-dlp for downloading and youtubesearchpython for search.
"""

import asyncio
import os
import re
import time
from typing import Optional, Tuple, Union

import aiohttp
import yt_dlp

COOKIES_PATH = "cookies.txt"


def is_youtube_url(url: str) -> bool:
    pattern = re.compile(
        r"(https?://)?(www\.)?"
        r"(youtube\.com/(watch\?v=|playlist\?list=|shorts/)|youtu\.be/)"
        r"[\w\-]+"
    )
    return bool(pattern.match(url))


def is_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


async def search_youtube(query: str, limit: int = 5) -> list:
    """Search YouTube and return list of results."""
    try:
        from youtubesearchpython import VideosSearch
        results = await asyncio.get_event_loop().run_in_executor(
            None, lambda: VideosSearch(query, limit=limit).result()
        )
        items = results.get("result", [])
        formatted = []
        for item in items:
            dur = item.get("duration") or "0:00"
            formatted.append({
                "title": item.get("title", "Unknown"),
                "url": item.get("link", ""),
                "duration": dur,
                "thumbnail": (item.get("thumbnails") or [{}])[0].get("url", ""),
                "channel": (item.get("channel") or {}).get("name", "Unknown"),
                "views": item.get("viewCount", {}).get("short", "N/A"),
            })
        return formatted
    except Exception as e:
        print(f"YouTube search error: {e}")
        return []


def _ydl_opts(audio_only: bool = True, output_path: str = "downloads") -> dict:
    opts = {
        "format": "bestaudio/best" if audio_only else "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "outtmpl": f"{output_path}/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "prefer_ffmpeg": True,
        "postprocessors": [],
    }
    if audio_only:
        opts["postprocessors"].append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        })
    if os.path.exists(COOKIES_PATH):
        opts["cookiefile"] = COOKIES_PATH
    return opts


async def get_youtube_info(url_or_query: str) -> Optional[dict]:
    """Get info dict from YouTube URL or search query."""
    try:
        if not is_url(url_or_query):
            results = await search_youtube(url_or_query, limit=1)
            if not results:
                return None
            url_or_query = results[0]["url"]

        def _fetch():
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "noplaylist": True}) as ydl:
                return ydl.extract_info(url_or_query, download=False)

        info = await asyncio.get_event_loop().run_in_executor(None, _fetch)
        if not info:
            return None

        duration_secs = info.get("duration", 0)
        minutes, seconds = divmod(duration_secs, 60)
        return {
            "title": info.get("title", "Unknown Title"),
            "url": info.get("webpage_url", url_or_query),
            "duration": f"{minutes}:{seconds:02d}",
            "duration_sec": duration_secs,
            "thumbnail": info.get("thumbnail", ""),
            "channel": info.get("uploader", "Unknown"),
            "views": info.get("view_count", 0),
            "id": info.get("id", ""),
        }
    except Exception as e:
        print(f"get_youtube_info error: {e}")
        return None


async def download_audio(url: str, output_path: str = "downloads") -> Optional[str]:
    """Download audio from YouTube URL. Returns file path."""
    os.makedirs(output_path, exist_ok=True)
    try:
        opts = _ydl_opts(audio_only=True, output_path=output_path)

        def _download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                ext = "mp3"
                path = f"{output_path}/{info['id']}.{ext}"
                return path

        path = await asyncio.get_event_loop().run_in_executor(None, _download)
        return path if os.path.exists(path) else None
    except Exception as e:
        print(f"download_audio error: {e}")
        return None


async def download_video(url: str, output_path: str = "downloads") -> Optional[str]:
    """Download video from YouTube URL. Returns file path."""
    os.makedirs(output_path, exist_ok=True)
    try:
        opts = _ydl_opts(audio_only=False, output_path=output_path)
        opts["outtmpl"] = f"{output_path}/%(id)s.%(ext)s"

        def _download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)

        path = await asyncio.get_event_loop().run_in_executor(None, _download)
        return path if os.path.exists(path) else None
    except Exception as e:
        print(f"download_video error: {e}")
        return None


async def get_stream_url(url: str) -> Optional[str]:
    """Get a direct stream URL (for pytgcalls streaming)."""
    try:
        def _fetch():
            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "geo_bypass": True,
            }
            if os.path.exists(COOKIES_PATH):
                ydl_opts["cookiefile"] = COOKIES_PATH
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get("formats", [])
                for f in reversed(formats):
                    if f.get("acodec") != "none" and f.get("url"):
                        return f["url"]
                return info.get("url")

        return await asyncio.get_event_loop().run_in_executor(None, _fetch)
    except Exception as e:
        print(f"get_stream_url error: {e}")
        return None
