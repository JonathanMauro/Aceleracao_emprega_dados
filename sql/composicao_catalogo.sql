-- Pergunta: como o catálogo se divide entre Pokémon, Treinadores e Energias?
-- Grão: uma linha por supertipo e subtipo de carta.
SELECT
    supertipo,
    subtipo,
    COUNT(*) AS qtd_cartas,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_catalogo
FROM silver.cartas
GROUP BY supertipo, subtipo
ORDER BY supertipo, qtd_cartas DESC
