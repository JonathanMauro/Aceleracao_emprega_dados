"""Testes dos SQLs da camada gold.

Os dados inventados do conftest passam pela silver e são gravados num DuckDB
em memória. O banco do projeto (data/pokemon.duckdb) nunca é aberto.
"""
import pandas as pd
import pytest

from pipeline.db import conectar, salvar_tabela
from pipeline.gold import INDICADORES, criar_indicador, criar_todos
from pipeline.config import PASTA_SQL
from pipeline.silver import construir_cartas, construir_deck, construir_movimentos


@pytest.fixture
def conexao(bronze_en, bronze_jp):
    conexao = conectar()
    cartas = construir_cartas(bronze_en, bronze_jp)
    deck = construir_deck(pd.DataFrame({"Card ID": ["10", "10", "30"]}), cartas)
    salvar_tabela(conexao, "silver", "cartas", cartas)
    salvar_tabela(conexao, "silver", "movimentos", construir_movimentos(bronze_en))
    salvar_tabela(conexao, "silver", "deck_exemplo", deck)
    yield conexao
    conexao.close()


def test_todo_indicador_tem_arquivo_sql():
    arquivos = sorted(arquivo.stem for arquivo in PASTA_SQL.glob("*.sql"))
    assert arquivos == sorted(INDICADORES)


def test_todos_os_indicadores_rodam_e_vao_para_o_schema_gold(conexao):
    resultados = criar_todos(conexao)
    tabelas = conexao.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'gold'"
    ).df()["table_name"]

    assert sorted(tabelas) == sorted(INDICADORES)
    assert all(len(tabela) > 0 for tabela in resultados.values())


def test_indicadores_gerais(conexao):
    valores = criar_indicador(conexao, "indicadores_gerais").set_index("indicador")["valor"]

    assert valores["Cartas no catálogo"] == 3
    assert valores["Pokémon no catálogo"] == 2
    assert valores["Pokémon ex ou Mega ex (%)"] == 50.0
    assert valores["HP médio dos Pokémon"] == 145.0
    assert valores["Pokémon com habilidade (%)"] == 50.0
    assert valores["Dano médio por energia (ataques de dano fixo)"] == 40.0


def test_composicao_catalogo(conexao):
    resultado = criar_indicador(conexao, "composicao_catalogo")

    assert resultado["qtd_cartas"].sum() == 3
    assert resultado["pct_catalogo"].round(0).sum() == 99  # 33,3 x 3


def test_perfil_por_tipo_usa_apenas_dano_fixo(conexao):
    resultado = criar_indicador(conexao, "perfil_por_tipo").set_index("tipo")

    assert resultado.loc["Elétrico", "hp_medio"] == 200
    assert resultado.loc["Elétrico", "pct_ex"] == 100
    assert resultado.loc["Elétrico", "dano_por_energia"] == 40
    assert resultado.loc["Grama", "recuo_medio"] == 0
    assert pd.isna(resultado.loc["Grama", "dano_medio"])  # único ataque é multiplicador


def test_hp_por_premio(conexao):
    resultado = criar_indicador(conexao, "hp_por_premio").set_index(["estagio", "regra"])

    assert resultado.loc[("Básico", "ex"), "premios_cedidos"] == 2
    assert resultado.loc[("Básico", "ex"), "hp_por_premio"] == 100
    assert resultado.loc[("Estágio 1", "Comum"), "hp_por_premio"] == 90


def test_vantagem_por_tipo(conexao):
    resultado = criar_indicador(conexao, "vantagem_por_tipo").set_index("tipo_atacante")

    assert resultado.loc["Lutador", "qtd_fracos"] == 1
    assert resultado.loc["Fogo", "pct_catalogo_fraco"] == 50
    assert resultado.loc["Elétrico", "saldo"] == 0


def test_matriz_fraquezas(conexao):
    resultado = criar_indicador(conexao, "matriz_fraquezas")
    par = resultado[(resultado["tipo"] == "Grama") & (resultado["fraqueza"] == "Fogo")]

    assert par["qtd_pokemon"].item() == 1
    assert par["pct_do_tipo"].item() == 100


def test_dano_por_custo(conexao):
    resultado = criar_indicador(conexao, "dano_por_custo").set_index("custo_total")

    assert resultado.loc[3, "dano_medio"] == 120
    assert resultado.loc[3, "dano_medio_por_energia"] == 40
    assert pd.isna(resultado.loc[0, "dano_medio"])


def test_ranking_ataques_ignora_dano_variavel(conexao):
    resultado = criar_indicador(conexao, "ranking_ataques")

    assert resultado["ataque"].tolist() == ["Raio Duplo"]
    assert resultado["posicao"].tolist() == [1]


def test_recuo_e_hp(conexao):
    resultado = criar_indicador(conexao, "recuo_e_hp").set_index("recuo")

    assert resultado.loc[0, "hp_medio"] == 90
    assert resultado.loc[2, "pct_ex"] == 100


def test_expansoes(conexao):
    resultado = criar_indicador(conexao, "expansoes").set_index("expansao")

    assert resultado.loc["XYZ", "qtd_cartas"] == 3
    assert resultado.loc["XYZ", "pct_ex_entre_pokemon"] == 50


def test_composicao_deck_exemplo(conexao):
    resultado = criar_indicador(conexao, "composicao_deck_exemplo").set_index("subtipo")

    assert resultado.loc["Básico", "copias"] == 2
    assert resultado.loc["Básico", "cartas_distintas"] == 1
    assert resultado["copias"].sum() == 3
