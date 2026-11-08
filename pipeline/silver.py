"""Camada silver: dado limpo, tipado e modelado.

O arquivo bruto em inglês mistura dois níveis de informação: dados da carta
(HP, tipo, fraqueza) repetidos em cada linha e dados do ataque ou habilidade.
Aqui eles são separados em tabelas ligadas pela chave card_id:

  silver.cartas        uma linha por carta, com o nome japonês vindo do JOIN com o arquivo JP
  silver.movimentos    uma linha por ataque, habilidade ou regra Tera de um Pokémon
  silver.deck_exemplo  uma linha por cópia de carta no deck exemplo de 60 cartas
"""
import re

import pandas as pd

COLUNAS_EN = {
    "Card ID": "card_id",
    "Card Name": "nome",
    "Expansion": "expansao",
    "Collection No.": "numero_colecao",
    "Stage (Pokémon)/Type (Energy and Trainer)": "estagio_tipo_original",
    "Rule": "regra_original",
    "Category": "categoria",
    "Previous stage": "evolui_de",
    "HP": "hp",
    "Type": "tipo_original",
    "Weakness": "fraqueza_original",
    "Resistance (Type)": "resistencia_original",
    "Retreat": "recuo",
    "Move Name": "nome_movimento_original",
    "Cost": "custo_original",
    "Damage": "dano_original",
    "Effect Explanation": "efeito",
    "Species": "especie",
}

COLUNAS_JP = {
    "カード ID": "card_id",
    "カード名": "nome_jp",
    "エキスパンションマーク": "expansao_jp",
    "コレクション番号": "numero_colecao_jp",
}

SIMBOLOS_TIPO = {
    "G": "Grama",
    "R": "Fogo",
    "W": "Água",
    "L": "Elétrico",
    "P": "Psíquico",
    "F": "Lutador",
    "D": "Escuridão",
    "M": "Metal",
    "N": "Dragão",
    "C": "Incolor",
    "A": "Qualquer tipo",
    "Team Rocket": "Equipe Rocket",
}

SUBTIPOS = {
    "Basic Pokémon": ("Pokémon", "Básico"),
    "Stage 1 Pokémon": ("Pokémon", "Estágio 1"),
    "Stage 2 Pokémon": ("Pokémon", "Estágio 2"),
    "Item": ("Treinador", "Item"),
    "Supporter": ("Treinador", "Apoiador"),
    "Stadium": ("Treinador", "Estádio"),
    "Pokémon Tool": ("Treinador", "Ferramenta"),
    "Basic Energy": ("Energia", "Energia Básica"),
    "Special Energy": ("Energia", "Energia Especial"),
}

REGRAS = {"Pokémon ex": "ex", "Mega Pokémon ex": "Mega ex", "ACE SPEC": "ACE SPEC"}
PREMIOS_POR_REGRA = {"Mega ex": 3, "ex": 2}

MODIFICADORES_DANO = {"": "Fixo", "×": "Multiplicador", "+": "Adicional", "-": "Redução"}

SIMBOLO_INCOLOR = "●"


def padronizar_ausentes(dados: pd.DataFrame) -> pd.DataFrame:
    """Remove espaços nas pontas e troca '' e 'n/a' por nulo."""
    limpo = dados.apply(lambda coluna: coluna.str.strip())
    return limpo.replace({"": pd.NA, "n/a": pd.NA})


def traduzir_simbolos(texto):
    """'{R}' vira 'Fogo'; símbolos repetidos aparecem uma vez só ('{A}{A}' vira 'Qualquer tipo')."""
    if pd.isna(texto):
        return pd.NA
    simbolos = re.findall(r"\{([^}]+)\}", texto)
    nomes = list(dict.fromkeys(SIMBOLOS_TIPO.get(s, s) for s in simbolos))
    return "/".join(nomes) if nomes else pd.NA


def classificar_estagio(estagio_tipo: str) -> tuple[str, str]:
    """Devolve (supertipo, subtipo). Ex.: 'Stage 1 Pokémon' vira ('Pokémon', 'Estágio 1')."""
    if estagio_tipo not in SUBTIPOS:
        raise ValueError(f"Estágio ou tipo de carta desconhecido: {estagio_tipo!r}")
    return SUBTIPOS[estagio_tipo]


def classificar_regra(regra) -> str:
    if pd.isna(regra):
        return "Comum"
    return REGRAS.get(regra, regra)


def premios_cedidos(supertipo: str, regra: str):
    """Quantas cartas de prêmio o oponente pega ao nocautear o Pokémon."""
    if supertipo != "Pokémon":
        return pd.NA
    return PREMIOS_POR_REGRA.get(regra, 1)


def agrupar_categoria(categoria):
    if pd.isna(categoria):
        return pd.NA
    if categoria.startswith("Trainer's Pokémon"):
        return "Pokémon de Treinador"
    if categoria.startswith("Tera"):
        return "Tera"
    return {"Ancient": "Antigo", "Future": "Futuro", "Fossil": "Fóssil"}.get(categoria, categoria)


def classificar_movimento(nome) -> tuple:
    """Separa o prefixo do nome. Devolve (tipo_movimento, nome_limpo)."""
    if pd.isna(nome):
        return pd.NA, pd.NA
    if nome.startswith("[Ability]"):
        return "Habilidade", nome.removeprefix("[Ability]").strip()
    if nome.startswith("[Tera]"):
        return "Regra Tera", "Tera"
    return "Ataque", nome


def analisar_custo(custo) -> tuple:
    """Conta as energias do custo. Devolve (total, incolor, colorida).

    '●' é a energia incolor (qualquer tipo serve); '{L}' é uma energia Elétrica.
    """
    if pd.isna(custo):
        return pd.NA, pd.NA, pd.NA
    if custo == "No cost":
        return 0, 0, 0
    if not re.fullmatch(r"(\{[A-Z]\}|●)+", custo):
        raise ValueError(f"Custo em formato inesperado: {custo!r}")
    incolor = custo.count(SIMBOLO_INCOLOR)
    colorida = len(re.findall(r"\{[A-Z]\}", custo))
    return incolor + colorida, incolor, colorida


def analisar_dano(dano) -> tuple:
    """'70×' vira (70, 'Multiplicador'); '30' vira (30, 'Fixo'); nulo vira (NA, 'Sem dano')."""
    if pd.isna(dano):
        return pd.NA, "Sem dano"
    encontrado = re.fullmatch(r"(\d+)([×+\-]?)", dano)
    if not encontrado:
        raise ValueError(f"Dano em formato inesperado: {dano!r}")
    return int(encontrado.group(1)), MODIFICADORES_DANO[encontrado.group(2)]


def preparar_en(bronze_en: pd.DataFrame) -> pd.DataFrame:
    dados = padronizar_ausentes(bronze_en).rename(columns=COLUNAS_EN)
    dados["card_id"] = dados["card_id"].astype(int)
    return dados


def construir_cartas(bronze_en: pd.DataFrame, bronze_jp: pd.DataFrame) -> pd.DataFrame:
    en = preparar_en(bronze_en)
    colunas_carta = [
        "nome", "expansao", "numero_colecao", "estagio_tipo_original", "regra_original",
        "categoria", "evolui_de", "hp", "tipo_original", "fraqueza_original",
        "resistencia_original", "recuo", "especie",
    ]
    # first() pega o primeiro valor não nulo de cada coluna dentro da carta
    cartas = en.groupby("card_id", sort=True)[colunas_carta].first().reset_index()

    classificacao = cartas["estagio_tipo_original"].map(classificar_estagio)
    cartas["supertipo"] = classificacao.str[0]
    cartas["subtipo"] = classificacao.str[1]
    cartas["regra"] = cartas["regra_original"].map(classificar_regra)
    cartas["premios_cedidos"] = pd.array(
        [premios_cedidos(s, r) for s, r in zip(cartas["supertipo"], cartas["regra"])], dtype="Int64"
    )
    cartas["grupo_categoria"] = cartas["categoria"].map(agrupar_categoria)
    cartas["tipo"] = cartas["tipo_original"].map(traduzir_simbolos)
    cartas["fraqueza"] = cartas["fraqueza_original"].map(traduzir_simbolos)
    cartas["resistencia"] = cartas["resistencia_original"].map(traduzir_simbolos)

    for coluna in ["numero_colecao", "hp", "recuo"]:
        cartas[coluna] = pd.to_numeric(cartas[coluna]).astype("Int64")
    # Pokémon sem custo de recuo impresso recuam de graça
    eh_pokemon = cartas["supertipo"] == "Pokémon"
    cartas.loc[eh_pokemon, "recuo"] = cartas.loc[eh_pokemon, "recuo"].fillna(0)

    # Texto de regra das cartas de Treinador e Energia (nos Pokémon o texto está nos movimentos)
    texto = en.loc[en["nome_movimento_original"].isna()].groupby("card_id")["efeito"].first()
    cartas["texto_carta"] = cartas["card_id"].map(texto)
    cartas.loc[eh_pokemon, "texto_carta"] = pd.NA

    jp = (
        padronizar_ausentes(bronze_jp)[list(COLUNAS_JP)]
        .rename(columns=COLUNAS_JP)
        .assign(card_id=lambda d: d["card_id"].astype(int))
        .drop_duplicates("card_id")
    )
    cartas = cartas.merge(jp, on="card_id", how="left", validate="one_to_one")

    ordem = [
        "card_id", "nome", "nome_jp", "supertipo", "subtipo", "regra", "premios_cedidos",
        "tipo", "hp", "fraqueza", "resistencia", "recuo", "evolui_de", "categoria",
        "grupo_categoria", "especie", "expansao", "numero_colecao", "expansao_jp",
        "numero_colecao_jp", "texto_carta",
    ]
    return cartas[ordem]


def construir_movimentos(bronze_en: pd.DataFrame) -> pd.DataFrame:
    en = preparar_en(bronze_en)
    movimentos = en.loc[en["nome_movimento_original"].notna()].copy()

    tipo_nome = movimentos["nome_movimento_original"].map(classificar_movimento)
    movimentos["tipo_movimento"] = tipo_nome.str[0]
    movimentos["nome_movimento"] = tipo_nome.str[1]

    custos = movimentos["custo_original"].map(analisar_custo)
    movimentos["custo_total"] = custos.str[0].astype("Int64")
    movimentos["custo_incolor"] = custos.str[1].astype("Int64")
    movimentos["custo_colorido"] = custos.str[2].astype("Int64")

    danos = movimentos["dano_original"].map(analisar_dano)
    movimentos["dano_base"] = danos.str[0].astype("Int64")
    movimentos["modificador_dano"] = danos.str[1]

    movimentos["ordem"] = movimentos.groupby("card_id").cumcount() + 1
    movimentos["movimento_id"] = movimentos["card_id"].astype(str) + "_" + movimentos["ordem"].astype(str)
    movimentos["tem_efeito"] = movimentos["efeito"].notna()

    ordem = [
        "movimento_id", "card_id", "ordem", "tipo_movimento", "nome_movimento",
        "custo_original", "custo_total", "custo_incolor", "custo_colorido",
        "dano_original", "dano_base", "modificador_dano", "tem_efeito", "efeito",
    ]
    return movimentos[ordem].reset_index(drop=True)


def construir_deck(bronze_deck: pd.DataFrame, cartas: pd.DataFrame) -> pd.DataFrame:
    deck = pd.DataFrame({
        "posicao": range(1, len(bronze_deck) + 1),
        "card_id": bronze_deck["Card ID"].str.strip().astype(int).to_numpy(),
    })
    desconhecidas = set(deck["card_id"]) - set(cartas["card_id"])
    if desconhecidas:
        raise ValueError(f"Deck tem cartas que não existem no catálogo: {sorted(desconhecidas)}")
    return deck


def checar_qualidade(cartas: pd.DataFrame, movimentos: pd.DataFrame) -> pd.DataFrame:
    """Regras de qualidade da silver. Cada linha é uma regra com o número de violações."""
    pokemon = cartas[cartas["supertipo"] == "Pokémon"]
    ataques = movimentos[movimentos["tipo_movimento"] == "Ataque"]
    regras = {
        "card_id repetido em silver.cartas": cartas["card_id"].duplicated().sum(),
        "movimento sem carta correspondente": (~movimentos["card_id"].isin(cartas["card_id"])).sum(),
        "carta sem nome japonês (JOIN EN x JP)": cartas["nome_jp"].isna().sum(),
        "Pokémon sem HP": pokemon["hp"].isna().sum(),
        "Pokémon sem tipo": pokemon["tipo"].isna().sum(),
        "Pokémon sem nenhum movimento": (~pokemon["card_id"].isin(movimentos["card_id"])).sum(),
        "ataque sem custo": ataques["custo_total"].isna().sum(),
        "HP fora do intervalo de 30 a 400": (~pokemon["hp"].between(30, 400)).sum(),
    }
    return pd.DataFrame({"regra": list(regras), "violacoes": [int(v) for v in regras.values()]})
