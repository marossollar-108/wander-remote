"""Hlavny modul hosta — ovladany pocitac."""

import asyncio
import base64
import json
import logging
import signal
import sys
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
        self.session_id = None
        self.password = None
        self.viewer_connected = False
        self.running = False

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

                # Registruj sa
                await ws.send(create_message(MessageType.HOST_REGISTER))

                # Cakaj na session_created
                raw = await ws.recv()
                msg = parse_message(raw)
                if msg["type"] != MessageType.SESSION_CREATED.value:
                    logger.error("Unexpected message: %s", msg["type"])
                    return

                self.session_id = msg["session_id"]
                self.password = msg["password"]

                logger.info(
                    "Session ID: %s | Password: %s",
                    self.session_id,
                    self.password,
                )
                print(f"\n  Session ID: {self.session_id}")
                print(f"  Password:   {self.password}\n")

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
            print("  Viewer connected!")

        elif msg_type == MessageType.PEER_DISCONNECTED.value:
            self.viewer_connected = False
            logger.info("Viewer disconnected")
            print("  Viewer disconnected. Waiting for new viewer...")

        elif msg_type == MessageType.MOUSE_MOVE.value:
            self.input_handler.move_mouse(msg.get("x", 0), msg.get("y", 0))

        elif msg_type == MessageType.MOUSE_CLICK.value:
            self.input_handler.click(
                msg.get("x", 0), msg.get("y", 0),
                msg.get("button", "left"), msg.get("action", "click"),
            )

        elif msg_type == MessageType.MOUSE_SCROLL.value:
            self.input_handler.scroll(
                msg.get("x", 0), msg.get("y", 0),
                msg.get("delta", 0),
            )

        elif msg_type == MessageType.KEY_EVENT.value:
            self.input_handler.key_press(
                msg.get("key", ""), msg.get("action", "press"),
            )

        elif msg_type == MessageType.KEY_COMBO.value:
            self.input_handler.key_combo(msg.get("keys", []))

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

    async def _capture_loop(self):
        """Hlavna slucka snimania obrazovky."""
        last_keyframe = 0

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

                if send_keyframe:
                    data = self.capture.capture_full()
                    last_keyframe = now
                    msg = create_message(
                        MessageType.FRAME_FULL,
                        timestamp=int(time.time() * 1000),
                        width=self.screen_width,
                        height=self.screen_height,
                        format="jpeg",
                        quality=self.capture.quality,
                        data=base64.b64encode(data).decode("ascii"),
                    )
                    await self.ws.send(msg)
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


async def main():
    host = RemoteHost(RELAY_URL)

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: setattr(host, 'running', False))

    await host.start()


if __name__ == "__main__":
    asyncio.run(main())
