"""Reproduz as experiencias e guarda resultados, sem confundir timeout com prova."""

import argparse
import csv
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import marimo
import z3

import modelo as m
import verificacao as v


def executar(timeout_ms=3000):
    provas = []
    for n in (4, 6, 8, 12, 16):
        print(f"A verificar n={n}...", flush=True)
        modular = v.verificar_modular(n, timeout_ms=timeout_ms)
        seguranca = v.verificar_seguranca(n, timeout_ms=timeout_ms)
        provas.append({"n": n, "modular": modular, "seguranca": seguranca})
    return {
        "ambiente": {"python": platform.python_version(), "marimo": marimo.__version__,
                     "z3": z3.get_version_string(), "sistema": platform.system(),
                     "data_utc": datetime.now(timezone.utc).isoformat(),
                     "timeout_ms_por_consulta": timeout_ms, "seed_z3": 0},
        "provas_por_largura": provas,
        "modular_k1": v.verificar_modular(4, 1, timeout_ms),
        "modular_k2_referencia": v.verificar_modular(8, 2, 30000),
        "seguranca_referencia": v.verificar_seguranca(8, timeout_ms=30000),
        "seguranca_com_sinal_corrigida": v.verificar_seguranca(6, "com_sinal", "produto_cabe", 30000),
        "terminacao": [v.verificar_terminacao(n) for n in (4, 8, 16, 32, 64)],
        "animacao_limitada": v.verificar_animacao_limitada(4),
        "sucesso_limitado": v.verificar_animacao_limitada(4, "enunciado", so_sucesso=True),
        "contraexemplo_sem_limites": v.bmc(4, m.erro, 10),
        "contraexemplo_com_sinal": v.bmc(4, m.erro, 12, "enunciado", "com_sinal"),
        "exemplo": m.simular(13, 11, 8),
        "exemplo_signed_15_15": m.simular(15, 15, 8, "com_sinal"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=Path(__file__).resolve().parent / "resultados")
    parser.add_argument("--timeout-ms", type=int, default=3000)
    args = parser.parse_args()
    if args.timeout_ms < 1:
        parser.error("timeout deve ser positivo")
    dados = executar(args.timeout_ms)
    args.saida.mkdir(parents=True, exist_ok=True)
    (args.saida / "verificacao.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.saida / "escala.csv").open("w", newline="", encoding="utf-8") as ficheiro:
        campos = ["n", "propriedade", "base", "passo", "segundos_base", "segundos_passo", "provado"]
        writer = csv.DictWriter(ficheiro, fieldnames=campos)
        writer.writeheader()
        for linha in dados["provas_por_largura"]:
            for nome in ("modular", "seguranca"):
                resultado = linha[nome]
                writer.writerow(dict(n=linha["n"], propriedade=nome,
                                     base=resultado["base"]["estado"], passo=resultado["passo"]["estado"],
                                     segundos_base=resultado["base"]["segundos"],
                                     segundos_passo=resultado["passo"]["segundos"],
                                     provado=resultado["provado"]))
    print(f"Resultados em {args.saida.resolve()}")


if __name__ == "__main__":
    main()
