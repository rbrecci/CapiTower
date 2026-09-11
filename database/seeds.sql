-- CapiTower: conteudo do jogo
--
-- Este arquivo e reexecutavel. Todo INSERT usa ON DUPLICATE KEY UPDATE com base
-- no slug, entao rodar de novo atualiza os valores em vez de duplicar linhas.
-- E assim que o balanceamento vai para producao: edita aqui, importa, pronto.
--
-- Ordem obrigatoria por causa das chaves estrangeiras:
--   classes -> habilidade_niveis -> arquetipos -> cartas
--   inimigos -> inimigo_acoes -> encontros
--   eventos
--   objetivos
--
-- STATUS: esqueleto. As 20 cartas da Conjuradora, o bestiario e os chefes entram
-- na Fase 3 do roadmap, depois que as questoes Q1 e Q3 de docs/07-decisoes.md
-- estiverem fechadas.

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- CLASSES
-- ---------------------------------------------------------------------------

INSERT INTO classes
  (slug, nome, descricao, mecanica_nome, mecanica_descricao,
   habilidade_nome, habilidade_descricao, hp_inicial, acao_por_turno, inicial, ordem)
VALUES
  ('conjuradora', 'A Conjuradora',
   'Capivara necromante. A unica classe cuja forca esta fora do proprio corpo.',
   'Lacaios',
   'Contadores persistentes que aparecem em campo como capivaras esqueleto. Nao sao alvejaveis, nao tem HP e so somem por efeito que diga consome ou dissipa.',
   'Legiao',
   'Comeca cada combate com lacaios ja em campo. A quantidade cresce com o nivel.',
   70, 3, 1, 1)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome),
  descricao = VALUES(descricao),
  mecanica_nome = VALUES(mecanica_nome),
  mecanica_descricao = VALUES(mecanica_descricao),
  habilidade_nome = VALUES(habilidade_nome),
  habilidade_descricao = VALUES(habilidade_descricao),
  hp_inicial = VALUES(hp_inicial),
  acao_por_turno = VALUES(acao_por_turno),
  inicial = VALUES(inicial),
  ordem = VALUES(ordem);

-- Classes 2 e 3: a definir no brainstorm. Ver docs/02-classes-e-arquetipos.md secao 4.

-- ---------------------------------------------------------------------------
-- ARQUETIPOS DA CONJURADORA
-- ---------------------------------------------------------------------------

INSERT INTO arquetipos (classe_id, slug, nome, descricao, cor, ordem)
SELECT c.id, v.slug, v.nome, v.descricao, v.cor, v.ordem
FROM classes c
JOIN (
  SELECT 'enxame'      AS slug, 'Enxame'      AS nome, 'Quantidade acima de qualidade. Invoca muito e barato, e escala com o numero de lacaios em campo.' AS descricao, '#7FB069' AS cor, 1 AS ordem
  UNION ALL SELECT 'sacrificio', 'Sacrificio', 'Consome lacaios para efeitos grandes e imediatos. Alto risco, alto retorno.', '#B03A48', 2
  UNION ALL SELECT 'ossada',     'Ossada',     'Muralha de ossos. Lacaios viram Bloco e mitigacao. Vence por atrito.', '#D9CBA3', 3
  UNION ALL SELECT 'putrefacao', 'Putrefacao', 'Decadencia lenta. Lacaios aplicam Veneno e estados. Nao precisa atacar para vencer.', '#6B8E5A', 4
) v
WHERE c.slug = 'conjuradora'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome),
  descricao = VALUES(descricao),
  cor = VALUES(cor),
  ordem = VALUES(ordem);

-- ---------------------------------------------------------------------------
-- HABILIDADE LEGIAO: NIVEIS 1 A 10
-- ---------------------------------------------------------------------------
-- Curva proposta em docs/02-classes-e-arquetipos.md secao 3.2, ainda [ajustar].
-- Entra na Fase 3.

-- ---------------------------------------------------------------------------
-- CARTAS
-- ---------------------------------------------------------------------------
-- 20 cartas: 5 por arquetipo. Entram na Fase 3.
-- Formato de efeito documentado em docs/04-arquitetura.md secao 6.
--
-- Exemplo do formato esperado:
-- INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
-- SELECT a.id, 'costela-solta', 'Costela Solta', 1, 'ataque',
--        'Causa {0} de dano. Invoca {1} lacaio.',
--        '[{"op":"dano","alvo":"inimigo","valor":6},{"op":"invocar","valor":1}]', 1
-- FROM arquetipos a WHERE a.slug = 'enxame';

-- ---------------------------------------------------------------------------
-- INIMIGOS, ENCONTROS E EVENTOS
-- ---------------------------------------------------------------------------
-- Bestiario esbocado em docs/03-conteudo.md secoes 5, 6 e 7. Entram na Fase 3.

-- ---------------------------------------------------------------------------
-- OBJETIVOS
-- ---------------------------------------------------------------------------
-- Entram na Fase 5, junto com a meta progressao.
