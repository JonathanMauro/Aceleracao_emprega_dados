-- Pergunta: quanto dano cada energia a mais no custo de um ataque entrega?
-- Grão: uma linha por custo total de energia.
-- Estatísticas de dano usam só ataques de dano fixo (decisão 7 da silver).
SELECT
    custo_total,
    COUNT(*) AS qtd_ataques,
    ROUND(100.0 * AVG(CASE WHEN modificador_dano = 'Sem dano' THEN 1 ELSE 0 END), 1) AS pct_sem_dano,
    COUNT(*) FILTER (WHERE modificador_dano = 'Fixo') AS qtd_dano_fixo,
    ROUND(AVG(dano_base) FILTER (WHERE modificador_dano = 'Fixo'), 1) AS dano_medio,
    MEDIAN(dano_base) FILTER (WHERE modificador_dano = 'Fixo') AS dano_mediano,
    MAX(dano_base) FILTER (WHERE modificador_dano = 'Fixo') AS dano_maximo,
    ROUND(AVG(dano_base) FILTER (WHERE modificador_dano = 'Fixo') / NULLIF(custo_total, 0), 1) AS dano_medio_por_energia
FROM silver.movimentos
WHERE tipo_movimento = 'Ataque'
GROUP BY custo_total
ORDER BY custo_total
