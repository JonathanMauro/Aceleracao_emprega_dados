"""Camada gold: indicadores.

Cada indicador é um arquivo .sql em sql/ que lê apenas o schema silver.
O nome do arquivo vira o nome da tabela no schema gold.
"""
from pathlib import Path

import pandas as pd

from pipeline.config import PASTA_SQL

INDICADORES = [
    "indicadores_gerais",
    "composicao_catalogo",
    "perfil_por_tipo",
    "hp_por_premio",
    "vantagem_por_tipo",
    "matriz_fraquezas",
    "dano_por_custo",
    "ranking_ataques",
    "recuo_e_hp",
    "expansoes",
    "composicao_deck_exemplo",
]


def ler_sql(nome: str, pasta: Path = PASTA_SQL) -> str:
    return (Path(pasta) / f"{nome}.sql").read_text(encoding="utf-8").strip().rstrip(";")


def criar_indicador(conexao, nome: str, pasta: Path = PASTA_SQL) -> pd.DataFrame:
    """Executa o SQL do indicador, grava em gold.<nome> e devolve o resultado."""
    conexao.execute("CREATE SCHEMA IF NOT EXISTS gold")
    conexao.execute(f"CREATE OR REPLACE TABLE gold.{nome} AS\n{ler_sql(nome, pasta)}")
    return conexao.execute(f"SELECT * FROM gold.{nome}").df()


def criar_todos(conexao, pasta: Path = PASTA_SQL) -> dict[str, pd.DataFrame]:
    return {nome: criar_indicador(conexao, nome, pasta) for nome in INDICADORES}
