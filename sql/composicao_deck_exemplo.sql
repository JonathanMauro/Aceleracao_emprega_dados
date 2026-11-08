-- Pergunta: como é montado o deck exemplo da competição?
-- Grão: uma linha por supertipo e subtipo de carta presentes no deck.
SELECT
    c.supertipo,
    c.subtipo,
    COUNT(*) AS copias,
    COUNT(DISTINCT c.card_id) AS cartas_distintas,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_deck,
    STRING_AGG(DISTINCT c.nome, ', ' ORDER BY c.nome) AS cartas
FROM silver.deck_exemplo AS d
JOIN silver.cartas AS c ON c.card_id = d.card_id
GROUP BY c.supertipo, c.subtipo
ORDER BY copias DESC
