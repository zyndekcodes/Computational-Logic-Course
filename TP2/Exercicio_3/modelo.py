"""SFOTS do CFA de multiplicacao, com valores na entrada dos nodos."""

from math import isqrt

import z3


INIT, SKIP, LEFT, RIGHT, STOP, ERRO_LEFT, ERRO_RIGHT = range(7)
NOMES = ("init", "skip", "left", "right", "stop", "erro_left", "erro_right")
CAMPOS = ("pc", "a", "b", "x", "y", "z")
SEMANTICAS = ("sem_sinal", "com_sinal")


def estado(nome, n):
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n tem de ser um inteiro positivo")
    return {
        "pc": z3.BitVec(f"{nome}_pc", 3),
        **{v: z3.BitVec(f"{nome}_{v}", n) for v in CAMPOS[1:]},
    }


def dominio(s):
    return z3.ULE(s["pc"], ERRO_RIGHT)


def erro(s):
    return z3.Or(s["pc"] == ERRO_LEFT, s["pc"] == ERRO_RIGHT)


def terminal(s):
    return z3.Or(s["pc"] == STOP, erro(s))


def par(y):
    return (y & 1) == 0


def capacidade(n, semantica):
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n tem de ser um inteiro positivo")
    if semantica not in SEMANTICAS:
        raise ValueError(f"semantica invalida: {semantica}")
    return (1 << (n - (semantica == "com_sinal"))) - 1


def produto_largo(s):
    n = s["a"].size()
    return z3.ZeroExt(n, s["a"]) * z3.ZeroExt(n, s["b"])


def condicao_entrada(s, condicao="livre", semantica="sem_sinal"):
    n = s["a"].size()
    cap = capacidade(n, semantica)
    # Em com_sinal so admitimos os inteiros nao negativos do programa.
    entrada = z3.And(z3.ULE(s["a"], cap), z3.ULE(s["b"], cap))
    if condicao == "livre":
        return entrada
    if condicao == "enunciado":
        # E exatamente a,b < sqrt(2**n), tambem para n impar.
        limite = isqrt((1 << n) - 1)
        return z3.And(entrada, z3.ULE(s["a"], limite), z3.ULE(s["b"], limite))
    if condicao == "produto_cabe":
        return z3.And(entrada, z3.ULE(produto_largo(s), cap))
    raise ValueError(f"condicao de entrada invalida: {condicao}")


def inicial(s, condicao="livre", semantica="sem_sinal"):
    # Normalizamos os valores de init; a sua acao volta a copiar a,b,0.
    return z3.And(
        s["pc"] == INIT,
        s["x"] == s["a"], s["y"] == s["b"], s["z"] == 0,
        condicao_entrada(s, condicao, semantica),
    )


def overflow_left(s, semantica="sem_sinal"):
    n = s["x"].size()
    cap = capacidade(n, semantica)
    if semantica == "sem_sinal":
        return z3.UGT(s["x"], cap // 2)
    # Para valores com sinal, x+x nao pode ultrapassar nenhum extremo.
    return z3.Not(z3.And(
        z3.BVAddNoOverflow(s["x"], s["x"], True),
        z3.BVAddNoUnderflow(s["x"], s["x"]),
    ))


def overflow_right(s, semantica="sem_sinal"):
    capacidade(s["x"].size(), semantica)
    if semantica == "sem_sinal":
        return z3.ULT(s["z"] + s["x"], s["z"])
    return z3.Not(z3.And(
        z3.BVAddNoOverflow(s["z"], s["x"], True),
        z3.BVAddNoUnderflow(s["z"], s["x"]),
    ))


def transicao(s, t, semantica="sem_sinal"):
    capacidade(s["x"].size(), semantica)

    def ramo(guarda, destino, **alteracoes):
        valores = dict(s)
        valores.update(alteracoes, pc=destino)
        return z3.And(guarda, *(t[v] == valores[v] for v in CAMPOS))

    ov_left = overflow_left(s, semantica)
    ov_right = overflow_right(s, semantica)
    return z3.And(dominio(s), dominio(t), z3.Or(
        ramo(s["pc"] == INIT, SKIP, x=s["a"], y=s["b"], z=0),
        ramo(z3.And(s["pc"] == SKIP, s["y"] == 0), STOP),
        ramo(z3.And(s["pc"] == SKIP, s["y"] != 0, par(s["y"])), LEFT),
        ramo(z3.And(s["pc"] == SKIP, s["y"] != 0, z3.Not(par(s["y"]))), RIGHT),
        ramo(s["pc"] == LEFT, z3.If(ov_left, z3.BitVecVal(ERRO_LEFT, 3), z3.BitVecVal(SKIP, 3)),
             x=s["x"] << 1, y=z3.LShR(s["y"], 1)),
        ramo(s["pc"] == RIGHT, z3.If(ov_right, z3.BitVecVal(ERRO_RIGHT, 3), z3.BitVecVal(SKIP, 3)),
             y=s["y"] - 1, z=s["z"] + s["x"]),
        # Stop e erros ficam absorventes para interpretar formulas temporais.
        ramo(terminal(s), s["pc"]),
    ))


def controlo(s):
    return z3.And(
        dominio(s),
        z3.Implies(s["pc"] == INIT,
                   z3.And(s["x"] == s["a"], s["y"] == s["b"], s["z"] == 0)),
        z3.Implies(s["pc"] == LEFT, z3.And(s["y"] != 0, par(s["y"]))),
        z3.Implies(s["pc"] == RIGHT, z3.And(s["y"] != 0, z3.Not(par(s["y"])))),
        z3.Implies(s["pc"] == STOP, s["y"] == 0),
    )


def invariante_modular(s):
    return s["x"] * s["y"] + s["z"] == s["a"] * s["b"]


def invariante_exato(s):
    n = s["a"].size()
    x, y, z = (z3.ZeroExt(n, s[v]) for v in ("x", "y", "z"))
    # 2n bits chegam: (2**n-1)**2 + (2**n-1) < 2**(2*n).
    return x * y + z == produto_largo(s)


def invariante_seguranca(s, condicao="enunciado", semantica="sem_sinal"):
    cap = capacidade(s["a"].size(), semantica)
    return z3.And(
        controlo(s), condicao_entrada(s, condicao, semantica),
        z3.Not(erro(s)), invariante_exato(s),
        *(z3.ULE(s[v], cap) for v in ("x", "y", "z")),
    )


def rank(s):
    """Variante natural, sem wraparound, que desce em cada passo nao terminal."""
    n = s["y"].size()
    y = z3.ZeroExt(2, s["y"])
    return z3.If(
        terminal(s), z3.BitVecVal(0, n + 2),
        (y << 1) + z3.If(s["pc"] == INIT, z3.BitVecVal(3, n + 2),
                        z3.If(s["pc"] == SKIP, z3.BitVecVal(2, n + 2),
                              z3.BitVecVal(1, n + 2))),
    )


def passo_concreto(s, n, semantica="sem_sinal"):
    """Interpretador pequeno e independente das formulas Z3."""
    cap = capacidade(n, semantica)
    t = dict(s)
    pc = s["pc"]
    if pc == INIT:
        t.update(pc=SKIP, x=s["a"], y=s["b"], z=0)
    elif pc == SKIP:
        t["pc"] = STOP if s["y"] == 0 else LEFT if s["y"] % 2 == 0 else RIGHT
    elif pc == LEFT:
        resultado = 2 * s["x"]
        t.update(pc=ERRO_LEFT if resultado > cap else SKIP,
                 x=resultado % (1 << n), y=s["y"] // 2)
    elif pc == RIGHT:
        resultado = s["z"] + s["x"]
        t.update(pc=ERRO_RIGHT if resultado > cap else SKIP,
                 y=s["y"] - 1, z=resultado % (1 << n))
    elif pc not in (STOP, ERRO_LEFT, ERRO_RIGHT):
        raise ValueError("local de controlo invalido")
    return t


def simular(a, b, n, semantica="sem_sinal"):
    cap = capacidade(n, semantica)
    if any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= cap
           for v in (a, b)):
        raise ValueError(f"as entradas devem estar entre 0 e {cap}")
    s = dict(pc=INIT, a=a, b=b, x=a, y=b, z=0)
    caminho = [s]
    # Popcount(b) + bit_length(b)-1 iteracoes, cada uma com dois passos.
    for _ in range(4 * n + 2):
        if s["pc"] in (STOP, ERRO_LEFT, ERRO_RIGHT):
            return caminho
        s = passo_concreto(s, n, semantica)
        caminho.append(s)
    raise AssertionError("a execucao ultrapassou o limite teorico")


def ler_estado(modelo, s):
    return {v: modelo.eval(s[v], model_completion=True).as_long() for v in CAMPOS}


def fixar(s, valores):
    return z3.And(*(s[v] == valores[v] for v in CAMPOS))
