import os
from dotenv import load_dotenv
load_dotenv()

RELAY_URL = os.getenv("RELAY_URL", "ws://localhost:8765")
CAPTURE_QUALITY = int(os.getenv("CAPTURE_QUALITY", "60"))
CAPTURE_MAX_FPS = int(os.getenv("CAPTURE_MAX_FPS", "30"))
CAPTURE_BLOCK_SIZE = 128
KEYFRAME_INTERVAL = 5
BLOCKED_COMBOS = [
    ["alt", "f4"],
    ["ctrl", "alt", "delete"],
]
