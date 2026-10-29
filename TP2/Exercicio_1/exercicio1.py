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

        São vizinhas as células cuja diferença máxima entre índices é 1,
        excluindo a própria célula. Cada célula normal tem assim até oito
        vizinhos, incluindo os diagonais.

        Consideram-se duas relações de transição: a atualização de uma célula
        normal escolhida por passo e a atualização simultânea de todas as
        células normais. No segundo caso, todas usam o mesmo estado anterior
        para contar os vizinhos. As células das fronteiras conservam o valor.

        As propriedades a verificar são a não alcançabilidade do estado em que
        todas as células normais estão mortas e a ausência de células normais
        permanentemente mortas ou vivas.
        """
    )
    return


@app.cell
def _():
    def contar_vizinhos(estado, i: int, j: int) -> int:
        n = len(estado) - 2
        if not (1 <= i <= n and 1 <= j <= n):
            raise ValueError("A célula tem de pertencer à grelha normal")

        return sum(
            estado[i + di][j + dj]
            for di in (-1, 0, 1)
            for dj in (-1, 0, 1)
            if di != 0 or dj != 0
        )

    def proximo_valor(estado, i: int, j: int) -> bool:
        vizinhos = contar_vizinhos(estado, i, j)
        return vizinhos == 3 or (estado[i][j] and vizinhos == 2)

    def transicao(estado, modo: str, celula: tuple[int, int] | None = None):
        n = len(estado) - 2

        if n <= 16 or any(len(linha) != n + 2 for linha in estado):
            raise ValueError("O estado deve ser uma grelha quadrada com N > 16")
        if any(estado[n + 1]) or any(estado[i][n + 1] for i in range(n + 1)):
            raise ValueError("A fronteira final tem de estar morta")

        seguinte = [list(linha) for linha in estado]

        if modo == "individual":
            if celula is None:
                raise ValueError("Indica a célula normal a atualizar")
            
            i, j = celula
            seguinte[i][j] = proximo_valor(estado, i, j)
        elif modo == "simultaneo":
            for i in range(1, n + 1):
                for j in range(1, n + 1):
                    seguinte[i][j] = proximo_valor(estado, i, j)
        else:
            raise ValueError("O modo deve ser 'individual' ou 'simultaneo'")

        return tuple(tuple(linha) for linha in seguinte)

    return contar_vizinhos, proximo_valor, transicao


@app.cell
def _(estado0, mo, n, transicao):
    modo = "simultaneo"
    celula = (1, 1)
    estado1 = transicao(
        estado0,
        modo,
        celula if modo == "individual" else None,
    )
    alteradas = sum(
        estado0[i][j] != estado1[i][j]
        for i in range(1, n + 1)
        for j in range(1, n + 1)
    )

    mo.md(
        f"No modo **{modo}**, mudaram **{alteradas} células normais** "
        "na primeira transição."
    )
    return (estado1, modo)


if __name__ == "__main__":
    app.run()
