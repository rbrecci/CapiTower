"""Estado de uma run: classe, deck, HP, torre e progressao."""

import random

from . import content
from .cards import POOLS, CardDef


class Run:
    def __init__(self, cls_id: str, seed: int | None = None):
        self.seed = seed if seed is not None else random.randrange(1_000_000)
        self.rng = random.Random(self.seed)
        self.cls_id = cls_id
        self.cls = content.CLASSES[cls_id]
        self.pool = POOLS[cls_id]

        self.max_hp = content.START_HP
        self.hp = self.max_hp
        self.level = 1
        self.deck: list[CardDef] = []
        self.temp_cards: list[CardDef] = []
        self.modifiers: list[str] = []
        self.perm_strength = 0

        # efeitos pendentes de eventos
        self.heal_after_combat = 0
        self.weak_next_combat = 0

        self.floor = 0  # 0 = ainda nao entrou; 1..51
        self.floors = self._generate_tower()
        self.bosses_defeated = 0
        self.victory = False
        self.dead = False

        # sorteio inicial: 5 distintas, com pelo menos 2 de Ataque para o deck
        # sempre ter como fechar um combate
        self.starting: list[CardDef] = self._draw_starting()
        self.rerolled = False

    # --------------------------------------------------------------- deck
    MIN_ATTACKS = 2

    def _draw_starting(self) -> list[CardDef]:
        while True:
            pick = self.rng.sample(self.pool, 5)
            if sum(c.kind == "Ataque" for c in pick) >= self.MIN_ATTACKS:
                return pick

    def reroll(self, idx: int):
        if self.rerolled:
            return
        rest = [c for c in self.pool if c not in self.starting]
        attacks_left = sum(c.kind == "Ataque" for i, c in enumerate(self.starting) if i != idx)
        if attacks_left < self.MIN_ATTACKS:
            rest = [c for c in rest if c.kind == "Ataque"]
        self.starting[idx] = self.rng.choice(rest)
        self.rerolled = True

    def build_starting_deck(self):
        self.deck = []
        for c in self.starting:
            self.deck += [c, c]

    def full_deck(self) -> list[CardDef]:
        return self.deck + self.temp_cards

    def reward_options(self, n=3) -> list[CardDef]:
        have = {c.id for c in self.deck}
        rest = [c for c in self.pool if c.id not in have]
        self.rng.shuffle(rest)
        return rest[:n]

    def add_card(self, card: CardDef):
        self.deck.append(card)

    def level_up(self):
        if self.level < content.MAX_LEVEL:
            self.level += 1

    def random_temp_card(self) -> CardDef:
        return self.rng.choice(self.pool)

    # -------------------------------------------------------------- torre
    def _generate_tower(self) -> list[dict]:
        floors = []
        for bi, block in enumerate(content.BLOCKS):
            combats = list(block["combats"])
            self.rng.shuffle(combats)
            entries = [{"type": "combat", "enemies": c} for c in combats]
            entries.append({"type": "elite", "enemies": block["elite"]})
            entries.append({"type": "event", "event": self.rng.choice(content.EVENTS)})
            entries.append({"type": "rest"})
            entries.append({"type": "challenge",
                            "enemies": self.rng.choice(block["combats"]),
                            "challenge": self.rng.choice(list(content.CHALLENGES))})
            self.rng.shuffle(entries)
            # elite sempre entre as posicoes 3 e 8 do bloco
            ei = next(i for i, e in enumerate(entries) if e["type"] == "elite")
            target = self.rng.randint(2, 7)
            entries[ei], entries[target] = entries[target], entries[ei]
            entries.append({"type": "boss", "enemies": block["boss"]})
            for e in entries:
                e["block"] = bi
            floors += entries
        floors.append({"type": "final", "enemies": content.FINAL_BOSS, "block": 4})
        return floors

    def current(self) -> dict:
        return self.floors[self.floor - 1]

    def block_info(self) -> dict:
        return content.BLOCKS[self.current()["block"]]

    def advance(self):
        self.floor += 1

    def is_last_floor(self) -> bool:
        return self.floor >= len(self.floors)

    # --------------------------------------------------------------- vida
    def heal(self, n: int):
        self.hp = min(self.max_hp, self.hp + n)

    def heal_pct(self, pct: float):
        self.heal(int(self.max_hp * pct))

    def add_modifier(self, key: str):
        self.modifiers.append(key)
        if key == "folego":
            self.max_hp += 5
            self.heal(5)

    def modifier_options(self, n=2) -> list[str]:
        rest = [m for m in content.MODIFIERS if m not in self.modifiers]
        self.rng.shuffle(rest)
        return rest[:n]

    # ---------------------------------------------------------------- meta
    def meta_points(self) -> int:
        return self.floor + self.bosses_defeated * 10 + (50 if self.victory else 0)
