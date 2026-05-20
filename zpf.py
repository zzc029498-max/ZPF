from __future__ import annotations

import argparse
import subprocess
import sys

from common import PUBLIC_FILE, SECRET_FILE, ensure_demo_keys


def main() -> None:
    parser = argparse.ArgumentParser(description="Zero-knowledge proof demo launcher.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup", help="generate demo public/secret key files")

    verifier_parser = subparsers.add_parser("verifier", help="run the verifier process")
    verifier_parser.add_argument("--host", default="127.0.0.1")
    verifier_parser.add_argument("--port", default="9000")
    verifier_parser.add_argument("--rounds", default="8")
    verifier_parser.add_argument("--once", action="store_true")

    prover_parser = subparsers.add_parser("prover", help="run the prover process")
    prover_parser.add_argument("--host", default="127.0.0.1")
    prover_parser.add_argument("--port", default="9000")

    args = parser.parse_args()

    if args.command == "setup":
        ensure_demo_keys(force=True)
        print(f"Created {PUBLIC_FILE.name} and {SECRET_FILE.name}")
        return

    if args.command == "verifier":
        command = [
            sys.executable,
            "verifier.py",
            "--host",
            args.host,
            "--port",
            args.port,
            "--rounds",
            args.rounds,
        ]
        if args.once:
            command.append("--once")
    else:
        command = [sys.executable, "prover.py", "--host", args.host, "--port", args.port]

    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()
