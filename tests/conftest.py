"""Dados inventados no mesmo formato do bruto, usados pelos testes de silver e gold."""
import pandas as pd
import pytest

from pipeline.silver import COLUNAS_EN, COLUNAS_JP


def linha_en(**valores):
    """Linha com todas as colunas do CSV em inglês; o que não for informado vem como 'n/a'."""
    linha = {coluna: "n/a" for coluna in COLUNAS_EN}
    nomes = {v: k for k, v in COLUNAS_EN.items()}
    for chave, valor in valores.items():
        linha[nomes[chave]] = valor
    return linha


@pytest.fixture
def bronze_en():
    pokemon_ex = dict(
        card_id="10", nome="Faisca ex", expansao="XYZ", numero_colecao="5",
        estagio_tipo_original="Basic Pokémon", regra_original="Pokémon ex", hp="200",
        tipo_original="{L}", fraqueza_original="{F}", resistencia_original="", recuo="2",
    )
    pokemon_comum = dict(
        card_id="20", nome="Brotinho", expansao="XYZ", numero_colecao="1",
        estagio_tipo_original="Stage 1 Pokémon", evolui_de="Semente", hp="90",
        tipo_original="{G}", fraqueza_original="{R}", resistencia_original="", recuo="n/a",
    )
    linhas = [
        linha_en(**pokemon_ex, nome_movimento_original="[Ability] Carga Rapida", efeito="Compre 1 carta."),
        linha_en(**pokemon_ex, nome_movimento_original="Raio Duplo", custo_original="{L}●●", dano_original="120"),
        linha_en(**pokemon_comum, nome_movimento_original="Folhada", custo_original="No cost", dano_original="20×",
                 efeito="Jogue 2 moedas."),
        linha_en(card_id="30", nome="Pocao Inventada", expansao="XYZ", numero_colecao="50",
                 estagio_tipo_original="Item", efeito="Cure 30 de dano."),
    ]
    return pd.DataFrame(linhas)


@pytest.fixture
def bronze_jp():
    linhas = [
        ["10", "ファイスカex", "SV1", "001/100"],
        ["10", "ファイスカex", "SV1", "001/100"],
        ["20", "ブロチーニョ", "SV1", "002/100"],
        ["30", "ポーション", "SV1", "050/100"],
    ]
    return pd.DataFrame(linhas, columns=list(COLUNAS_JP))
