"""Catalogo de cartas do MVP.

Cada carta e um CardDef com uma lista de efeitos. Um efeito e uma tupla
("tipo", *args). O resolvedor fica em combat.py. Vocabulario:

  ("dmg", n, alvo)               alvo: "enemy" (selecionado) ou "all". Abre um golpe novo.
  ("dmg_plus", n, alvo)          soma ao golpe aberto (mesmo golpe: Forca e espinhos uma vez)
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
  ("dmg_per_consumed", n, alvo)  os dmg_per_* e dmg_block tambem somam ao golpe aberto
  ("dmg_per_minion", n, alvo)
  ("block_per_minion", n, teto)
  ("dmg_block", teto)            dano igual a Defesa atual do jogador
  ("keep_block",)                a Defesa nao zera no fim deste turno
  ("spread_poison",)             os outros inimigos ficam com Veneno >= o do alvo
  ("adren", n)                   Brutamontes
  ("consume_adren", n)           -> ctx["consumed"]
  ("dmg_per_adren", n, teto)     nao consome
  ("block_per_adren", n, teto)
  ("block_per_consumed", n)
  ("action_per_consumed", n)
  ("retaliation", valor, turnos)
  ("evasion", n)                 Ligeira
  ("dmg_per_impulso", n, teto)   n por carta jogada antes desta no turno
  ("block_per_impulso", n, teto)
  ("return_last",)               devolve a ultima carta (custo > 0) a mao
  ("next_free",)                 proxima carta do turno custa 0
  ("redraw_hand",)               descarta a mao e compra o mesmo numero
  ("power", nome)                registra um poder persistente no combate
  ("if", condicao, [efeitos])    condicoes em combat.check_condition

Golpe: o dano de uma carta e um golpe so, que resolve antes do proximo efeito que nao for
dano (ou no fim da carta). "Causa 4 de dano duas vezes" sao dois ("dmg", 4, ...) seguidos;
"Causa 6, +4 se..." e ("dmg", 6, ...) mais ("dmg_plus", 4, ...) dentro do "if".

Regra de composicao (D28): todo arquetipo tem 5 cartas, com pelo menos 1 Ataque, 1 Defesa,
1 Poder e 1 Utilidade. O arquetipo e um nicho dentro do jeito de jogar da classe, nao uma
funcao dentro do deck.
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
    # Enxame: quantidade de lacaios em campo
    _c("cm_costela", "Costela Solta", "capimaga", "Enxame", 1, "Ataque",
       "Causa 7 de dano. Invoca 1 lacaio.",
       ("dmg", 7, "enemy"), ("summon", 1)),
    _c("cm_amontoado", "Amontoado", "capimaga", "Enxame", 1, "Defesa",
       "Ganha 3 de Defesa. Invoca 2 lacaios.",
       ("block", 3), ("summon", 2)),
    _c("cm_vala", "Vala Comum", "capimaga", "Enxame", 2, "Poder",
       "No início do seu turno, invoca 1 lacaio.",
       ("power", "vala_comum")),
    _c("cm_chamado", "Chamado da Vala", "capimaga", "Enxame", 1, "Utilidade",
       "Invoca 3 lacaios.",
       ("summon", 3)),
    _c("cm_marcha", "Marcha dos Ossos", "capimaga", "Enxame", 2, "Ataque",
       "Causa 4 de dano por lacaio em campo.",
       ("dmg_per_minion", 4, "enemy")),
    # Sacrificio: consumir lacaios por efeito imediato
    _c("cm_explosao", "Explosão Óssea", "capimaga", "Sacrifício", 1, "Ataque",
       "Consome até 2 lacaios. Causa 6 de dano por lacaio consumido.",
       ("consume", 2), ("dmg_per_consumed", 6, "enemy")),
    _c("cm_carne", "Escudo de Carne", "capimaga", "Sacrifício", 1, "Defesa",
       "Consome até 2 lacaios. Ganha 3 de Defesa, +4 por lacaio consumido.",
       ("consume", 2), ("block", 3), ("block_per_consumed", 4)),
    _c("cm_banquete", "Banquete", "capimaga", "Sacrifício", 2, "Poder",
       "Sempre que consumir pelo menos 1 lacaio, compra 1 carta.",
       ("power", "banquete")),
    _c("cm_oferenda", "Oferenda", "capimaga", "Sacrifício", 0, "Utilidade",
       "Consome 1 lacaio. Se consumiu, ganha 1 Ação e compra 1 carta.",
       ("consume", 1), ("if", "consumed>=1", [("action", 1), ("draw", 1)])),
    _c("cm_ritual", "Ritual Ganancioso", "capimaga", "Sacrifício", 2, "Ataque",
       "Consome até 3 lacaios. Causa 4 de dano a todos os inimigos por lacaio consumido.",
       ("consume", 3), ("dmg_per_consumed", 4, "all")),
    # Ossada: lacaios como muralha, vence por atrito
    _c("cm_ariete", "Aríete de Costelas", "capimaga", "Ossada", 1, "Ataque",
       "Causa dano igual à sua Defesa atual (limite 10).",
       ("dmg_block", 10)),
    _c("cm_muralha", "Muralha de Costelas", "capimaga", "Ossada", 1, "Defesa",
       "Ganha 4 de Defesa, +1 por lacaio em campo (limite 8).",
       ("block", 4), ("block_per_minion", 1, 8)),
    _c("cm_ossos", "Ossos Firmes", "capimaga", "Ossada", 2, "Poder",
       "No fim do seu turno, ganha 1 de Defesa por lacaio em campo.",
       ("power", "ossos_firmes")),
    _c("cm_cimento", "Cimento de Osso", "capimaga", "Ossada", 1, "Utilidade",
       "Ganha 2 de Defesa. A sua Defesa não se perde no fim deste turno.",
       ("block", 2), ("keep_block",)),
    _c("cm_escudo", "Escudo de Crânios", "capimaga", "Ossada", 1, "Defesa",
       "Ganha 5 de Defesa. Invoca 1 lacaio.",
       ("block", 5), ("summon", 1)),
    # Putrefacao: veneno e estados
    _c("cm_baforada", "Baforada Podre", "capimaga", "Putrefação", 1, "Ataque",
       "Aplica 5 de Veneno.",
       ("poison", 5, "enemy")),
    _c("cm_pus", "Pus Endurecido", "capimaga", "Putrefação", 1, "Defesa",
       "Ganha 4 de Defesa. Aplica 2 de Veneno.",
       ("block", 4), ("poison", 2, "enemy")),
    _c("cm_peste", "Peste Óssea", "capimaga", "Putrefação", 2, "Poder",
       "No fim do seu turno, aplica 2 de Veneno a todos os inimigos.",
       ("power", "peste")),
    _c("cm_contagio", "Contágio", "capimaga", "Putrefação", 1, "Utilidade",
       "Espalha o Veneno do alvo para os outros inimigos. Compra 1 carta.",
       ("spread_poison",), ("draw", 1)),
    _c("cm_mordida", "Mordida Gangrenada", "capimaga", "Putrefação", 1, "Ataque",
       "Causa 6 de dano. Se o alvo está envenenado, invoca 1 lacaio e aplica Fraqueza 1.",
       ("dmg", 6, "enemy"), ("if", "target_poisoned", [("summon", 1), ("weak", 1, "enemy")])),
]

# ------------------------------------------------------------ Brutamontes
BRUTAMONTES = [
    # Suor: gerar Adrenalina de proposito, pagando vida
    _c("bm_peitada", "Peitada", "brutamontes", "Suor", 1, "Ataque",
       "Causa 10 de dano. Perde 2 de vida.",
       ("dmg", 10, "enemy"), ("lose_hp", 2)),
    _c("bm_sanguefrio", "Sangue Frio", "brutamontes", "Suor", 1, "Defesa",
       "Perde 2 de vida. Ganha 9 de Defesa.",
       ("lose_hp", 2), ("block", 9)),
    _c("bm_rugido", "Rugido", "brutamontes", "Suor", 1, "Poder",
       "Sempre que perder vida, ganha 1 de Adrenalina extra.",
       ("power", "rugido")),
    _c("bm_bufo", "Bufo", "brutamontes", "Suor", 0, "Utilidade",
       "Perde 2 de vida. Ganha 2 de Adrenalina. Compra 1 carta.",
       ("lose_hp", 2), ("adren", 2), ("draw", 1)),
    _c("bm_serie", "Mais Uma Série", "brutamontes", "Suor", 1, "Utilidade",
       "Perde 3 de vida. Ganha 1 Ação e 2 de Adrenalina.",
       ("lose_hp", 3), ("action", 1), ("adren", 2)),
    # Estouro: gastar Adrenalina de uma vez
    _c("bm_cabecada", "Cabeçada Final", "brutamontes", "Estouro", 2, "Ataque",
       "Consome até 6 de Adrenalina. Causa 10 de dano, +3 por ponto consumido.",
       ("consume_adren", 6), ("dmg", 10, "enemy"), ("dmg_per_consumed", 3, "enemy")),
    _c("bm_pele", "Pele de Bicho", "brutamontes", "Estouro", 2, "Defesa",
       "Consome até 4 de Adrenalina. Ganha 6 de Defesa, +3 por ponto consumido.",
       ("consume_adren", 4), ("block", 6), ("block_per_consumed", 3)),
    _c("bm_pavio", "Pavio Curto", "brutamontes", "Estouro", 2, "Poder",
       "Sempre que gastar Adrenalina, causa 1 de dano a todos os inimigos por ponto gasto.",
       ("power", "pavio_curto")),
    _c("bm_folego", "Explosão de Fôlego", "brutamontes", "Estouro", 0, "Utilidade",
       "Consome até 2 de Adrenalina. Ganha 1 Ação por ponto consumido.",
       ("consume_adren", 2), ("action_per_consumed", 1)),
    _c("bm_estampido", "Estampido", "brutamontes", "Estouro", 2, "Ataque",
       "Consome até 3 de Adrenalina. Causa 6 de dano a todos, +2 por ponto consumido.",
       ("consume_adren", 3), ("dmg", 6, "all"), ("dmg_per_consumed", 2, "all")),
    # Couro: Adrenalina acumulada, sem gastar
    _c("bm_soco", "Soco de Sobra", "brutamontes", "Couro", 1, "Ataque",
       "Causa 7 de dano, +1 por Adrenalina acumulada (limite 8).",
       ("dmg", 7, "enemy"), ("dmg_per_adren", 1, 8)),
    _c("bm_costado", "Costado", "brutamontes", "Couro", 1, "Defesa",
       "Ganha 6 de Defesa, +1 por Adrenalina acumulada (limite 8).",
       ("block", 6), ("block_per_adren", 1, 8)),
    _c("bm_calo", "Calo", "brutamontes", "Couro", 2, "Poder",
       "No início do seu turno, ganha Defesa igual à metade da Adrenalina acumulada.",
       ("power", "calo")),
    _c("bm_guardado", "Fôlego Guardado", "brutamontes", "Couro", 1, "Utilidade",
       "Compra 2 cartas. Se tem 5+ de Adrenalina, ganha 1 Ação.",
       ("draw", 2), ("if", "adren>=5", [("action", 1)])),
    _c("bm_fincar", "Fincar Pé", "brutamontes", "Couro", 1, "Defesa",
       "Ganha 8 de Defesa. Se tem 5+ de Adrenalina, ganha 1 de Força.",
       ("block", 8), ("if", "adren>=5", [("strength", 1)])),
    # Troco: Retaliacao, ganhar por ser atingida
    _c("bm_cotovelada", "Cotovelada", "brutamontes", "Troco", 1, "Ataque",
       "Causa 6 de dano. Ganha Retaliação 2 por 1 turno.",
       ("dmg", 6, "enemy"), ("retaliation", 2, 1)),
    _c("bm_naofaz", "Não Faz Isso", "brutamontes", "Troco", 1, "Defesa",
       "Ganha Retaliação 4 por 2 turnos.",
       ("retaliation", 4, 2)),
    _c("bm_olho", "Olho por Olho", "brutamontes", "Troco", 2, "Poder",
       "Sempre que perder vida para um ataque, causa 3 de dano ao atacante.",
       ("power", "olho_por_olho")),
    _c("bm_provocar", "Provocar", "brutamontes", "Troco", 0, "Utilidade",
       "Ganha 4 de Defesa e Retaliação 2 por 1 turno.",
       ("block", 4), ("retaliation", 2, 1)),
    _c("bm_queixo", "Queixo de Ferro", "brutamontes", "Troco", 2, "Defesa",
       "Ganha 8 de Defesa e Retaliação 3 por 2 turnos.",
       ("block", 8), ("retaliation", 3, 2)),
]

# ----------------------------------------------------------------- Ligeira
LIGEIRA = [
    # Corrente: esticar o turno com custo 0 e compra
    _c("lg_passo", "Passo Curto", "ligeira", "Corrente", 0, "Ataque",
       "Causa 2 de dano. Compra 1 carta.",
       ("dmg", 2, "enemy"), ("draw", 1)),
    _c("lg_rolamento", "Rolamento", "ligeira", "Corrente", 0, "Defesa",
       "Ganha 3 de Defesa. Compra 1 carta.",
       ("block", 3), ("draw", 1)),
    _c("lg_segundo", "Segundo Fôlego", "ligeira", "Corrente", 1, "Poder",
       "Sempre que jogar a 3ª carta do turno, compra 1 carta.",
       ("power", "segundo_folego")),
    _c("lg_respiro", "Respiro", "ligeira", "Corrente", 0, "Utilidade",
       "Compra 1 carta. Se já jogou 3 cartas neste turno, ganha 1 Ação.",
       ("draw", 1), ("if", "impulso>=3", [("action", 1)])),
    _c("lg_cambalhota", "Cambalhota", "ligeira", "Corrente", 1, "Ataque",
       "Causa 4 de dano duas vezes.",
       ("dmg", 4, "enemy"), ("dmg", 4, "enemy")),
    # Estocada: finalizador que escala com o Impulso
    _c("lg_pontocego", "Ponto Cego", "ligeira", "Estocada", 1, "Ataque",
       "Causa 3 de dano por carta jogada antes desta neste turno (limite 5).",
       ("dmg_per_impulso", 3, 5)),
    _c("lg_finta", "Finta", "ligeira", "Estocada", 1, "Defesa",
       "Ganha 4 de Defesa, +2 por carta jogada antes desta neste turno (limite 3).",
       ("block", 4), ("block_per_impulso", 2, 3)),
    _c("lg_vista", "Golpe de Vista", "ligeira", "Estocada", 2, "Poder",
       "Sempre que jogar a 4ª carta do turno, causa 6 de dano ao alvo.",
       ("power", "golpe_de_vista")),
    _c("lg_rasteira", "Rasteira", "ligeira", "Estocada", 1, "Utilidade",
       "Aplica Fragilidade 2. Se já jogou 3 cartas neste turno, compra 1 carta.",
       ("frail", 2, "enemy"), ("if", "impulso>=3", [("draw", 1)])),
    _c("lg_dentada", "Dentada Rápida", "ligeira", "Estocada", 1, "Ataque",
       "Causa 6 de dano. Se já jogou 2 cartas neste turno, causa 4 a mais.",
       ("dmg", 6, "enemy"), ("if", "impulso>=2", [("dmg_plus", 4, "enemy")])),
    # Fumaca: Evasao e negacao de golpe
    _c("lg_bote", "Bote da Névoa", "ligeira", "Fumaça", 1, "Ataque",
       "Causa 5 de dano. Se tem Evasão, causa 5 a mais.",
       ("dmg", 5, "enemy"), ("if", "evasion>=1", [("dmg_plus", 5, "enemy")])),
    _c("lg_lama", "Banho de Lama", "ligeira", "Fumaça", 1, "Defesa",
       "Ganha 1 de Evasão, ou 2 se já jogou 3 cartas neste turno.",
       ("evasion", 1), ("if", "impulso>=3", [("evasion", 1)])),
    _c("lg_rastro", "Rastro de Lama", "ligeira", "Fumaça", 1, "Poder",
       "Sempre que a Evasão anular um ataque, compra 1 carta.",
       ("power", "rastro")),
    _c("lg_truque", "Truque de Fumaça", "ligeira", "Fumaça", 1, "Utilidade",
       "Compra 1 carta. Se tem Evasão, ganha 1 Ação.",
       ("draw", 1), ("if", "evasion>=1", [("action", 1)])),
    _c("lg_cortina", "Cortina de Lama", "ligeira", "Fumaça", 2, "Defesa",
       "Ganha 1 de Evasão. Aplica Fraqueza 2 a todos os inimigos.",
       ("evasion", 1), ("weak", 2, "all")),
    # Contrabando: mexer na mao e no descarte
    _c("lg_golpebaixo", "Golpe Baixo", "ligeira", "Contrabando", 1, "Ataque",
       "Causa 5 de dano. A próxima carta jogada neste turno custa 0.",
       ("dmg", 5, "enemy"), ("next_free",)),
    _c("lg_troca", "Troca Rápida", "ligeira", "Contrabando", 1, "Defesa",
       "Ganha 4 de Defesa. Descarta a mão e compra o mesmo número de cartas.",
       ("block", 4), ("redraw_hand",)),
    _c("lg_bolso", "Bolso Fundo", "ligeira", "Contrabando", 1, "Poder",
       "No fim do seu turno, guarda 1 carta aleatória da mão em vez de descartá-la.",
       ("power", "bolso_fundo")),
    _c("lg_pega", "Pega de Volta", "ligeira", "Contrabando", 1, "Utilidade",
       "Devolve à mão a última carta jogada neste turno (não alcança carta de custo 0).",
       ("return_last",)),
    _c("lg_marcado", "Baralho Marcado", "ligeira", "Contrabando", 1, "Utilidade",
       "Compra 1 carta. A próxima carta jogada neste turno custa 0.",
       ("draw", 1), ("next_free",)),
]

POOLS = {
    "capimaga": CAPIMAGA,
    "brutamontes": BRUTAMONTES,
    "ligeira": LIGEIRA,
}

BY_ID = {c.id: c for pool in POOLS.values() for c in pool}

# nome visivel de cada poder, usado na HUD
POWER_NAMES = {
    c.effects[0][1]: c.name for pool in POOLS.values() for c in pool if c.kind == "Poder"
}
