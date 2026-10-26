# TP2 — Exercício 1

Estudo de uma variante do Conway's Game of Life através de uma máquina de estados finita.

## Problema

As células normais formam uma grelha $N \times N$, com $N > 16$. No estado inicial, apenas as células $(1,1)$, $(1,2)$, $(2,1)$ e $(2,2)$ estão vivas. As células da fronteira inicial têm valores fixos escolhidos aleatoriamente; as da fronteira final estão sempre mortas.

Cada célula normal evolui segundo a regra B3/S23. O modelo considera duas formas de atualização: uma célula por transição ou todas as células em simultâneo.

Pretende-se verificar se o estado em que todas as células normais estão mortas é alcançável e se alguma célula normal pode permanecer morta ou viva para sempre.

## Abrir o notebook

```bash
marimo edit exercicio1.py
```
