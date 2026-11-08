-- Pergunta: um Pokémon ex ou Mega ex compensa o risco de entregar mais prêmios ao oponente?
-- Grão: uma linha por estágio de evolução e regra.
-- hp_por_premio = HP médio dividido pelos prêmios que o oponente ganha ao nocautear a carta.
WITH dano_maximo AS (
    SELECT card_id, MAX(dano_base) AS maior_dano
    FROM silver.movimentos
    WHERE tipo_movimento = 'Ataque'
    GROUP BY card_id
)
SELECT
    c.subtipo AS estagio,
    c.regra,
    MAX(c.premios_cedidos) AS premios_cedidos,
    COUNT(*) AS qtd_pokemon,
    ROUND(AVG(c.hp), 1) AS hp_medio,
    ROUND(AVG(c.hp) / MAX(c.premios_cedidos), 1) AS hp_por_premio,
    ROUND(AVG(d.maior_dano), 1) AS maior_dano_medio
FROM silver.cartas AS c
LEFT JOIN dano_maximo AS d ON d.card_id = c.card_id
WHERE c.supertipo = 'Pokémon'
GROUP BY c.subtipo, c.regra
ORDER BY estagio, premios_cedidos
