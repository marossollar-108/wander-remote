"""Vykonava prikazy mysi a klavesnice cez Quartz/CoreGraphics (macOS)."""

import logging
import platform
import time

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
from shared.protocol import (
    validate_mouse_coords,
    validate_key,
    validate_button,
    validate_click_action,
    validate_key_action,
)

logger = logging.getLogger(__name__)

# Detect platform
IS_MACOS = platform.system() == "Darwin"

if IS_MACOS:
    import Quartz
    from Quartz import (
        CGEventCreateMouseEvent,
        CGEventCreateScrollWheelEvent,
        CGEventCreateKeyboardEvent,
        CGEventPost,
        CGEventSetIntegerValueField,
        kCGEventMouseMoved,
        kCGEventLeftMouseDown,
        kCGEventLeftMouseUp,
        kCGEventRightMouseDown,
        kCGEventRightMouseUp,
        kCGEventOtherMouseDown,
        kCGEventOtherMouseUp,
        kCGEventLeftMouseDragged,
        kCGEventScrollWheel,
        kCGHIDEventTap,
        kCGMouseButtonLeft,
        kCGMouseButtonRight,
        kCGMouseButtonCenter,
        kCGScrollEventUnitLine,
        kCGKeyboardEventKeycode,
    )

    BUTTON_MAP = {
        "left": kCGMouseButtonLeft,
        "right": kCGMouseButtonRight,
        "middle": kCGMouseButtonCenter,
    }

    DOWN_EVENT = {
        "left": kCGEventLeftMouseDown,
        "right": kCGEventRightMouseDown,
        "middle": kCGEventOtherMouseDown,
    }

    UP_EVENT = {
        "left": kCGEventLeftMouseUp,
        "right": kCGEventRightMouseUp,
        "middle": kCGEventOtherMouseUp,
    }

    # macOS virtual keycodes
    KEYCODE_MAP = {
        "a": 0, "b": 11, "c": 8, "d": 2, "e": 14, "f": 3, "g": 5,
        "h": 4, "i": 34, "j": 38, "k": 40, "l": 37, "m": 46, "n": 45,
        "o": 31, "p": 35, "q": 12, "r": 15, "s": 1, "t": 17, "u": 32,
        "v": 9, "w": 13, "x": 7, "y": 16, "z": 6,
        "0": 29, "1": 18, "2": 19, "3": 20, "4": 21,
        "5": 23, "6": 22, "7": 26, "8": 28, "9": 25,
        "enter": 36, "return": 36, "tab": 48, "space": 49,
        "backspace": 51, "delete": 117, "escape": 53, "esc": 53,
        "up": 126, "down": 125, "left": 123, "right": 124,
        "home": 115, "end": 119, "pageup": 116, "pagedown": 121,
        "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "f6": 97,
        "f7": 98, "f8": 100, "f9": 101, "f10": 109, "f11": 103, "f12": 111,
        "shift": 56, "shiftleft": 56, "shiftright": 60,
        "ctrl": 59, "ctrlleft": 59, "ctrlright": 62,
        "alt": 58, "altleft": 58, "altright": 61,
        "cmd": 55, "meta": 55, "win": 55,
        "capslock": 57,
        "period": 47, "comma": 43, "slash": 44, "backslash": 42,
        "semicolon": 41, "apostrophe": 39,
        "bracketleft": 33, "bracketright": 30,
        "minus": 27, "equal": 24, "grave": 50,
    }
else:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0


class InputHandler:
    """Vykonava prikazy mysi a klavesnice."""

    def __init__(self, screen_width: int, screen_height: int, blocked_combos: list[list[str]] | None = None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.blocked_combos = [
            sorted(combo) for combo in (blocked_combos or [])
        ]
        self._input_count = 0
        self._input_window_start = time.monotonic()
        self._max_inputs_per_sec = 100
        self._last_pos = (0, 0)

    def _check_rate_limit(self) -> bool:
        now = time.monotonic()
        if now - self._input_window_start >= 1.0:
            self._input_count = 0
            self._input_window_start = now
        self._input_count += 1
        return self._input_count <= self._max_inputs_per_sec

    def _to_screen_coords(self, x_ratio: float, y_ratio: float) -> tuple[int, int]:
        x = int(x_ratio * self.screen_width)
        y = int(y_ratio * self.screen_height)
        return (
            max(0, min(x, self.screen_width - 1)),
            max(0, min(y, self.screen_height - 1)),
        )

    def _is_blocked_combo(self, keys: list[str]) -> bool:
        sorted_keys = sorted(k.lower() for k in keys)
        return sorted_keys in self.blocked_combos

    # ---- Mouse ----

    def move_mouse(self, x_ratio: float, y_ratio: float):
        if not self._check_rate_limit():
            return
        if not validate_mouse_coords(x_ratio, y_ratio):
            return
        x, y = self._to_screen_coords(x_ratio, y_ratio)
        self._last_pos = (x, y)

        if IS_MACOS:
            event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (x, y), kCGMouseButtonLeft)
            CGEventPost(kCGHIDEventTap, event)
        else:
            pyautogui.moveTo(x, y, _pause=False)

    def click(self, x_ratio: float, y_ratio: float, button: str, action: str):
        if not self._check_rate_limit():
            return
        if not validate_mouse_coords(x_ratio, y_ratio):
            return
        if not validate_button(button):
            return
        if not validate_click_action(action):
            return

        x, y = self._to_screen_coords(x_ratio, y_ratio)
        self._last_pos = (x, y)

        if IS_MACOS:
            btn = BUTTON_MAP.get(button, kCGMouseButtonLeft)
            down_type = DOWN_EVENT.get(button, kCGEventLeftMouseDown)
            up_type = UP_EVENT.get(button, kCGEventLeftMouseUp)

            if action == "click":
                down = CGEventCreateMouseEvent(None, down_type, (x, y), btn)
                CGEventPost(kCGHIDEventTap, down)
                up = CGEventCreateMouseEvent(None, up_type, (x, y), btn)
                CGEventPost(kCGHIDEventTap, up)
            elif action == "double":
                for click_num in (1, 2):
                    down = CGEventCreateMouseEvent(None, down_type, (x, y), btn)
                    CGEventSetIntegerValueField(down, Quartz.kCGMouseEventClickState, click_num)
                    CGEventPost(kCGHIDEventTap, down)
                    up = CGEventCreateMouseEvent(None, up_type, (x, y), btn)
                    CGEventSetIntegerValueField(up, Quartz.kCGMouseEventClickState, click_num)
                    CGEventPost(kCGHIDEventTap, up)
            elif action == "down":
                down = CGEventCreateMouseEvent(None, down_type, (x, y), btn)
                CGEventPost(kCGHIDEventTap, down)
            elif action == "up":
                up = CGEventCreateMouseEvent(None, up_type, (x, y), btn)
                CGEventPost(kCGHIDEventTap, up)
        else:
            pyautogui.moveTo(x, y, _pause=False)
            if action == "click":
                pyautogui.click(x, y, button=button, _pause=False)
            elif action == "double":
                pyautogui.doubleClick(x, y, button=button, _pause=False)
            elif action == "down":
                pyautogui.mouseDown(x, y, button=button, _pause=False)
            elif action == "up":
                pyautogui.mouseUp(x, y, button=button, _pause=False)

    def scroll(self, x_ratio: float, y_ratio: float, delta: int):
        if not self._check_rate_limit():
            return
        if not validate_mouse_coords(x_ratio, y_ratio):
            return
        x, y = self._to_screen_coords(x_ratio, y_ratio)

        if IS_MACOS:
            # Najprv presun mys
            move = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (x, y), kCGMouseButtonLeft)
            CGEventPost(kCGHIDEventTap, move)
            # Scroll
            scroll_event = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, int(-delta))
            CGEventPost(kCGHIDEventTap, scroll_event)
        else:
            pyautogui.moveTo(x, y, _pause=False)
            pyautogui.scroll(delta, x, y, _pause=False)

    # ---- Keyboard ----

    def key_press(self, key: str, action: str):
        if not self._check_rate_limit():
            return
        if not validate_key(key):
            return
        if not validate_key_action(action):
            return

        if IS_MACOS:
            keycode = KEYCODE_MAP.get(key.lower())
            if keycode is None:
                logger.warning("Unknown keycode for: %s", key)
                return
            if action == "press":
                down = CGEventCreateKeyboardEvent(None, keycode, True)
                CGEventPost(kCGHIDEventTap, down)
                up = CGEventCreateKeyboardEvent(None, keycode, False)
                CGEventPost(kCGHIDEventTap, up)
            elif action == "down":
                event = CGEventCreateKeyboardEvent(None, keycode, True)
                CGEventPost(kCGHIDEventTap, event)
            elif action == "up":
                event = CGEventCreateKeyboardEvent(None, keycode, False)
                CGEventPost(kCGHIDEventTap, event)
        else:
            if action == "press":
                pyautogui.press(key, _pause=False)
            elif action == "down":
                pyautogui.keyDown(key, _pause=False)
            elif action == "up":
                pyautogui.keyUp(key, _pause=False)

    def key_combo(self, keys: list[str]):
        if not self._check_rate_limit():
            return
        for key in keys:
            if not validate_key(key):
                return
        if self._is_blocked_combo(keys):
            logger.warning("Blocked key combo: %s", keys)
            return

        if IS_MACOS:
            # Stlac vsetky modifikatory, potom klavesu, potom pusti
            keycodes = []
            for key in keys:
                kc = KEYCODE_MAP.get(key.lower())
                if kc is None:
                    logger.warning("Unknown keycode in combo: %s", key)
                    return
                keycodes.append(kc)

            # Press all
            for kc in keycodes:
                event = CGEventCreateKeyboardEvent(None, kc, True)
                CGEventPost(kCGHIDEventTap, event)
            # Release all (reverse order)
            for kc in reversed(keycodes):
                event = CGEventCreateKeyboardEvent(None, kc, False)
                CGEventPost(kCGHIDEventTap, event)
        else:
            pyautogui.hotkey(*keys, _pause=False)
