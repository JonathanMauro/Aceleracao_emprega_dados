"""Caminhos usados pelo pipeline."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA_DADOS = RAIZ / "data"
PASTA_SQL = RAIZ / "sql"

ARQUIVO_CARTAS_EN = PASTA_DADOS / "EN_Card_Data_R2_full.csv"
ARQUIVO_CARTAS_JP = PASTA_DADOS / "JP_Card_Data_R2_full.csv"
ARQUIVO_DECK = PASTA_DADOS / "deck_exemplo.csv"

# Um único arquivo DuckDB com um schema por camada: bronze, silver e gold
BANCO = PASTA_DADOS / "pokemon.duckdb"
