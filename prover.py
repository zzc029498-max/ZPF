from __future__ import annotations

import argparse
import socket

from common import G, P, PUBLIC_FILE, Q, SECRET_FILE, ensure_demo_keys, load_json, random_scalar, recv_json, send_json


def run_proof(sock: socket.socket, secret_key: int) -> bool:
    stream = sock.makefile("rwb")
    hello = recv_json(stream)
    if hello.get("type") != "hello":
        raise ValueError("expected verifier hello message")

    rounds = int(hello["rounds"])
    print(f"Connected to verifier, starting {rounds} rounds.")

    try:
        for round_index in range(1, rounds + 1):
            nonce = random_scalar()
            commitment = pow(G, nonce, P)
            send_json(stream, {"type": "commitment", "round": round_index, "t": str(commitment)})

            challenge_message = recv_json(stream)
            if challenge_message.get("type") != "challenge":
                raise ValueError(f"round {round_index}: expected challenge message")

            challenge = int(challenge_message["c"])
            response = (nonce + challenge * secret_key) % Q
            send_json(stream, {"type": "response", "round": round_index, "s": str(response)})

            result = recv_json(stream)
            if result.get("type") != "round_result":
                raise ValueError(f"round {round_index}: expected round_result message")

            print(f"Round {round_index}: {'accepted' if result['accepted'] else 'rejected'}")
            if not result["accepted"]:
                return False

        final_result = recv_json(stream)
        return bool(final_result.get("accepted"))
    finally:
        stream.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Prover for a Schnorr identification demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()

    ensure_demo_keys()
    public_data = load_json(PUBLIC_FILE)
    secret_data = load_json(SECRET_FILE)
    secret_key = int(secret_data["x"])

    print(f"Loaded public key y = {public_data['y']}")
    with socket.create_connection((args.host, args.port)) as sock:
        accepted = run_proof(sock, secret_key)
    print("Proof completed successfully." if accepted else "Proof failed.")


if __name__ == "__main__":
    main()
