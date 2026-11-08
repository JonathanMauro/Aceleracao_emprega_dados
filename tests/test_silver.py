"""Testes da camada silver com dados inventados (definidos em conftest.py)."""
import pandas as pd
import pytest

from pipeline.silver import (
    analisar_custo,
    analisar_dano,
    checar_qualidade,
    classificar_estagio,
    classificar_movimento,
    classificar_regra,
    construir_cartas,
    construir_deck,
    construir_movimentos,
    padronizar_ausentes,
    premios_cedidos,
    traduzir_simbolos,
)


def test_padronizar_ausentes_troca_na_e_vazio_por_nulo():
    dados = pd.DataFrame({"a": ["n/a", "", " 10 ", "x"]})
    resultado = padronizar_ausentes(dados)["a"]

    assert resultado.isna().tolist() == [True, True, False, False]
    assert resultado.iloc[2] == "10"


@pytest.mark.parametrize("texto, esperado", [
    ("{R}", "Fogo"),
    ("{A}{A}", "Qualquer tipo"),
    ("{Team Rocket}{Team Rocket}", "Equipe Rocket"),
    ("{L}{F}", "Elétrico/Lutador"),
])
def test_traduzir_simbolos(texto, esperado):
    assert traduzir_simbolos(texto) == esperado


def test_traduzir_simbolos_nulo():
    assert pd.isna(traduzir_simbolos(pd.NA))


def test_classificar_estagio():
    assert classificar_estagio("Stage 2 Pokémon") == ("Pokémon", "Estágio 2")
    assert classificar_estagio("Supporter") == ("Treinador", "Apoiador")
    with pytest.raises(ValueError):
        classificar_estagio("Carta Misteriosa")


def test_regra_e_premios():
    assert classificar_regra(pd.NA) == "Comum"
    assert classificar_regra("Mega Pokémon ex") == "Mega ex"
    assert premios_cedidos("Pokémon", "Mega ex") == 3
    assert premios_cedidos("Pokémon", "ex") == 2
    assert premios_cedidos("Pokémon", "Comum") == 1
    assert pd.isna(premios_cedidos("Treinador", "ACE SPEC"))


def test_classificar_movimento():
    assert classificar_movimento("[Ability] Run Away Draw") == ("Habilidade", "Run Away Draw")
    assert classificar_movimento("[Tera]") == ("Regra Tera", "Tera")
    assert classificar_movimento("Gnaw") == ("Ataque", "Gnaw")


@pytest.mark.parametrize("custo, esperado", [
    ("●", (1, 1, 0)),
    ("{L}{F}", (2, 0, 2)),
    ("{P}●●", (3, 2, 1)),
    ("No cost", (0, 0, 0)),
])
def test_analisar_custo(custo, esperado):
    assert analisar_custo(custo) == esperado


def test_analisar_custo_formato_inesperado():
    with pytest.raises(ValueError):
        analisar_custo("duas energias")


@pytest.mark.parametrize("dano, esperado", [
    ("30", (30, "Fixo")),
    ("70×", (70, "Multiplicador")),
    ("120-", (120, "Redução")),
    ("50+", (50, "Adicional")),
])
def test_analisar_dano(dano, esperado):
    assert analisar_dano(dano) == esperado


def test_analisar_dano_nulo():
    base, modificador = analisar_dano(pd.NA)
    assert pd.isna(base) and modificador == "Sem dano"


def test_cartas_tem_uma_linha_por_carta_e_nome_japones(bronze_en, bronze_jp):
    cartas = construir_cartas(bronze_en, bronze_jp).set_index("card_id")

    assert list(cartas.index) == [10, 20, 30]
    assert cartas.loc[10, "nome_jp"] == "ファイスカex"
    assert cartas.loc[10, "regra"] == "ex"
    assert cartas.loc[10, "premios_cedidos"] == 2
    assert cartas.loc[10, "tipo"] == "Elétrico"
    assert cartas.loc[10, "hp"] == 200


def test_cartas_regras_de_limpeza(bronze_en, bronze_jp):
    cartas = construir_cartas(bronze_en, bronze_jp).set_index("card_id")

    assert cartas.loc[20, "recuo"] == 0  # recuo n/a em Pokémon vira 0
    assert pd.isna(cartas.loc[30, "recuo"])  # Treinador não tem recuo
    assert cartas.loc[30, "supertipo"] == "Treinador"
    assert cartas.loc[30, "texto_carta"] == "Cure 30 de dano."
    assert pd.isna(cartas.loc[10, "texto_carta"])
    assert pd.isna(cartas.loc[10, "resistencia"])


def test_movimentos(bronze_en):
    movimentos = construir_movimentos(bronze_en).set_index("movimento_id")

    assert list(movimentos.index) == ["10_1", "10_2", "20_1"]
    assert movimentos.loc["10_1", "tipo_movimento"] == "Habilidade"
    assert movimentos.loc["10_2", "custo_total"] == 3
    assert movimentos.loc["10_2", "custo_incolor"] == 2
    assert movimentos.loc["20_1", "custo_total"] == 0
    assert movimentos.loc["20_1", "modificador_dano"] == "Multiplicador"


def test_deck_rejeita_carta_fora_do_catalogo(bronze_en, bronze_jp):
    cartas = construir_cartas(bronze_en, bronze_jp)
    deck_ok = construir_deck(pd.DataFrame({"Card ID": ["10", "10", "30"]}), cartas)
    assert deck_ok["posicao"].tolist() == [1, 2, 3]

    with pytest.raises(ValueError):
        construir_deck(pd.DataFrame({"Card ID": ["10", "999"]}), cartas)


def test_qualidade_sem_violacoes_nos_dados_inventados(bronze_en, bronze_jp):
    cartas = construir_cartas(bronze_en, bronze_jp)
    movimentos = construir_movimentos(bronze_en)
    qualidade = checar_qualidade(cartas, movimentos)

    assert qualidade["violacoes"].sum() == 0


def test_coluna_de_texto_toda_nula_continua_texto(bronze_en, bronze_jp):
    cartas = construir_cartas(bronze_en, bronze_jp)

    assert cartas["resistencia"].isna().all()
    assert cartas["resistencia"].dtype == "string"
