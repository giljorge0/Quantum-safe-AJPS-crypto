import secrets


def low_hamming_weight_number(n: int, weight: int):
    """Gera um número de n bits com um Peso de Hamming específico."""
    bits = [0] * n
    indices = set()
    while len(indices) < weight:
        indices.add(secrets.randbelow(n))
    for i in indices:
        bits[i] = 1
    return int("".join(map(str, bits)), 2)

# PARÂMETROS MELHORES:
n = 521  # Primo de Mersenne (2^521 - 1 também é primo)
p = 2**n - 1
h = 11  # Peso Hamming maior


F = low_hamming_weight_number(n, h)
G = low_hamming_weight_number(n, h)

def seq(F, G, p):
    f = F % p
    g = G % p
    g_inv = pow(g, -1, p)
    ratio = f * g_inv % p
    return ratio

# MUDANÇA: Retorna int, não bin()
def encryptar(pk, b, n, p):
    A = low_hamming_weight_number(n, h)
    B = low_hamming_weight_number(n, h)
    
    resultado = ((A * pk % p) + B) % p
    
    if int(b) % 2 == 1:
        resultado = (-resultado) % p
    
    return resultado  # ✓ Retorna int diretamente

def iterar(m, pk, n):
    mens = bin(m)[2:]
    nova = [encryptar(pk, bit, n, p) for bit in mens]
    return nova

def hamming_weight(x):
    """Calcula o Peso de Hamming (quantidade de bits '1')."""
    return bin(x).count('1')

def decryptar(entrada_criptograma, sk, n, h):
    prod = entrada_criptograma * sk % p
    d = hamming_weight(prod)
    
    if d <= 2 * pow(h, 2):
        return 0
    elif d >= n - 2 * pow(h, 2):
        return 1
    else:
        return None

def iterar_descriptar(criptograma, G, n, h):
    # Agora criptograma já é lista de ints
    nova = [decryptar(c, G, n, h) for c in criptograma]
    return nova

H = seq(F, G, p)

mensagem = int("1101101010110101011001010101011100001011011011", 2)
print(f"\nMensagem original: {bin(mensagem)[2:]}")

encriptada = iterar(mensagem, H, n)

resultado = iterar_descriptar(encriptada, G, n, h)

print(f"Mensagem recuperada: {''.join(map(str, [x for x in resultado if x is not None]))}")