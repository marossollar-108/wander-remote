"""GUI wrapper pre Wander Remote Host — tkinter."""

import asyncio
import logging
import sys
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# Rovnaky sys.path hack ako v host.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from host import RemoteHost
from config import RELAY_URL

# Farby
RED = "#EB002F"
RED_HOVER = "#C50028"
BLACK = "#1A1A1A"
WHITE = "#FFFFFF"
GRAY = "#777777"
BORDER = "#D2D2D2"
GREEN = "#10B981"

LOG_FORMAT = "%(asctime)s %(message)s"
LOG_DATEFMT = "%H:%M:%S"


class GUILogHandler(logging.Handler):
    """Posiela log zaznamy do tkinter Text widgetu."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        msg = self.format(record)
        self.callback(msg)


class WanderRemoteGUI:
    """Hlavne GUI okno."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wander Remote Host")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.root.configure(bg=WHITE)

        self.host = None
        self.host_thread = None
        self.loop = None
        self.running = False

        self._build_ui()
        self._setup_logging()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        """Postav cele GUI."""
        pad = 15

        # --- Header ---
        header = tk.Frame(self.root, bg=RED, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Wander Remote Host",
            font=("Helvetica", 16, "bold"),
            bg=RED,
            fg=WHITE,
        ).pack(pady=12)

        # --- Main content ---
        content = tk.Frame(self.root, bg=WHITE, padx=pad, pady=pad)
        content.pack(fill=tk.BOTH, expand=True)

        # Relay URL
        tk.Label(
            content,
            text="Relay server URL",
            font=("Helvetica", 11),
            bg=WHITE,
            fg=BLACK,
            anchor="w",
        ).pack(fill=tk.X)

        url_frame = tk.Frame(content, bg=BORDER, bd=1, relief=tk.SOLID)
        url_frame.pack(fill=tk.X, pady=(2, 10))

        self.url_var = tk.StringVar(value=RELAY_URL)
        self.url_entry = tk.Entry(
            url_frame,
            textvariable=self.url_var,
            font=("Helvetica", 11),
            bd=0,
            highlightthickness=0,
            bg=WHITE,
            fg=BLACK,
        )
        self.url_entry.pack(fill=tk.X, padx=4, pady=4)

        # Start button
        self.start_btn = tk.Button(
            content,
            text="Spustit",
            font=("Helvetica", 12, "bold"),
            bg=RED,
            fg=WHITE,
            activebackground=RED_HOVER,
            activeforeground=WHITE,
            bd=0,
            cursor="hand2",
            command=self._start_host,
            height=1,
        )
        self.start_btn.pack(fill=tk.X, pady=(0, 10))
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg=RED_HOVER))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg=RED))

        # Session info frame
        self.info_frame = tk.Frame(content, bg=WHITE)
        self.info_frame.pack(fill=tk.X, pady=(0, 5))

        # Session ID row
        tk.Label(
            self.info_frame,
            text="Host ID",
            font=("Helvetica", 10),
            bg=WHITE,
            fg=GRAY,
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        self.session_label = tk.Label(
            self.info_frame,
            text="---",
            font=("Helvetica", 24, "bold"),
            bg=WHITE,
            fg=BLACK,
            anchor="w",
        )
        self.session_label.grid(row=1, column=0, sticky="w")

        self.copy_session_btn = tk.Button(
            self.info_frame,
            text="Kopirovat",
            font=("Helvetica", 9),
            bg=BORDER,
            fg=BLACK,
            bd=0,
            cursor="hand2",
            command=lambda: self._copy_to_clipboard(self.session_label.cget("text")),
        )
        self.copy_session_btn.grid(row=1, column=1, padx=(10, 0))

        # Password row
        tk.Label(
            self.info_frame,
            text="Heslo",
            font=("Helvetica", 10),
            bg=WHITE,
            fg=GRAY,
            anchor="w",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.password_label = tk.Label(
            self.info_frame,
            text="---",
            font=("Helvetica", 24, "bold"),
            bg=WHITE,
            fg=BLACK,
            anchor="w",
        )
        self.password_label.grid(row=3, column=0, sticky="w")

        self.copy_pass_btn = tk.Button(
            self.info_frame,
            text="Kopirovat",
            font=("Helvetica", 9),
            bg=BORDER,
            fg=BLACK,
            bd=0,
            cursor="hand2",
            command=lambda: self._copy_to_clipboard(self.password_label.cget("text")),
        )
        self.copy_pass_btn.grid(row=3, column=1, padx=(10, 0))

        self.info_frame.columnconfigure(0, weight=1)

        # Status
        self.status_label = tk.Label(
            content,
            text="",
            font=("Helvetica", 11),
            bg=WHITE,
            fg=GRAY,
            anchor="w",
        )
        self.status_label.pack(fill=tk.X, pady=(5, 5))

        # Stop button (hidden initially)
        self.stop_btn = tk.Button(
            content,
            text="Zastavit",
            font=("Helvetica", 11, "bold"),
            bg=BLACK,
            fg=WHITE,
            activebackground="#333333",
            activeforeground=WHITE,
            bd=0,
            cursor="hand2",
            command=self._stop_host,
            height=1,
        )
        # stop_btn sa packne az po spusteni

        # Log area
        tk.Label(
            content,
            text="Log",
            font=("Helvetica", 10),
            bg=WHITE,
            fg=GRAY,
            anchor="w",
        ).pack(fill=tk.X, pady=(5, 2))

        log_frame = tk.Frame(content, bg=BORDER, bd=1, relief=tk.SOLID)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_frame,
            font=("Courier", 9),
            bg="#F5F5F5",
            fg=BLACK,
            bd=0,
            highlightthickness=0,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=6,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _setup_logging(self):
        """Nastav logging handler do GUI."""
        handler = GUILogHandler(self._append_log)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT))
        handler.setLevel(logging.INFO)

        # Pridaj handler na root logger a host logger
        for name in ("host", ""):
            log = logging.getLogger(name)
            log.addHandler(handler)

    def _append_log(self, msg: str):
        """Pridaj riadok do log widgetu (thread-safe)."""
        def _do():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _do)

    def _copy_to_clipboard(self, text: str):
        """Skopiruj text do schranky cez pbcopy (macOS)."""
        if text and text != "---":
            import subprocess
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            self._set_status(f"Skopirovane: {text}", GREEN)

    def _set_status(self, text: str, color: str = GRAY):
        """Nastav status label (thread-safe)."""
        def _do():
            self.status_label.config(text=text, fg=color)
        self.root.after(0, _do)

    def _start_host(self):
        """Spusti hosta v background threade."""
        if self.running:
            return

        relay_url = self.url_var.get().strip()
        if not relay_url:
            self._set_status("Zadajte URL relay servera!", RED)
            return

        self.running = True
        self.start_btn.pack_forget()
        self.url_entry.config(state=tk.DISABLED)

        self.stop_btn.pack(fill=tk.X, pady=(0, 5))

        self._set_status("Pripajam sa...", GRAY)
        self._append_log(f"Pripajam sa na {relay_url}")

        self.host_thread = threading.Thread(
            target=self._run_host_thread,
            args=(relay_url,),
            daemon=True,
        )
        self.host_thread.start()

        # Polling na session info
        self.root.after(200, self._poll_host_state)

    def _run_host_thread(self, relay_url: str):
        """Background thread s asyncio event loopom."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.host = RemoteHost(relay_url)
            self.loop.run_until_complete(self.host.start())
        except Exception as e:
            self._set_status(f"Chyba: {e}", RED)
            self._append_log(f"Chyba: {e}")
        finally:
            self.loop.close()
            self.loop = None
            self.running = False
            self._on_host_stopped()

    def _poll_host_state(self):
        """Periodicky kontroluj stav hosta a aktualizuj GUI."""
        if not self.running or self.host is None:
            return

        # Session info
        if self.host.session_id:
            self.session_label.config(text=self.host.session_id)
        if self.host.password:
            self.password_label.config(text=self.host.password)

        # Viewer status
        if self.host.viewer_connected:
            self._set_status("Viewer pripojeny!", GREEN)
        elif self.host.session_id:
            self._set_status("Cakam na pripojenie...", GRAY)

        if self.running:
            self.root.after(500, self._poll_host_state)

    def _stop_host(self):
        """Zastav hosta."""
        if self.host:
            self.host.running = False
            # Zatvor websocket ak existuje
            if self.host.ws and self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.host.ws.close(), self.loop
                )
        self._set_status("Zastavujem...", GRAY)

    def _on_host_stopped(self):
        """Callback ked host skonci (volane z threadu)."""
        def _do():
            self.stop_btn.pack_forget()
            self.start_btn.pack(fill=tk.X, pady=(0, 10))
            self.url_entry.config(state=tk.NORMAL)
            self.session_label.config(text="---")
            self.password_label.config(text="---")
            self._set_status("Odpojeny", GRAY)
        self.root.after(0, _do)

    def _on_close(self):
        """Zatvor okno."""
        self._stop_host()
        self.root.after(300, self.root.destroy)

    def run(self):
        """Spusti GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    app = WanderRemoteGUI()
    app.run()
