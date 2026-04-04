"""Generovanie a ulozenie persistentneho host ID z MAC adresy."""

import hashlib
import os
import uuid

HOST_ID_DIR = os.path.expanduser("~/.wander-remote")
HOST_ID_FILE = os.path.join(HOST_ID_DIR, "host_id")


def get_mac_address() -> str:
    """Vrat MAC adresu ako string."""
    mac = uuid.getnode()
    return ":".join(f"{(mac >> (8 * i)) & 0xff:02x}" for i in range(5, -1, -1))


def generate_host_id(mac: str) -> str:
    """Vygeneruj 6-ciferne cislo z MAC adresy (deterministicky)."""
    hash_bytes = hashlib.sha256(mac.encode()).digest()
    num = int.from_bytes(hash_bytes[:4], "big")
    return str(100000 + (num % 900000))


def get_or_create_host_id() -> str:
    """Nacitaj existujuce host ID alebo vygeneruj nove z MAC adresy.

    ID sa ulozi do ~/.wander-remote/host_id a uz sa nemeni.
    """
    if os.path.exists(HOST_ID_FILE):
        with open(HOST_ID_FILE, "r") as f:
            host_id = f.read().strip()
            if host_id:
                return host_id

    mac = get_mac_address()
    host_id = generate_host_id(mac)

    os.makedirs(HOST_ID_DIR, exist_ok=True)
    with open(HOST_ID_FILE, "w") as f:
        f.write(host_id)

    return host_id
