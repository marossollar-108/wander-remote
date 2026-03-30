"""Testovaci viewer pre overenie funkcnosti."""

import asyncio
import base64
import json
import logging
import os
import signal
import sys
import time

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))

import websockets

from config import RELAY_URL
from shared.protocol import MessageType, create_message, parse_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("viewer")

FRAMES_DIR = os.path.join(os.path.dirname(__file__), "frames")


class RemoteViewer:
    """Testovaci viewer pre overenie funkcnosti."""

    def __init__(self, relay_url: str):
        self.relay_url = relay_url
        self.ws = None
        self.connected = False
        self.running = False
        self.host_screen = None
        self.frame_count = 0

        os.makedirs(FRAMES_DIR, exist_ok=True)

    async def connect(self, session_id: str, password: str):
        """Pripoj sa na relay a potom k hostovi."""
        self.running = True
        try:
            async with websockets.connect(self.relay_url) as ws:
                self.ws = ws
                logger.info("Connected to relay: %s", self.relay_url)

                # Posli viewer_connect
                await ws.send(create_message(
                    MessageType.VIEWER_CONNECT,
                    session_id=session_id,
                    password=password,
                ))

                # Cakaj na odpoved
                raw = await ws.recv()
                msg = parse_message(raw)

                if msg["type"] == MessageType.ERROR.value:
                    logger.error("Connection failed: %s", msg.get("message"))
                    print(f"  Error: {msg.get('message')}")
                    return

                if msg["type"] != MessageType.CONNECT_SUCCESS.value:
                    logger.error("Unexpected response: %s", msg["type"])
                    return

                self.host_screen = msg.get("host_screen", {})
                self.connected = True
                logger.info(
                    "Connected to host. Screen: %sx%s",
                    self.host_screen.get("width", "?"),
                    self.host_screen.get("height", "?"),
                )
                print(f"\n  Connected to host!")
                print(f"  Screen: {self.host_screen.get('width')}x{self.host_screen.get('height')}")
                print(f"  Frames saved to: {FRAMES_DIR}")
                print(f"\n  Commands: m x y | c x y | k key | s delta | q\n")

                await asyncio.gather(
                    self._receive_loop(),
                    self._input_loop(),
                    self._ping_loop(),
                )
        except websockets.ConnectionClosed:
            logger.info("Disconnected from relay")
        except Exception:
            logger.exception("Viewer error")
        finally:
            self.running = False
            self.connected = False

    async def _receive_loop(self):
        """Prijimaj snimky a ukladaj do /frames."""
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

        if msg_type == MessageType.FRAME_FULL.value:
            self.frame_count += 1
            data = base64.b64decode(msg["data"])
            filename = os.path.join(FRAMES_DIR, f"frame_{self.frame_count:06d}_full.jpg")
            with open(filename, "wb") as f:
                f.write(data)
            logger.info(
                "Frame #%d FULL %dx%d size=%dKB",
                self.frame_count,
                msg.get("width", 0),
                msg.get("height", 0),
                len(data) // 1024,
            )

        elif msg_type == MessageType.FRAME_DELTA.value:
            self.frame_count += 1
            regions = msg.get("regions", [])
            total_size = 0
            for i, region in enumerate(regions):
                data = base64.b64decode(region["data"])
                total_size += len(data)
                filename = os.path.join(
                    FRAMES_DIR,
                    f"frame_{self.frame_count:06d}_delta_{i}.jpg",
                )
                with open(filename, "wb") as f:
                    f.write(data)
            logger.info(
                "Frame #%d DELTA regions=%d size=%dKB",
                self.frame_count,
                len(regions),
                total_size // 1024,
            )

        elif msg_type == MessageType.PEER_DISCONNECTED.value:
            logger.info("Host disconnected")
            print("  Host disconnected.")
            self.running = False

        elif msg_type == MessageType.PONG.value:
            ts = msg.get("timestamp", 0)
            latency = int(time.time() * 1000) - ts
            logger.debug("Latency: %dms", latency)

    async def _input_loop(self):
        """Interaktivne CLI pre testovanie."""
        loop = asyncio.get_event_loop()

        while self.running:
            try:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                cmd = parts[0].lower()

                if cmd == "q":
                    self.running = False
                    break

                elif cmd == "m" and len(parts) == 3:
                    x, y = float(parts[1]), float(parts[2])
                    await self.ws.send(create_message(
                        MessageType.MOUSE_MOVE, x=x, y=y,
                    ))

                elif cmd == "c" and len(parts) >= 3:
                    x, y = float(parts[1]), float(parts[2])
                    button = parts[3] if len(parts) > 3 else "left"
                    await self.ws.send(create_message(
                        MessageType.MOUSE_CLICK,
                        x=x, y=y, button=button, action="click",
                    ))

                elif cmd == "k" and len(parts) >= 2:
                    key = parts[1]
                    await self.ws.send(create_message(
                        MessageType.KEY_EVENT, key=key, action="press",
                    ))

                elif cmd == "s" and len(parts) >= 2:
                    delta = int(parts[1])
                    await self.ws.send(create_message(
                        MessageType.MOUSE_SCROLL, x=0.5, y=0.5, delta=delta,
                    ))

                else:
                    print("  Commands: m x y | c x y [btn] | k key | s delta | q")

            except Exception as e:
                logger.warning("Input error: %s", e)

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
    if len(sys.argv) < 3:
        print("Usage: python viewer.py <session_id> <password>")
        sys.exit(1)

    session_id = sys.argv[1]
    password = sys.argv[2]

    viewer = RemoteViewer(RELAY_URL)

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: setattr(viewer, 'running', False))

    await viewer.connect(session_id, password)


if __name__ == "__main__":
    asyncio.run(main())
