import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # TP2 — Exercício 1: autómato celular

        Considera-se uma grelha de células booleanas, em que 0 representa uma
        célula morta e 1 representa uma célula viva. As células normais ocupam
        as posições $(i,j) \in \{1,\ldots,N\}^2$, com $N > 16$.

        No estado inicial, apenas $(1,1)$, $(1,2)$, $(2,1)$ e $(2,2)$ estão vivas.
        As células da fronteira inicial mantêm os valores escolhidos no início;
        as da fronteira final mantêm-se mortas.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Estado inicial

        O estado é uma grelha $(N+2) \times (N+2)$. Os índices de 1 a $N$
        correspondem às células normais. A linha e a coluna de índice 0 formam
        a fronteira inicial; a linha e a coluna de índice $N+1$ formam a
        fronteira final.

        Cada célula da fronteira inicial é escolhida de forma independente,
        com probabilidade $1/2$ de estar viva. O parâmetro `seed` permite reproduzir
        a mesma escolha num exemplo concreto.
        """
    )
    return


@app.cell
def _():
    import random

    return (random,)


@app.cell
def _(random):
    def criar_estado_inicial(n: int, seed: int | None = None) -> tuple[tuple[bool, ...], ...]:
        if n <= 16:
            raise ValueError("N tem de ser maior que 16")

        rng = random.Random(seed)
        estado = [[False for _ in range(n + 2)] for _ in range(n + 2)]

        for j in range(n + 1):
            estado[0][j] = bool(rng.getrandbits(1))
        for i in range(1, n + 1):
            estado[i][0] = bool(rng.getrandbits(1))

        for i, j in ((1, 1), (1, 2), (2, 1), (2, 2)):
            estado[i][j] = True

        return tuple(tuple(linha) for linha in estado)

    return (criar_estado_inicial,)


@app.cell
def _(criar_estado_inicial, mo):
    n = 17
    estado0 = criar_estado_inicial(n, seed=2026)
    vivas_normais = sum(
        estado0[i][j]
        for i in range(1, n + 1)
        for j in range(1, n + 1)
    )
    vivas_fronteira = (
        sum(estado0[0][j] for j in range(n + 1))
        + sum(estado0[i][0] for i in range(1, n + 1))
    )

    mo.md(
        f"Para $N={n}$, o estado inicial tem **{vivas_normais} células normais vivas** "
        f"e **{vivas_fronteira} células vivas na fronteira inicial**."
    )
    return (estado0, n)


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Evolução e propriedades

        Uma célula morta nasce quando tem exatamente três vizinhos vivos.
        Uma célula viva sobrevive quando tem dois ou três vizinhos vivos.
        Nos restantes casos, a célula fica morta.

        Consideram-se duas relações de transição: a atualização de uma célula
        normal por passo e a atualização simultânea de todas as células normais.

        As propriedades a verificar são a não alcançabilidade do estado em que
        todas as células normais estão mortas e a ausência de células normais
        permanentemente mortas ou vivas.
        """
    )
    return


if __name__ == "__main__":
    app.run()
