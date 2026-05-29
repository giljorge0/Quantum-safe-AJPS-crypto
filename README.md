# Mersenne Prime Cryptosystem

Implementation of a post-quantum public-key cryptosystem based on Mersenne primes, inspired by:

> *A New Public-Key Cryptosystem via Mersenne Numbers* — Aggarwal, Joux, Prakash, Santha (2018)

The security relies on the hardness of the **Mersenne Low Hamming Combination (MLHC) problem**: given $(R,\ F \cdot R + G \bmod p)$ where $F, G$ have low Hamming weight $h$, no probabilistic polynomial-time adversary can distinguish $T$ from a uniformly random $n$-bit string.

---


## System Overview

### Key Generation
- Choose a Mersenne prime $p = 2^n - 1$ with $n > 10h^2$
- Sample secret key $F$ and noise term $G$ with Hamming weight exactly $h$
- Sample random $R \in \{0,1\}^n$
- Public key: $(R,\ T = F \cdot R + G \bmod p)$
- Secret key: $F$

### Encryption
Given message $m$ and public key $(R, T)$:
- Sample fresh low-weight $A, B_1, B_2$ with Hamming weight $h$
- $C_1 = A \cdot R + B_1 \bmod p$
- $C_2 = (A \cdot T + B_2 \bmod p)\ \oplus\ E(m)$

where $E(m)$ is an error-correcting encoding of $m$.

### Decryption
- Compute $F \cdot C_1 \bmod p$, which approximates $A \cdot T \bmod p$ up to low-weight noise
- Recover $E(m) \oplus \text{noise}$ via XOR with $C_2$
- Apply majority-vote decoder $D(\cdot)$ to strip the noise and recover $m$

---

## What the Notebook Covers

**Section 1 — Baseline (no error correction)**  
Minimal working example with $n=17$, no noise tolerance. Shows the raw structure of the scheme.

**Section 2 — Repetition Code**  
Replaces each message bit with a block of repeated bits. Majority voting corrects noise. Uses $n=127$, $k=7$, weight $= 4$.

**Section 3 — Bit-by-Bit Encryption**  
Encrypts one bit at a time via Hamming distance thresholding. Public key takes the form $H = F \cdot G^{-1} \bmod p$.

**Section 4 — Block PKE with Repetition Code**  
Full block-level public-key encryption with automatic Mersenne exponent selection based on security parameter $\lambda$.

**Section 5 — KEM + Hybrid PKE (IND-CCA2)**  
The complete production-grade construction:
- Key Encapsulation Mechanism (KEM) with Fujisaki-Okamoto transform
- Random oracles $H_1, H_2, H_3$ simulated via SHAKE-256
- Shared secret derived with SHA-256, used to key an XOR stream cipher
- 500-sample error rate test (zero failures observed)

**Section 6 — Security Analysis**  
- Theoretical complexity table for brute-force, LLL-based (BCGN17), Meet-in-the-Middle (dBDJdW17), and weak-key attacks across parameter sets
- Basic pseudorandomness check: compares mean and variance of $\text{Ham}(T)$ against a uniform random string

---

## Reed-Muller Variant (`reed_main_cryptosystem.py`)

Replaces the repetition code with a **Reed-Muller RM(m, 1)** code:

- Generator matrix constructed for first-order RM with $m$ variables
- Codeword length $n_{cw} = 2^m$, dimension $k = m+1$, minimum distance $d = 2^{m-1}$
- Corrects up to $\lfloor (d-1)/2 \rfloor = 2^{m-2} - 1$ bit errors
- Optimal majority-vote decoder (Reed's algorithm) recovers message coefficients variable by variable

The Mersenne exponent is chosen to satisfy both $n \geq 10h^2$ (security) and $n \geq n_{cw}$ (the codeword must fit).

**Why RM over repetition?** For a given rate, Reed-Muller corrects far more errors: RM(4,1) corrects up to 7 bit-flips in a 16-bit codeword, whereas a length-16 repetition code encoding 1 bit corrects up to 7 flips for that single bit only. RM encodes $m+1$ bits simultaneously with the same redundancy.

---

## Security Parameters

| $\lambda = h$ | $n$ (Mersenne exp.) | $\log_2\binom{n}{h}$ | LLL quantum cost | MITM classical cost |
|:---:|---:|---:|---:|---:|
| 8 | 607 | ≈ 35 bits | $2^8$ | $> 2^8$ |
| 16 | 2281 | ≈ 72 bits | $2^{16}$ | $> 2^{16}$ |
| 32 | 9689 | ≈ 150 bits | $2^{32}$ | $> 2^{32}$ |
| 64 | 19937 | ≈ 310 bits | $2^{64}$ | $> 2^{64}$ |
| **256** | **756839** | **≈ 1264 bits** | $2^{256}$ | $> 2^{256}$ |

Setting $h = \lambda$ ensures that even the LLL attack accelerated by Grover's algorithm costs $\Omega(2^\lambda)$, giving $\lambda$ bits of post-quantum security.

### Known Attacks

| Attack | Classical | Quantum | Mitigation |
|--------|-----------|---------|------------|
| Brute-force | $\binom{n}{h}$ | $\binom{n}{h}^{1/2}$ (Grover) | Large $h$ |
| LLL-based (BCGN17) | $O(2^{2h})$ | $O(2^h)$ | Set $h = \lambda$ |
| Meet-in-the-Middle (dBDJdW17) | $O\!\left(\binom{n-1}{h-1}^{1/2}\right)$ | $O\!\left(\binom{n-1}{h-1}^{1/3}\right)$ | Large $n$ |
| Weak-key (BCGN17) | Polynomial if $F, G < \sqrt{p}$ | — | Uniform random key generation |

---

## Requirements

```
python >= 3.9
numpy
scipy        # for statistical tests (Section 6)
jupyter
```

Install:
```bash
pip install numpy scipy jupyter
```

Run the notebook:
```bash
jupyter notebook Mersenne_Prime_Cryptosystem.ipynb
```

Run the Reed-Muller standalone:
```bash
python reed_main_cryptosystem.py
```

---

## References

- Aggarwal, D., Joux, A., Prakash, A., Santha, M. (2018). *A New Public-Key Cryptosystem via Mersenne Numbers*. CRYPTO 2018. [ePrint 2017/481](https://eprint.iacr.org/2017/481)
- Bernstein, D.J., Chou, T., Groot Bruinderink, L., Hülsing, A., Lange, T., Panny, L., Schwabe, P. (2017). *NTRU Prime*. (context for lattice-based comparison)
