"""
In-memory database for KanhaMusic.
Handles active streams, queues, auth users, and settings per group.
"""

from typing import Dict, List


class InMemoryDB:
    def __init__(self):
        self.active_chats: Dict[int, dict] = {}
        self.queues: Dict[int, list] = {}
        self.loop: Dict[int, int] = {}
        self.pause: Dict[int, bool] = {}
        self.mute: Dict[int, bool] = {}
        self.volume: Dict[int, int] = {}
        self.auth_users: Dict[int, list] = {}
        self.gbanned_users: List[int] = []
        self.settings: Dict[int, dict] = {}

    # ── Active Chats ──────────────────────────────────────────────
    def is_active(self, chat_id: int) -> bool:
        return chat_id in self.active_chats

    def add_active(self, chat_id: int, data: dict):
        self.active_chats[chat_id] = data

    def remove_active(self, chat_id: int):
        self.active_chats.pop(chat_id, None)

    def get_active(self, chat_id: int) -> dict:
        return self.active_chats.get(chat_id, {})

    def get_all_active(self) -> dict:
        return self.active_chats

    # ── Queue ──────────────────────────────────────────────────────
    def get_queue(self, chat_id: int) -> list:
        return self.queues.get(chat_id, [])

    def add_to_queue(self, chat_id: int, item: dict):
        if chat_id not in self.queues:
            self.queues[chat_id] = []
        self.queues[chat_id].append(item)

    def clear_queue(self, chat_id: int):
        self.queues.pop(chat_id, None)

    def remove_from_queue(self, chat_id: int, index: int):
        q = self.queues.get(chat_id, [])
        if 0 <= index < len(q):
            q.pop(index)

    def shuffle_queue(self, chat_id: int):
        import random
        q = self.queues.get(chat_id, [])
        random.shuffle(q)
        self.queues[chat_id] = q

    # ── Loop ──────────────────────────────────────────────────────
    def get_loop(self, chat_id: int) -> int:
        return self.loop.get(chat_id, 0)

    def set_loop(self, chat_id: int, mode: int):
        self.loop[chat_id] = mode

    # ── Pause / Mute ──────────────────────────────────────────────
    def is_paused(self, chat_id: int) -> bool:
        return self.pause.get(chat_id, False)

    def set_pause(self, chat_id: int, state: bool):
        self.pause[chat_id] = state

    def is_muted(self, chat_id: int) -> bool:
        return self.mute.get(chat_id, False)

    def set_mute(self, chat_id: int, state: bool):
        self.mute[chat_id] = state

    # ── Volume ────────────────────────────────────────────────────
    def get_volume(self, chat_id: int) -> int:
        return self.volume.get(chat_id, 100)

    def set_volume(self, chat_id: int, vol: int):
        self.volume[chat_id] = vol

    # ── Auth Users ────────────────────────────────────────────────
    def get_auth_users(self, chat_id: int) -> list:
        return self.auth_users.get(chat_id, [])

    def add_auth_user(self, chat_id: int, user_id: int):
        if chat_id not in self.auth_users:
            self.auth_users[chat_id] = []
        if user_id not in self.auth_users[chat_id]:
            self.auth_users[chat_id].append(user_id)

    def remove_auth_user(self, chat_id: int, user_id: int):
        users = self.auth_users.get(chat_id, [])
        if user_id in users:
            users.remove(user_id)

    def is_auth_user(self, chat_id: int, user_id: int) -> bool:
        return user_id in self.auth_users.get(chat_id, [])

    # ── Global Ban ────────────────────────────────────────────────
    def is_gbanned(self, user_id: int) -> bool:
        return user_id in self.gbanned_users

    def gban_user(self, user_id: int):
        if user_id not in self.gbanned_users:
            self.gbanned_users.append(user_id)

    def ungban_user(self, user_id: int):
        if user_id in self.gbanned_users:
            self.gbanned_users.remove(user_id)

    # ── Settings ──────────────────────────────────────────────────
    def get_settings(self, chat_id: int) -> dict:
        return self.settings.get(chat_id, {
            "playmode": "direct",
            "lang": "en",
        })

    def update_setting(self, chat_id: int, key: str, value):
        if chat_id not in self.settings:
            self.settings[chat_id] = {}
        self.settings[chat_id][key] = value


db = InMemoryDB()
