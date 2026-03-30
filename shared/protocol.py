"""Spolocne definicie pre host aj viewer."""

import json
from enum import Enum


class MessageType(Enum):
    # Registracia
    HOST_REGISTER = "host_register"
    SESSION_CREATED = "session_created"
    VIEWER_CONNECT = "viewer_connect"
    CONNECT_SUCCESS = "connect_success"
    VIEWER_JOINED = "viewer_joined"
    PEER_DISCONNECTED = "peer_disconnected"

    # Snimky
    FRAME_FULL = "frame_full"
    FRAME_DELTA = "frame_delta"

    # Vstup
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    MOUSE_SCROLL = "mouse_scroll"
    KEY_EVENT = "key_event"
    KEY_COMBO = "key_combo"

    # System
    PING = "ping"
    PONG = "pong"
    QUALITY_CHANGE = "quality_change"
    ERROR = "error"


ALLOWED_KEYS = {
    # Letters
    *"abcdefghijklmnopqrstuvwxyz",
    # Numbers
    *"0123456789",
    # Modifiers
    "shift", "ctrl", "alt", "cmd", "win", "meta",
    "shiftleft", "shiftright", "ctrlleft", "ctrlright",
    "altleft", "altright",
    # Navigation
    "enter", "return", "tab", "space", "backspace", "delete",
    "escape", "esc",
    "up", "down", "left", "right",
    "home", "end", "pageup", "pagedown",
    # Function keys
    "f1", "f2", "f3", "f4", "f5", "f6",
    "f7", "f8", "f9", "f10", "f11", "f12",
    # Punctuation
    "period", "comma", "slash", "backslash",
    "semicolon", "apostrophe", "bracketleft", "bracketright",
    "minus", "equal", "grave",
    # Special
    "capslock", "numlock", "scrolllock",
    "printscreen", "insert", "pause",
    "volumeup", "volumedown", "volumemute",
}

VALID_BUTTONS = {"left", "right", "middle"}
VALID_CLICK_ACTIONS = {"click", "double", "down", "up"}
VALID_KEY_ACTIONS = {"press", "down", "up"}


def create_message(msg_type: MessageType, **kwargs) -> str:
    """Vytvor JSON spravu."""
    return json.dumps({"type": msg_type.value, **kwargs})


def parse_message(raw: str) -> dict:
    """Parsuj JSON spravu s validaciou."""
    msg = json.loads(raw)
    if "type" not in msg:
        raise ValueError("Missing 'type' field")
    return msg


def validate_mouse_coords(x: float, y: float) -> bool:
    return 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0


def validate_key(key: str) -> bool:
    """Skontroluj ci je klavesa povolena."""
    return key.lower() in ALLOWED_KEYS


def validate_button(button: str) -> bool:
    return button in VALID_BUTTONS


def validate_click_action(action: str) -> bool:
    return action in VALID_CLICK_ACTIONS


def validate_key_action(action: str) -> bool:
    return action in VALID_KEY_ACTIONS
