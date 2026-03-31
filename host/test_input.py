"""Minimalny test — simuluje host, prijima mouse eventy, vykonava cez Quartz."""

import asyncio
import json
import sys
import time
import threading
import queue

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))

import websockets
import Quartz
from Quartz import (
    CGEventCreateMouseEvent, CGEventPost,
    kCGEventMouseMoved, kCGEventLeftMouseDown, kCGEventLeftMouseUp,
    kCGHIDEventTap, kCGMouseButtonLeft,
)

RELAY = "ws://localhost:8765"
input_queue = queue.Queue()
running = True

# Screen size
screen = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
SW = int(screen.size.width)
SH = int(screen.size.height)


async def run_host():
    global running
    async with websockets.connect(RELAY) as ws:
        await ws.send(json.dumps({"type": "host_register"}))
        resp = json.loads(await ws.recv())
        print(f"\n  Session ID: {resp['session_id']}")
        print(f"  Password:   {resp['password']}")
        print(f"  Screen:     {SW}x{SH}\n")

        await ws.send(json.dumps({
            "type": "host_screen_info",
            "width": SW, "height": SH,
        }))

        print("Cakam na viewer... (otvor http://localhost:6100)\n")

        async for raw in ws:
            if isinstance(raw, bytes):
                continue
            msg = json.loads(raw)
            t = msg.get("type")

            if t == "viewer_joined":
                print(">>> Viewer pripojeny!")
            elif t == "peer_disconnected":
                print(">>> Viewer odpojeny")
            elif t == "mouse_move":
                input_queue.put(("move", msg["x"], msg["y"]))
            elif t == "mouse_click":
                input_queue.put(("click", msg["x"], msg["y"],
                    msg.get("button", "left"), msg.get("action", "click")))
            elif t == "ping":
                await ws.send(json.dumps({"type": "pong", "timestamp": msg.get("timestamp", 0)}))

    running = False


def main():
    global running
    print(f"Screen: {SW}x{SH}")
    print(f"Relay: {RELAY}")

    t = threading.Thread(target=lambda: asyncio.run(run_host()), daemon=True)
    t.start()

    count = 0
    try:
        while running and t.is_alive():
            while not input_queue.empty():
                cmd = input_queue.get_nowait()
                if cmd[0] == "move":
                    px = int(cmd[1] * SW)
                    py = int(cmd[2] * SH)
                    event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (px, py), kCGMouseButtonLeft)
                    CGEventPost(kCGHIDEventTap, event)
                    count += 1
                    if count % 30 == 0:
                        print(f"  moved {count}x (last: {px},{py})")
                elif cmd[0] == "click":
                    px = int(cmd[1] * SW)
                    py = int(cmd[2] * SH)
                    down = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, (px, py), kCGMouseButtonLeft)
                    CGEventPost(kCGHIDEventTap, down)
                    up = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, (px, py), kCGMouseButtonLeft)
                    CGEventPost(kCGHIDEventTap, up)
                    print(f"  click({px},{py})")
            time.sleep(0.001)
    except KeyboardInterrupt:
        print("\nStopping...")


if __name__ == "__main__":
    main()
