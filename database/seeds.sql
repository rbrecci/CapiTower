-- CapiTower: conteudo do jogo
--
-- Gerado a partir do catalogo real da Fase 3 (public/assets/js/data/{cards,enemy,events,challenges}.json)
-- por um script de uso unico (nao versionado). Nao edite este arquivo a mao para conteudo que ja
-- existe num JSON de origem: edite o JSON e gere de novo. Classes, arquetipos e a habilidade Legiao
-- nao tem JSON proprio ainda, entao esses INSERTs sao escritos direto aqui.
--
-- Todo INSERT usa ON DUPLICATE KEY UPDATE com base no slug, entao rodar de novo atualiza em vez de duplicar.
--
-- Ordem obrigatoria por causa das chaves estrangeiras:
--   classes -> habilidade_niveis -> arquetipos -> cartas
--   inimigos -> encontros
--   eventos
--   desafios

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- CLASSES
-- ---------------------------------------------------------------------------

INSERT INTO classes
  (slug, nome, descricao, mecanica_nome, mecanica_descricao,
   habilidade_nome, habilidade_descricao, hp_inicial, acao_por_turno, inicial, ordem)
VALUES
  ('capimaga', 'Capimaga',
   'Capivara necromante. A unica classe cuja forca esta fora do proprio corpo.',
   'Lacaios',
   'Contadores persistentes que aparecem em campo como capivaras esqueleto. Nao sao alvejaveis, nao tem HP e so somem por efeito que diga consome ou dissipa.',
   'Legiao',
   'Comeca cada combate com lacaios ja em campo. A quantidade cresce com o nivel.',
   80, 3, 1, 1)
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

-- Classes 2 e 3: Brutamontes (mecanica Adrenalina) e Ligeira (mecanica Impulso).
-- Entram no seed junto com as cartas delas, na Fase 6 do roadmap.

-- ---------------------------------------------------------------------------
-- HABILIDADE LEGIAO: NIVEIS 1 A 10
-- ---------------------------------------------------------------------------

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 1, 'Comeca o combate com 1 lacaio', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 2, '+1 lacaio inicial (2)', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 3, '+1 lacaio inicial (3)', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 4, '+1 lacaio inicial (4)', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 5, 'Ao invocar, 20% de chance de invocar 1 a mais', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 6, '+1 lacaio inicial (5)', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 7, '+1 lacaio inicial (6)', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 8, '+1 lacaio inicial (7)', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 9, 'Uma vez por combate, ao ficar sem lacaios, invoca 2', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

INSERT INTO habilidade_niveis (classe_id, nivel, descricao, efeitos)
SELECT c.id, 10, 'Comeca o combate com o dobro de lacaios', '[]'
FROM classes c WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao), efeitos = VALUES(efeitos);

-- ---------------------------------------------------------------------------
-- ARQUETIPOS DA CAPIMAGA
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
WHERE c.slug = 'capimaga'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome),
  descricao = VALUES(descricao),
  cor = VALUES(cor),
  ordem = VALUES(ordem);

-- ---------------------------------------------------------------------------
-- CARTAS DA CAPIMAGA (20, portadas de flet_mvp/capitower/cards.py)
-- ---------------------------------------------------------------------------

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_costela', 'Costela Solta', 1, 'ataque', 'Causa 7 de dano. Invoca 1 lacaio.', '[{"op":"dano","alvo":"inimigo","valor":7},{"op":"invocar","valor":1}]', 1
FROM arquetipos a WHERE a.slug = 'enxame'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_amontoado', 'Amontoado', 1, 'defesa', 'Ganha 3 de Bloco. Invoca 2 lacaios.', '[{"op":"bloco","valor":3},{"op":"invocar","valor":2}]', 1
FROM arquetipos a WHERE a.slug = 'enxame'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_vala', 'Vala Comum', 2, 'poder', 'No inicio do seu turno, invoca 1 lacaio.', '[{"op":"poder","nome":"vala_comum"}]', 1
FROM arquetipos a WHERE a.slug = 'enxame'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_chamado', 'Chamado da Vala', 1, 'utilidade', 'Invoca 3 lacaios.', '[{"op":"invocar","valor":3}]', 1
FROM arquetipos a WHERE a.slug = 'enxame'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_marcha', 'Marcha dos Ossos', 2, 'ataque', 'Causa 4 de dano por lacaio em campo.', '[{"op":"dano_por_lacaio","alvo":"inimigo","valor":4}]', 1
FROM arquetipos a WHERE a.slug = 'enxame'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_explosao', 'Explosao Ossea', 1, 'ataque', 'Consome ate 2 lacaios. Causa 6 de dano por lacaio consumido.', '[{"op":"consumir_lacaios","valor":2},{"op":"dano_por_lacaio","alvo":"inimigo","valor":6,"fonte":"consumidos"}]', 1
FROM arquetipos a WHERE a.slug = 'sacrificio'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_carne', 'Escudo de Carne', 1, 'defesa', 'Consome ate 2 lacaios. Ganha 3 de Bloco, +4 por lacaio consumido.', '[{"op":"consumir_lacaios","valor":2},{"op":"bloco","valor":3},{"op":"bloco_por_lacaio","valor":4,"fonte":"consumidos"}]', 1
FROM arquetipos a WHERE a.slug = 'sacrificio'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_banquete', 'Banquete', 2, 'poder', 'Sempre que consumir pelo menos 1 lacaio, compra 1 carta.', '[{"op":"poder","nome":"banquete"}]', 1
FROM arquetipos a WHERE a.slug = 'sacrificio'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_oferenda', 'Oferenda', 0, 'utilidade', 'Consome 1 lacaio. Se consumiu, ganha 1 Acao e compra 1 carta.', '[{"op":"consumir_lacaios","valor":1},{"op":"se","condicao":"consumidos>=1","efeitos":[{"op":"ganhar_acao","valor":1},{"op":"comprar","valor":1}]}]', 1
FROM arquetipos a WHERE a.slug = 'sacrificio'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_ritual', 'Ritual Ganancioso', 2, 'ataque', 'Consome ate 3 lacaios. Causa 4 de dano a todos os inimigos por lacaio consumido.', '[{"op":"consumir_lacaios","valor":3},{"op":"dano_por_lacaio","alvo":"todos","valor":4,"fonte":"consumidos"}]', 1
FROM arquetipos a WHERE a.slug = 'sacrificio'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_ariete', 'Ariete de Costelas', 1, 'ataque', 'Causa dano igual ao seu Bloco atual (limite 10).', '[{"op":"dano_defesa","alvo":"inimigo","teto":10}]', 1
FROM arquetipos a WHERE a.slug = 'ossada'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_muralha', 'Muralha de Costelas', 1, 'defesa', 'Ganha 4 de Bloco, +1 por lacaio em campo (limite 8).', '[{"op":"bloco","valor":4},{"op":"bloco_por_lacaio","valor":1,"teto":8}]', 1
FROM arquetipos a WHERE a.slug = 'ossada'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_ossos', 'Ossos Firmes', 2, 'poder', 'No fim do seu turno, ganha 1 de Bloco por lacaio em campo.', '[{"op":"poder","nome":"ossos_firmes"}]', 1
FROM arquetipos a WHERE a.slug = 'ossada'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_cimento', 'Cimento de Osso', 1, 'utilidade', 'Ganha 2 de Bloco. O seu Bloco nao se perde no fim deste turno.', '[{"op":"bloco","valor":2},{"op":"manter_bloco"}]', 1
FROM arquetipos a WHERE a.slug = 'ossada'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_escudo', 'Escudo de Craneos', 1, 'defesa', 'Ganha 5 de Bloco. Invoca 1 lacaio.', '[{"op":"bloco","valor":5},{"op":"invocar","valor":1}]', 1
FROM arquetipos a WHERE a.slug = 'ossada'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_baforada', 'Baforada Podre', 1, 'ataque', 'Aplica 5 de Veneno.', '[{"op":"estado","alvo":"inimigo","estado":"veneno","valor":5}]', 0
FROM arquetipos a WHERE a.slug = 'putrefacao'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_pus', 'Pus Endurecido', 1, 'defesa', 'Ganha 4 de Bloco. Aplica 2 de Veneno.', '[{"op":"bloco","valor":4},{"op":"estado","alvo":"inimigo","estado":"veneno","valor":2}]', 0
FROM arquetipos a WHERE a.slug = 'putrefacao'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_peste', 'Peste Ossea', 2, 'poder', 'No fim do seu turno, aplica 2 de Veneno a todos os inimigos.', '[{"op":"poder","nome":"peste"}]', 0
FROM arquetipos a WHERE a.slug = 'putrefacao'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_contagio', 'Contagio', 1, 'utilidade', 'Espalha o Veneno do alvo para os outros inimigos. Compra 1 carta.', '[{"op":"espalhar_veneno"},{"op":"comprar","valor":1}]', 0
FROM arquetipos a WHERE a.slug = 'putrefacao'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

INSERT INTO cartas (arquetipo_id, slug, nome, custo, tipo, texto, efeitos, inicial)
SELECT a.id, 'cm_mordida', 'Mordida Gangrenada', 1, 'ataque', 'Causa 6 de dano. Se o alvo esta envenenado, invoca 1 lacaio e aplica Fraqueza 1.', '[{"op":"dano","alvo":"inimigo","valor":6},{"op":"se","condicao":"alvo_envenenado","efeitos":[{"op":"invocar","valor":1},{"op":"estado","alvo":"inimigo","estado":"fraqueza","valor":1}]}]', 0
FROM arquetipos a WHERE a.slug = 'putrefacao'
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), custo = VALUES(custo), tipo = VALUES(tipo),
  texto = VALUES(texto), efeitos = VALUES(efeitos), inicial = VALUES(inicial);

-- ---------------------------------------------------------------------------
-- INIMIGOS (bestiario completo, portado de flet_mvp/capitower/content.py)
-- ---------------------------------------------------------------------------

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('capivarinha', 'Capivarinha Encharcada', 'comum', 2, 8, 'fraca, ataca todo turno, aparece em grupo', NULL, '[[{"tipo":"ataque","valor":3}],[{"tipo":"ataque","valor":4}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('sapo', 'Sapo Musculoso', 'comum', 1, 26, 'Alterna entre defesa e golpe. Leia a intencao antes de agir.', NULL, '[[{"tipo":"bloco","valor":6}],[{"tipo":"ataque","valor":8}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('rato', 'Rato de Academia', 'comum', 1, 18, 'rouba Acao', NULL, '[[{"tipo":"ataque","valor":3,"vezes":2}],[{"tipo":"roubar","valor":1}],[{"tipo":"ataque","valor":4,"vezes":2}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('halter', 'Halter Vivo', 'comum', 2, 50, 'alto HP, dano baixo, cansa o jogador', NULL, '[[{"tipo":"ataque","valor":6}],[{"tipo":"bloco","valor":8},{"tipo":"ataque","valor":4}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('spinning', 'Capivara do Spinning', 'comum', 2, 26, 'age varias vezes, dano baixo', NULL, '[[{"tipo":"ataque","valor":4,"vezes":2}],[{"tipo":"ataque","valor":3,"vezes":2}],[{"tipo":"bloco","valor":5},{"tipo":"ataque","valor":4}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('personal', 'Personal Trainer', 'comum', 2, 28, 'buffa os outros inimigos da sala', NULL, '[[{"tipo":"forca_todos","valor":1}],[{"tipo":"ataque","valor":7}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('frasco', 'Frasco Ambulante', 'comum', 3, 38, 'aplica Veneno', NULL, '[[{"tipo":"veneno","valor":3}],[{"tipo":"ataque","valor":8}],[{"tipo":"veneno","valor":4},{"tipo":"ataque","valor":4}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('experimental', 'Capivara Experimental', 'comum', 3, 48, 'muda de padrao ao levar dano', '{"mudaPadrao":true}', '[[{"tipo":"ataque","valor":10}],[{"tipo":"bloco","valor":10}],[{"tipo":"ataque","valor":6,"vezes":2}],[{"tipo":"fraqueza","valor":2}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('bolha', 'Bolha de Soro', 'comum', 3, 45, 'reflete 25% do dano recebido', '{"reflete":0.25}', '[[{"tipo":"ataque","valor":7}],[{"tipo":"bloco","valor":12}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('marmita', 'Capivara de Marmita', 'comum', 4, 60, 'se cura', NULL, '[[{"tipo":"ataque","valor":11}],[{"tipo":"curar","valor":8},{"tipo":"bloco","valor":6}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('garcom', 'Garcom Bombado', 'comum', 4, 95, 'HP muito alto, golpe unico devastador telegrafado com 2 turnos', '{"inicioFixo":true}', '[[{"tipo":"carregar"}],[{"tipo":"carregar"}],[{"tipo":"ataque","valor":30}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('sobremesa', 'Sobremesa Viva', 'comum', 4, 42, 'aplica Fraqueza', NULL, '[[{"tipo":"fraqueza","valor":2},{"tipo":"ataque","valor":5}],[{"tipo":"ataque","valor":12}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('guarda', 'Guarda de Avental', 'comum', 5, 75, 'contra ataca com 3', '{"espinhos":3}', '[[{"tipo":"bloco","valor":12},{"tipo":"ataque","valor":8}],[{"tipo":"ataque","valor":14}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('jardineira', 'Jardineira Furiosa', 'comum', 5, 65, '+2 de Forca por turno', '{"crescimento":2}', '[[{"tipo":"ataque","valor":8}],[{"tipo":"ataque","valor":10}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('vaso', 'Vaso Sentinela', 'comum', 5, 40, 'nao ataca, buffa e cura o resto da sala', NULL, '[[{"tipo":"curar_todos","valor":6}],[{"tipo":"forca_todos","valor":2}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('elite1', 'Capivara de Pulso', 'elite', 1, 48, NULL, '{"elite":true}', '[[{"tipo":"ataque","valor":4,"vezes":2}],[{"tipo":"bloco","valor":8},{"tipo":"ataque","valor":5}],[{"tipo":"ataque","valor":10}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('elite2', 'Instrutora de Cross', 'elite', 2, 70, NULL, '{"elite":true}', '[[{"tipo":"ataque","valor":5,"vezes":2}],[{"tipo":"forca","valor":1}],[{"tipo":"ataque","valor":8,"vezes":2}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('elite3', 'Cobaia Alfa', 'elite', 3, 100, NULL, '{"elite":true}', '[[{"tipo":"veneno","valor":5}],[{"tipo":"fragilidade","valor":2},{"tipo":"ataque","valor":8}],[{"tipo":"ataque","valor":16}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('elite4', 'Chef de Cozinha', 'elite', 4, 130, NULL, '{"elite":true}', '[[{"tipo":"ataque","valor":14}],[{"tipo":"curar","valor":12},{"tipo":"bloco","valor":10}],[{"tipo":"ataque","valor":18}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('elite5', 'Capita da Guarda', 'elite', 5, 150, NULL, '{"elite":true,"espinhos":4}', '[[{"tipo":"bloco","valor":15},{"tipo":"ataque","valor":12}],[{"tipo":"ataque","valor":10,"vezes":2}],[{"tipo":"forca","valor":3}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('dorival', 'Dorival Supino', 'chefe', 1, 75, 'carrega e golpeia', '{"chefe":true}', '[[{"tipo":"bloco","valor":10},{"tipo":"carregar"}],[{"tipo":"ataque","valor":16}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('marlene', 'Marlene Cardio', 'chefe', 2, 120, 'age duas vezes por turno', '{"chefe":true}', '[[{"tipo":"ataque","valor":5,"vezes":2}],[{"tipo":"ataque","valor":4,"vezes":2},{"tipo":"fraqueza","valor":1}],[{"tipo":"bloco","valor":8},{"tipo":"ataque","valor":6,"vezes":2}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('helio', 'Professor Helio Whey', 'chefe', 3, 190, 'estados e buff proprio', '{"chefe":true}', '[[{"tipo":"fraqueza","valor":2},{"tipo":"fragilidade","valor":2}],[{"tipo":"ataque","valor":14}],[{"tipo":"forca","valor":3},{"tipo":"bloco","valor":10}],[{"tipo":"veneno","valor":6},{"tipo":"ataque","valor":8}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('gemeo_a', 'Gemeo Rosca (Esq.)', 'chefe', 4, 120, 'o irmao herda +5 de Forca', '{"chefe":true,"gemeo":5}', '[[{"tipo":"ataque","valor":11}],[{"tipo":"bloco","valor":8},{"tipo":"ataque","valor":6}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('gemeo_b', 'Gemeo Rosca (Dir.)', 'chefe', 4, 120, 'o irmao herda +5 de Forca', '{"chefe":true,"gemeo":5}', '[[{"tipo":"bloco","valor":8},{"tipo":"ataque","valor":6}],[{"tipo":"ataque","valor":11}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('capitolino', 'Sargento Capitolino', 'chefe', 5, 260, 'ganha 12 de Bloco todo turno', '{"chefe":true,"blocoTodoTurno":12}', '[[{"tipo":"ataque","valor":16}],[{"tipo":"ataque","valor":10},{"tipo":"fraqueza","valor":1}],[{"tipo":"ataque","valor":20}]]', NULL)
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

INSERT INTO inimigos (slug, nome, tipo, bloco, hp, nota, flags, padrao, fases)
VALUES ('gertrudes', 'Soberana Gertrudes', 'chefao', 6, 340, 'tres fases', '{"chefe":true,"fases":true}', '[[{"tipo":"bloco","valor":14},{"tipo":"carregar"}],[{"tipo":"ataque","valor":26}]]', '[{"fracaoMin":0.66,"padrao":[[{"tipo":"bloco","valor":14},{"tipo":"carregar"}],[{"tipo":"ataque","valor":26}]]},{"fracaoMin":0.33,"padrao":[[{"tipo":"ataque","valor":7,"vezes":3}],[{"tipo":"ataque","valor":6,"vezes":2},{"tipo":"fraqueza","valor":1}],[{"tipo":"forca","valor":2},{"tipo":"bloco","valor":10}]]},{"fracaoMin":0,"padrao":[[{"tipo":"fragilidade","valor":2},{"tipo":"veneno","valor":6}],[{"tipo":"ataque","valor":18}],[{"tipo":"curar","valor":15},{"tipo":"bloco","valor":20}]]}]')
ON DUPLICATE KEY UPDATE
  nome = VALUES(nome), tipo = VALUES(tipo), bloco = VALUES(bloco), hp = VALUES(hp),
  nota = VALUES(nota), flags = VALUES(flags), padrao = VALUES(padrao), fases = VALUES(fases);

-- ---------------------------------------------------------------------------
-- ENCONTROS (composicao das salas de cada bloco)
-- ---------------------------------------------------------------------------

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco1-comum-1', 1, 'comum', '["capivarinha","capivarinha","capivarinha"]', 1)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco1-comum-2', 1, 'comum', '["sapo"]', 2)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco1-comum-3', 1, 'comum', '["rato","capivarinha"]', 3)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco1-comum-4', 1, 'comum', '["sapo","capivarinha"]', 4)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco1-comum-5', 1, 'comum', '["rato"]', 5)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco1-elite', 1, 'elite', '["elite1"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco1-chefe', 1, 'chefe', '["dorival"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco2-comum-1', 2, 'comum', '["halter"]', 1)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco2-comum-2', 2, 'comum', '["spinning","spinning"]', 2)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco2-comum-3', 2, 'comum', '["personal","spinning"]', 3)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco2-comum-4', 2, 'comum', '["halter","personal"]', 4)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco2-comum-5', 2, 'comum', '["spinning","capivarinha","capivarinha"]', 5)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco2-elite', 2, 'elite', '["elite2"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco2-chefe', 2, 'chefe', '["marlene"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco3-comum-1', 3, 'comum', '["frasco","frasco"]', 1)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco3-comum-2', 3, 'comum', '["experimental"]', 2)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco3-comum-3', 3, 'comum', '["bolha"]', 3)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco3-comum-4', 3, 'comum', '["frasco","bolha"]', 4)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco3-comum-5', 3, 'comum', '["experimental","frasco"]', 5)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco3-elite', 3, 'elite', '["elite3"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco3-chefe', 3, 'chefe', '["helio"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco4-comum-1', 4, 'comum', '["marmita"]', 1)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco4-comum-2', 4, 'comum', '["sobremesa","sobremesa"]', 2)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco4-comum-3', 4, 'comum', '["garcom"]', 3)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco4-comum-4', 4, 'comum', '["marmita","sobremesa"]', 4)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco4-comum-5', 4, 'comum', '["garcom","sobremesa"]', 5)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco4-elite', 4, 'elite', '["elite4"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco4-chefe', 4, 'chefe', '["gemeo_a","gemeo_b"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco5-comum-1', 5, 'comum', '["guarda"]', 1)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco5-comum-2', 5, 'comum', '["jardineira"]', 2)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco5-comum-3', 5, 'comum', '["vaso","guarda"]', 3)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco5-comum-4', 5, 'comum', '["jardineira","vaso"]', 4)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco5-comum-5', 5, 'comum', '["guarda","guarda"]', 5)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco5-elite', 5, 'elite', '["elite5"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('bloco5-chefe', 5, 'chefe', '["capitolino"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

INSERT INTO encontros (slug, bloco, tipo, composicao, ordem) VALUES ('chefao-final', 6, 'chefao', '["gertrudes"]', 0)
ON DUPLICATE KEY UPDATE composicao = VALUES(composicao), ordem = VALUES(ordem);

-- ---------------------------------------------------------------------------
-- EVENTOS
-- ---------------------------------------------------------------------------

INSERT INTO eventos (slug, titulo, texto, bloco_min, bloco_max, opcoes) VALUES ('bebedouro', 'O Bebedouro', 'Uma fonte de agua suspeita borbulhando sozinha.', 1, 5, '[{"texto":"Beber","resultado":"Cura 20% do HP maximo. 50% de chance de comecar o proximo combate com Fraqueza 1.","efeitos":[{"op":"curar_pct","valor":0.2},{"op":"chance_fraqueza","chance":0.5,"valor":1}]},{"texto":"Encher o cantil","resultado":"Cura 10% agora e mais 10% depois do proximo combate.","efeitos":[{"op":"curar_pct","valor":0.1},{"op":"curar_pct_diferido","valor":0.1}]},{"texto":"Seguir","resultado":"Nada acontece.","efeitos":[{"op":"nada"}]}]')
ON DUPLICATE KEY UPDATE titulo = VALUES(titulo), texto = VALUES(texto), opcoes = VALUES(opcoes);

INSERT INTO eventos (slug, titulo, texto, bloco_min, bloco_max, opcoes) VALUES ('halteres_perdida', 'A Halteres Perdida', 'Um halter esquecido no corredor, pesado demais para carregar.', 1, 5, '[{"texto":"Levantar","resultado":"Perde 8 de vida, ganha 1 de Forca permanente na run.","efeitos":[{"op":"perder_hp","valor":8},{"op":"forca_permanente","valor":1}]},{"texto":"Deixar","resultado":"Nada acontece.","efeitos":[{"op":"nada"}]}]')
ON DUPLICATE KEY UPDATE titulo = VALUES(titulo), texto = VALUES(texto), opcoes = VALUES(opcoes);

INSERT INTO eventos (slug, titulo, texto, bloco_min, bloco_max, opcoes) VALUES ('vestiario', 'O Vestiario', 'Armarios abertos, cheiro forte, alguem esqueceu alguma coisa.', 1, 5, '[{"texto":"Vasculhar","resultado":"Ganha uma carta aleatoria da sua classe ate o proximo chefe de bloco.","efeitos":[{"op":"carta_temporaria"}]},{"texto":"Descansar ali mesmo","resultado":"Cura 15% do HP maximo.","efeitos":[{"op":"curar_pct","valor":0.15}]}]')
ON DUPLICATE KEY UPDATE titulo = VALUES(titulo), texto = VALUES(texto), opcoes = VALUES(opcoes);

-- ---------------------------------------------------------------------------
-- DESAFIOS (modificadores de desafio opcional, D25)
-- ---------------------------------------------------------------------------

INSERT INTO desafios (slug, nome, texto, efeito, ordem) VALUES ('forca_bruta', 'Forca Bruta', '+1 de Forca permanente pelo resto da run.', '{"op":"forca_permanente","valor":1}', 1)
ON DUPLICATE KEY UPDATE nome = VALUES(nome), texto = VALUES(texto), efeito = VALUES(efeito), ordem = VALUES(ordem);

INSERT INTO desafios (slug, nome, texto, efeito, ordem) VALUES ('folego_extra', 'Folego Extra', '+5 de HP maximo permanente na run, cura 5 agora.', '{"op":"hp_max_permanente","valor":5}', 2)
ON DUPLICATE KEY UPDATE nome = VALUES(nome), texto = VALUES(texto), efeito = VALUES(efeito), ordem = VALUES(ordem);

-- ---------------------------------------------------------------------------
-- OBJETIVOS (Fase 5: meta progressao, D12/D13)
-- ---------------------------------------------------------------------------
-- Rascunho de 12 objetivos para revisao. Cada um trava um pouco do pool inicial de cartas
-- reduzido acima (as 5 cartas da Putrefacao, marcadas inicial = 0 nesta mesma Fase 5) atras de
-- uma conquista nomeada, nunca de XP passivo ou moeda de meta (D13). O campo "condicao" e um
-- JSON {"tipo":..., ...} avaliado em app/models/Meta.php::condicaoBatida(); "recompensa_tipo"
-- 'arquetipo' destrava de uma vez todas as cartas nao iniciais daquele arquetipo (hoje, so
-- Putrefacao), sem precisar de uma linha por carta.

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('marco-andar-10', 'Primeiros Passos', 'Alcance o andar 10 numa run.', '{"tipo":"andar_alcancado","valor":10}', 'carta', 'cm_baforada', 0, 1)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('marco-andar-25', 'Meio da Subida', 'Alcance o andar 25 numa run.', '{"tipo":"andar_alcancado","valor":25}', 'carta', 'cm_pus', 0, 2)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('marco-andar-50', 'Portas do Chefao', 'Alcance o andar 50 numa run.', '{"tipo":"andar_alcancado","valor":50}', 'carta', 'cm_contagio', 0, 3)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('vitoria-torre', 'A Torre Caiu', 'Derrote a Soberana Gertrudes e venca a run.', '{"tipo":"vitoria"}', 'arquetipo', 'putrefacao', 0, 4)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('derrotar-dorival', 'Fim da Serie de Dorival', 'Derrote Dorival Supino, chefe do Bloco 1.', '{"tipo":"chefe_derrotado","slug":"dorival"}', 'carta', 'cm_baforada', 0, 5)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('derrotar-marlene', 'Cardio Interrompido', 'Derrote Marlene Cardio, chefe do Bloco 2.', '{"tipo":"chefe_derrotado","slug":"marlene"}', 'carta', 'cm_pus', 0, 6)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('derrotar-helio', 'Aula Cancelada', 'Derrote o Professor Helio Whey, chefe do Bloco 3.', '{"tipo":"chefe_derrotado","slug":"helio"}', 'carta', 'cm_peste', 0, 7)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('derrotar-gemeos', 'Os Dois Caem Juntos', 'Derrote os Gemeos Rosca, chefes do Bloco 4.', '{"tipo":"chefe_derrotado","slug":"gemeo_a"}', 'carta', 'cm_contagio', 0, 8)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('derrotar-capitolino', 'Sem Sargento', 'Derrote o Sargento Capitolino, chefe do Bloco 5.', '{"tipo":"chefe_derrotado","slug":"capitolino"}', 'carta', 'cm_mordida', 0, 9)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('so-no-osso', 'So no Osso', 'Venca a run inteira sem escolher a recompensa de habilidade nenhuma vez.', '{"tipo":"vitoria_sem_habilidade"}', 'arquetipo', 'putrefacao', 1, 10)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('pureza-de-nicho', 'Pureza de Nicho', 'Termine uma run com o baralho inteiro, sem contar copias temporarias, vindo de um so arquetipo.', '{"tipo":"baralho_arquetipo_unico"}', 'arquetipo', 'putrefacao', 1, 11)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);

INSERT INTO objetivos (slug, nome, descricao, condicao, recompensa_tipo, recompensa_ref, oculto, ordem) VALUES
('queda-precoce', 'Queda Precoce', 'Perca uma run antes do andar 5. Nem toda licao vem de vitoria.', '{"tipo":"derrota_precoce","andar_maximo":5}', 'carta', 'cm_baforada', 0, 12)
ON DUPLICATE KEY UPDATE nome=VALUES(nome), descricao=VALUES(descricao), condicao=VALUES(condicao), recompensa_tipo=VALUES(recompensa_tipo), recompensa_ref=VALUES(recompensa_ref), oculto=VALUES(oculto), ordem=VALUES(ordem);
