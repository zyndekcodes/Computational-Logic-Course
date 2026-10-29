"""Seis testes de aceitacao; executar: python -B -m unittest -v testes."""

import unittest
from math import isqrt

import z3

import modelo as m
import verificacao as v
from bonus_convolucao import multiplicar_convolucao


class TestesMultiplicacao(unittest.TestCase):
    def test_01_produtos_e_percursos(self):
        for n, a, b in ((8, 13, 11), (8, 15, 15), (16, 173, 249),
                        (32, 12345, 54321), (8, 0, 15), (8, 15, 0)):
            with self.subTest(n=n, a=a, b=b):
                caminho = m.simular(a, b, n)
                self.assertEqual(caminho[-1]["pc"], m.STOP)
                self.assertEqual(caminho[-1]["z"], a * b)
                self.assertEqual(len(caminho) - 1,
                                 2 + 2 * (b.bit_count() + max(0, b.bit_length() - 1)))
                self.assertEqual(multiplicar_convolucao(a, b)["produto"], a * b)
        self.assertEqual(multiplicar_convolucao(0, 0)["produto"], 0)
        self.assertEqual(multiplicar_convolucao(2**64 - 1, 2**64 - 1)["produto"],
                         (2**64 - 1)**2)

    def test_02_exaustivo_e_correspondencia_com_z3(self):
        # Todas as entradas de quatro bits, nos dois modelos de overflow.
        for semantica in m.SEMANTICAS:
            cap = m.capacidade(4, semantica)
            s, t = m.estado("s", 4), m.estado("t", 4)
            transicao = m.transicao(s, t, semantica)
            for a in range(cap + 1):
                for b in range(cap + 1):
                    caminho = m.simular(a, b, 4, semantica)
                    for antes, depois in zip(caminho, caminho[1:]):
                        substituicoes = [(s[c], z3.BitVecVal(antes[c], s[c].size())) for c in m.CAMPOS]
                        substituicoes += [(t[c], z3.BitVecVal(depois[c], t[c].size())) for c in m.CAMPOS]
                        formula = z3.simplify(z3.substitute(transicao, *substituicoes))
                        self.assertTrue(z3.is_true(formula))
                    fim = caminho[-1]
                    self.assertEqual((fim["x"] * fim["y"] + fim["z"]) % 16, (a * b) % 16)
                    if a * b <= cap:
                        self.assertEqual(fim["pc"], m.STOP)
                        self.assertEqual(fim["z"], a * b)
                    else:
                        self.assertIn(fim["pc"], (m.ERRO_LEFT, m.ERRO_RIGHT))

    def test_03_invariante_por_k_inducao(self):
        for n in (1, 4, 6, 8):
            with self.subTest(n=n):
                self.assertTrue(v.verificar_modular(n)["provado"])

    def test_04_seguranca_e_exemplo_com_sinal(self):
        for n in (4, 5, 6, 8):
            with self.subTest(n=n):
                self.assertTrue(v.verificar_seguranca(n, timeout_ms=30000)["provado"])
        self.assertTrue(v.verificar_seguranca(6, "com_sinal", "produto_cabe", 30000)["provado"])
        caminho = m.simular(15, 15, 8, "com_sinal")
        self.assertEqual(caminho[-1]["pc"], m.ERRO_RIGHT)
        self.assertLessEqual(15, isqrt(255))

    def test_05_terminacao_e_contraprova_de_sucesso_universal(self):
        for n in (1, 4, 8, 16, 32, 64):
            for semantica in m.SEMANTICAS:
                self.assertTrue(v.verificar_terminacao(n, semantica)["provado"])
        caminho = m.simular(200, 2, 8)
        self.assertEqual(caminho[-1]["pc"], m.ERRO_LEFT)
        resultado = v.bmc(4, m.erro, 10)
        self.assertEqual(resultado["estado"], "sat")
        resultado_sinal = v.bmc(4, m.erro, 12, "enunciado", "com_sinal")
        self.assertEqual(resultado_sinal["estado"], "sat")
        self.assertEqual(v.verificar_animacao_limitada(4)["estado"], "unsat")
        self.assertEqual(v.verificar_animacao_limitada(4, "enunciado", so_sucesso=True)["estado"], "unsat")

    def test_06_determinismo_e_prioridade_do_erro(self):
        s, t, u = (m.estado(nome, 4) for nome in ("d0", "d1", "d2"))
        for semantica in m.SEMANTICAS:
            resultado = v.consultar(z3.And(
                m.transicao(s, t, semantica), m.transicao(s, u, semantica),
                z3.Or(*(t[c] != u[c] for c in m.CAMPOS)),
            ))
            self.assertEqual(resultado["estado"], "unsat")
        valores = dict(pc=m.LEFT, a=200, b=2, x=200, y=2, z=0)
        self.assertEqual(v.consultar(z3.And(m.fixar(s, valores),
                         m.transicao(s, t), t["pc"] != m.ERRO_LEFT))["estado"], "unsat")


if __name__ == "__main__":
    unittest.main()
