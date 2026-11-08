-- Pergunta: Pokémon mais resistentes custam mais para recuar?
-- Grão: uma linha por custo de recuo.
SELECT
    recuo,
    COUNT(*) AS qtd_pokemon,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_pokemon,
    ROUND(AVG(hp), 1) AS hp_medio,
    ROUND(100.0 * AVG(CASE WHEN regra IN ('ex', 'Mega ex') THEN 1 ELSE 0 END), 1) AS pct_ex
FROM silver.cartas
WHERE supertipo = 'Pokémon'
GROUP BY recuo
ORDER BY recuo
