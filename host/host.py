"""Hlavny modul hosta — ovladany pocitac."""

import asyncio
import base64
import concurrent.futures
import json
import logging
import queue
import signal
import sys
import threading
import time

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))

import websockets

from config import (
    RELAY_URL,
    CAPTURE_QUALITY,
    CAPTURE_MAX_FPS,
    CAPTURE_BLOCK_SIZE,
    KEYFRAME_INTERVAL,
    BLOCKED_COMBOS,
)
from host_id import get_or_create_host_id
from screen_capture import ScreenCapture
from input_handler import InputHandler
from shared.protocol import MessageType, create_message, parse_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("host")


class RemoteHost:
    """Hlavna trieda hosta."""

    def __init__(self, relay_url: str):
        self.relay_url = relay_url
        self.ws = None
        self.host_id = get_or_create_host_id()
        self.session_id = None
        self.password = None
        self.viewer_connected = False
        self.running = False

        self._input_queue = queue.Queue()
        self._input_thread = None

        self.capture = ScreenCapture(
            quality=CAPTURE_QUALITY,
            max_fps=CAPTURE_MAX_FPS,
            block_size=CAPTURE_BLOCK_SIZE,
        )
        width, height = self.capture.get_screen_size()
        self.input_handler = InputHandler(width, height, BLOCKED_COMBOS)
        self.screen_width = width
        self.screen_height = height

    async def start(self):
        """Pripoj sa na relay a spusti hlavne slucky."""
        self.running = True
        try:
            async with websockets.connect(self.relay_url) as ws:
                self.ws = ws
                logger.info("Connected to relay: %s", self.relay_url)

                # Registruj sa s persistentnym host ID
                logger.info("Host ID: %s", self.host_id)
                await ws.send(create_message(
                    MessageType.HOST_REGISTER, host_id=self.host_id
                ))

                # Cakaj na session_created
                raw = await ws.recv()
                msg = parse_message(raw)
                if msg["type"] != MessageType.SESSION_CREATED.value:
                    logger.error("Unexpected message: %s", msg["type"])
                    return

                self.session_id = msg["session_id"]
                self.password = msg["password"]

                logger.info(
                    "Host ID: %s | Password: %s",
                    self.session_id,
                    self.password,
                )
                print(f"\n  Host ID:   {self.session_id}")
                print(f"  Password:  {self.password}\n")

                # Posli screen info
                await ws.send(json.dumps({
                    "type": "host_screen_info",
                    "width": self.screen_width,
                    "height": self.screen_height,
                }))

                # Spusti receive + capture loop
                await asyncio.gather(
                    self._receive_loop(),
                    self._capture_loop(),
                    self._ping_loop(),
                )
        except websockets.ConnectionClosed:
            logger.info("Disconnected from relay")
        except Exception:
            logger.exception("Host error")
        finally:
            self.running = False
            self.capture.close()

    async def _receive_loop(self):
        """Prijimaj spravy od relay."""
        try:
            async for raw in self.ws:
                if isinstance(raw, bytes):
                    continue
                await self._handle_message(raw)
        except websockets.ConnectionClosed:
            pass

    def _process_inputs(self):
        """Spracuj vsetky input prikazy z queue (volane z main threadu)."""
        while not self._input_queue.empty():
            try:
                cmd = self._input_queue.get_nowait()
            except queue.Empty:
                break
            try:
                action = cmd[0]
                if action == "move":
                    self.input_handler.move_mouse(cmd[1], cmd[2])
                elif action == "click":
                    self.input_handler.click(cmd[1], cmd[2], cmd[3], cmd[4])
                elif action == "scroll":
                    self.input_handler.scroll(cmd[1], cmd[2], cmd[3])
                elif action == "key":
                    self.input_handler.key_press(cmd[1], cmd[2])
                elif action == "combo":
                    self.input_handler.key_combo(cmd[1])
            except Exception as e:
                logger.error("Input error: %s", e)

    async def _handle_message(self, raw: str):
        """Spracuj prichadzajuce spravy."""
        try:
            msg = parse_message(raw)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("Invalid message: %s", e)
            return

        msg_type = msg.get("type")

        if msg_type == MessageType.VIEWER_JOINED.value:
            self.viewer_connected = True
            logger.info("Viewer connected!")

        elif msg_type == MessageType.PEER_DISCONNECTED.value:
            self.viewer_connected = False
            logger.info("Viewer disconnected")

        elif msg_type == MessageType.MOUSE_MOVE.value:
            self._input_queue.put(("move", msg.get("x", 0), msg.get("y", 0)))

        elif msg_type == MessageType.MOUSE_CLICK.value:
            self._input_queue.put(("click", msg.get("x", 0), msg.get("y", 0),
                msg.get("button", "left"), msg.get("action", "click")))

        elif msg_type == MessageType.MOUSE_SCROLL.value:
            self._input_queue.put(("scroll", msg.get("x", 0), msg.get("y", 0),
                msg.get("delta", 0)))

        elif msg_type == MessageType.KEY_EVENT.value:
            self._input_queue.put(("key", msg.get("key", ""), msg.get("action", "press")))

        elif msg_type == MessageType.KEY_COMBO.value:
            self._input_queue.put(("combo", msg.get("keys", [])))

        elif msg_type == MessageType.QUALITY_CHANGE.value:
            quality = msg.get("quality")
            max_fps = msg.get("max_fps")
            if quality is not None:
                self.capture.set_quality(quality)
            if max_fps is not None:
                self.capture.set_max_fps(max_fps)
            logger.info("Quality changed: quality=%s, max_fps=%s", quality, max_fps)

        elif msg_type == MessageType.PONG.value:
            ts = msg.get("timestamp", 0)
            latency = int(time.time() * 1000) - ts
            logger.debug("Latency: %dms", latency)

    def _capture_frame(self, send_keyframe):
        """Synchronne zachytenie framu (bezi v thread poole)."""
        if send_keyframe:
            data = self.capture.capture_full()
            msg = create_message(
                MessageType.FRAME_FULL,
                timestamp=int(time.time() * 1000),
                width=self.screen_width,
                height=self.screen_height,
                format="jpeg",
                quality=self.capture.quality,
                data=base64.b64encode(data).decode("ascii"),
            )
            return msg
        else:
            regions = self.capture.capture_delta()
            if regions:
                encoded_regions = []
                for r in regions:
                    encoded_regions.append({
                        "x": r["x"],
                        "y": r["y"],
                        "width": r["width"],
                        "height": r["height"],
                        "data": base64.b64encode(r["data"]).decode("ascii"),
                    })
                msg = create_message(
                    MessageType.FRAME_DELTA,
                    timestamp=int(time.time() * 1000),
                    regions=encoded_regions,
                )
                return msg
        return None

    async def _capture_loop(self):
        """Hlavna slucka snimania obrazovky."""
        last_keyframe = 0
        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        while self.running:
            if not self.viewer_connected:
                await asyncio.sleep(0.5)
                continue

            if not self.capture.can_capture():
                await asyncio.sleep(0.005)
                continue

            try:
                now = time.monotonic()
                send_keyframe = (now - last_keyframe) >= KEYFRAME_INTERVAL

                msg = await loop.run_in_executor(executor, self._capture_frame, send_keyframe)

                if send_keyframe:
                    last_keyframe = now

                if msg:
                    await self.ws.send(msg)

            except websockets.ConnectionClosed:
                break
            except Exception:
                logger.exception("Capture error")
                await asyncio.sleep(0.1)

    async def _ping_loop(self):
        """Posielaj ping kazdych 10 sekund."""
        while self.running:
            try:
                await self.ws.send(create_message(
                    MessageType.PING,
                    timestamp=int(time.time() * 1000),
                ))
            except websockets.ConnectionClosed:
                break
            await asyncio.sleep(10)


def main():
    host = RemoteHost(RELAY_URL)

    def run_async():
        asyncio.run(host.start())

    # Asyncio bezi v background threade
    async_thread = threading.Thread(target=run_async, daemon=True)
    async_thread.start()

    logger.info("Host running — main thread processing inputs (Ctrl+C to stop)")

    # Main thread spracovava input queue (macOS vyzaduje main thread pre Quartz)
    try:
        while async_thread.is_alive():
            host._process_inputs()
            time.sleep(0.001)  # 1ms polling
    except KeyboardInterrupt:
        host.running = False
        logger.info("Stopping...")

    async_thread.join(timeout=3)


if __name__ == "__main__":
    main()
