"""Obrigacoes de prova e contraprovas do exercicio 3.

`sat` no passo indutivo nao prova um erro alcancavel.
"""

from time import perf_counter

import z3

import modelo as m


def consultar(formula, estados=(), timeout_ms=10000):
    solver = z3.Solver()
    solver.set(timeout=timeout_ms, random_seed=0)
    inicio = perf_counter()
    solver.add(formula)
    resultado = solver.check()
    dados = {"estado": str(resultado), "segundos": round(perf_counter() - inicio, 6)}
    if resultado == z3.sat:
        modelo = solver.model()
        dados["caminho"] = [m.ler_estado(modelo, s) for s in estados]
    elif resultado == z3.unknown:
        dados["motivo"] = solver.reason_unknown()
    return dados


def k_inducao(n, propriedade, k=1, condicao="livre", semantica="sem_sinal",
              timeout_ms=10000):
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k tem de ser positivo")
    estados = [m.estado(f"s{i}", n) for i in range(k + 1)]
    transicoes = [m.transicao(estados[i], estados[i + 1], semantica) for i in range(k)]
    propriedades = [propriedade(s) for s in estados]
    base = consultar(z3.And(
        m.inicial(estados[0], condicao, semantica), *transicoes,
        z3.Or(*(z3.Not(p) for p in propriedades)),
    ), estados, timeout_ms)
    # Nao introduzimos o estado inicial no passo indutivo.
    passo = consultar(z3.And(*transicoes, *propriedades[:-1],
                             z3.Not(propriedades[-1])), estados, timeout_ms)
    return {"n": n, "k": k, "base": base, "passo": passo,
            "provado": base["estado"] == passo["estado"] == "unsat"}


def verificar_modular(n, k=2, timeout_ms=10000):
    return k_inducao(n, m.invariante_modular, k, timeout_ms=timeout_ms)


def verificar_seguranca(n, semantica="sem_sinal", condicao="enunciado", timeout_ms=10000):
    def propriedade(s):
        return m.invariante_seguranca(s, condicao, semantica)

    return k_inducao(n, propriedade, 1, condicao, semantica, timeout_ms)


def bmc(n, mau, limite, condicao="livre", semantica="sem_sinal", timeout_ms=10000):
    if limite < 0:
        raise ValueError("limite negativo")
    estados = [m.estado(f"b{i}", n) for i in range(limite + 1)]
    transicoes = [m.transicao(estados[i], estados[i + 1], semantica) for i in range(limite)]
    return consultar(z3.And(
        m.inicial(estados[0], condicao, semantica), *transicoes,
        z3.Or(*(mau(s) for s in estados)),
    ), estados, timeout_ms)


def verificar_terminacao(n, semantica="sem_sinal", timeout_ms=10000):
    s, t = m.estado("r0", n), m.estado("r1", n)
    controlo = k_inducao(n, m.controlo, 1, semantica=semantica, timeout_ms=timeout_ms)
    positiva = consultar(z3.And(m.controlo(s), z3.Not(m.terminal(s)),
                                m.rank(s) == 0), timeout_ms=timeout_ms)
    descida = consultar(z3.And(
        m.controlo(s), m.transicao(s, t, semantica), z3.Not(m.terminal(s)),
        z3.Not(z3.ULT(m.rank(t), m.rank(s))),
    ), (s, t), timeout_ms)
    return {"n": n, "controlo": controlo, "rank_positivo": positiva,
            "rank_desce": descida,
            "provado": controlo["provado"] and positiva["estado"] == descida["estado"] == "unsat"}


def eventualmente_terminal(estados, so_sucesso=False):
    """F terminal num prefixo: disjuncao das posicoes em que se atinge o alvo."""
    return z3.Or(*(s["pc"] == m.STOP if so_sucesso else m.terminal(s) for s in estados))


def verificar_animacao_limitada(n, condicao="livre", semantica="sem_sinal",
                                so_sucesso=False, timeout_ms=10000):
    # O limite 4n e demonstrado no relatorio, nao escolhido por tentativa.
    limite = 4 * n
    estados = [m.estado(f"f{i}", n) for i in range(limite + 1)]
    formula = z3.And(
        m.inicial(estados[0], condicao, semantica),
        *(m.transicao(estados[i], estados[i + 1], semantica) for i in range(limite)),
        z3.Not(eventualmente_terminal(estados, so_sucesso)),
    )
    return {"limite": limite, **consultar(formula, estados, timeout_ms)}


def tabela_caminho(caminho):
    return [{"passo": i, "local": m.NOMES[s["pc"]],
             **{v: s[v] for v in ("a", "b", "x", "y", "z")}} for i, s in enumerate(caminho)]


def tabela_markdown(linhas):
    """Tabela simples, legivel tanto em Marimo como na copia PDF."""
    if not linhas:
        return "Sem linhas."
    colunas = list(linhas[0])
    cabecalho = "| " + " | ".join(colunas) + " |"
    separador = "| " + " | ".join("---" for _ in colunas) + " |"
    corpo = ["| " + " | ".join(str(linha[c]) for c in colunas) + " |" for linha in linhas]
    return "\n".join([cabecalho, separador, *corpo])
