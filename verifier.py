from __future__ import annotations

import argparse
import secrets
import socket
from typing import Iterable

from common import DEFAULT_ROUNDS, G, P, PUBLIC_FILE, Q, ensure_demo_keys, load_json, recv_json, send_json


def verify_session(conn: socket.socket, rounds: int, public_key: int) -> bool:
    stream = conn.makefile("rwb")
    send_json(stream, {"type": "hello", "protocol": "schnorr-identification", "rounds": rounds})

    try:
        for round_index in range(1, rounds + 1):
            commitment_message = recv_json(stream)
            if commitment_message.get("type") != "commitment":
                raise ValueError(f"round {round_index}: expected commitment message")

            commitment = int(commitment_message["t"])
            challenge = secrets.randbits(1)
            send_json(stream, {"type": "challenge", "round": round_index, "c": challenge})

            response_message = recv_json(stream)
            if response_message.get("type") != "response":
                raise ValueError(f"round {round_index}: expected response message")

            response = int(response_message["s"])
            left = pow(G, response, P)
            right = (commitment * pow(public_key, challenge, P)) % P
            accepted = left == right
            send_json(
                stream,
                {
                    "type": "round_result",
                    "round": round_index,
                    "accepted": accepted,
                },
            )
            if not accepted:
                return False

        send_json(stream, {"type": "final_result", "accepted": True})
        return True
    finally:
        stream.close()


def iter_connections(server_socket: socket.socket) -> Iterable[tuple[socket.socket, tuple[str, int]]]:
    while True:
        conn, address = server_socket.accept()
        yield conn, address


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifier for a Schnorr identification demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    parser.add_argument("--once", action="store_true", help="handle a single prover session and exit")
    args = parser.parse_args()

    ensure_demo_keys()
    public_data = load_json(PUBLIC_FILE)
    public_key = int(public_data["y"])

    with socket.create_server((args.host, args.port), reuse_port=False) as server:
        print(f"Verifier listening on {args.host}:{args.port}")
        print(f"Using public key y = {public_key}")
        for conn, address in iter_connections(server):
            print(f"Accepted connection from {address[0]}:{address[1]}")
            with conn:
                accepted = verify_session(conn, args.rounds, public_key)
                print("Authentication accepted." if accepted else "Authentication rejected.")
            if args.once:
                break


if __name__ == "__main__":
    main()
