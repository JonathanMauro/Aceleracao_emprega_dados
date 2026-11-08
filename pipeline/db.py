"""Acesso ao DuckDB. Cada camada fica em um schema próprio (bronze, silver, gold)."""
from pathlib import Path

import duckdb
import pandas as pd


def conectar(caminho: Path | str = ":memory:") -> duckdb.DuckDBPyConnection:
    """Abre o banco do projeto ou, sem argumento, um banco em memória (usado nos testes)."""
    return duckdb.connect(str(caminho))


def salvar_tabela(conexao, schema: str, nome: str, dados: pd.DataFrame) -> None:
    """Grava o DataFrame em schema.nome, substituindo a versão anterior."""
    conexao.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    conexao.register("_dados", dados)
    conexao.execute(f"CREATE OR REPLACE TABLE {schema}.{nome} AS SELECT * FROM _dados")
    conexao.unregister("_dados")


def ler_tabela(conexao, schema: str, nome: str) -> pd.DataFrame:
    return conexao.execute(f"SELECT * FROM {schema}.{nome}").df()


def listar_tabelas(conexao, schema: str) -> list[str]:
    sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = ? ORDER BY table_name"
    return [linha[0] for linha in conexao.execute(sql, [schema]).fetchall()]
