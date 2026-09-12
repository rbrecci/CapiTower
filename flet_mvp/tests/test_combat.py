"""Testes de regra do motor de combate. Rode de dentro de flet_mvp/:

    python tests/test_combat.py

Cada função test_* monta um combate com seed fixa, força a mão ou o estado que precisa e
confere um número. Sem pytest instalado, o bloco no fim roda todas em sequência; com pytest,
`pytest tests/` também funciona.
"""

import os
import random
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capitower import content  # noqa: E402
from capitower.cards import BY_ID  # noqa: E402
from capitower.combat import Combat, Enemy  # noqa: E402
from capitower.run import Run  # noqa: E402


def combat(cls="brutamontes", enemies=("capivarinha",), seed=1, hp=999) -> Combat:
    run = Run(cls, seed=seed)
    run.build_starting_deck()
    c = Combat(run, list(enemies))
    for e in c.enemies:
        e.hp = e.max_hp = hp
    return c


def give(c: Combat, *card_ids):
    """Substitui a mão pelas cartas dadas, com Ação de sobra."""
    c.hand = [BY_ID[i] for i in card_ids]
    c.actions = 9
    return c


def enemy_phase(c: Combat):
    """Fase inimiga completa sem o turno do jogador seguinte (para ler estados intermediários)."""
    c.end_turn_start()
    c.enemies_begin()
    for e in list(c.living()):
        c.enemy_act(e)
    c.enemies_end()


# ----------------------------------------------------------- estados no jogador
def test_weak_1_from_enemy_lasts_one_player_turn():
    c = combat(enemies=("marlene",))
    c.enemies[0].idx = 1  # [attack 4x2, weak 1]
    enemy_phase(c)
    c.start_next_turn()
    assert c.weak == 1, f"Fraqueza sumiu antes do turno do jogador (weak={c.weak})"
    c.end_turn()
    assert c.weak == 0, "Fraqueza 1 deveria acabar depois de um turno"


def test_frail_2_from_enemy_covers_two_enemy_phases():
    c = combat(enemies=("elite3",))
    c.enemies[0].idx = 1  # [frail 2, attack 8]
    enemy_phase(c)
    c.start_next_turn()
    assert c.frail == 2, f"Fragilidade perdeu 1 antes de qualquer fase inimiga (frail={c.frail})"
    enemy_phase(c)  # fase 1 sob Fragilidade
    c.start_next_turn()
    assert c.frail == 1, f"Fragilidade 2 deveria ter 1 restante (frail={c.frail})"
    enemy_phase(c)  # fase 2 sob Fragilidade
    c.start_next_turn()
    assert c.frail == 0


def test_weak_next_combat_from_event_lasts_full_value():
    run = Run("ligeira", seed=5)
    run.build_starting_deck()
    run.weak_next_combat = 2
    c = Combat(run, ["capivarinha"])
    assert c.weak == 2, f"Fraqueza do evento perdeu 1 antes do turno 1 (weak={c.weak})"


# ------------------------------------------------------------------ retaliação
def test_retaliation_one_turn_hits_only_next_enemy_phase():
    c = combat(seed=2)
    give(c, "bm_provocar")  # Retaliação 2 por 1 turno
    c.play(0)
    e = c.enemies[0]
    hp0 = e.hp
    c.end_turn()
    assert hp0 - e.hp == 2, "Retaliação deveria devolver 2 na primeira fase inimiga"
    assert c.retaliation == 0, f"Retaliação de 1 turno ainda ativa (turns={c.retaliation_turns})"
    hp0 = e.hp
    c.end_turn()
    assert hp0 - e.hp == 0, "Retaliação de 1 turno bateu na segunda fase"


# ----------------------------------------------------------- um golpe por carta
def test_split_damage_card_is_one_hit():
    c = combat(cls="ligeira", seed=3)
    c.strength = 3
    c.played_this_turn = 2  # Dentada Rápida: 6, +4 se já jogou 2
    give(c, "lg_dentada")
    hp0 = c.enemies[0].hp
    c.play(0)
    assert hp0 - c.enemies[0].hp == 13, f"Força contou duas vezes: {hp0 - c.enemies[0].hp} (esperado 6+4+3)"


def test_split_damage_card_triggers_thorns_once():
    c = combat(cls="brutamontes", enemies=("guarda",), seed=3)  # espinhos 3
    c.adrenaline = 4
    give(c, "bm_soco")  # 7, +1 por Adrenalina
    hp0 = c.hp
    c.play(0)
    assert hp0 - c.hp == 3, f"Espinhos dispararam mais de uma vez: perdeu {hp0 - c.hp}"


def test_two_strikes_card_still_hits_twice():
    c = combat(cls="ligeira", enemies=("guarda",), seed=3)
    give(c, "lg_cambalhota")  # 4 duas vezes
    hp0, php0 = c.enemies[0].hp, c.hp
    c.play(0)
    assert hp0 - c.enemies[0].hp == 8
    assert php0 - c.hp == 6, "Cambalhota é dois golpes: espinhos deveriam pegar duas vezes"


def test_consume_bonus_joins_base_hit():
    c = combat(cls="brutamontes", seed=3)
    c.adrenaline = 6
    c.strength = 1
    give(c, "bm_cabecada")  # 10, +3 por ponto (até 6)
    hp0 = c.enemies[0].hp
    c.play(0)
    assert hp0 - c.enemies[0].hp == 10 + 18 + 1


def test_hit_resolves_before_following_effects():
    """Costela Solta: 7 de dano, depois invoca. O log tem que mostrar o dano antes do lacaio."""
    c = combat(cls="capimaga", seed=3)
    give(c, "cm_costela")
    c.play(0)
    log = "\n".join(c.log)
    assert log.index("recebe 7") < log.index("Invoca 1"), log


# ------------------------------------------------------------- padrão inicial
def test_fixed_start_enemy_never_opens_with_charged_blow():
    starts = {Enemy(content.ENEMIES["garcom"], random.Random(s)).intent[0][0] for s in range(100)}
    assert starts == {"charge"}, f"Garçom abriu com {starts}"


# --------------------------------------------------------------------- alvo
def test_target_moves_to_living_enemy_after_kill():
    c = combat(cls="capimaga", enemies=("capivarinha", "capivarinha"), seed=4)
    c.enemies[0].hp = 1
    c._hit(5, "enemy")
    assert not c.enemies[0].alive
    assert c.target == 1, f"alvo ficou no cadáver (target={c.target})"


# ------------------------------------------------------------------- poderes
def test_duplicate_power_is_blocked_without_spending_action():
    c = combat(cls="brutamontes", seed=6)
    give(c, "bm_rugido", "bm_rugido")
    c.play(0)
    assert c.powers == ["rugido"]
    assert c.block_reason(c.hand[0]) == "Poder já em campo"
    assert not c.can_play(c.hand[0])
    actions = c.actions
    c.play(0)
    assert c.actions == actions and c.powers == ["rugido"] and len(c.hand) == 1


# ------------------------------------------------------------------ gertrudes
def test_gertrudes_phase_never_regresses_after_heal():
    c = combat(cls="ligeira", enemies=("gertrudes",), seed=7)
    g = c.enemies[0]
    g.max_hp = 340
    g.hp = 100  # fase 3 (< 33%)
    c._damage_enemy(g, 1, None, is_attack=True)
    assert g.phase == 2
    g.hp = 130  # curou de volta acima de 33%
    c._damage_enemy(g, 1, None, is_attack=True)
    assert g.phase == 2, "Gertrudes voltou para a fase 2 depois de curar"


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"ok    {name}")
        except Exception:
            failed += 1
            print(f"FALHA {name}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passaram")
    sys.exit(1 if failed else 0)
