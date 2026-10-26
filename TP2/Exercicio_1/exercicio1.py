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
