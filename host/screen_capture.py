"""Efektivne snimanie obrazovky s delta detekciou."""

import hashlib
import io
import logging
import time

import mss
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ScreenCapture:
    """Efektivne snimanie obrazovky s delta detekciou."""

    def __init__(self, monitor=0, quality=60, max_fps=30, block_size=128):
        self.monitor_index = monitor
        self.quality = quality
        self.max_fps = max_fps
        self.block_size = block_size
        self.sct = mss.mss()
        self._prev_hashes = {}
        self._last_capture_time = 0
        self._min_interval = 1.0 / max_fps

    @property
    def _monitor(self):
        monitors = self.sct.monitors
        # monitors[0] is "all monitors", [1] is primary
        idx = self.monitor_index + 1
        if idx >= len(monitors):
            idx = 1
        return monitors[idx]

    def get_screen_size(self) -> tuple[int, int]:
        """Vrat (width, height) aktualneho monitora."""
        mon = self._monitor
        return mon["width"], mon["height"]

    def _capture_raw(self) -> np.ndarray:
        """Zachyt obrazovku ako numpy array (BGRA)."""
        sct_img = self.sct.grab(self._monitor)
        return np.frombuffer(sct_img.rgb, dtype=np.uint8).reshape(
            sct_img.height, sct_img.width, 3
        )

    def _encode_jpeg(self, img_array: np.ndarray, quality: int | None = None) -> bytes:
        """Konvertuj numpy array na JPEG bytes."""
        q = quality if quality is not None else self.quality
        img = Image.fromarray(img_array, "RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=q)
        return buf.getvalue()

    def _encode_region(self, img_array: np.ndarray, x: int, y: int, w: int, h: int) -> bytes:
        """Encode konkretnu oblast ako JPEG."""
        region = img_array[y:y + h, x:x + w]
        return self._encode_jpeg(region)

    def capture_full(self) -> bytes:
        """Zachyt celu obrazovku, vrat JPEG bytes."""
        frame = self._capture_raw()
        self._update_hashes(frame)
        return self._encode_jpeg(frame)

    def _compute_block_hash(self, block: np.ndarray) -> str:
        """Rychly hash bloku."""
        return hashlib.md5(block.tobytes()).hexdigest()

    def _update_hashes(self, frame: np.ndarray):
        """Aktualizuj hashe vsetkych blokov."""
        h, w = frame.shape[:2]
        bs = self.block_size
        self._prev_hashes = {}
        for by in range(0, h, bs):
            for bx in range(0, w, bs):
                bh = min(bs, h - by)
                bw = min(bs, w - bx)
                block = frame[by:by + bh, bx:bx + bw]
                self._prev_hashes[(bx, by)] = self._compute_block_hash(block)

    def capture_delta(self) -> list[dict] | None:
        """
        Porovnaj s predchadzajucim snimkom.
        Vrat len zmenene oblasti alebo None ak sa nic nezmenilo.
        """
        frame = self._capture_raw()
        h, w = frame.shape[:2]
        bs = self.block_size
        changed = []

        for by in range(0, h, bs):
            for bx in range(0, w, bs):
                bh = min(bs, h - by)
                bw = min(bs, w - bx)
                block = frame[by:by + bh, bx:bx + bw]
                new_hash = self._compute_block_hash(block)
                old_hash = self._prev_hashes.get((bx, by))

                if new_hash != old_hash:
                    self._prev_hashes[(bx, by)] = new_hash
                    changed.append({
                        "x": bx,
                        "y": by,
                        "width": bw,
                        "height": bh,
                        "data": self._encode_jpeg(block),
                    })

        if not changed:
            return None

        return changed

    def can_capture(self) -> bool:
        """Skontroluj ci uplynul minimalny interval medzi snimkami."""
        now = time.monotonic()
        if now - self._last_capture_time >= self._min_interval:
            self._last_capture_time = now
            return True
        return False

    def set_quality(self, quality: int):
        """Zmen JPEG kvalitu."""
        self.quality = max(10, min(100, quality))

    def set_max_fps(self, fps: int):
        """Zmen maximalny FPS."""
        self.max_fps = max(1, min(60, fps))
        self._min_interval = 1.0 / self.max_fps

    def close(self):
        """Uvolni resources."""
        self.sct.close()
