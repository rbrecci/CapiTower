-- CapiTower: estrutura do banco
-- MySQL 8 / MariaDB 10.4+ (InfinityFree). Charset utf8mb4 em tudo.
-- Colunas JSON funcionam como LONGTEXT no MariaDB, o que e suficiente aqui.

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

-- Uma linha por nivel (1 a 10) da habilidade de cada classe.
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
  texto         VARCHAR(255) NOT NULL, -- texto exibido, com {0}, {1} para valores
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
  hp_min      SMALLINT UNSIGNED NOT NULL,
  hp_max      SMALLINT UNSIGNED NOT NULL,
  arte        VARCHAR(120) NULL,
  descricao   TEXT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_inimigos_slug (slug),
  KEY ix_inimigos_bloco_tipo (bloco, tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Intencoes que o inimigo pode telegrafar. A IA escolhe entre as acoes da fase atual.
CREATE TABLE IF NOT EXISTS inimigo_acoes (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  inimigo_id    SMALLINT UNSIGNED NOT NULL,
  fase          TINYINT UNSIGNED NOT NULL DEFAULT 1, -- chefes usam mais de uma
  ordem         TINYINT UNSIGNED NOT NULL DEFAULT 0, -- 0 = sorteio livre, >0 = ciclo fixo
  peso          TINYINT UNSIGNED NOT NULL DEFAULT 1,
  intencao      ENUM('atacar','defender','buffar','debuffar','especial') NOT NULL,
  efeitos       JSON NOT NULL,
  condicao      JSON NULL, -- ex: {"hp_abaixo_de": 50}
  PRIMARY KEY (id),
  KEY ix_acoes_inimigo_fase (inimigo_id, fase),
  CONSTRAINT fk_acoes_inimigo FOREIGN KEY (inimigo_id) REFERENCES inimigos (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Grupos de inimigos que formam uma sala de combate.
CREATE TABLE IF NOT EXISTS encontros (
  id          SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  slug        VARCHAR(48) NOT NULL,
  bloco       TINYINT UNSIGNED NOT NULL,
  tipo        ENUM('comum','elite','chefe','chefao','desafio') NOT NULL,
  composicao  JSON NOT NULL, -- [{"inimigo":"rato-de-academia","qtd":2}]
  regra       JSON NULL,     -- condicao extra do desafio opcional
  peso        TINYINT UNSIGNED NOT NULL DEFAULT 1,
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
  opcoes      JSON NOT NULL, -- [{"texto":"Beber","efeitos":[...]}]
  arte        VARCHAR(120) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_eventos_slug (slug)
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

-- Deck da run. Uma linha por copia de carta.
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
  recompensa_tipo ENUM('carta','classe','habilidade','cosmetico') NOT NULL,
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
  tipo           ENUM('carta','classe','habilidade','cosmetico') NOT NULL,
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
