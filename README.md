# ZPF

Zero-Knowledge Proof Demo

This project implements a simple zero-knowledge identification protocol using two independent Python processes:

- `verifier.py`: runs a TCP server
- `prover.py`: connects to the server and proves knowledge of the secret

The protocol is Schnorr identification over a large prime modulus. Python's built-in arbitrary-precision integers are enough for the required 200-digit scale.

## Files

- `common.py`: shared group parameters, JSON message helpers, and key generation
- `verifier.py`: verifier/server process
- `prover.py`: prover/client process
- `zpf.py`: convenience launcher
- `public_data.json`: public parameters and public key, generated automatically
- `prover_secret.json`: prover-only secret key, generated automatically
- `report.md`: 4-5 page report draft

## Quick Start

Generate demo keys:

```bash
python3 zpf.py setup
```

Start the verifier in one terminal:

```bash
python3 verifier.py --host 127.0.0.1 --port 9000 --once
```

Start the prover in another terminal:

```bash
python3 prover.py --host 127.0.0.1 --port 9000
```

You can also use the launcher:

```bash
python3 zpf.py verifier --once
python3 zpf.py prover
```

## Protocol Summary

For each round:

1. The prover chooses a random nonce `r` and sends `t = g^r mod p`.
2. The verifier sends a random one-bit challenge `c`.
3. The prover answers with `s = r + c*x mod q`.
4. The verifier checks `g^s = t * y^c mod p`.

Repeating the protocol several times lowers the cheating probability.

## Demo Notes

- The verifier knows only the public key `y`.
- The prover never sends the secret `x`.
- Both sides exchange newline-delimited JSON over TCP sockets.
- The current demo uses 8 rounds by default, which gives a cheating probability of at most `1 / 2^8`.
