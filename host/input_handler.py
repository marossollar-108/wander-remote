"""Vykonava prikazy mysi a klavesnice."""

import logging
import time

import pyautogui

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

# Disable pyautogui failsafe (move mouse to corner to abort)
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

    def _check_rate_limit(self) -> bool:
        """Max 100 vstupov za sekundu."""
        now = time.monotonic()
        if now - self._input_window_start >= 1.0:
            self._input_count = 0
            self._input_window_start = now
        self._input_count += 1
        return self._input_count <= self._max_inputs_per_sec

    def _to_screen_coords(self, x_ratio: float, y_ratio: float) -> tuple[int, int]:
        """Konvertuj relativne suradnice (0-1) na pixely."""
        x = int(x_ratio * self.screen_width)
        y = int(y_ratio * self.screen_height)
        return (
            max(0, min(x, self.screen_width - 1)),
            max(0, min(y, self.screen_height - 1)),
        )

    def _is_blocked_combo(self, keys: list[str]) -> bool:
        """Skontroluj ci je kombinacia klavesov blokovana."""
        sorted_keys = sorted(k.lower() for k in keys)
        return sorted_keys in self.blocked_combos

    def move_mouse(self, x_ratio: float, y_ratio: float):
        """Presun mys. x_ratio a y_ratio su 0.0-1.0."""
        if not self._check_rate_limit():
            return
        if not validate_mouse_coords(x_ratio, y_ratio):
            logger.warning("Invalid mouse coords: %s, %s", x_ratio, y_ratio)
            return
        x, y = self._to_screen_coords(x_ratio, y_ratio)
        pyautogui.moveTo(x, y, _pause=False)

    def click(self, x_ratio: float, y_ratio: float, button: str, action: str):
        """Klik mysou."""
        if not self._check_rate_limit():
            return
        if not validate_mouse_coords(x_ratio, y_ratio):
            logger.warning("Invalid mouse coords: %s, %s", x_ratio, y_ratio)
            return
        if not validate_button(button):
            logger.warning("Invalid button: %s", button)
            return
        if not validate_click_action(action):
            logger.warning("Invalid click action: %s", action)
            return

        x, y = self._to_screen_coords(x_ratio, y_ratio)
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
        """Scroll kolieskom. delta: kladne = hore, zaporne = dole."""
        if not self._check_rate_limit():
            return
        if not validate_mouse_coords(x_ratio, y_ratio):
            logger.warning("Invalid mouse coords: %s, %s", x_ratio, y_ratio)
            return
        x, y = self._to_screen_coords(x_ratio, y_ratio)
        pyautogui.moveTo(x, y, _pause=False)
        pyautogui.scroll(delta, x, y, _pause=False)

    def key_press(self, key: str, action: str):
        """Stlac/pusti klavesu."""
        if not self._check_rate_limit():
            return
        if not validate_key(key):
            logger.warning("Invalid key: %s", key)
            return
        if not validate_key_action(action):
            logger.warning("Invalid key action: %s", action)
            return

        if action == "press":
            pyautogui.press(key, _pause=False)
        elif action == "down":
            pyautogui.keyDown(key, _pause=False)
        elif action == "up":
            pyautogui.keyUp(key, _pause=False)

    def key_combo(self, keys: list[str]):
        """Stlac kombinaciu klavesov (napr. ["ctrl", "c"])."""
        if not self._check_rate_limit():
            return
        for key in keys:
            if not validate_key(key):
                logger.warning("Invalid key in combo: %s", key)
                return
        if self._is_blocked_combo(keys):
            logger.warning("Blocked key combo: %s", keys)
            return
        pyautogui.hotkey(*keys, _pause=False)
