-- Pergunta: qual o perfil de cada tipo de Pokémon em resistência (HP), mobilidade (recuo) e força de ataque?
-- Grão: uma linha por tipo de Pokémon.
-- Dano considera só ataques de dano fixo com custo maior que zero (decisão 7 da silver).
WITH pokemon AS (
    SELECT * FROM silver.cartas WHERE supertipo = 'Pokémon'
),
ataques_por_tipo AS (
    SELECT
        p.tipo,
        COUNT(*) AS qtd_ataques_dano_fixo,
        ROUND(AVG(m.dano_base), 1) AS dano_medio,
        ROUND(AVG(m.dano_base / m.custo_total), 1) AS dano_por_energia
    FROM silver.movimentos AS m
    JOIN pokemon AS p ON p.card_id = m.card_id
    WHERE m.tipo_movimento = 'Ataque'
      AND m.modificador_dano = 'Fixo'
      AND m.custo_total > 0
    GROUP BY p.tipo
),
cartas_por_tipo AS (
    SELECT
        tipo,
        COUNT(*) AS qtd_pokemon,
        ROUND(AVG(hp), 1) AS hp_medio,
        MEDIAN(hp) AS hp_mediano,
        ROUND(AVG(recuo), 2) AS recuo_medio,
        ROUND(100.0 * AVG(CASE WHEN regra IN ('ex', 'Mega ex') THEN 1 ELSE 0 END), 1) AS pct_ex
    FROM pokemon
    GROUP BY tipo
)
SELECT
    c.tipo,
    c.qtd_pokemon,
    c.hp_medio,
    c.hp_mediano,
    c.recuo_medio,
    c.pct_ex,
    a.qtd_ataques_dano_fixo,
    a.dano_medio,
    a.dano_por_energia
FROM cartas_por_tipo AS c
LEFT JOIN ataques_por_tipo AS a ON a.tipo = c.tipo
ORDER BY c.qtd_pokemon DESC
