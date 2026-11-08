"""Camada bronze: cópia fiel dos arquivos de origem.

Todas as colunas são lidas como texto e nenhum valor é tratado. Cada carga
gera um registro de controle com contagem de linhas e hash do arquivo, para
que seja possível conferir que o dado bruto não foi alterado.
"""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def ler_csv_bruto(caminho: Path, cabecalho: bool = True, nomes: list[str] | None = None) -> pd.DataFrame:
    """Lê o CSV preservando o texto original (sem conversão de tipos nem de nulos)."""
    return pd.read_csv(
        caminho,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
        header=0 if cabecalho else None,
        names=nomes,
    )


def hash_arquivo(caminho: Path) -> str:
    return hashlib.md5(Path(caminho).read_bytes()).hexdigest()


def registro_controle(tabela: str, caminho: Path, dados: pd.DataFrame) -> dict:
    return {
        "tabela": tabela,
        "arquivo_origem": Path(caminho).name,
        "linhas": len(dados),
        "colunas": dados.shape[1],
        "md5_arquivo": hash_arquivo(caminho),
        "carregado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def carregar_bronze(fontes: dict[str, dict]) -> dict[str, pd.DataFrame]:
    """Lê todas as fontes e devolve as tabelas brutas mais a tabela de controle.

    fontes: {nome_tabela: {"caminho": Path, "cabecalho": bool, "nomes": list | None}}
    """
    tabelas = {}
    controle = []
    for nome, parametros in fontes.items():
        caminho = parametros["caminho"]
        dados = ler_csv_bruto(caminho, parametros.get("cabecalho", True), parametros.get("nomes"))
        tabelas[nome] = dados
        controle.append(registro_controle(nome, caminho, dados))
    tabelas["bronze_controle_carga"] = pd.DataFrame(controle)
    return tabelas
