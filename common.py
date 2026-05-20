from __future__ import annotations

import json
import secrets
import socket
from pathlib import Path
from typing import BinaryIO


BASE_DIR = Path(__file__).resolve().parent
PUBLIC_FILE = BASE_DIR / "public_data.json"
SECRET_FILE = BASE_DIR / "prover_secret.json"

# 768-bit MODP group prime from RFC 2409, comfortably above 200 decimal digits.
P = int(
    "155251809230070893513091813125848175563133404943451431320235119490296"
    "623994910210725866945387659164244291000768028886422915080371891804634"
    "263272761303128298374438082089019628850917069131659317536746955176311"
    "9843371637221007211169123"
)
G = 2
Q = (P - 1) // 2
DEFAULT_ROUNDS = 8


def random_scalar() -> int:
    return secrets.randbelow(Q - 1) + 1


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_demo_keys(force: bool = False) -> tuple[dict, dict]:
    if not force and PUBLIC_FILE.exists() and SECRET_FILE.exists():
        return load_json(PUBLIC_FILE), load_json(SECRET_FILE)

    secret = random_scalar()
    public = pow(G, secret, P)

    public_payload = {
        "protocol": "schnorr-identification",
        "p": str(P),
        "q": str(Q),
        "g": str(G),
        "y": str(public),
        "rounds": DEFAULT_ROUNDS,
    }
    secret_payload = {
        "protocol": "schnorr-identification",
        "x": str(secret),
    }
    save_json(PUBLIC_FILE, public_payload)
    save_json(SECRET_FILE, secret_payload)
    return public_payload, secret_payload


def send_json(stream: BinaryIO, payload: dict) -> None:
    data = (json.dumps(payload) + "\n").encode("utf-8")
    stream.write(data)
    stream.flush()


def recv_json(stream: BinaryIO) -> dict:
    line = stream.readline()
    if not line:
        raise ConnectionError("socket closed before a complete JSON message arrived")
    return json.loads(line.decode("utf-8"))
