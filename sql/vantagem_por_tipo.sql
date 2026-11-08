-- Pergunta: atacar com qual tipo dá vantagem contra mais Pokémon do catálogo?
-- Grão: uma linha por tipo atacante.
-- saldo = Pokémon fracos ao tipo menos Pokémon que resistem a ele.
WITH pokemon AS (
    SELECT tipo, fraqueza, resistencia FROM silver.cartas WHERE supertipo = 'Pokémon'
),
tipos AS (
    SELECT tipo FROM pokemon
    UNION
    SELECT fraqueza FROM pokemon WHERE fraqueza IS NOT NULL
    UNION
    SELECT resistencia FROM pokemon WHERE resistencia IS NOT NULL
)
SELECT
    t.tipo AS tipo_atacante,
    COUNT(*) FILTER (WHERE p.fraqueza = t.tipo) AS qtd_fracos,
    COUNT(*) FILTER (WHERE p.resistencia = t.tipo) AS qtd_resistentes,
    COUNT(*) FILTER (WHERE p.fraqueza = t.tipo) - COUNT(*) FILTER (WHERE p.resistencia = t.tipo) AS saldo,
    ROUND(100.0 * COUNT(*) FILTER (WHERE p.fraqueza = t.tipo) / COUNT(*), 1) AS pct_catalogo_fraco
FROM tipos AS t
CROSS JOIN pokemon AS p
GROUP BY t.tipo
ORDER BY saldo DESC, tipo_atacante
