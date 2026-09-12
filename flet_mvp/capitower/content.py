"""Classes, inimigos, chefes, eventos e modificadores do MVP.

Numeros sao ponto de partida para playtest (ver docs/01-gdd.md).
"""

from dataclasses import dataclass, field

# ------------------------------------------------------------------ classes

CLASSES = {
    "capimaga": {
        "name": "Capimaga",
        "image": "capimaga.png",
        "tagline": "Capivara necromante. A força dela mora no campo.",
        "mechanic": "Lacaios: contadores que ficam ao seu lado. No fim do seu turno, cada lacaio causa 2 de dano a um inimigo aleatório. Zeram ao fim do combate.",
        "ability": "Legião",
        "ability_text": {
            1: "Começa o combate com 1 lacaio",
            2: "+1 lacaio inicial (2)",
            3: "+1 lacaio inicial (3)",
            4: "+1 lacaio inicial (4)",
            5: "Ao invocar, 20% de chance de invocar 1 a mais",
            6: "+1 lacaio inicial (5)",
            7: "+1 lacaio inicial (6)",
            8: "+1 lacaio inicial (7)",
            9: "Uma vez por combate, ao ficar sem lacaios, invoca 2",
            10: "Começa o combate com o dobro de lacaios",
        },
        "resource": "Lacaios",
    },
    "brutamontes": {
        "name": "Brutamontes",
        "image": "brutamontes.png",
        "tagline": "Nunca chegou perto do poço. Tudo que tem veio de teimosia.",
        "mechanic": "Adrenalina: toda vez que perde vida (dano que passou pela Defesa), ganha 1. Cartas gastam ou escalam com ela. Zera ao fim do combate.",
        "ability": "Casca Grossa",
        "ability_text": {
            1: "Começa cada combate com 2 de Adrenalina",
            2: "+1 de Adrenalina inicial (3)",
            3: "+1 de Adrenalina inicial (4)",
            4: "A primeira vez que perde vida no combate rende 2",
            5: "Ganha 1 também quando a Defesa absorve um ataque inteiro",
            6: "+1 de Adrenalina inicial (5)",
            7: "Teto de Adrenalina sobe de 10 para 15",
            8: "+1 de Adrenalina inicial (6)",
            9: "Ao cair a metade da vida, ganha 3 na hora (1x por combate)",
            10: "Toda Adrenalina ganha é dobrada",
        },
        "resource": "Adrenalina",
    },
    "ligeira": {
        "name": "Ligeira",
        "image": "ligeira.png",
        "tagline": "Pequena, encharcada e impossível de segurar.",
        "mechanic": "Impulso: conta as cartas jogadas neste turno. Zera no fim de todo turno. Cartas consultam quantas vieram antes.",
        "ability": "Ligeireza",
        "ability_text": {
            1: "Ao jogar a 5ª carta do turno, ganha +1 Ação",
            2: "Passa a ativar na 4ª carta",
            3: "A ativação também compra 1 carta",
            4: "Passa a ativar na 3ª carta",
            5: "Começa cada combate com +1 Ação no primeiro turno",
            6: "A ativação passa a dar +2 Ação",
            7: "Passa a ativar na 2ª carta",
            8: "A ativação compra 2 cartas",
            9: "Ativa duas vezes por turno (a 2ª exige o dobro)",
            10: "A primeira carta de cada turno custa 0",
        },
        "resource": "Impulso",
    },
}

MAX_LEVEL = 10
START_HP = 80
ACTIONS_PER_TURN = 3
HAND_SIZE = 5
MINION_CAP = 10
MINION_BITE = 2  # dano de cada lacaio no fim do turno

# ------------------------------------------------------------- modificadores

MODIFIERS = {
    "casco_duro": ("Casco Duro", "+1 de Defesa toda vez que ganhar Defesa"),
    "musculo": ("Músculo Teimoso", "+1 de Força permanente"),
    "folego": ("Fôlego", "+5 de HP máximo, e cura os 5 na hora"),
    "largada": ("Largada", "+1 Ação no primeiro turno de cada combate"),
    "mao_firme": ("Mão Firme", "Compra +1 carta no primeiro turno de cada combate"),
}

# ----------------------------------------------------------------- inimigos


@dataclass(frozen=True)
class EnemyDef:
    id: str
    name: str
    hp: int
    # cada turno e uma lista de acoes (tipo, valor[, vezes])
    pattern: tuple
    flags: dict = field(default_factory=dict)
    note: str = ""


def _e(id, name, hp, pattern, flags=None, note=""):
    return EnemyDef(id, name, hp, tuple(tuple(t) for t in pattern), flags or {}, note)


# acoes: ("attack", dano, vezes) ("block", n) ("strength", n) ("strength_all", n)
#        ("weak", turnos) ("frail", turnos) ("poison", n) ("heal", n)
#        ("heal_all", n) ("steal", 1) ("charge", 0)
# flags: "fixed_start" nao sorteia a acao inicial (padrao que carrega um golpe).

ENEMIES = {e.id: e for e in [
    # Bloco 1: O Poco
    _e("capivarinha", "Capivarinha Encharcada", 8, [[("attack", 3)], [("attack", 4)]]),
    _e("sapo", "Sapo Musculoso", 26, [[("block", 6)], [("attack", 8)]]),
    _e("rato", "Rato de Academia", 18, [[("attack", 3, 2)], [("steal", 1)], [("attack", 4, 2)]],
       note="rouba Ação"),
    # Bloco 2: A Academia
    _e("halter", "Halter Vivo", 50, [[("attack", 6)], [("block", 8), ("attack", 4)]]),
    _e("spinning", "Capivara do Spinning", 26, [[("attack", 4, 2)], [("attack", 3, 2)], [("block", 5), ("attack", 4)]]),
    _e("personal", "Personal Trainer", 28, [[("strength_all", 1)], [("attack", 7)]]),
    # Bloco 3: O Laboratorio
    _e("frasco", "Frasco Ambulante", 38, [[("poison", 3)], [("attack", 8)], [("poison", 4), ("attack", 4)]]),
    _e("experimental", "Capivara Experimental", 48, [[("attack", 10)], [("block", 10)], [("attack", 6, 2)], [("weak", 2)]],
       flags={"shift": True}, note="muda de padrão ao levar dano"),
    _e("bolha", "Bolha de Soro", 45, [[("attack", 7)], [("block", 12)]],
       flags={"reflect": 0.25}, note="reflete 25% do dano recebido"),
    # Bloco 4: O Refeitorio
    _e("marmita", "Capivara de Marmita", 60, [[("attack", 11)], [("heal", 8), ("block", 6)]],
       note="se cura"),
    _e("garcom", "Garçom Bombado", 95, [[("charge", 0)], [("charge", 0)], [("attack", 30)]],
       flags={"fixed_start": True}, note="golpe devastador em 2 turnos"),
    _e("sobremesa", "Sobremesa Viva", 42, [[("weak", 2), ("attack", 5)], [("attack", 12)]]),
    # Bloco 5: O Jardim Suspenso
    _e("guarda", "Guarda de Avental", 75, [[("block", 12), ("attack", 8)], [("attack", 14)]],
       flags={"thorns": 3}, note="contra ataca com 3"),
    _e("jardineira", "Jardineira Furiosa", 65, [[("attack", 8)], [("attack", 10)]],
       flags={"ramp": 2}, note="+2 de Força por turno"),
    _e("vaso", "Vaso Sentinela", 40, [[("heal_all", 6)], [("strength_all", 2)]],
       note="buffa e cura a sala"),
    # Elites
    _e("elite1", "Capivara de Pulso", 48, [[("attack", 4, 2)], [("block", 8), ("attack", 5)], [("attack", 10)]],
       flags={"elite": True}),
    _e("elite2", "Instrutora de Cross", 70, [[("attack", 5, 2)], [("strength", 1)], [("attack", 8, 2)]],
       flags={"elite": True}),
    _e("elite3", "Cobaia Alfa", 100, [[("poison", 5)], [("frail", 2), ("attack", 8)], [("attack", 16)]],
       flags={"elite": True}),
    _e("elite4", "Chef de Cozinha", 130, [[("attack", 14)], [("heal", 12), ("block", 10)], [("attack", 18)]],
       flags={"elite": True}),
    _e("elite5", "Capitã da Guarda", 150, [[("block", 15), ("attack", 12)], [("attack", 10, 2)], [("strength", 3)]],
       flags={"elite": True, "thorns": 4}),
    # Chefes
    _e("dorival", "Dorival Supino", 75, [[("block", 10), ("charge", 0)], [("attack", 16)]],
       flags={"boss": True}, note="carrega e golpeia."),
    _e("marlene", "Marlene Cardio", 120, [[("attack", 5, 2)], [("attack", 4, 2), ("weak", 1)], [("block", 8), ("attack", 6, 2)]],
       flags={"boss": True}, note="age duas vezes por turno"),
    _e("helio", "Professor Hélio Whey", 190, [[("weak", 2), ("frail", 2)], [("attack", 14)], [("strength", 3), ("block", 10)], [("poison", 6), ("attack", 8)]],
       flags={"boss": True}, note="estados e buff próprio"),
    _e("gemeo_a", "Gêmeo Rosca (Esq.)", 120, [[("attack", 11)], [("block", 8), ("attack", 6)]],
       flags={"boss": True, "twin": 5}, note="o irmão herda +5 de Força"),
    _e("gemeo_b", "Gêmeo Rosca (Dir.)", 120, [[("block", 8), ("attack", 6)], [("attack", 11)]],
       flags={"boss": True, "twin": 5}, note="o irmão herda +5 de Força"),
    _e("capitolino", "Sargento Capitolino", 260, [[("attack", 16)], [("attack", 10), ("weak", 1)], [("attack", 20)]],
       flags={"boss": True, "block_each_turn": 12}, note="ganha 12 de Defesa todo turno"),
    _e("gertrudes", "Soberana Gertrudes", 340, [[("block", 14), ("charge", 0)], [("attack", 26)]],
       flags={"boss": True, "phases": True}, note="três fases"),
]}

# fases da Gertrudes: (fracao de hp minima, padrao)
GERTRUDES_PHASES = [
    (0.66, (( ("block", 14), ("charge", 0) ), ( ("attack", 26), ))),
    (0.33, (( ("attack", 7, 3), ), ( ("attack", 6, 2), ("weak", 1) ), ( ("strength", 2), ("block", 10) ))),
    (0.0,  (( ("frail", 2), ("poison", 6) ), ( ("attack", 18), ), ( ("heal", 15), ("block", 20) ))),
]

# --------------------------------------------------------------------- torre

BLOCKS = [
    {"name": "O Poço", "desc": "Onde tudo começou. Úmido, verde, cheirando a suplemento vencido.",
     "combats": [["capivarinha", "capivarinha", "capivarinha"], ["sapo"], ["rato", "capivarinha"], ["sapo", "capivarinha"], ["rato"]],
     "elite": ["elite1"], "boss": ["dorival"]},
    {"name": "A Academia", "desc": "Ferro por todo lado. Inimigos rápidos, muito barulho.",
     "combats": [["halter"], ["spinning", "spinning"], ["personal", "spinning"], ["halter", "personal"], ["spinning", "capivarinha", "capivarinha"]],
     "elite": ["elite2"], "boss": ["marlene"]},
    {"name": "O Laboratório", "desc": "Onde o esteroide vira ciência. Efeitos estranhos.",
     "combats": [["frasco", "frasco"], ["experimental"], ["bolha"], ["frasco", "bolha"], ["experimental", "frasco"]],
     "elite": ["elite3"], "boss": ["helio"]},
    {"name": "O Refeitório", "desc": "Buffet infinito. Inimigos gordos, lentos, com HP alto.",
     "combats": [["marmita"], ["sobremesa", "sobremesa"], ["garcom"], ["marmita", "sobremesa"], ["garcom", "sobremesa"]],
     "elite": ["elite4"], "boss": ["gemeo_a", "gemeo_b"]},
    {"name": "O Jardim Suspenso", "desc": "Flores, ordem e violência. A guarda pessoal da Soberana.",
     "combats": [["guarda"], ["jardineira"], ["vaso", "guarda"], ["jardineira", "vaso"], ["guarda", "guarda"]],
     "elite": ["elite5"], "boss": ["capitolino"]},
]

FINAL_BOSS = ["gertrudes"]

# condicoes do desafio opcional
CHALLENGES = {
    "forca": "Os inimigos começam com +2 de Força.",
    "pressa": "A partir do 6º turno, os inimigos ganham +3 de Força por turno.",
}

# ------------------------------------------------------------------- eventos

EVENTS = [
    {
        "id": "bebedouro",
        "title": "O Bebedouro",
        "text": "Uma fonte de água suspeita borbulhando sozinha.",
        "choices": [
            ("Beber: cura 20% do HP máximo, 50% de chance de começar o próximo combate com Fraqueza.", "heal20_risk"),
            ("Encher o cantil: cura 10% agora e 10% depois do próximo combate.", "heal10_later"),
            ("Seguir: nada acontece.", "nothing"),
        ],
    },
    {
        "id": "halteres",
        "title": "A Halteres Perdida",
        "text": "Um halter esquecido no corredor, pesado demais para carregar.",
        "choices": [
            ("Levantar: perde 8 de vida, ganha +1 de Força permanente na run.", "strength_for_hp"),
            ("Deixar: nada acontece.", "nothing"),
        ],
    },
    {
        "id": "vestiario",
        "title": "O Vestiário",
        "text": "Armários abertos, cheiro forte, alguém esqueceu alguma coisa.",
        "choices": [
            ("Vasculhar: ganha uma carta aleatória da sua classe até o próximo chefe.", "temp_card"),
            ("Descansar ali mesmo: cura 15% do HP máximo.", "heal15"),
        ],
    },
]
