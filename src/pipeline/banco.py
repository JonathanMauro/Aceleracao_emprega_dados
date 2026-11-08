"""Leitura e gravação de tabelas em bancos SQLite, um banco por camada."""
import sqlite3
from pathlib import Path

import pandas as pd


def salvar_tabelas(tabelas: dict[str, pd.DataFrame], caminho_banco: Path) -> None:
    """Grava cada DataFrame como uma tabela, substituindo a versão anterior."""
    caminho_banco = Path(caminho_banco)
    caminho_banco.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(caminho_banco) as conexao:
        for nome, tabela in tabelas.items():
            tabela.to_sql(nome, conexao, if_exists="replace", index=False)


def ler_tabela(nome: str, caminho_banco: Path) -> pd.DataFrame:
    with sqlite3.connect(caminho_banco) as conexao:
        return pd.read_sql(f'SELECT * FROM "{nome}"', conexao)


def consultar(sql: str, caminho_banco: Path) -> pd.DataFrame:
    with sqlite3.connect(caminho_banco) as conexao:
        return pd.read_sql(sql, conexao)


def listar_tabelas(caminho_banco: Path) -> list[str]:
    sql = "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    return consultar(sql, caminho_banco)["name"].tolist()
