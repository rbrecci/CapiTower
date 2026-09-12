"""Motor de combate por turnos.

Roda inteiramente no cliente (D04). A UI so chama play(), end_turn() e
select_target(), e le o estado publico para desenhar a tela.
"""

import math
import random

from . import content
from .cards import CardDef
from .content import EnemyDef
from .run import Run


class Enemy:
    def __init__(self, edef: EnemyDef, rng: random.Random):
        self.edef = edef
        self.name = edef.name
        self.max_hp = edef.hp
        self.hp = edef.hp
        self.block = 0
        self.strength = 0
        self.weak = 0
        self.frail = 0
        self.poison = 0
        self.flags = dict(edef.flags)
        self.pattern = edef.pattern
        self.idx = rng.randrange(len(self.pattern)) if len(self.pattern) > 1 and not self.is_boss else 0
        self.phase = 0

    @property
    def alive(self):
        return self.hp > 0

    @property
    def is_boss(self):
        return self.flags.get("boss", False)

    @property
    def intent(self):
        return self.pattern[self.idx % len(self.pattern)]

    def intent_parts(self) -> list[tuple[str, str, str]]:
        """Intenção do próximo turno como (tipo, valor curto, descrição)."""
        parts = []
        for act in self.intent:
            kind, val = act[0], act[1]
            times = act[2] if len(act) > 2 else 1
            if kind == "attack":
                dmg = max(0, val + self.strength)
                if self.weak:
                    dmg = math.floor(dmg * 0.75)
                short = f"{dmg}" + (f"×{times}" if times > 1 else "")
                parts.append(("attack", short, f"Ataca {dmg}" + (f" {times} vezes" if times > 1 else "")))
            elif kind == "block":
                parts.append(("block", str(val), f"Ganha {val} de Defesa"))
            elif kind == "strength":
                parts.append(("strength", f"+{val}", f"Ganha {val} de Força"))
            elif kind == "strength_all":
                parts.append(("strength_all", f"+{val}", f"Toda a sala ganha {val} de Força"))
            elif kind == "weak":
                parts.append(("weak", str(val), f"Aplica Fraqueza {val} em você"))
            elif kind == "frail":
                parts.append(("frail", str(val), f"Aplica Fragilidade {val} em você"))
            elif kind == "poison":
                parts.append(("poison", str(val), f"Aplica Veneno {val} em você"))
            elif kind == "heal":
                parts.append(("heal", str(val), f"Cura {val}"))
            elif kind == "heal_all":
                parts.append(("heal_all", str(val), f"Cura a sala em {val}"))
            elif kind == "steal":
                parts.append(("steal", "-1", "Rouba 1 Ação do seu próximo turno"))
            elif kind == "charge":
                parts.append(("charge", "", "Carregando o próximo golpe"))
        return parts

    def intent_label(self) -> str:
        return " + ".join(p[2] for p in self.intent_parts())


class Combat:
    def __init__(self, run: Run, enemy_ids: list[str], challenge: str | None = None):
        self.run = run
        self.rng = random.Random(run.rng.randrange(1_000_000))
        self.cls = run.cls_id
        self.level = run.level
        self.challenge = challenge
        self.log: list[str] = []
        self.status = "ongoing"  # ongoing | won | lost
        self.turn = 0

        self.enemies = [Enemy(content.ENEMIES[i], self.rng) for i in enemy_ids]
        self.target = 0

        # pilhas
        self.draw_pile = list(run.full_deck())
        self.rng.shuffle(self.draw_pile)
        self.hand: list[CardDef] = []
        self.discard: list[CardDef] = []
        self.powers: list[str] = []

        # estado do jogador dentro do combate
        self.block = 0
        self.keep_block = False
        self.actions = 0
        self.strength = run.perm_strength + (1 if "musculo" in run.modifiers else 0)
        self.weak = run.weak_next_combat
        run.weak_next_combat = 0
        self.frail = 0
        self.poison = 0
        self.retaliation = 0
        self.retaliation_turns = 0
        self.evasion = 0
        self.steal_next = 0

        # recursos de classe
        self.minions = 0
        self.adrenaline = 0
        self.adren_cap = 15 if (self.cls == "brutamontes" and self.level >= 7) else 10
        self.played_this_turn = 0
        self.last_played: CardDef | None = None
        self.next_free = False
        self.ligeireza_triggers = 0
        self.first_loss_done = False
        self.half_hp_done = False
        self.legiao9_done = False

        self._setup_class()
        if challenge == "forca":
            for e in self.enemies:
                e.strength += 2
        self._start_player_turn()

    # ------------------------------------------------------------ helpers
    def say(self, msg: str):
        self.log.append(msg)
        if len(self.log) > 60:
            self.log = self.log[-60:]

    @property
    def hp(self):
        return self.run.hp

    @hp.setter
    def hp(self, v):
        self.run.hp = v

    @property
    def max_hp(self):
        return self.run.max_hp

    def living(self) -> list[Enemy]:
        return [e for e in self.enemies if e.alive]

    def resource_label(self) -> str:
        if self.cls == "capimaga":
            return f"Lacaios {self.minions}/{content.MINION_CAP}"
        if self.cls == "brutamontes":
            return f"Adrenalina {self.adrenaline}/{self.adren_cap}"
        return f"Impulso {self.played_this_turn}"

    def _setup_class(self):
        lv = self.level
        if self.cls == "capimaga":
            table = {1: 1, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 6, 8: 7, 9: 7, 10: 7}
            n = table[lv] * (2 if lv >= 10 else 1)
            self.minions = min(content.MINION_CAP, n)
            self.say(f"Legião: começa com {self.minions} lacaio(s).")
        elif self.cls == "brutamontes":
            table = {1: 2, 2: 3, 3: 4, 4: 4, 5: 4, 6: 5, 7: 5, 8: 6, 9: 6, 10: 6}
            self.adrenaline = table[lv]
            self.say(f"Casca Grossa: começa com {self.adrenaline} de Adrenalina.")

    # ------------------------------------------------------- turno jogador
    def _start_player_turn(self):
        self.turn += 1
        if not self.keep_block:
            self.block = 0
        self.keep_block = False
        if "calo" in self.powers and self.adrenaline >= 2:
            self.gain_block(self.adrenaline // 2)
            self.say(f"Calo: +{self.adrenaline // 2} de Defesa.")
        if "vala_comum" in self.powers:
            self.summon(1)
        self.actions = content.ACTIONS_PER_TURN - self.steal_next
        self.steal_next = 0
        self.played_this_turn = 0
        self.last_played = None
        self.next_free = False
        self.ligeireza_triggers = 0
        if self.weak:
            self.weak -= 1
        if self.frail:
            self.frail -= 1
        if self.retaliation_turns:
            self.retaliation_turns -= 1
            if self.retaliation_turns == 0:
                self.retaliation = 0
        draw = content.HAND_SIZE
        if self.turn == 1:
            if "largada" in self.run.modifiers:
                self.actions += 1
            if "mao_firme" in self.run.modifiers:
                draw += 1
            if self.cls == "ligeira" and self.level >= 5:
                self.actions += 1
        self.draw_cards(draw)
        if self.status == "ongoing":
            self.say(f"--- Turno {self.turn} ---")

    def draw_cards(self, n: int):
        for _ in range(n):
            if not self.draw_pile:
                if not self.discard:
                    return
                self.draw_pile = self.discard
                self.discard = []
                self.rng.shuffle(self.draw_pile)
            self.hand.append(self.draw_pile.pop())

    def cost_of(self, card: CardDef) -> int:
        if self.next_free:
            return 0
        if self.cls == "ligeira" and self.level >= 10 and self.played_this_turn == 0:
            return 0
        return card.cost

    def can_play(self, card: CardDef) -> bool:
        return self.status == "ongoing" and self.actions >= self.cost_of(card)

    def select_target(self, idx: int):
        if 0 <= idx < len(self.enemies) and self.enemies[idx].alive:
            self.target = idx

    def _target(self) -> Enemy | None:
        if self.enemies[self.target].alive:
            return self.enemies[self.target]
        alive = self.living()
        if alive:
            self.target = self.enemies.index(alive[0])
            return alive[0]
        return None

    def play(self, hand_index: int):
        if self.status != "ongoing" or not (0 <= hand_index < len(self.hand)):
            return
        card = self.hand[hand_index]
        cost = self.cost_of(card)
        if self.actions < cost:
            self.say("Ação insuficiente.")
            return
        self.actions -= cost
        self.next_free = False
        self.hand.pop(hand_index)
        ctx = {"consumed": 0, "impulso": self.played_this_turn}
        self.say(f"Joga {card.name}.")
        self._resolve(card.effects, ctx)
        if card.kind == "Poder":
            pass  # ja registrado em self.powers
        else:
            self.discard.append(card)
        self.played_this_turn += 1
        if card.cost > 0 and not any(e[0] == "return_last" for e in card.effects):
            self.last_played = card
        if "segundo_folego" in self.powers and self.played_this_turn == 3:
            self.draw_cards(1)
            self.say("Segundo Fôlego: compra 1.")
        if "golpe_de_vista" in self.powers and self.played_this_turn == 4 and self.living():
            self.say("Golpe de Vista!")
            self._hit(6, "enemy")
        self._ligeireza_check()
        self._check_end()

    def _ligeireza_check(self):
        if self.cls != "ligeira":
            return
        lv = self.level
        threshold = 5
        if lv >= 2:
            threshold = 4
        if lv >= 4:
            threshold = 3
        if lv >= 7:
            threshold = 2
        max_triggers = 2 if lv >= 9 else 1
        if self.ligeireza_triggers >= max_triggers:
            return
        need = threshold * (self.ligeireza_triggers + 1)
        if self.played_this_turn >= need:
            self.ligeireza_triggers += 1
            gain = 2 if lv >= 6 else 1
            self.actions += gain
            msg = f"Ligeireza: +{gain} Ação"
            if lv >= 8:
                self.draw_cards(2)
                msg += ", compra 2"
            elif lv >= 3:
                self.draw_cards(1)
                msg += ", compra 1"
            self.say(msg + ".")

    # ------------------------------------------------------- resolvedor
    def check_condition(self, cond: str, ctx: dict) -> bool:
        if cond == "target_poisoned":
            t = self._target()
            return bool(t and t.poison > 0)
        key, _, val = cond.partition(">=")
        val = int(val)
        if key == "consumed":
            return ctx["consumed"] >= val
        if key == "impulso":
            return ctx["impulso"] >= val
        if key == "adren":
            return self.adrenaline >= val
        if key == "evasion":
            return self.evasion >= val
        return False

    def _resolve(self, effects, ctx: dict):
        for eff in effects:
            kind = eff[0]
            if kind == "dmg":
                self._hit(eff[1], eff[2])
            elif kind == "block":
                self.gain_block(eff[1])
            elif kind == "draw":
                self.draw_cards(eff[1])
            elif kind == "action":
                self.actions += eff[1]
            elif kind == "lose_hp":
                self._lose_hp(eff[1], source=None, from_attack=False)
            elif kind == "poison":
                for e in self._targets(eff[2]):
                    e.poison += eff[1]
            elif kind == "weak":
                for e in self._targets(eff[2]):
                    e.weak += eff[1]
            elif kind == "frail":
                for e in self._targets(eff[2]):
                    e.frail += eff[1]
            elif kind == "strength":
                self.strength += eff[1]
                self.say(f"+{eff[1]} de Força.")
            elif kind == "summon":
                self.summon(eff[1])
            elif kind == "consume":
                n = min(eff[1], self.minions)
                self.minions -= n
                ctx["consumed"] = n
                if n:
                    self.say(f"Consome {n} lacaio(s).")
                    if "banquete" in self.powers:
                        self.draw_cards(1)
                        self.say("Banquete: compra 1.")
                self._legiao9_check()
            elif kind == "dmg_per_consumed":
                if ctx["consumed"]:
                    self._hit(eff[1] * ctx["consumed"], eff[2])
            elif kind == "dmg_per_minion":
                if self.minions:
                    self._hit(eff[1] * self.minions, eff[2])
            elif kind == "block_per_minion":
                self.gain_block(min(eff[2], eff[1] * self.minions))
            elif kind == "dmg_block":
                if self.block:
                    self._hit(min(eff[1], self.block), "enemy")
                else:
                    self.say("Sem Defesa para bater. Nada acontece.")
            elif kind == "keep_block":
                self.keep_block = True
                self.say("A Defesa fica para o próximo turno.")
            elif kind == "spread_poison":
                t = self._target()
                if t and t.poison:
                    for e in self.living():
                        if e is not t and e.poison < t.poison:
                            e.poison = t.poison
                    self.say(f"Contágio: Veneno {t.poison} se espalha.")
                else:
                    self.say("O alvo não está envenenado. Nada para espalhar.")
            elif kind == "adren":
                self.gain_adrenaline(eff[1])
            elif kind == "consume_adren":
                n = min(eff[1], self.adrenaline)
                self.adrenaline -= n
                ctx["consumed"] = n
                if n:
                    self.say(f"Gasta {n} de Adrenalina.")
                    if "pavio_curto" in self.powers:
                        for e in self.living():
                            self._damage_enemy(e, n, "Pavio Curto")
            elif kind == "dmg_per_adren":
                self._hit(min(eff[2], eff[1] * self.adrenaline), "enemy")
            elif kind == "block_per_adren":
                self.gain_block(min(eff[2], eff[1] * self.adrenaline))
            elif kind == "block_per_consumed":
                self.gain_block(eff[1] * ctx["consumed"])
            elif kind == "action_per_consumed":
                if ctx["consumed"]:
                    self.actions += eff[1] * ctx["consumed"]
            elif kind == "block_per_impulso":
                self.gain_block(eff[1] * min(eff[2], ctx["impulso"]))
            elif kind == "retaliation":
                self.retaliation = max(self.retaliation, eff[1])
                self.retaliation_turns = max(self.retaliation_turns, eff[2] + 1)
                self.say(f"Retaliação {eff[1]}.")
            elif kind == "evasion":
                self.evasion += eff[1]
                self.say(f"+{eff[1]} de Evasão.")
            elif kind == "dmg_per_impulso":
                n = min(eff[2], ctx["impulso"])
                if n:
                    self._hit(eff[1] * n, "enemy")
                else:
                    self.say("Nenhuma carta antes desta. Nada acontece.")
            elif kind == "return_last":
                if self.last_played and self.last_played in self.discard:
                    self.discard.remove(self.last_played)
                    self.hand.append(self.last_played)
                    self.say(f"{self.last_played.name} volta à mão.")
                    self.last_played = None
                else:
                    self.say("Nada para devolver.")
            elif kind == "next_free":
                self.next_free = True
            elif kind == "redraw_hand":
                n = len(self.hand)
                self.discard += self.hand
                self.hand = []
                self.draw_cards(n)
            elif kind == "power":
                self.powers.append(eff[1])
                self.say("Poder em campo.")
            elif kind == "if":
                if self.check_condition(eff[1], ctx):
                    self._resolve(eff[2], ctx)

    def _targets(self, which: str) -> list[Enemy]:
        if which == "all":
            return self.living()
        t = self._target()
        return [t] if t else []

    # --------------------------------------------------------- jogador
    def gain_block(self, n: int):
        if n <= 0:
            return
        if "casco_duro" in self.run.modifiers:
            n += 1
        self.block += n

    def summon(self, n: int):
        if self.cls != "capimaga":
            return
        if self.level >= 5 and self.rng.random() < 0.2:
            n += 1
            self.say("Legião: lacaio extra!")
        before = self.minions
        self.minions = min(content.MINION_CAP, self.minions + n)
        got = self.minions - before
        if got:
            self.say(f"Invoca {got} lacaio(s).")

    def _legiao9_check(self):
        if self.cls == "capimaga" and self.level >= 9 and self.minions == 0 and not self.legiao9_done:
            self.legiao9_done = True
            self.minions = 2
            self.say("Legião: sem lacaios, invoca 2.")

    def gain_adrenaline(self, n: int):
        if self.cls != "brutamontes" or n <= 0:
            return
        if self.level >= 10:
            n *= 2
        before = self.adrenaline
        self.adrenaline = min(self.adren_cap, self.adrenaline + n)
        got = self.adrenaline - before
        if got:
            self.say(f"+{got} de Adrenalina.")

    def _lose_hp(self, n: int, source: Enemy | None, from_attack: bool):
        if n <= 0:
            return
        self.hp -= n
        self.say(f"Perde {n} de vida.")
        # Adrenalina
        gain = 1
        if self.cls == "brutamontes" and self.level >= 4 and not self.first_loss_done:
            gain = 2
        self.first_loss_done = True
        if "rugido" in self.powers:
            gain += 1
        self.gain_adrenaline(gain)
        if (self.cls == "brutamontes" and self.level >= 9 and not self.half_hp_done
                and self.hp <= self.max_hp / 2):
            self.half_hp_done = True
            self.gain_adrenaline(3)
        if from_attack and source is not None and source.alive and "olho_por_olho" in self.powers:
            self._damage_enemy(source, 3, "Olho por Olho")
        if self.hp <= 0:
            self.hp = 0
            self.status = "lost"
            self.say("Você caiu.")

    def _receive_attack(self, source: Enemy, raw: int):
        dmg = max(0, raw + source.strength)
        if source.weak:
            dmg = math.floor(dmg * 0.75)
        if self.frail:
            dmg = math.floor(dmg * 1.5)
        if self.evasion > 0:
            self.evasion -= 1
            self.say(f"Evasão anula o ataque de {source.name}.")
            if "rastro" in self.powers:
                self.draw_cards(1)
                self.say("Rastro de Lama: compra 1.")
            return
        absorbed = min(self.block, dmg)
        self.block -= absorbed
        through = dmg - absorbed
        if through == 0 and dmg > 0:
            self.say(f"Defesa absorve {absorbed} de {source.name}.")
            if self.cls == "brutamontes" and self.level >= 5:
                self.gain_adrenaline(1)
        elif through > 0:
            if absorbed:
                self.say(f"Defesa absorve {absorbed}.")
            self._lose_hp(through, source, from_attack=True)
        if self.retaliation and source.alive:
            self._damage_enemy(source, self.retaliation, "Retaliação")

    # --------------------------------------------------------- inimigos
    def _hit(self, base: int, which: str):
        dmg = base + self.strength
        if self.weak:
            dmg = math.floor(dmg * 0.75)
        for e in self._targets(which):
            self._damage_enemy(e, dmg, None, is_attack=True)

    def _damage_enemy(self, e: Enemy, dmg: int, label: str | None, is_attack: bool = False):
        if not e.alive or dmg <= 0:
            return
        if is_attack and e.frail:
            dmg = math.floor(dmg * 1.5)
        absorbed = min(e.block, dmg)
        e.block -= absorbed
        through = dmg - absorbed
        e.hp -= through
        src = f"{label}: " if label else ""
        self.say(f"{src}{e.name} recebe {through} de dano" + (f" ({absorbed} no Defesa)" if absorbed else "") + ".")
        if is_attack and through > 0:
            if e.flags.get("reflect"):
                back = math.floor(through * e.flags["reflect"])
                if back:
                    self.say(f"{e.name} reflete {back}.")
                    absorbed_b = min(self.block, back)
                    self.block -= absorbed_b
                    self._lose_hp(back - absorbed_b, e, from_attack=False)
            if e.flags.get("thorns"):
                t = e.flags["thorns"]
                self.say(f"{e.name} contra ataca com {t}.")
                absorbed_b = min(self.block, t)
                self.block -= absorbed_b
                self._lose_hp(t - absorbed_b, e, from_attack=False)
            if e.flags.get("shift"):
                e.idx += 1
        self._after_enemy_hp_change(e)

    def _after_enemy_hp_change(self, e: Enemy):
        if e.hp <= 0:
            e.hp = 0
            self.say(f"{e.name} cai!")
            if e.flags.get("twin"):
                for o in self.living():
                    if o.flags.get("twin"):
                        o.strength += e.flags["twin"]
                        self.say(f"{o.name} herda +{e.flags['twin']} de Força!")
            return
        self._gertrudes_phase(e)

    def _gertrudes_phase(self, e: Enemy):
        if not e.flags.get("phases") or not e.alive:
            return
        frac = e.hp / e.max_hp
        for i, (mn, pattern) in enumerate(content.GERTRUDES_PHASES):
            if frac > mn:
                if e.phase != i:
                    e.phase = i
                    e.pattern = pattern
                    e.idx = 0
                    self.say(f"{e.name} muda de postura! (fase {i + 1})")
                return

    def _check_end(self):
        if self.status != "ongoing":
            return
        if not self.living():
            self.status = "won"
            self.say("Sala limpa.")

    # ------------------------------------------------------- fim de turno
    def end_turn(self):
        """Turno inteiro de uma vez (bot / testes). A UI chama as fases separadas para animar."""
        if not self.end_turn_start():
            return
        self.enemies_begin()
        for e in list(self.living()):
            if self.status != "ongoing":
                break
            self.enemy_act(e)
        self.enemies_end()
        self.start_next_turn()

    # fases do fim de turno -------------------------------------------------
    def end_turn_start(self) -> bool:
        """Efeitos de fim de turno do jogador e descarte da mão. False se o combate acabou."""
        if self.status != "ongoing":
            return False
        if self.cls == "capimaga" and self.minions:
            alive = self.living()
            total = 0
            for _ in range(self.minions):
                if not self.living():
                    break
                e = self.rng.choice(self.living())
                self._damage_enemy(e, content.MINION_BITE, None)
                total += 1
            if total:
                self.say(f"Lacaios morderam {total} vez(es).")
        if "ossos_firmes" in self.powers and self.minions:
            self.gain_block(self.minions)
            self.say(f"Ossos Firmes: +{self.minions} de Defesa.")
        if "peste" in self.powers:
            for e in self.living():
                e.poison += 2
            self.say("Peste Óssea: Veneno 2 em todos.")
        if self.poison:
            self._lose_hp(self.poison, None, from_attack=False)
            self.poison -= 1
        kept = []
        if "bolso_fundo" in self.powers and self.hand:
            kept = [self.rng.choice(self.hand)]
            self.hand.remove(kept[0])
            self.say(f"Bolso Fundo: guarda {kept[0].name}.")
        self.discard += self.hand
        self.hand = kept
        self._check_end()
        return self.status == "ongoing"

    def enemies_begin(self):
        if self.challenge == "pressa" and self.turn >= 6:
            for e in self.living():
                e.strength += 3
            self.say("Pressa: inimigos ganham +3 de Força.")

    def enemy_act(self, e: Enemy):
        """Um inimigo executa a intenção do turno."""
        if not e.alive or self.status != "ongoing":
            return
        e.block = 0
        if e.flags.get("block_each_turn"):
            e.block += e.flags["block_each_turn"]
        for act in e.intent:
            if self.status != "ongoing":
                return
            kind, val = act[0], act[1]
            times = act[2] if len(act) > 2 else 1
            if kind == "attack":
                for _ in range(times):
                    self._receive_attack(e, val)
                    if not e.alive or self.status != "ongoing":
                        break
            elif kind == "block":
                e.block += val
            elif kind == "strength":
                e.strength += val
                self.say(f"{e.name} ganha +{val} de Força.")
            elif kind == "strength_all":
                for o in self.living():
                    o.strength += val
                self.say(f"{e.name} buffa a sala (+{val} Força).")
            elif kind == "weak":
                self.weak += val
                self.say(f"{e.name} aplica Fraqueza {val}.")
            elif kind == "frail":
                self.frail += val
                self.say(f"{e.name} aplica Fragilidade {val}.")
            elif kind == "poison":
                self.poison += val
                self.say(f"{e.name} aplica Veneno {val}.")
            elif kind == "heal":
                e.hp = min(e.max_hp, e.hp + val)
                self.say(f"{e.name} cura {val}.")
            elif kind == "heal_all":
                for o in self.living():
                    o.hp = min(o.max_hp, o.hp + val)
                self.say(f"{e.name} cura a sala em {val}.")
            elif kind == "steal":
                self.steal_next += val
                self.say(f"{e.name} rouba {val} Ação do próximo turno.")
            elif kind == "charge":
                pass
        if e.alive:
            e.idx += 1
            if e.flags.get("ramp"):
                e.strength += e.flags["ramp"]

    def enemies_end(self):
        """Veneno e estados dos inimigos caem no fim do turno deles."""
        if self.status != "ongoing":
            return
        for e in self.living():
            if e.poison:
                e.hp -= e.poison
                self.say(f"{e.name} sofre {e.poison} de Veneno.")
                e.poison -= 1
                self._after_enemy_hp_change(e)
            if e.weak:
                e.weak -= 1
            if e.frail:
                e.frail -= 1
        self._check_end()

    def start_next_turn(self):
        if self.status == "ongoing":
            self._start_player_turn()
