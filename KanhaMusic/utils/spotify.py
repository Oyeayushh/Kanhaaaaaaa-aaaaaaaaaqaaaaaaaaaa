"""
Spotify utility for KanhaMusic.
Fetches track/playlist/album info from Spotify and maps to YouTube for playback.
"""

import asyncio
import re
from typing import Optional, List

SPOTIFY_ENABLED = False
sp = None

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    from KanhaMusic.config import Config

    if Config.SPOTIFY_CLIENT_ID and Config.SPOTIFY_CLIENT_SECRET:
        auth_manager = SpotifyClientCredentials(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        SPOTIFY_ENABLED = True
except Exception as e:
    print(f"Spotify not configured: {e}")


def _extract_spotify_id(url: str, kind: str) -> Optional[str]:
    pattern = rf"spotify\.com/{kind}/([A-Za-z0-9]+)"
    m = re.search(pattern, url)
    return m.group(1) if m else None


def is_spotify_url(url: str) -> bool:
    return "open.spotify.com" in url


def get_spotify_url_type(url: str) -> Optional[str]:
    if "track" in url:
        return "track"
    if "playlist" in url:
        return "playlist"
    if "album" in url:
        return "album"
    return None


async def get_spotify_track(url: str) -> Optional[dict]:
    if not SPOTIFY_ENABLED or not sp:
        return None
    try:
        track_id = _extract_spotify_id(url, "track")
        if not track_id:
            return None
        track = await asyncio.get_event_loop().run_in_executor(
            None, lambda: sp.track(track_id)
        )
        artists = ", ".join(a["name"] for a in track["artists"])
        return {
            "title": f"{track['name']} {artists}",
            "duration_sec": track["duration_ms"] // 1000,
            "thumbnail": track["album"]["images"][0]["url"] if track["album"]["images"] else "",
            "query": f"{track['name']} {artists}",
        }
    except Exception as e:
        print(f"Spotify track error: {e}")
        return None


async def get_spotify_playlist(url: str, limit: int = 25) -> List[dict]:
    if not SPOTIFY_ENABLED or not sp:
        return []
    try:
        playlist_id = _extract_spotify_id(url, "playlist")
        if not playlist_id:
            return []
        results = await asyncio.get_event_loop().run_in_executor(
            None, lambda: sp.playlist_tracks(playlist_id, limit=limit)
        )
        tracks = []
        for item in results.get("items", []):
            t = item.get("track")
            if not t:
                continue
            artists = ", ".join(a["name"] for a in t["artists"])
            tracks.append({
                "title": f"{t['name']} {artists}",
                "query": f"{t['name']} {artists}",
                "duration_sec": t["duration_ms"] // 1000,
                "thumbnail": t["album"]["images"][0]["url"] if t["album"]["images"] else "",
            })
        return tracks
    except Exception as e:
        print(f"Spotify playlist error: {e}")
        return []


async def get_spotify_album(url: str, limit: int = 25) -> List[dict]:
    if not SPOTIFY_ENABLED or not sp:
        return []
    try:
        album_id = _extract_spotify_id(url, "album")
        if not album_id:
            return []
        album = await asyncio.get_event_loop().run_in_executor(
            None, lambda: sp.album_tracks(album_id, limit=limit)
        )
        tracks = []
        for t in album.get("items", []):
            artists = ", ".join(a["name"] for a in t["artists"])
            tracks.append({
                "title": f"{t['name']} {artists}",
                "query": f"{t['name']} {artists}",
                "duration_sec": t["duration_ms"] // 1000,
                "thumbnail": "",
            })
        return tracks
    except Exception as e:
        print(f"Spotify album error: {e}")
        return []
