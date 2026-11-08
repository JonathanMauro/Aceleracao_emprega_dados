"""Testes da camada bronze com arquivos inventados em pasta temporária."""
import pandas as pd

from pipeline.banco import ler_tabela, listar_tabelas, salvar_tabelas
from pipeline.bronze import carregar_bronze, hash_arquivo, ler_csv_bruto


def criar_csv(pasta, nome, conteudo):
    caminho = pasta / nome
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def test_leitura_preserva_texto_original(tmp_path):
    caminho = criar_csv(tmp_path, "cartas.csv", "Card ID,HP,Rule\n1,n/a,\n2,070,Pokémon ex\n")
    dados = ler_csv_bruto(caminho)

    assert dados["HP"].tolist() == ["n/a", "070"]
    assert dados["Rule"].tolist() == ["", "Pokémon ex"]
    assert all(dados[coluna].dtype == object for coluna in dados.columns)


def test_leitura_sem_cabecalho_usa_nomes_informados(tmp_path):
    caminho = criar_csv(tmp_path, "deck.csv", "10\n10\n3\n")
    dados = ler_csv_bruto(caminho, cabecalho=False, nomes=["Card ID"])

    assert list(dados.columns) == ["Card ID"]
    assert dados["Card ID"].tolist() == ["10", "10", "3"]


def test_carga_gera_controle_com_linhas_e_hash(tmp_path):
    caminho = criar_csv(tmp_path, "cartas.csv", "Card ID,Card Name\n1,Pikachu\n2,Raichu\n")
    tabelas = carregar_bronze({"bronze_cartas": {"caminho": caminho}})

    controle = tabelas["bronze_controle_carga"].iloc[0]
    assert controle["tabela"] == "bronze_cartas"
    assert controle["linhas"] == 2
    assert controle["md5_arquivo"] == hash_arquivo(caminho)


def test_gravacao_e_leitura_em_banco_temporario(tmp_path):
    banco = tmp_path / "teste.db"
    original = pd.DataFrame({"Card ID": ["1", "2"], "HP": ["n/a", "60"]})
    salvar_tabelas({"bronze_cartas": original}, banco)

    assert listar_tabelas(banco) == ["bronze_cartas"]
    pd.testing.assert_frame_equal(ler_tabela("bronze_cartas", banco), original)
