"""Catalogo de cartas do MVP.

Cada carta e um CardDef com uma lista de efeitos. Um efeito e uma tupla
("tipo", *args). O resolvedor fica em combat.py. Vocabulario:

  ("dmg", n, alvo)               alvo: "enemy" (selecionado) ou "all"
  ("block", n)
  ("draw", n)
  ("action", n)
  ("lose_hp", n)
  ("poison", n, alvo)
  ("weak", turnos, alvo)
  ("frail", turnos, alvo)
  ("strength", n)                Forca do jogador ate o fim do combate
  ("summon", n)                  Capimaga
  ("consume", n)                 consome ate n lacaios -> ctx["consumed"]
  ("dmg_per_consumed", n, alvo)
  ("dmg_per_minion", n, alvo)
  ("block_per_minion", n, teto)
  ("adren", n)                   Brutamontes
  ("consume_adren", n)           -> ctx["consumed"]
  ("dmg_per_adren", n, teto)     nao consome
  ("block_per_adren", n, teto)
  ("block_per_consumed", n)
  ("retaliation", valor, turnos)
  ("evasion", n)                 Ligeira
  ("dmg_per_impulso", n, teto)   n por carta jogada antes desta no turno
  ("return_last",)               devolve a ultima carta (custo > 0) a mao
  ("next_free",)                 proxima carta do turno custa 0
  ("redraw_hand",)               descarta a mao e compra o mesmo numero
  ("power", nome)                registra um poder persistente no combate
  ("if", condicao, [efeitos])    condicoes em combat.check_condition
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CardDef:
    id: str
    name: str
    cls: str
    arch: str
    cost: int
    kind: str  # Ataque, Defesa, Poder, Utilidade
    text: str
    effects: tuple = field(default_factory=tuple)


def _freeze(x):
    return tuple(_freeze(i) for i in x) if isinstance(x, (list, tuple)) else x


def _c(id, name, cls, arch, cost, kind, text, *effects):
    return CardDef(id, name, cls, arch, cost, kind, text, _freeze(effects))


# ---------------------------------------------------------------- Capimaga
CAPIMAGA = [
    # Enxame
    _c("cm_costela", "Costela Solta", "capimaga", "Enxame", 1, "Ataque",
       "Causa 7 de dano. Invoca 1 lacaio.",
       ("dmg", 7, "enemy"), ("summon", 1)),
    _c("cm_chamado", "Chamado da Vala", "capimaga", "Enxame", 1, "Utilidade",
       "Invoca 3 lacaios.",
       ("summon", 3)),
    _c("cm_marcha", "Marcha dos Ossos", "capimaga", "Enxame", 2, "Ataque",
       "Causa 4 de dano por lacaio em campo.",
       ("dmg_per_minion", 4, "enemy")),
    # Sacrificio
    _c("cm_explosao", "Explosão Óssea", "capimaga", "Sacrifício", 1, "Ataque",
       "Consome até 2 lacaios. Causa 6 de dano por lacaio consumido.",
       ("consume", 2), ("dmg_per_consumed", 6, "enemy")),
    _c("cm_oferenda", "Oferenda", "capimaga", "Sacrifício", 0, "Utilidade",
       "Consome 1 lacaio. Se consumiu, ganha 1 Ação e compra 1 carta.",
       ("consume", 1), ("if", "consumed>=1", [("action", 1), ("draw", 1)])),
    _c("cm_ritual", "Ritual Ganancioso", "capimaga", "Sacrifício", 2, "Ataque",
       "Consome até 3 lacaios. Causa 4 de dano a todos os inimigos por lacaio consumido.",
       ("consume", 3), ("dmg_per_consumed", 4, "all")),
    # Ossada
    _c("cm_muralha", "Muralha de Costelas", "capimaga", "Ossada", 1, "Defesa",
       "Ganha 4 de Defesa, +1 por lacaio em campo (limite 8).",
       ("block", 4), ("block_per_minion", 1, 8)),
    _c("cm_escudo", "Escudo de Crânios", "capimaga", "Ossada", 1, "Defesa",
       "Ganha 5 de Defesa. Invoca 1 lacaio.",
       ("block", 5), ("summon", 1)),
    _c("cm_ossos", "Ossos Firmes", "capimaga", "Ossada", 2, "Poder",
       "No fim do seu turno, ganha 1 de Defesa por lacaio em campo.",
       ("power", "ossos_firmes")),
    # Putrefacao
    _c("cm_baforada", "Baforada Podre", "capimaga", "Putrefação", 1, "Ataque",
       "Aplica 5 de Veneno.",
       ("poison", 5, "enemy")),
    _c("cm_peste", "Peste Óssea", "capimaga", "Putrefação", 2, "Poder",
       "No fim do seu turno, aplica 2 de Veneno a todos os inimigos.",
       ("power", "peste")),
    _c("cm_mordida", "Mordida Gangrenada", "capimaga", "Putrefação", 1, "Ataque",
       "Causa 6 de dano. Se o alvo está envenenado, invoca 1 lacaio e aplica Fraqueza 1.",
       ("dmg", 6, "enemy"), ("if", "target_poisoned", [("summon", 1), ("weak", 1, "enemy")])),
]

# ------------------------------------------------------------ Brutamontes
BRUTAMONTES = [
    # Suor
    _c("bm_bufo", "Bufo", "brutamontes", "Suor", 0, "Utilidade",
       "Perde 2 de vida. Ganha 2 de Adrenalina. Compra 1 carta.",
       ("lose_hp", 2), ("adren", 2), ("draw", 1)),
    _c("bm_peitada", "Peitada", "brutamontes", "Suor", 1, "Ataque",
       "Causa 10 de dano. Perde 2 de vida.",
       ("dmg", 10, "enemy"), ("lose_hp", 2)),
    _c("bm_rugido", "Rugido", "brutamontes", "Suor", 1, "Poder",
       "Sempre que perder vida, ganha 1 de Adrenalina extra.",
       ("power", "rugido")),
    # Estouro
    _c("bm_cabecada", "Cabeçada Final", "brutamontes", "Estouro", 2, "Ataque",
       "Consome até 6 de Adrenalina. Causa 10 de dano, +3 por ponto consumido.",
       ("consume_adren", 6), ("dmg", 10, "enemy"), ("dmg_per_consumed", 3, "enemy")),
    _c("bm_soco", "Soco de Sobra", "brutamontes", "Estouro", 1, "Ataque",
       "Causa 7 de dano, +1 por Adrenalina acumulada (limite 8).",
       ("dmg", 7, "enemy"), ("dmg_per_adren", 1, 8)),
    _c("bm_estampido", "Estampido", "brutamontes", "Estouro", 2, "Ataque",
       "Consome até 3 de Adrenalina. Causa 6 de dano a todos, +2 por ponto consumido.",
       ("consume_adren", 3), ("dmg", 6, "all"), ("dmg_per_consumed", 2, "all")),
    # Couro
    _c("bm_costado", "Costado", "brutamontes", "Couro", 1, "Defesa",
       "Ganha 6 de Defesa, +1 por Adrenalina acumulada (limite 8).",
       ("block", 6), ("block_per_adren", 1, 8)),
    _c("bm_pele", "Pele de Bicho", "brutamontes", "Couro", 2, "Defesa",
       "Consome até 4 de Adrenalina. Ganha 6 de Defesa, +3 por ponto consumido.",
       ("consume_adren", 4), ("block", 6), ("block_per_consumed", 3)),
    _c("bm_fincar", "Fincar Pé", "brutamontes", "Couro", 1, "Defesa",
       "Ganha 8 de Defesa. Se tem 5+ de Adrenalina, ganha 1 de Força.",
       ("block", 8), ("if", "adren>=5", [("strength", 1)])),
    # Troco
    _c("bm_naofaz", "Não Faz Isso", "brutamontes", "Troco", 1, "Defesa",
       "Ganha Retaliação 4 por 2 turnos.",
       ("retaliation", 4, 2)),
    _c("bm_provocar", "Provocar", "brutamontes", "Troco", 0, "Utilidade",
       "Ganha 4 de Defesa e Retaliação 2 por 1 turno.",
       ("block", 4), ("retaliation", 2, 1)),
    _c("bm_olho", "Olho por Olho", "brutamontes", "Troco", 2, "Poder",
       "Sempre que perder vida para um ataque, causa 3 de dano ao atacante.",
       ("power", "olho_por_olho")),
]

# ----------------------------------------------------------------- Ligeira
LIGEIRA = [
    # Corrente
    _c("lg_passo", "Passo Curto", "ligeira", "Corrente", 0, "Ataque",
       "Causa 2 de dano. Compra 1 carta.",
       ("dmg", 2, "enemy"), ("draw", 1)),
    _c("lg_respiro", "Respiro", "ligeira", "Corrente", 0, "Utilidade",
       "Compra 1 carta. Se já jogou 3 cartas neste turno, ganha 1 Ação.",
       ("draw", 1), ("if", "impulso>=3", [("action", 1)])),
    _c("lg_cambalhota", "Cambalhota", "ligeira", "Corrente", 1, "Ataque",
       "Causa 4 de dano duas vezes.",
       ("dmg", 4, "enemy"), ("dmg", 4, "enemy")),
    # Estocada
    _c("lg_pontocego", "Ponto Cego", "ligeira", "Estocada", 1, "Ataque",
       "Causa 3 de dano por carta jogada antes desta neste turno (limite 5).",
       ("dmg_per_impulso", 3, 5)),
    _c("lg_dentada", "Dentada Rápida", "ligeira", "Estocada", 1, "Ataque",
       "Causa 6 de dano. Se já jogou 2 cartas neste turno, causa 4 a mais.",
       ("dmg", 6, "enemy"), ("if", "impulso>=2", [("dmg", 4, "enemy")])),
    _c("lg_rasteira", "Rasteira", "ligeira", "Estocada", 2, "Ataque",
       "Causa 10 de dano. Se já jogou 3 cartas neste turno, aplica Fragilidade 2.",
       ("dmg", 10, "enemy"), ("if", "impulso>=3", [("frail", 2, "enemy")])),
    # Fumaca
    _c("lg_lama", "Banho de Lama", "ligeira", "Fumaça", 1, "Defesa",
       "Ganha 1 de Evasão, ou 2 se já jogou 3 cartas neste turno.",
       ("evasion", 1), ("if", "impulso>=3", [("evasion", 1)])),
    _c("lg_esquiva", "Esquiva", "ligeira", "Fumaça", 1, "Defesa",
       "Ganha 5 de Defesa, ou 8 se já jogou 2 cartas neste turno.",
       ("block", 5), ("if", "impulso>=2", [("block", 3)])),
    _c("lg_cortina", "Cortina de Lama", "ligeira", "Fumaça", 2, "Defesa",
       "Ganha 1 de Evasão. Aplica Fraqueza 2 a todos os inimigos.",
       ("evasion", 1), ("weak", 2, "all")),
    # Contrabando
    _c("lg_pega", "Pega de Volta", "ligeira", "Contrabando", 1, "Utilidade",
       "Devolve à mão a última carta jogada neste turno (não alcança carta de custo 0).",
       ("return_last",)),
    _c("lg_marcado", "Baralho Marcado", "ligeira", "Contrabando", 1, "Utilidade",
       "Compra 1 carta. A próxima carta jogada neste turno custa 0.",
       ("draw", 1), ("next_free",)),
    _c("lg_troca", "Troca Rápida", "ligeira", "Contrabando", 1, "Utilidade",
       "Descarta a mão e compra o mesmo número de cartas.",
       ("redraw_hand",)),
]

POOLS = {
    "capimaga": CAPIMAGA,
    "brutamontes": BRUTAMONTES,
    "ligeira": LIGEIRA,
}

BY_ID = {c.id: c for pool in POOLS.values() for c in pool}
