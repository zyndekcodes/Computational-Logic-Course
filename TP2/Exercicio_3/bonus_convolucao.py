"""Ilustracao elementar de produto por convolucao, nao o algoritmo do artigo."""


def multiplicar_convolucao(a, b):
    if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in (a, b)):
        raise ValueError("as entradas devem ser inteiros nao negativos")
    bits_a = [(a >> i) & 1 for i in range(max(1, a.bit_length()))]
    bits_b = [(b >> i) & 1 for i in range(max(1, b.bit_length()))]
    coeficientes = [0] * (len(bits_a) + len(bits_b) - 1)
    for i, bit_a in enumerate(bits_a):
        for j, bit_b in enumerate(bits_b):
            coeficientes[i + j] += bit_a * bit_b

    # Passamos o excesso de cada coluna para a seguinte.
    resultado, carry = 0, 0
    for i, coeficiente in enumerate(coeficientes):
        coluna = coeficiente + carry
        resultado |= (coluna % 2) << i
        carry = coluna // 2
    resultado |= carry << len(coeficientes)
    return {"a_bits": bits_a, "b_bits": bits_b,
            "coeficientes": coeficientes, "produto": resultado}
