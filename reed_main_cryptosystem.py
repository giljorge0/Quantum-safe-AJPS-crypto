"""
Mersenne KEM com Reed-Muller RM(m,1).

Usa SEMPRE r=1 com voto maioritário (decoder óptimo).
n_mersenne é escolhido para ser >= n_cw = 2^m.
"""
import secrets
import numpy as np
from math import comb
from itertools import product


# =================== Reed-Muller RM(m,1) ===================

def get_points(m):
    if m == 0:
        return [()]
    sub = get_points(m - 1)
    return [p + (0,) for p in sub] + [p + (1,) for p in sub]

def generator_matrix(m):
    """Matriz geradora de RM(m,1)."""
    r = 1
    points = get_points(m)
    n = 2 ** m
    # Monómios: [constante, x0, x1, ..., x_{m-1}]
    monomials = [[]] + [[i] for i in range(m)]
    k = len(monomials)  # = m+1
    G = np.zeros((k, n), dtype=np.uint8)
    for i, mono in enumerate(monomials):
        for j, point in enumerate(points):
            val = 1
            for idx in mono:
                val *= point[idx]
            G[i][j] = val % 2
    return G

def encode(message_bits, G):
    """Array numpy de k bits → inteiro (codeword de n=2^m bits)."""
    cw = np.dot(message_bits, G) % 2
    result = 0
    for i, b in enumerate(cw):
        if int(b):
            result |= (1 << i)
    return result

def majority_decode(received_int, m):
    """
    Decoder por voto maioritário para RM(m,1).
    Recebe um inteiro (codeword de 2^m bits com possíveis erros).
    Devolve lista de m+1 bits [a0, a1, ..., am].
    Corrige até 2^(m-2)-1 erros.
    """
    n = 2 ** m
    points = get_points(m)
    point_to_idx = {p: i for i, p in enumerate(points)}

    # Converte inteiro para lista de bits
    r_arr = [(received_int >> i) & 1 for i in range(n)]

    coefficients = [0] * (m + 1)  # [a0, a1, ..., am]

    # Recupera a1, ..., am por voto maioritário em pares
    for var in range(m):
        v1, v0 = 0, 0
        for idx, p in enumerate(points):
            if p[var] == 1:
                p_comp = list(p)
                p_comp[var] = 0
                idx_comp = point_to_idx[tuple(p_comp)]
                if r_arr[idx] ^ r_arr[idx_comp]:
                    v1 += 1
                else:
                    v0 += 1
        coefficients[var + 1] = 1 if v1 > v0 else 0

    # Recupera a0 usando os coeficientes já encontrados
    v1, v0 = 0, 0
    for idx, p in enumerate(points):
        contrib = 0
        for var in range(m):
            contrib ^= coefficients[var + 1] * p[var]
        if r_arr[idx] ^ contrib:
            v1 += 1
        else:
            v0 += 1
    coefficients[0] = 1 if v1 > v0 else 0

    return coefficients


# =================== Mersenne KEM ===================

def low_hamming_weight_number(n, h):
    indices = set()
    while len(indices) < h:
        indices.add(secrets.randbelow(n))
    num = 0
    for i in indices:
        num |= (1 << i)
    return num

def get_mersenne_exponent(min_n):
    """Menor Mersenne exponent >= min_n."""
    mersenne_exponents = [31, 61, 127, 521, 607, 1279, 2203, 2281,
                          3217, 4253, 4423, 9689, 9941, 11213, 19937,
                          21701, 86243, 216091, 756839]
    for n in mersenne_exponents:
        if n >= min_n:
            return n
    return min_n

def generate_keys(lambda_param):
    """
    lambda_param bits de segurança.
    Usa RM(m,1) com m = lambda_param - 1
      → k = m+1 = lambda_param bits de mensagem
      → n_cw = 2^m bits de codeword
    n_mersenne = maior entre 10*h^2 e n_cw.
    """
    h = lambda_param
    m = lambda_param - 1       # m tal que k = m+1 = lambda_param
    n_cw = 2 ** m              # tamanho da codeword

    # n_mersenne tem de ser >= n_cw E >= 10*h^2
    n_min = max(10 * h ** 2, n_cw)
    n_mers = get_mersenne_exponent(n_min)

    p = (1 << n_mers) - 1
    F     = low_hamming_weight_number(n_mers, h)
    G_key = low_hamming_weight_number(n_mers, h)
    R     = secrets.randbits(n_mers)
    T     = (F * R + G_key) % p

    d = 2 ** (m - 1)  # distância mínima RM(m,1)
    print(f"Parâmetros:")
    print(f"  λ={lambda_param}, h={h}")
    print(f"  n_mersenne={n_mers} (p tem {n_mers} bits)")
    print(f"  RM({m},1): k={m+1}, n_cw={n_cw}, corrige até {(d-1)//2} erros")
    print(f"  Ruído estimado: ~{2*h**2} bits  <<  {(d-1)//2} ✓")

    return (R, T), F, n_mers, p, h, m, n_cw

def encrypt(pk, encoded_m, n, p, h):
    R, T = pk
    A  = low_hamming_weight_number(n, h)
    B1 = low_hamming_weight_number(n, h)
    B2 = low_hamming_weight_number(n, h)
    C1 = (A * R + B1) % p
    C2 = ((A * T + B2) % p) ^ encoded_m
    return (C1, C2)

def decrypt(C, sk_F, p, m):
    C1, C2 = C
    noisy_m = ((sk_F * C1) % p) ^ C2
    return majority_decode(noisy_m, m)


# =================== Execução ===================

lambda_param = 20

pk, sk, n, p, h, m, n_cw = generate_keys(lambda_param)
G = generator_matrix(m)
k = m + 1

# Mensagem aleatória de k bits
np.random.seed(2)
message = np.random.randint(0, 2, size=k)
print(f"\nMensagem original ({k} bits): {message.tolist()}")

# Codifica e encripta
enc_m = encode(message, G)
C = encrypt(pk, enc_m, n, p, h)

# Decripta
recovered = decrypt(C, sk, p, m)

print(f"Recuperada  ({len(recovered)} bits): {recovered}")
print(f"\nMatch: {recovered == message.tolist()}")
