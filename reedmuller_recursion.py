from itertools import combinations, product
import numpy as np

from itertools import combinations, product
import numpy as np

def get_points(m):
    """
    Gera pontos com x_{m-1} variando mais lentamente:
    Primeiros 2^(m-1) pontos têm x_{m-1}=0
    Últimos    2^(m-1) pontos têm x_{m-1}=1
    """
    if m == 0:
        return [()]
    sub = get_points(m-1)
    # x_{m-1}=0 primeiro, x_{m-1}=1 depois
    return [p + (0,) for p in sub] + [p + (1,) for p in sub]


def get_monomials(m, r):
    if m == 0:
        return [[]]
    without_xm = get_monomials(m-1, r)
    if r >= 1:
        with_xm_base = get_monomials(m-1, r-1)
        with_xm = [mono + [m-1] for mono in with_xm_base]
    else:
        with_xm = []
    return without_xm + with_xm


def generator_matrix(m, r):
    points = get_points(m)  # ← usa a nova ordem!
    n = 2**m
    monomials = get_monomials(m, r)
    k = len(monomials)
    G = np.zeros((k, n), dtype=int)
    for i, mono in enumerate(monomials):
        for j, point in enumerate(points):
            val = 1
            for idx in mono:
                val *= point[idx]
            G[i][j] = val % 2
    return G, monomials


def encode(message, G):
    return np.dot(message, G) % 2


def inverse_mod2(M):
    n = M.shape[0]
    A = np.concatenate([M.copy(), np.eye(n, dtype=int)], axis=1) % 2
    for i in range(n):
        if A[i,i] == 0:
            for j in range(i+1, n):
                if A[j,i] == 1:
                    A[[i,j]] = A[[j,i]]
                    break
        for j in range(n):
            if j != i and A[j,i] == 1:
                A[j] = (A[j] + A[i]) % 2
    return A[:, n:]


def decode_recursive(received, m, r, G_inv_cache=None):
    if G_inv_cache is None:
        G_inv_cache = {}
    n = 2**m

    if r == m:
        if (m, r) not in G_inv_cache:
            G, _ = generator_matrix(m, r)
            G_inv_cache[(m, r)] = inverse_mod2(G)
        G_inv = G_inv_cache[(m, r)]
        return (np.dot(received, G_inv) % 2).tolist()

    if r == 0:
        bit = 1 if sum(received) > len(received)/2 else 0
        return [bit]

    half = n // 2
    u   = received[:half]
    upv = received[half:]
    v = [u[i] ^ upv[i] for i in range(half)]

    coefs_h = decode_recursive(v, m-1, r-1, G_inv_cache)
    coefs_g = decode_recursive(list(u), m-1, r, G_inv_cache)

    return coefs_g + coefs_h


# ===== TESTE RM(4,3) =====

m, r = 22, 1

G, monomials = generator_matrix(m, r)
k = len(monomials)

# Gera mensagem aleatória do tamanho correcto
mensagem = np.random.randint(0, 2, size=k)

print(f"RM({m},{r}): n={2**m}, k={len(monomials)}, d={2**(m-r)}")
print()

codeword = encode(mensagem, G)

print(f"Mensagem:   {mensagem.tolist()}")
print(f"Codeword:   {codeword.tolist()}")

# Introduz 1 erro
recebido = codeword.copy()
recebido[11] ^=1
recebido[21] ^=1
recebido[9] ^=1
print(f"Recebido:   {recebido.tolist()}  (erro na posição 5)")

recuperado = decode_recursive(recebido.tolist(), m, r)
print(f"Recuperado: {recuperado}")
print(f"Correcto:   {recuperado == mensagem.tolist()}")