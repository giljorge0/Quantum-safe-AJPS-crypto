# Mersenne Prime Cryptosystem Implementation

## 📌 Overview
This project implements a **public-key cryptosystem based on Mersenne primes**, inspired by the paper:

> *A New Public-Key Cryptosystem via Mersenne Numbers* (Aggarwal, Joux, Prakash, Santha)

The system is designed as a **post-quantum cryptographic candidate**, relying on the hardness of recovering low Hamming weight vectors in modular arithmetic over Mersenne primes.

---

## 🧠 Key Concepts

- **Mersenne Prime**: A prime of the form \( p = 2^n - 1 \)
- **Hamming Weight**: Number of `1`s in a binary string
- **Public-Key Cryptography**: Uses separate keys for encryption and decryption
- **Error-Correcting Codes**: Ensures reliable decryption despite noise

---

## 🔐 Cryptosystem Structure

### Key Generation
- Select a Mersenne prime \( p = 2^n - 1 \)
- Generate:
  - Secret key: low Hamming weight vector \( F \)
  - Public key: \( (R, T = F·R + G) \)

### Encryption
- Input: message \( m \)
- Randomly generate low-weight values \( A, B_1, B_2 \)
- Compute:
  - \( C_1 = A·R + B_1 \)
  - \( C_2 = (A·T + B_2) ⊕ E(m) \)

### Decryption
- Recover message using:
  - \( D((F·C_1) ⊕ C_2) \)

---

## ⚙️ Implementation Details

- Language: Python (Jupyter Notebook)
- Core operations:
  - Modular arithmetic over \( 2^n - 1 \)
  - Bitwise operations
  - Random low Hamming weight vector generation
- Includes:
  - Key generation
  - Encryption & decryption
  - Error correction handling

---

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. Open the notebook:
   ```bash
   jupyter notebook Mersenne_Prime_Cryptosystem.ipynb
   ```

3. Run all cells to:
   - Generate keys
   - Encrypt sample messages
   - Decrypt and verify correctness

---

## 📊 Security Notes

- Security relies on:
  - **Mersenne Low Hamming Combination Assumption**
- Resistant to:
  - Classical brute force (≈ 2^h complexity)
  - Known lattice-based attacks (with proper parameters)
- Designed with **post-quantum considerations**

⚠️ This is an **academic implementation** and not production-ready.

---

## 📚 References

- Aggarwal et al., *A New Public-Key Cryptosystem via Mersenne Numbers*
- Course Project List 2026 (CPS)

---

## 👨‍💻 Authors

- [Your Name / Team Name]

---

## 📄 License

This project is for educational purposes. Add a license if needed.
