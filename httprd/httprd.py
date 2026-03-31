# httprd: web-based remote desktop
# Copyright (C) 2022-2023  bitrate16
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

VERSION = '4.2'

import json
import aiohttp
import aiohttp.web
import argparse
import base64
import gzip
import PIL
import PIL.Image
import PIL.ImageGrab
import PIL.ImageChops
import platform
import traceback

from datetime import datetime

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

# Const config
DOWNSAMPLE = PIL.Image.BILINEAR
MIN_PARTIAL_FRAMES_BEFORE_FULL_REPAINT = 60
MIN_EMPTY_FRAMES_BEFORE_FULL_REPAINT = 120

# Input event types
INPUT_EVENT_MOUSE_MOVE   = 0
INPUT_EVENT_MOUSE_DOWN   = 1
INPUT_EVENT_MOUSE_UP     = 2
INPUT_EVENT_MOUSE_SCROLL = 3
INPUT_EVENT_KEY_DOWN     = 4
INPUT_EVENT_KEY_UP       = 5

# --- Input backend ---
IS_MACOS = platform.system() == "Darwin"

if IS_MACOS:
    import Quartz
    from Quartz import (
        CGEventCreateMouseEvent, CGEventCreateScrollWheelEvent,
        CGEventCreateKeyboardEvent, CGEventPost, CGEventSetIntegerValueField,
        kCGEventMouseMoved, kCGEventLeftMouseDown, kCGEventLeftMouseUp,
        kCGEventRightMouseDown, kCGEventRightMouseUp,
        kCGEventOtherMouseDown, kCGEventOtherMouseUp,
        kCGHIDEventTap, kCGMouseButtonLeft, kCGMouseButtonRight, kCGMouseButtonCenter,
        kCGScrollEventUnitLine,
    )

    _BUTTON_CG = [kCGMouseButtonLeft, kCGMouseButtonCenter, kCGMouseButtonRight]
    _DOWN_EV = [kCGEventLeftMouseDown, kCGEventOtherMouseDown, kCGEventRightMouseDown]
    _UP_EV = [kCGEventLeftMouseUp, kCGEventOtherMouseUp, kCGEventRightMouseUp]

    # pyautogui key name -> macOS virtual keycode
    _KEYCODE = {
        "a": 0, "b": 11, "c": 8, "d": 2, "e": 14, "f": 3, "g": 5,
        "h": 4, "i": 34, "j": 38, "k": 40, "l": 37, "m": 46, "n": 45,
        "o": 31, "p": 35, "q": 12, "r": 15, "s": 1, "t": 17, "u": 32,
        "v": 9, "w": 13, "x": 7, "y": 16, "z": 6,
        "0": 29, "1": 18, "2": 19, "3": 20, "4": 21,
        "5": 23, "6": 22, "7": 26, "8": 28, "9": 25,
        "enter": 36, "return": 36, "tab": 48, "space": 49,
        "backspace": 51, "delete": 117, "escape": 53,
        "up": 126, "down": 125, "left": 123, "right": 124,
        "home": 115, "end": 119, "pageup": 116, "pagedown": 121,
        "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "f6": 97,
        "f7": 98, "f8": 100, "f9": 101, "f10": 109, "f11": 103, "f12": 111,
        "shiftleft": 56, "shiftright": 60, "shift": 56,
        "ctrlleft": 59, "ctrlright": 62, "ctrl": 59,
        "altleft": 58, "altright": 61, "alt": 58,
        "winleft": 55, "winright": 55, "cmd": 55, "meta": 55,
        "capslock": 57, "numlock": 71, "scrolllock": 107,
        "'": 39, ",": 43, "-": 27, ".": 47, "/": 44,
        ";": 41, "=": 24, "[": 33, "\\": 42, "]": 30, "`": 50,
        "+": 24,
    }

    def _input_move(x, y):
        ev = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (x, y), kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, ev)

    def _input_mouse_down(x, y, button):
        btn = _BUTTON_CG[button] if button < 3 else kCGMouseButtonLeft
        ev_type = _DOWN_EV[button] if button < 3 else kCGEventLeftMouseDown
        ev = CGEventCreateMouseEvent(None, ev_type, (x, y), btn)
        CGEventPost(kCGHIDEventTap, ev)

    def _input_mouse_up(x, y, button):
        btn = _BUTTON_CG[button] if button < 3 else kCGMouseButtonLeft
        ev_type = _UP_EV[button] if button < 3 else kCGEventLeftMouseUp
        ev = CGEventCreateMouseEvent(None, ev_type, (x, y), btn)
        CGEventPost(kCGHIDEventTap, ev)

    def _input_scroll(x, y, dy):
        _input_move(x, y)
        ev = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, int(dy))
        CGEventPost(kCGHIDEventTap, ev)

    def _input_key_down(keycode):
        kc = _KEYCODE.get(keycode)
        if kc is not None:
            ev = CGEventCreateKeyboardEvent(None, kc, True)
            CGEventPost(kCGHIDEventTap, ev)

    def _input_key_up(keycode):
        kc = _KEYCODE.get(keycode)
        if kc is not None:
            ev = CGEventCreateKeyboardEvent(None, kc, False)
            CGEventPost(kCGHIDEventTap, ev)

    print("[INPUT] Using Quartz/CoreGraphics backend")

else:
    import pyautogui
    pyautogui.FAILSAFE = False

    def _input_move(x, y):
        pyautogui.moveTo(x, y)

    def _input_mouse_down(x, y, button):
        pyautogui.mouseDown(x, y, button=['left', 'middle', 'right'][button])

    def _input_mouse_up(x, y, button):
        pyautogui.mouseUp(x, y, button=['left', 'middle', 'right'][button])

    def _input_scroll(x, y, dy):
        pyautogui.scroll(dy, x, y)

    def _input_key_down(keycode):
        pyautogui.keyDown(keycode)

    def _input_key_up(keycode):
        pyautogui.keyUp(keycode)

    print("[INPUT] Using pyautogui backend")

# Args
args = {}

# Real resolution
real_width, real_height = 0, 0

# Webapp
app: aiohttp.web.Application


def decode_int8(data):
    return int.from_bytes(data[0:1], 'little')

def decode_int16(data):
    return int.from_bytes(data[0:2], 'little')

def decode_int24(data):
    return int.from_bytes(data[0:3], 'little')

def encode_int8(i):
    return int.to_bytes(i, 1, 'little')

def encode_int16(i):
    return int.to_bytes(i, 2, 'little')

def encode_int24(i):
    return int.to_bytes(i, 3, 'little')

def dump_bytes_dec(data):
    for i in range(len(data)):
        print(data[i], end=' ')
    print()


async def get__connect_input_ws(request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
    """
    WebSocket endpoint for input & control data stream
    """

    # Check access
    access = (args.password == request.query.get('password', '').strip())

    # Log request
    now = datetime.now()
    now = now.strftime("%d.%m.%Y-%H:%M:%S")
    print(f'[{ now }] { request.remote } { request.method } [{ "INPUT" if access else "NO ACCESS" }] { request.path_qs }')

    # Open socket
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    # Close with error code on no access
    if not access:
        await ws.close(code=4001, message=b'Unauthorized')
        return ws

    # Track pressed key state for future reset on disconnect
    state_keys = {}

    def release_keys():
        for k in state_keys.keys():
            if state_keys[k]:
                _input_key_up(k)

    def update_key_state(key, state):
        state_keys[key] = state

    # Read stream
    async def async_worker():

        try:

            # Reply to requests
            async for msg in ws:

                # Receive input data
                if msg.type == aiohttp.WSMsgType.BINARY:
                    try:

                        # Drop on invalid packet
                        if len(msg.data) == 0:
                            continue

                        # Parse params
                        packet_type = decode_int8(msg.data[0:1])
                        payload = msg.data[1:]

                        # Input request
                        if packet_type == 0x03:

                            # Unpack events data
                            data = json.loads(bytes.decode(payload, encoding='ascii'))

                            # Iterate events
                            for event in data:
                                if event[0] == INPUT_EVENT_MOUSE_MOVE:
                                    mouse_x = max(0, min(real_width, event[1]))
                                    mouse_y = max(0, min(real_height, event[2]))
                                    _input_move(mouse_x, mouse_y)

                                elif event[0] == INPUT_EVENT_MOUSE_DOWN:
                                    mouse_x = max(0, min(real_width, event[1]))
                                    mouse_y = max(0, min(real_height, event[2]))
                                    button = event[3]
                                    if button < 0 or button > 2:
                                        continue
                                    _input_mouse_down(mouse_x, mouse_y, button)

                                elif event[0] == INPUT_EVENT_MOUSE_UP:
                                    mouse_x = max(0, min(real_width, event[1]))
                                    mouse_y = max(0, min(real_height, event[2]))
                                    button = event[3]
                                    if button < 0 or button > 2:
                                        continue
                                    _input_mouse_up(mouse_x, mouse_y, button)

                                elif event[0] == INPUT_EVENT_MOUSE_SCROLL:
                                    mouse_x = max(0, min(real_width, event[1]))
                                    mouse_y = max(0, min(real_height, event[2]))
                                    dy = int(event[3])
                                    _input_scroll(mouse_x, mouse_y, dy)

                                elif event[0] == INPUT_EVENT_KEY_DOWN:
                                    keycode = event[1]
                                    _input_key_down(keycode)
                                    update_key_state(keycode, True)

                                elif event[0] == INPUT_EVENT_KEY_UP:
                                    keycode = event[1]
                                    _input_key_up(keycode)
                                    update_key_state(keycode, False)
                    except:
                        traceback.print_exc()
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'ws connection closed with exception { ws.exception() }')
        except:
            traceback.print_exc()

    await async_worker()

    # Release stuck keys
    release_keys()

    return ws


async def get__connect_view_ws(request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
    """
    WebSocket endpoint for frame stream
    """

    # Check access
    access = (args.password == request.query.get('password', '').strip()) or (args.view_password == request.query.get('password', '').strip())

    # Log request
    now = datetime.now()
    now = now.strftime("%d.%m.%Y-%H:%M:%S")
    print(f'[{ now }] { request.remote } { request.method } [{ "VIEW" if access else "NO ACCESS" }] { request.path_qs }')

    # Open socket
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    # Close with error code on no access
    if not access:
        await ws.close(code=4001, message=b'Unauthorized')
        return ws

    # Frame buffer
    buffer = BytesIO()

    # Read stream
    async def async_worker():

        # Last screen frame
        last_frame = None
        # Track count of partial frames send since last full repaint frame send and prevent firing full frames on low internet
        partial_frames_since_last_full_repaint_frame = 0
        # Track count of empty frames send since last full repaint frame send and prevent firing full frames on low internet
        empty_frames_since_last_full_repaint_frame = 0

        # Store remote viewport size to force-push full repaint
        viewport_width = 0
        viewport_height = 0

        try:

            # Reply to requests
            async for msg in ws:

                # Receive input data
                if msg.type == aiohttp.WSMsgType.BINARY:
                    try:

                        # Drop on invalid packet
                        if len(msg.data) == 0:
                            continue

                        # Parse params
                        packet_type = decode_int8(msg.data[0:1])
                        payload = msg.data[1:]

                        # Frame request
                        if packet_type == 0x01:
                            req_viewport_width = decode_int16(payload[0:2])
                            req_viewport_height = decode_int16(payload[2:4])
                            quality = decode_int8(payload[4:5])

                            # Grab frame
                            if args.fullscreen:
                                image = PIL.ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=True)
                            else:
                                image = PIL.ImageGrab.grab()

                            # Real dimensions
                            global real_width, real_height
                            real_width, real_height = image.width, image.height

                            # Resize
                            if image.width > req_viewport_width or image.height > req_viewport_height:
                                image.thumbnail((req_viewport_width, req_viewport_height), DOWNSAMPLE)

                            # Write header: frame response
                            buffer.seek(0)
                            buffer.write(encode_int8(0x02))
                            buffer.write(encode_int16(real_width))
                            buffer.write(encode_int16(real_height))

                            # Compare frames
                            if last_frame is not None:
                                diff_bbox = PIL.ImageChops.difference(last_frame, image).getbbox()

                            # Check if this is first frame of should force repaint full surface
                            if last_frame is None or \
                                    viewport_width != req_viewport_width or \
                                    viewport_height != req_viewport_height or \
                                    partial_frames_since_last_full_repaint_frame > MIN_PARTIAL_FRAMES_BEFORE_FULL_REPAINT or \
                                    empty_frames_since_last_full_repaint_frame > MIN_EMPTY_FRAMES_BEFORE_FULL_REPAINT:
                                buffer.write(encode_int8(0x01))

                                # Write body
                                image = image.convert('RGB')
                                image.save(fp=buffer, format='JPEG', quality=quality)
                                last_frame = image

                                viewport_width = req_viewport_width
                                viewport_height = req_viewport_height
                                partial_frames_since_last_full_repaint_frame = 0
                                empty_frames_since_last_full_repaint_frame = 0

                            # Send nop
                            elif diff_bbox is None :
                                buffer.write(encode_int8(0x00))
                                empty_frames_since_last_full_repaint_frame += 1

                            # Send partial repaint region
                            else:
                                buffer.write(encode_int8(0x02))
                                buffer.write(encode_int16(diff_bbox[0])) # crop_x
                                buffer.write(encode_int16(diff_bbox[1])) # crop_y

                                # Write body
                                cropped = image.crop(diff_bbox)
                                cropped = cropped.convert('RGB')
                                cropped.save(fp=buffer, format='JPEG', quality=quality)
                                last_frame = image
                                partial_frames_since_last_full_repaint_frame += 1

                            buflen = buffer.tell()
                            buffer.seek(0)
                            mbytes = buffer.read(buflen)
                            buffer.seek(0)

                            await ws.send_bytes(mbytes)

                    except:
                        traceback.print_exc()
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'ws connection closed with exception { ws.exception() }')
        except:
            traceback.print_exc()

    await async_worker()

    return ws


# Encoded page hoes here
# <template:INDEX_CONTENT>
# </template:INDEX_CONTENT>


# handler for /
async def get__root(request: aiohttp.web.Request):

    # Log request
    now = datetime.now()
    now = now.strftime("%d.%m.%Y-%H:%M:%S")
    print(f'[{ now }] { request.remote } { request.method } { request.path_qs }')

    # Page
    # <template:get__root>
    return aiohttp.web.FileResponse('index.html')
    # </template:get__root>


if __name__ == '__main__':

    # Args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', type=int, default=7417, metavar='{1..65535}', choices=range(1, 65535), help='server port')
    parser.add_argument('--password', type=str, default=None, help='password for remote control session')
    parser.add_argument('--view_password', type=str, default=None, help='password for view only session (can only be set if --password is set)')
    parser.add_argument('--fullscreen', action='store_true', default=False, help='enable multi-display screen capture')
    args = parser.parse_args()

    # Password post-process
    if args.password is None:

        # If no passwords set, enable no-password input+view mode
        if args.view_password is None:
            args.password = ''

        # If only view password set, enable password-protected view mode
        else:
            args.view_password = args.view_password.strip()

    else:

        # Enable password-protected input+view mode
        args.password = args.password.strip()

        # If view password is set, enable password-protected view mode
        if args.view_password is not None:
            args.view_password = args.view_password.strip()

    # Check for match and fallback to input + view mode
    if args.password == args.view_password:
        args.view_password = None

    # Set up server
    app = aiohttp.web.Application()

    # Routes
    app.router.add_get('/connect_input_ws', get__connect_input_ws)
    app.router.add_get('/connect_view_ws', get__connect_view_ws)
    app.router.add_get('/', get__root)

    # Listen
    aiohttp.web.run_app(app=app, port=args.port)
