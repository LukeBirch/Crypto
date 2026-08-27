# LWE Cryptography

A Python implementation exploring **Learning With Errors (LWE)** encryption and key-recovery attacks.

The project implements key generation, encryption and decryption, alongside several approaches for attempting to recover the private key from the public key.

## Features

* LWE-style key generation
* Binary plaintext encryption and decryption
* Finite-field arithmetic using `galois`
* Private-key recovery using linear algebra
* Brute-force/probabilistic secret recovery
* Experimental lattice-based attack

## Technologies

* Python
* NumPy
* SciPy
* `galois`
* `more-itertools`

## Main Functions

* `keygen()` — Generates the public and private keys.
* `encrypt()` — Encrypts binary plaintext using the public key.
* `decrypt()` — Recovers plaintext using the private key.
* `crack1()` — Attempts to recover the secret using a subset of the public equations.
* `crack2()` — Uses repeated random subsets to identify likely secret values.
* `crack3()` — Experimental lattice-based approach to secret recovery.

## Purpose

This university project was developed to explore finite fields, lattice-based cryptography, and LWE.

## Author

**Luke Birch**
