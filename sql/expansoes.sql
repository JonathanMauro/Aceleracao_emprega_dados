-- Pergunta: como as expansões se diferenciam em volume e em força das cartas?
-- Grão: uma linha por expansão. As 8 cartas sem expansão aparecem como 'Não informada' (decisão 12 da silver).
SELECT
    COALESCE(expansao, 'Não informada') AS expansao,
    COUNT(*) AS qtd_cartas,
    COUNT(*) FILTER (WHERE supertipo = 'Pokémon') AS qtd_pokemon,
    COUNT(*) FILTER (WHERE supertipo = 'Treinador') AS qtd_treinador,
    COUNT(*) FILTER (WHERE supertipo = 'Energia') AS qtd_energia,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE regra IN ('ex', 'Mega ex'))
        / NULLIF(COUNT(*) FILTER (WHERE supertipo = 'Pokémon'), 0), 1
    ) AS pct_ex_entre_pokemon,
    ROUND(AVG(hp), 1) AS hp_medio_pokemon
FROM silver.cartas
GROUP BY COALESCE(expansao, 'Não informada')
ORDER BY qtd_cartas DESC
