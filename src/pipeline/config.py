"""Caminhos usados pelo pipeline."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PASTA_DADOS = RAIZ / "data"
PASTA_FONTE = PASTA_DADOS / "fonte"

ARQUIVO_CARTAS_EN = PASTA_FONTE / "EN_Card_Data_R2_full.csv"
ARQUIVO_CARTAS_JP = PASTA_FONTE / "JP_Card_Data_R2_full.csv"
ARQUIVO_DECK = PASTA_FONTE / "deck_exemplo.csv"

BANCO_BRONZE = PASTA_DADOS / "bronze" / "bronze.db"
BANCO_SILVER = PASTA_DADOS / "silver" / "silver.db"
BANCO_GOLD = PASTA_DADOS / "gold" / "gold.db"

PASTA_FIGURAS = RAIZ / "reports" / "figuras"
