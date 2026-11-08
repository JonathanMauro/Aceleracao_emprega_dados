-- Pergunta: a qual tipo cada tipo de Pokémon costuma ser fraco?
-- Grão: uma linha por par tipo do Pokémon e tipo da fraqueza.
SELECT
    tipo,
    COALESCE(fraqueza, 'Nenhuma') AS fraqueza,
    COUNT(*) AS qtd_pokemon,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY tipo), 1) AS pct_do_tipo
FROM silver.cartas
WHERE supertipo = 'Pokémon'
GROUP BY tipo, COALESCE(fraqueza, 'Nenhuma')
ORDER BY tipo, qtd_pokemon DESC
