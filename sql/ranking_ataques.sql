-- Pergunta: quais ataques entregam mais dano por energia gasta?
-- Grão: uma linha por ataque, só as 20 primeiras posições.
-- Considera ataques de dano fixo e custo maior que zero. Empate desfeito pelo maior dano.
SELECT
    RANK() OVER (ORDER BY m.dano_base / m.custo_total DESC, m.dano_base DESC) AS posicao,
    c.nome AS pokemon,
    c.tipo,
    c.subtipo AS estagio,
    c.regra,
    m.nome_movimento AS ataque,
    m.custo_original AS custo,
    m.custo_total,
    m.dano_base,
    ROUND(m.dano_base / m.custo_total, 1) AS dano_por_energia,
    m.tem_efeito
FROM silver.movimentos AS m
JOIN silver.cartas AS c ON c.card_id = m.card_id
WHERE m.tipo_movimento = 'Ataque'
  AND m.modificador_dano = 'Fixo'
  AND m.custo_total > 0
QUALIFY posicao <= 20
ORDER BY posicao, pokemon
