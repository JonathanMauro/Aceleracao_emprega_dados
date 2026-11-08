-- Pergunta: quais são os números gerais do catálogo de cartas?
-- Grão: uma linha por indicador.
WITH pokemon AS (
    SELECT * FROM silver.cartas WHERE supertipo = 'Pokémon'
),
ataques AS (
    SELECT * FROM silver.movimentos WHERE tipo_movimento = 'Ataque'
),
ataques_fixos AS (
    SELECT * FROM ataques WHERE modificador_dano = 'Fixo' AND custo_total > 0
)
SELECT 1 AS ordem, 'Cartas no catálogo' AS indicador, (SELECT COUNT(*) FROM silver.cartas)::DOUBLE AS valor
UNION ALL
SELECT 2, 'Pokémon no catálogo', COUNT(*)::DOUBLE FROM pokemon
UNION ALL
SELECT 3, 'Pokémon ex ou Mega ex (%)', ROUND(100.0 * AVG(CASE WHEN regra IN ('ex', 'Mega ex') THEN 1 ELSE 0 END), 1) FROM pokemon
UNION ALL
SELECT 4, 'HP médio dos Pokémon', ROUND(AVG(hp), 1) FROM pokemon
UNION ALL
SELECT 5, 'Pokémon com habilidade (%)',
    ROUND(100.0 * COUNT(DISTINCT h.card_id) / (SELECT COUNT(*) FROM pokemon), 1)
FROM silver.movimentos AS h
JOIN pokemon AS p ON p.card_id = h.card_id
WHERE h.tipo_movimento = 'Habilidade'
UNION ALL
SELECT 6, 'Ataques no catálogo', COUNT(*)::DOUBLE FROM ataques
UNION ALL
SELECT 7, 'Ataques sem dano (%)', ROUND(100.0 * AVG(CASE WHEN modificador_dano = 'Sem dano' THEN 1 ELSE 0 END), 1) FROM ataques
UNION ALL
SELECT 8, 'Dano médio por energia (ataques de dano fixo)', ROUND(AVG(dano_base / custo_total), 1) FROM ataques_fixos
UNION ALL
SELECT 9, 'Correlação entre HP e custo de recuo', ROUND(CORR(hp, recuo), 2) FROM pokemon
UNION ALL
SELECT 10, 'Pokémon sem fraqueza', COUNT(*)::DOUBLE FROM pokemon WHERE fraqueza IS NULL
ORDER BY ordem
