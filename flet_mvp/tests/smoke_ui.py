"""Smoke test headless da UI: percorre todas as telas com uma Page falsa.

Não renderiza nada; só garante que cada tela monta sem exceção e que as animações (Stage,
Typewriter, sequência de fim de turno) rodam até o fim. Rode de dentro de flet_mvp/:

    python tests/smoke_ui.py
"""

import asyncio
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft  # noqa: E402

from capitower import content  # noqa: E402
from capitower.ui import App  # noqa: E402


class FakeWindow:
    width = height = min_width = 0


class FakePrefs:
    async def get(self, k):
        return None

    async def set(self, k, v):
        pass


class FakePage:
    """Só o que a App usa. `update()` não faz nada; `run_task` agenda no loop atual."""

    def __init__(self):
        self.width = 430
        self.height = 860
        self.window = FakeWindow()
        self.shared_preferences = FakePrefs()
        self.fonts = {}
        self.tasks = []
        self.errors = []
        self.controls = []

    def add(self, *controls):
        self.controls += controls

    def update(self, *a):
        pass

    def run_task(self, fn, *args):
        t = asyncio.get_running_loop().create_task(fn(*args))
        self.tasks.append(t)
        return t

    def show_dialog(self, d):
        self.dialog = d

    def pop_dialog(self):
        self.dialog = None


async def settle(page, timeout=6.0):
    """Espera as tarefas de fundo (transições, stagger, typewriter) terminarem."""
    end = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < end:
        pending = [t for t in page.tasks if not t.done()]
        if not pending:
            break
        await asyncio.wait(pending, timeout=0.2)
    for t in page.tasks:
        if t.done() and not t.cancelled() and t.exception():
            raise t.exception()


def screen_text(app) -> str:
    out = []

    def walk(c):
        if c is None:
            return
        if isinstance(c, ft.Text):
            out.append(str(c.value))
        for attr in ("content", "controls", "title"):
            v = getattr(c, attr, None)
            if isinstance(v, list):
                for x in v:
                    walk(x)
            elif v is not None and not isinstance(v, str):
                walk(v)
    walk(app.root.content)
    return " ".join(out)


def check_error(app):
    txt = screen_text(app)
    assert "Deu ruim" not in txt, "tela de erro: " + txt[:600]


async def main():
    page = FakePage()
    app = App(page)
    await app.load_records()
    await settle(page)
    check_error(app)
    assert "Nova run" in screen_text(app)

    # menu -> classe -> sorteio -> reroll -> torre
    app.show_class_select()
    await settle(page)
    check_error(app)
    for cid in content.CLASSES:
        app.pick_class(cid)
        await settle(page)
        check_error(app)
        assert "sorteio inicial" in screen_text(app)
        app.reroll(0)
        await settle(page)
        check_error(app)
    app.enter_tower()
    await settle(page)
    check_error(app)
    assert "Lutar" in screen_text(app) or "Andar" in screen_text(app)

    # combate completo com o bot mais burro possível (joga a 1a carta jogável, encerra).
    # O andar 1 pode não ser combate (torre é sorteada), então força um inimigo do bloco 1.
    f = app.run.current()
    enemies = f.get("enemies") or [next(e for e in content.ENEMIES.values() if not e.flags.get("boss")
                                        and not e.flags.get("elite")).id]
    app.start_combat(enemies)
    await settle(page)
    check_error(app)
    c = app.combat
    turns = 0
    while c.status == "ongoing" and turns < 40:
        played = False
        for i, card in enumerate(list(c.hand)):
            if c.can_play(card):
                app.tap_card(i)          # seleciona
                await settle(page)
                app.tap_card(i)          # joga (animação)
                await settle(page)
                check_error(app)
                played = True
                break
        if not played:
            app.end_turn()
            await settle(page, 12)
            check_error(app)
            turns += 1
    await settle(page, 4)
    check_error(app)
    txt = screen_text(app)
    # pós-combate depende do tipo do andar sorteado: comum, elite/chefe, desafio ou derrota
    assert any(k in txt for k in ("Sala limpa", "Recompensa", "Desafio vencido", "Você caiu")), txt[:300]

    # elite: o banner com o nome cobre a tela inteira e precisa sumir de verdade depois do
    # fade, senão continua engolindo os toques e o jogo parece travado
    app.busy = False
    app.run.hp = app.run.max_hp
    app.run.floor = next(i for i, f in enumerate(app.run.floors) if f["type"] == "elite") + 1
    app.start_combat(app.run.current()["enemies"])
    await settle(page)
    check_error(app)
    overlays = app.root.content.controls[1:]
    assert overlays, "banner de elite não foi montado"
    assert all(o.visible is False for o in overlays), "overlay do banner ainda está por cima da tela"
    assert not app.busy and app.combat.status == "ongoing"

    # telas restantes, forçadas direto (não dependem do sorteio da torre)
    app.busy = False
    app.show_reward()
    await settle(page)
    check_error(app)
    assert "Recompensa" in screen_text(app)

    app.busy = False
    app.show_modifier_choice()
    await settle(page)
    check_error(app)
    assert "Desafio vencido" in screen_text(app)

    app.busy = False
    ev = content.EVENTS[0]
    app.show_event(ev)
    await settle(page)
    check_error(app)
    assert ev["title"] in screen_text(app)
    for _, key in ev["choices"]:
        app.busy = False
        app.resolve_event(ev, key)
        await settle(page)
        check_error(app)

    app.busy = False
    app.do_rest()
    await settle(page)
    check_error(app)
    assert "Descanso" in screen_text(app)

    app.busy = False
    app.show_deck()

    app.busy = False
    app.run.victory = False
    app.show_end()
    await settle(page)
    check_error(app)
    assert "Você caiu" in screen_text(app)

    app.busy = False
    app.show_menu()
    await settle(page)
    check_error(app)
    print("smoke ok: todas as telas montaram e as animações terminaram")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
