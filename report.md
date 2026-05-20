# Zero-Knowledge Proof Prototype Report

## 1. Objective

The objective of this assignment is to build a small prototype of a zero-knowledge proof system with the following constraints:

- one process must play the role of the prover;
- another independent process must play the role of the verifier;
- both processes must communicate through sockets or a similar communication channel;
- public-key cryptography must use large integers, around 200 decimal digits;
- the result must be demonstrable in a short oral interview.

To satisfy these requirements, I implemented a prototype of the **Schnorr identification protocol** in Python. The system demonstrates how a prover can convince a verifier that it knows a secret key without ever revealing that secret.

## 2. Choice of Protocol

I selected the Schnorr identification protocol because it is one of the simplest and clearest examples of a zero-knowledge proof of knowledge. It fits the assignment very well for four reasons.

First, it is an interactive protocol, so it naturally maps to two communicating processes. The verifier sends a challenge and the prover must answer it correctly.

Second, it uses modular arithmetic over very large integers, which directly satisfies the requirement for public cryptography with large values. Python is convenient for this because arbitrary-precision integers are built into the language.

Third, the protocol is easy to explain during a short demonstration. Each round contains only three messages: commitment, challenge, and response.

Fourth, the protocol has a clean security intuition. A prover who does not know the secret can answer correctly only with a certain probability, and repeating the protocol several times makes cheating unlikely.

## 3. Mathematical Basis

The implementation uses a large prime modulus `p` and a generator `g` of a multiplicative subgroup. The prover owns a secret integer `x`, and the corresponding public key is:

`y = g^x mod p`

The public information is `(p, g, y)`, while `x` remains private.

In each round of the proof:

1. The prover chooses a fresh random nonce `r`.
2. The prover computes the commitment `t = g^r mod p` and sends it to the verifier.
3. The verifier chooses a random challenge bit `c` in `{0, 1}`.
4. The prover computes the response `s = r + c*x mod q`, where `q` is the subgroup order.
5. The verifier checks:

`g^s mod p = t * y^c mod p`

If the equation holds, the round is accepted.

This works because:

- if `c = 0`, then `s = r`, so the verifier checks `g^r = t`;
- if `c = 1`, then `s = r + x`, so the verifier checks `g^(r+x) = g^r * g^x = t * y`.

The secret key is never transmitted. The verifier only sees values that are mathematically consistent with knowledge of the secret.

## 4. Software Architecture

The prototype is divided into separate files to keep the responsibilities clear.

- `common.py` contains the public group parameters, key generation, random number generation, and JSON socket helpers.
- `verifier.py` implements the verifier as a TCP server.
- `prover.py` implements the prover as a TCP client.
- `zpf.py` is a convenience launcher with simple subcommands.

The communication model is intentionally simple. Both processes exchange newline-delimited JSON messages through a TCP socket. This makes the execution easy to inspect during a demonstration and keeps the code readable.

The verifier starts first and listens on a configurable host and port. The prover then connects to the verifier and starts the protocol. Each round produces three main messages:

1. prover to verifier: commitment;
2. verifier to prover: challenge;
3. prover to verifier: response.

After each round, the verifier sends an explicit round result, and at the end it sends a final acceptance or rejection message.

## 5. Large Integer Cryptography

The assignment requires public cryptography with large integers of about 200 decimal digits. To satisfy this, I used a 768-bit MODP prime from a standard Internet group definition. A 768-bit prime is more than 200 decimal digits long, so it clearly meets the requirement.

This choice has several advantages:

- it avoids using insecure toy numbers;
- it makes the arithmetic realistic;
- it is still small enough to run instantly on a normal laptop;
- it demonstrates that Python can handle large integer modular exponentiation directly.

The implementation relies on Python's built-in `pow(base, exp, mod)` function, which performs modular exponentiation efficiently even for very large operands.

## 6. Key Generation

The demo includes a small setup phase. A secret key `x` is chosen at random, and the public key `y = g^x mod p` is derived from it.

The setup produces two files:

- `public_data.json`, containing the public parameters and the public key;
- `prover_secret.json`, containing the secret key known only to the prover.

This separation is useful for the demonstration because it makes the trust model explicit: the verifier can read only the public file, while the prover uses both the public and secret data.

## 7. Execution and Demonstration

To run the prototype:

1. generate the demo keys with `python3 zpf.py setup`;
2. start the verifier with `python3 verifier.py --once`;
3. start the prover with `python3 prover.py`.

During execution, the prover prints the progress of each round, and the verifier prints whether the authentication is accepted or rejected. This is suitable for the oral interview because it allows the protocol to be shown live in two terminals.

In the demonstration, I can explain:

- which value is public and which value is secret;
- why the prover does not reveal the secret key;
- how each challenge creates uncertainty for a dishonest prover;
- why repeating rounds reduces the probability of cheating.

## 8. Security Discussion

This prototype is educational rather than production-ready. It captures the essential idea of zero-knowledge identification, but some engineering choices are simplified because the assignment focuses on the protocol, not on a hardened security product.

For example:

- the verifier uses a one-bit challenge per round, which is standard for the basic protocol but requires multiple rounds;
- the communication is plain TCP and not encrypted with TLS;
- there is no persistent user database or certificate infrastructure;
- the system demonstrates proof of knowledge of a secret, not a full non-interactive proof system.

Even with these simplifications, the prototype still correctly shows the zero-knowledge property at a practical level: the prover convinces the verifier without disclosing the secret.

## 9. Conclusion

The final prototype satisfies the assignment requirements:

- it uses two independent processes;
- the processes communicate through sockets;
- it relies on public-key cryptography with large integers above 200 decimal digits;
- it is simple enough to explain and demonstrate interactively.

The Schnorr identification protocol was a good fit because it combines solid mathematical foundations with a small and understandable implementation. The prototype can be run live in a few seconds and provides a clear demonstration of the main idea behind zero-knowledge proofs: proving knowledge without revealing the secret itself.
