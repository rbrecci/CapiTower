-- CapiTower: estrutura do banco
-- MySQL 8 / MariaDB 10.4+ (InfinityFree). Charset utf8mb4 em tudo.
-- Colunas JSON funcionam como LONGTEXT no MariaDB, o que e suficiente aqui.
--
-- Revisado na Fase 4 para bater com o catalogo real que saiu da Fase 3
-- (public/assets/js/data/{cards,enemy,events,challenges}.json). Duas mudancas em relacao
-- ao esqueleto da Fase 0:
--   - inimigos guarda hp unico e o padrao de turnos inteiro em JSON (padrao), em vez de
--     hp_min/hp_max e uma tabela normalizada inimigo_acoes: o bestiario real usa um ciclo fixo
--     de turnos com varios sub-efeitos por turno (ex: bloco + carregar), o que nao cabia bem
--     no formato peso/intencao pensado antes do conteudo existir.
--   - nasceu a tabela desafios: os modificadores de desafio opcional (D25) sao globais da run,
--     nao amarrados a um encontro especifico, e o esqueleto da Fase 0 nao previa isso.
--
-- Revisado na Fase 5 (meta progressao, D12/D13): objetivos.recompensa_tipo e
-- usuario_desbloqueios.tipo ganharam o valor 'arquetipo', para um objetivo poder destravar um
-- arquetipo inteiro de uma vez (todas as cartas dele com inicial = 0), sem exigir uma linha de
-- desbloqueio por carta.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------------
-- CONTAS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS usuarios (
  id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
  usuario         VARCHAR(24)  NOT NULL,
  email           VARCHAR(160) NOT NULL,
  senha_hash      VARCHAR(255) NOT NULL,
  criado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultimo_login    DATETIME     NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_usuarios_usuario (usuario),
  UNIQUE KEY uk_usuarios_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS login_tentativas (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ip          VARCHAR(45)  NOT NULL,
  usuario     VARCHAR(24)  NULL,
  sucesso     TINYINT(1)   NOT NULL DEFAULT 0,
  criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_login_ip_data (ip, criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- CATALOGO: CLASSES, ARQUETIPOS E CARTAS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS classes (
  id                  TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  slug                VARCHAR(32)  NOT NULL,
  nome                VARCHAR(48)  NOT NULL,
  descricao           TEXT         NOT NULL,
  mecanica_nome       VARCHAR(48)  NOT NULL,
  mecanica_descricao  TEXT         NOT NULL,
  habilidade_nome     VARCHAR(48)  NOT NULL,
  habilidade_descricao TEXT        NOT NULL,
  hp_inicial          SMALLINT UNSIGNED NOT NULL DEFAULT 70,
  acao_por_turno      TINYINT UNSIGNED NOT NULL DEFAULT 3,
  inicial             TINYINT(1)   NOT NULL DEFAULT 0, -- 1 = desbloqueada desde o comeco
  ordem               TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_classes_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Uma linha por nivel (1 a 10) da habilidade de cada classe. O efeito mecanico de cada nivel
-- da Legiao ainda mora no cliente (core/combat.js); "efeitos" fica reservado para quando essa
-- mecanica virar dado, e comeca vazio.
CREATE TABLE IF NOT EXISTS habilidade_niveis (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
  classe_id   TINYINT UNSIGNED NOT NULL,
  nivel       TINYINT UNSIGNED NOT NULL,
  descricao   TEXT NOT NULL,
  efeitos     JSON NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_habilidade_classe_nivel (classe_id, nivel),
  CONSTRAINT fk_habilidade_classe FOREIGN KEY (classe_id) REFERENCES classes (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS arquetipos (
  id          TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  classe_id   TINYINT UNSIGNED NOT NULL,
  slug        VARCHAR(32) NOT NULL,
  nome        VARCHAR(48) NOT NULL,
  descricao   TEXT NOT NULL,
  cor         VARCHAR(7) NOT NULL DEFAULT '#888888', -- identidade visual da carta
  ordem       TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_arquetipos_slug (slug),
  KEY ix_arquetipos_classe (classe_id),
  CONSTRAINT fk_arquetipos_classe FOREIGN KEY (classe_id) REFERENCES classes (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cartas (
  id            SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  arquetipo_id  TINYINT UNSIGNED NOT NULL,
  slug          VARCHAR(48) NOT NULL,
  nome          VARCHAR(48) NOT NULL,
  custo         TINYINT UNSIGNED NOT NULL DEFAULT 1,
  tipo          ENUM('ataque','defesa','poder','utilidade') NOT NULL,
  texto         VARCHAR(255) NOT NULL, -- texto de jogo ja com os valores finais embutidos
  efeitos       JSON NOT NULL,         -- ver docs/04-arquitetura.md secao 6
  arte          VARCHAR(120) NULL,
  inicial       TINYINT(1) NOT NULL DEFAULT 0, -- 1 = ja vem no pool desbloqueado
  PRIMARY KEY (id),
  UNIQUE KEY uk_cartas_slug (slug),
  KEY ix_cartas_arquetipo (arquetipo_id),
  CONSTRAINT fk_cartas_arquetipo FOREIGN KEY (arquetipo_id) REFERENCES arquetipos (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- CATALOGO: INIMIGOS E ENCONTROS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS inimigos (
  id          SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  slug        VARCHAR(48) NOT NULL,
  nome        VARCHAR(48) NOT NULL,
  tipo        ENUM('comum','elite','chefe','chefao') NOT NULL,
  bloco       TINYINT UNSIGNED NOT NULL, -- 1 a 5, 6 = chefao do andar 51
  hp          SMALLINT UNSIGNED NOT NULL,
  nota        TEXT NULL,        -- dica de leitura de intencao, so texto
  flags       JSON NULL,        -- {"elite":true,"chefe":true,"reflete":0.25,"espinhos":4, ...}
  padrao      JSON NOT NULL,    -- lista de turnos; cada turno e uma lista de sub-acoes
                                 -- {"tipo":"ataque|bloco|forca|forca_todos|fraqueza|fragilidade|
                                 --  veneno|curar|curar_todos|roubar|carregar","valor":N,"vezes":N}
  fases       JSON NULL,        -- so a Soberana Gertrudes usa: [{"fracaoMin":0.66,"padrao":[...]}]
  arte        VARCHAR(120) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_inimigos_slug (slug),
  KEY ix_inimigos_bloco_tipo (bloco, tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Grupos de inimigos que formam uma sala de combate. composicao e a lista de slugs de inimigo
-- na ordem em que entram na sala (repete slug quando o grupo tem copias, ex: duas capivarinhas).
CREATE TABLE IF NOT EXISTS encontros (
  id          SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  slug        VARCHAR(48) NOT NULL,
  bloco       TINYINT UNSIGNED NOT NULL, -- 1 a 5, 6 = chefao do andar 51
  tipo        ENUM('comum','elite','chefe','chefao') NOT NULL,
  composicao  JSON NOT NULL, -- ["capivarinha","capivarinha","capivarinha"]
  ordem       TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_encontros_slug (slug),
  KEY ix_encontros_bloco_tipo (bloco, tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS eventos (
  id          SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  slug        VARCHAR(48) NOT NULL,
  titulo      VARCHAR(64) NOT NULL,
  texto       TEXT NOT NULL,
  bloco_min   TINYINT UNSIGNED NOT NULL DEFAULT 1,
  bloco_max   TINYINT UNSIGNED NOT NULL DEFAULT 5,
  opcoes      JSON NOT NULL, -- [{"texto":"Beber","resultado":"...","efeitos":[...]}]
  arte        VARCHAR(120) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_eventos_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Modificadores de desafio opcional (D25). Sao globais da run, escolhidos na sala tipo
-- "desafio" e aplicados aos atributos da run inteira, sem ligacao com um encontro especifico.
CREATE TABLE IF NOT EXISTS desafios (
  id      TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  slug    VARCHAR(32)  NOT NULL,
  nome    VARCHAR(64)  NOT NULL,
  texto   VARCHAR(255) NOT NULL,
  efeito  JSON NOT NULL, -- {"op":"forca_permanente","valor":1}
  ordem   TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_desafios_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- RUNS
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS runs (
  id                 INT UNSIGNED NOT NULL AUTO_INCREMENT,
  usuario_id         INT UNSIGNED NOT NULL,
  classe_id          TINYINT UNSIGNED NOT NULL,
  seed               INT UNSIGNED NOT NULL,
  estado             ENUM('ativa','vitoria','derrota','abandonada') NOT NULL DEFAULT 'ativa',
  andar_atual        TINYINT UNSIGNED NOT NULL DEFAULT 1,
  andar_maximo       TINYINT UNSIGNED NOT NULL DEFAULT 1,
  hp_atual           SMALLINT UNSIGNED NOT NULL,
  hp_max             SMALLINT UNSIGNED NOT NULL,
  nivel_habilidade   TINYINT UNSIGNED NOT NULL DEFAULT 1,
  estado_json        JSON NOT NULL,
  pontos_meta        SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  criado_em          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  finalizado_em      DATETIME NULL,
  PRIMARY KEY (id),
  KEY ix_runs_usuario_estado (usuario_id, estado),
  CONSTRAINT fk_runs_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
  CONSTRAINT fk_runs_classe  FOREIGN KEY (classe_id)  REFERENCES classes (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Deck da run. Uma linha por copia de carta. Reservado para estatisticas futuras (ex: cartas
-- mais usadas); o save/load em si usa so o array "deck" dentro de estado_json (secao 5).
CREATE TABLE IF NOT EXISTS run_cartas (
  id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
  run_id    INT UNSIGNED NOT NULL,
  carta_id  SMALLINT UNSIGNED NOT NULL,
  origem    ENUM('inicial','elite','chefe','evento') NOT NULL DEFAULT 'inicial',
  andar     TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  KEY ix_run_cartas_run (run_id),
  CONSTRAINT fk_run_cartas_run   FOREIGN KEY (run_id)   REFERENCES runs (id) ON DELETE CASCADE,
  CONSTRAINT fk_run_cartas_carta FOREIGN KEY (carta_id) REFERENCES cartas (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- META PROGRESSAO
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS objetivos (
  id             SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  slug           VARCHAR(48) NOT NULL,
  nome           VARCHAR(64) NOT NULL,
  descricao      VARCHAR(255) NOT NULL,
  condicao       JSON NOT NULL, -- ex: {"tipo":"andar_alcancado","valor":20}
  recompensa_tipo ENUM('carta','arquetipo','classe','habilidade','cosmetico') NOT NULL,
  recompensa_ref  VARCHAR(48) NOT NULL, -- slug do que sera desbloqueado
  oculto         TINYINT(1) NOT NULL DEFAULT 0,
  ordem          SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_objetivos_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuario_objetivos (
  usuario_id    INT UNSIGNED NOT NULL,
  objetivo_id   SMALLINT UNSIGNED NOT NULL,
  progresso     INT UNSIGNED NOT NULL DEFAULT 0,
  concluido_em  DATETIME NULL,
  PRIMARY KEY (usuario_id, objetivo_id),
  CONSTRAINT fk_uobj_usuario  FOREIGN KEY (usuario_id)  REFERENCES usuarios (id) ON DELETE CASCADE,
  CONSTRAINT fk_uobj_objetivo FOREIGN KEY (objetivo_id) REFERENCES objetivos (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuario_desbloqueios (
  usuario_id     INT UNSIGNED NOT NULL,
  tipo           ENUM('carta','arquetipo','classe','habilidade','cosmetico') NOT NULL,
  ref            VARCHAR(48) NOT NULL,
  desbloqueado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  origem         VARCHAR(48) NULL, -- slug do objetivo que liberou
  PRIMARY KEY (usuario_id, tipo, ref),
  CONSTRAINT fk_udesb_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuario_estatisticas (
  usuario_id        INT UNSIGNED NOT NULL,
  runs_totais       INT UNSIGNED NOT NULL DEFAULT 0,
  vitorias          INT UNSIGNED NOT NULL DEFAULT 0,
  andar_recorde     TINYINT UNSIGNED NOT NULL DEFAULT 0,
  pontos_meta_total INT UNSIGNED NOT NULL DEFAULT 0,
  chefes_derrotados INT UNSIGNED NOT NULL DEFAULT 0,
  atualizado_em     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id),
  CONSTRAINT fk_ustats_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
