"""Telas do MVP em Flet. Coluna única pensada para celular, centralizada no desktop.

Direção visual: cada tela é uma cena (cenário do bloco ao fundo, HUD translúcido por cima).
No combate os inimigos ficam em pé no cenário, o jogador embaixo à esquerda e a mão em leque.
Chefes e elites ainda não têm arte: são silhuetas com ícone, destacadas por cor e tamanho.

Regra de leitura: número + ícone sempre que der, texto só onde o ícone não basta.
Todo chip tem tooltip com o nome por extenso (passa o mouse no desktop, segura no celular).
"""

import asyncio
import functools
import inspect
import json
import traceback

import flet as ft

from . import content
from .anim import A, BACK, IN, INOUT, OUT, Stage, Typewriter, flush
from .cards import POWER_NAMES, CardDef
from .combat import Combat, Enemy
from .run import Run

# ------------------------------------------------------------------ tema
FONT = "LuckiestGuy"  # títulos e números grandes; corpo fica na fonte padrão por legibilidade
BG = "#141f19"
INK = "#0b110e"
TEXT = "#f3eedd"
MUTED = "#b9c2b6"
ACCENT = "#f2b638"
ACCENT_DARK = "#8a5a10"
HP = "#e8524d"
DEF = "#5aa7ea"
GOOD = "#7ccf7f"
BAD = "#d194e3"
POISON = "#9be04f"
SILHOUETTE = "#0d1411"
KIND_COLORS = {
    "Ataque": "#e0563f",
    "Defesa": "#4c93de",
    "Poder": "#a66be0",
    "Utilidade": "#5cb872",
}
KIND_ICONS = {
    "Ataque": ft.Icons.SPORTS_MMA,
    "Defesa": ft.Icons.SHIELD,
    "Poder": ft.Icons.AUTO_AWESOME,
    "Utilidade": ft.Icons.BUILD,
}
KIND_FRAMES = {
    "Ataque": "frame_ataque.png",
    "Defesa": "frame_defesa.png",
    "Poder": "frame_poder.png",
    "Utilidade": "frame_utilidade.png",
}
# onde ficam os buracos de cada moldura, em fração da largura/altura da carta:
# gema (cx, cy), janela de arte (x0, y0, x1, y1), caixa de texto (x0, y0, x1, y1)
FRAME_LAYOUT = {
    "Ataque":    ((0.165, 0.115), (0.19, 0.15, 0.81, 0.55), (0.17, 0.65, 0.83, 0.87)),
    "Defesa":    ((0.177, 0.095), (0.16, 0.13, 0.84, 0.54), (0.14, 0.62, 0.86, 0.90)),
    "Poder":     ((0.165, 0.110), (0.16, 0.14, 0.84, 0.61), (0.15, 0.68, 0.85, 0.90)),
    "Utilidade": ((0.195, 0.127), (0.19, 0.21, 0.81, 0.59), (0.16, 0.65, 0.84, 0.84)),
}
# cenário e cor de destaque de cada bloco (índice = bloco em content.BLOCKS)
BLOCK_THEMES = [
    {"bg": "bg_poco.jpg", "accent": "#7fd39a"},
    {"bg": "bg_academia.jpg", "accent": "#ff6a4d"},
    {"bg": "bg_laboratorio.jpg", "accent": "#b6ff5c"},
    {"bg": "bg_refeitorio.jpg", "accent": "#ffb347"},
    {"bg": "bg_jardim.jpg", "accent": "#ff9ccc"},
]
MENU_BG = "bg_menu.jpg"
# ícone da silhueta placeholder de cada inimigo sem arte
ENEMY_ICONS = {
    "capivarinha": ft.Icons.WATER_DROP, "sapo": ft.Icons.BUBBLE_CHART, "rato": ft.Icons.PEST_CONTROL_RODENT,
    "halter": ft.Icons.FITNESS_CENTER, "spinning": ft.Icons.DIRECTIONS_BIKE, "personal": ft.Icons.SPORTS,
    "frasco": ft.Icons.SCIENCE, "experimental": ft.Icons.BIOTECH, "bolha": ft.Icons.BUBBLE_CHART,
    "marmita": ft.Icons.LUNCH_DINING, "garcom": ft.Icons.ROOM_SERVICE, "sobremesa": ft.Icons.CAKE,
    "guarda": ft.Icons.SECURITY, "jardineira": ft.Icons.YARD, "vaso": ft.Icons.LOCAL_FLORIST,
    "elite1": ft.Icons.FRONT_HAND, "elite2": ft.Icons.SPORTS, "elite3": ft.Icons.BIOTECH,
    "elite4": ft.Icons.RESTAURANT, "elite5": ft.Icons.SHIELD,
    "dorival": ft.Icons.FITNESS_CENTER, "marlene": ft.Icons.DIRECTIONS_RUN, "helio": ft.Icons.SCIENCE,
    "gemeo_a": ft.Icons.FITNESS_CENTER, "gemeo_b": ft.Icons.FITNESS_CENTER, "capitolino": ft.Icons.MILITARY_TECH,
}
ENEMY_ART = {"gertrudes": "gertrudes.png"}
# ícone, cor e nome por extenso de cada estado / recurso
STAT = {
    "hp": (ft.Icons.FAVORITE, HP, "Vida"),
    "def": (ft.Icons.SHIELD, DEF, "Defesa"),
    "action": (ft.Icons.BOLT, ACCENT, "Ação"),
    "minions": (ft.Icons.GROUPS, "#cfd8dc", "Lacaios"),
    "adren": (ft.Icons.LOCAL_FIRE_DEPARTMENT, "#ff8a50", "Adrenalina"),
    "impulso": (ft.Icons.SPEED, "#80d8ff", "Impulso"),
    "strength": (ft.Icons.FITNESS_CENTER, "#ffb74d", "Força"),
    "weak": (ft.Icons.TRENDING_DOWN, BAD, "Fraqueza"),
    "frail": (ft.Icons.HEART_BROKEN, BAD, "Fragilidade"),
    "poison": (ft.Icons.SCIENCE, POISON, "Veneno"),
    "retaliation": (ft.Icons.REPLY, "#ffb74d", "Retaliação"),
    "evasion": (ft.Icons.AIR, "#80d8ff", "Evasão"),
    "free": (ft.Icons.MONEY_OFF, ACCENT, "Próxima carta custa 0"),
    "deck": (ft.Icons.STYLE, MUTED, "Cartas no deck"),
    "level": (ft.Icons.MILITARY_TECH, ACCENT, "Nível da habilidade"),
    "floor": (ft.Icons.STAIRS, MUTED, "Andar"),
    "turn": (ft.Icons.HOURGLASS_TOP, MUTED, "Turno"),
    "draw": (ft.Icons.STYLE, MUTED, "Pilha de compra"),
    "discard": (ft.Icons.DELETE_OUTLINE, MUTED, "Descarte"),
    "boss": (ft.Icons.EMOJI_EVENTS, ACCENT, "Chefes derrotados"),
    "points": (ft.Icons.STAR, ACCENT, "Pontos de meta"),
    "runs": (ft.Icons.REPLAY, MUTED, "Runs"),
    "wins": (ft.Icons.WORKSPACE_PREMIUM, ACCENT, "Vitórias"),
    "seed": (ft.Icons.CASINO, MUTED, "Seed da run"),
}
# intenções do inimigo
INTENT = {
    "attack": (ft.Icons.SPORTS_MMA, HP),
    "block": (ft.Icons.SHIELD, DEF),
    "strength": (ft.Icons.FITNESS_CENTER, "#ffb74d"),
    "strength_all": (ft.Icons.GROUPS, "#ffb74d"),
    "weak": (ft.Icons.TRENDING_DOWN, BAD),
    "frail": (ft.Icons.HEART_BROKEN, BAD),
    "poison": (ft.Icons.SCIENCE, POISON),
    "heal": (ft.Icons.HEALING, GOOD),
    "heal_all": (ft.Icons.HEALING, GOOD),
    "steal": (ft.Icons.BOLT, BAD),
    "charge": (ft.Icons.HOURGLASS_TOP, MUTED),
}
# tipos de andar
FLOOR = {
    "combat": (ft.Icons.SPORTS_MMA, "Combate", "Sem recompensa, só progresso."),
    "elite": (ft.Icons.STAR, "Elite", "Bem mais difícil. Vencer dá um ponto de recompensa."),
    "boss": (ft.Icons.EMOJI_EVENTS, "Chefe", "Fim do bloco. Dá um ponto de recompensa."),
    "final": (ft.Icons.WORKSPACE_PREMIUM, "Soberana Gertrudes", "O topo da torre. Três fases."),
    "event": (ft.Icons.HELP_OUTLINE, "Evento", "Uma escolha com consequência imediata."),
    "rest": (ft.Icons.HOTEL, "Descanso", "Recupera 30% do HP máximo."),
    "challenge": (ft.Icons.FLAG, "Desafio opcional", "Pode pular sem custo. Vencendo, ganha um modificador de run."),
}


def alpha(color: str, a: float) -> str:
    return ft.Colors.with_opacity(a, color)


PANEL = alpha(INK, 0.80)
PANEL_2 = alpha("#1f2e26", 0.88)
LINE = alpha("#ffffff", 0.14)


# ---------------------------------------------------------- primitivos
def txt(value, size=13, color=TEXT, weight=None, align=None, max_lines=None, font=None):
    return ft.Text(value, size=size, color=color, weight=weight, text_align=align, max_lines=max_lines,
                   font_family=font, overflow=ft.TextOverflow.ELLIPSIS if max_lines else None)


def display(value, size=22, color=ACCENT, align=None, max_lines=None):
    """Texto de destaque na fonte de jogo, com contorno escuro para ler sobre cenário."""
    return ft.Stack([
        ft.Text(value, size=size, font_family=FONT, text_align=align, max_lines=max_lines,
                style=ft.TextStyle(foreground=ft.Paint(color=INK, stroke_width=size * 0.18,
                                                        style=ft.PaintingStyle.STROKE))),
        ft.Text(value, size=size, font_family=FONT, color=color, text_align=align, max_lines=max_lines),
    ])


def title(value, size=22):
    return display(value, size)


def button(label, on_click, icon=None, primary=True, disabled=False, expand=False):
    """Botão 'gordo' de jogo: cor chapada, borda escura e sombra embaixo (parece apertável)."""
    fg = INK if primary else TEXT
    bg = ACCENT if primary else alpha("#2a3a31", 0.92)
    if disabled:
        bg, fg = alpha("#3a4a41", 0.7), MUTED
    inner = [txt(label, 15, fg, font=FONT)]
    if icon:
        inner.insert(0, ft.Icon(icon, color=fg, size=18))
    return ft.Container(
        content=ft.Row(inner, spacing=6, alignment=ft.MainAxisAlignment.CENTER, tight=True),
        bgcolor=bg, padding=ft.Padding.symmetric(horizontal=16, vertical=10),
        border=ft.Border.all(2, INK), border_radius=ft.BorderRadius.all(12),
        shadow=None if disabled else ft.BoxShadow(blur_radius=0, offset=ft.Offset(0, 3),
                                                   color=ACCENT_DARK if primary else INK),
        on_click=None if disabled else on_click, ink=not disabled, expand=expand,
        disabled=disabled, alignment=ft.Alignment.CENTER,
    )


def wide(btn):
    """Botão ocupando a largura toda."""
    btn.expand = True
    return ft.Row([btn])


def panel(content, padding=10, bgcolor=PANEL, border_color=LINE, on_click=None, width=None, tooltip=None):
    return ft.Container(
        content=content, padding=padding, bgcolor=bgcolor, width=width, tooltip=tooltip,
        border=ft.Border.all(1, border_color), border_radius=ft.BorderRadius.all(12),
        on_click=on_click, ink=on_click is not None,
    )


def bar(value, color, height=8):
    return ft.ProgressBar(value=max(0.0, min(1.0, value)), color=color, bgcolor=alpha(INK, 0.8),
                          bar_height=height, border_radius=ft.BorderRadius.all(4))


def hp_bar(cur: int, mx: int, width: float, color=HP, height=16, label=True):
    """Barra com o número dentro, borda escura grossa (combina com o traço da arte)."""
    frac = max(0.0, min(1.0, cur / mx if mx else 0))
    layers = [
        ft.Container(width=width, height=height, bgcolor=alpha(INK, 0.9), border_radius=ft.BorderRadius.all(height / 2),
                     border=ft.Border.all(2, INK)),
        ft.Container(width=max(0, (width - 4) * frac), height=height - 4, bgcolor=color, left=2, top=2,
                     border_radius=ft.BorderRadius.all(height / 2)),
    ]
    if label:
        layers.append(ft.Container(width=width, height=height, alignment=ft.Alignment.CENTER,
                                   content=txt(f"{cur}/{mx}", height - 5, TEXT, ft.FontWeight.BOLD)))
    return ft.Stack(layers, width=width, height=height)


def chip(key, value, size=13, label=None, bold=True):
    """Ícone + número, com tooltip do nome por extenso."""
    icon, color, name = STAT[key]
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, color=color, size=size + 3),
            txt(str(value), size, color, ft.FontWeight.BOLD if bold else None),
        ], spacing=3, tight=True),
        tooltip=label or name,
    )


def icon_line(icon, text, color=TEXT, size=12, icon_color=None):
    return ft.Row([ft.Icon(icon, color=icon_color or color, size=size + 4),
                   ft.Container(content=txt(text, size, color), expand=True)],
                  spacing=6, vertical_alignment=ft.CrossAxisAlignment.START)


def heading(icon, text, color=ACCENT, size=20):
    return ft.Row([ft.Icon(icon, color=color, size=size + 8), display(text, size, color)], spacing=8)


def card_view(card: CardDef, on_click=None, cost=None, playable=True, reason: str | None = None,
              width=118, height=176, raised=False):
    """Carta com a moldura do tipo. Custo na gema, ícone e nome na janela de arte, texto na caixa."""
    cost = card.cost if cost is None else cost
    color = KIND_COLORS[card.kind]
    (gx, gy), (ax0, ay0, ax1, ay1), (tx0, ty0, tx1, ty1) = FRAME_LAYOUT[card.kind]
    w, h = width, height
    art_h = (ay1 - ay0) * h
    icon_size = min(art_h * 0.42, (ax1 - ax0) * w * 0.5)
    art = ft.Container(
        left=ax0 * w, top=ay0 * h, width=(ax1 - ax0) * w, height=art_h,
        alignment=ft.Alignment.CENTER,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column([
            ft.Icon(KIND_ICONS[card.kind], color=color, size=icon_size),
            display(card.name, max(10, w * 0.088), TEXT, align=ft.TextAlign.CENTER, max_lines=2),
        ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True),
    )
    text_h = (ty1 - ty0) * h
    text_size = max(8, w * 0.068)
    body = ft.Container(
        left=tx0 * w + 3, top=ty0 * h + 2, width=(tx1 - tx0) * w - 6, height=text_h - 4,
        alignment=ft.Alignment.CENTER, clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Text(card.text, size=text_size, color=INK, weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.CENTER, overflow=ft.TextOverflow.ELLIPSIS,
                        max_lines=max(2, int((text_h - 4) / (text_size * 1.2))),
                        style=ft.TextStyle(height=1.15)),
    )
    gem_size = w * 0.16
    gem = ft.Container(
        left=gx * w - gem_size / 2, top=gy * h - gem_size / 2, width=gem_size, height=gem_size,
        alignment=ft.Alignment.CENTER, tooltip=f"Custo: {cost} Ação",
        content=display(str(cost), gem_size * 0.95, ACCENT if cost < card.cost else TEXT),
    )
    # etiqueta do arquétipo, como uma aba na borda de cima da caixa de texto
    pill_h = max(11, h * 0.075)
    pill_w = min(w * 0.7, len(card.arch) * w * 0.062 + w * 0.12)
    arch = ft.Container(
        left=(w - pill_w) / 2, top=ty0 * h - pill_h * 0.62, width=pill_w, height=pill_h,
        bgcolor=color, border=ft.Border.all(1.5, INK), border_radius=ft.BorderRadius.all(pill_h / 2),
        alignment=ft.Alignment.CENTER, tooltip=f"Arquétipo: {card.arch}",
        content=ft.Text(card.arch.upper(), size=max(7, w * 0.058), color=INK, weight=ft.FontWeight.W_800,
                        text_align=ft.TextAlign.CENTER, max_lines=1, style=ft.TextStyle(letter_spacing=0.5)),
    )
    stack = ft.Stack([
        # fundo escuro atrás da janela de arte e branco-creme atrás da caixa de texto
        ft.Container(left=w * 0.08, top=h * 0.05, width=w * 0.84, height=h * 0.9, bgcolor="#1d2a23",
                     border_radius=ft.BorderRadius.all(w * 0.06)),
        ft.Container(left=tx0 * w, top=ty0 * h, width=(tx1 - tx0) * w, height=text_h, bgcolor="#f1e9d2",
                     border_radius=ft.BorderRadius.all(w * 0.05)),
        art,
        ft.Image(src=KIND_FRAMES[card.kind], fit=ft.BoxFit.FILL, left=0, top=0, width=w, height=h),
        gem,
        body,
        arch,
    ], width=w, height=h)
    tip = f"{card.name} ({card.kind} · {card.arch}) · custo {cost}\n{card.text}"
    return ft.Container(
        content=stack, width=w, height=h, on_click=on_click, ink=False,
        opacity=1.0 if playable else 0.6,
        tooltip=tip if playable else tip + (f"\n({reason})" if reason else "\n(Ação insuficiente)"),
        shadow=ft.BoxShadow(blur_radius=14, color=alpha(ACCENT, 0.9)) if raised else
        ft.BoxShadow(blur_radius=8, color=alpha(INK, 0.7), offset=ft.Offset(0, 3)),
        border_radius=ft.BorderRadius.all(w * 0.06),
    )


def silhouette(size: float, accent: str, icon, elite=False, boss=False):
    """Placeholder de inimigo sem arte: vulto de capivara com ícone, brilho na cor do bloco."""
    ring = ACCENT if boss else ("#ffd66b" if elite else accent)
    body_w, body_h = size, size * 0.62
    head = size * 0.46
    layers = [
        ft.Container(left=0, top=size * 0.34, width=body_w, height=body_h, bgcolor=SILHOUETTE,
                     border_radius=ft.BorderRadius.all(size * 0.31), border=ft.Border.all(3, ring)),
        ft.Container(left=size * 0.5, top=size * 0.04, width=head, height=head * 0.86, bgcolor=SILHOUETTE,
                     border_radius=ft.BorderRadius.all(size * 0.2), border=ft.Border.all(3, ring)),
        ft.Container(left=size * 0.56, top=0, width=size * 0.13, height=size * 0.13, bgcolor=SILHOUETTE,
                     border_radius=ft.BorderRadius.all(size), border=ft.Border.all(2, ring)),
        ft.Container(left=size * 0.8, top=0, width=size * 0.13, height=size * 0.13, bgcolor=SILHOUETTE,
                     border_radius=ft.BorderRadius.all(size), border=ft.Border.all(2, ring)),
        ft.Container(left=size * 0.66, top=size * 0.17, width=size * 0.07, height=size * 0.07, bgcolor=ring,
                     border_radius=ft.BorderRadius.all(size)),
        ft.Container(left=0, top=size * 0.34, width=body_w, height=body_h, alignment=ft.Alignment.CENTER,
                     content=ft.Icon(icon, color=alpha(ring, 0.9), size=size * 0.34)),
    ]
    if boss or elite:
        layers.append(ft.Container(left=size * 0.62, top=-size * 0.14, width=size * 0.22, height=size * 0.22,
                                   alignment=ft.Alignment.CENTER,
                                   content=ft.Icon(ft.Icons.EMOJI_EVENTS if boss else ft.Icons.STAR, color=ring,
                                                   size=size * 0.22)))
    return ft.Stack(layers, width=size, height=size)


def enemy_sprite(edef, size: float, accent: str):
    if edef.id in ENEMY_ART:
        return ft.Container(width=size, height=size, content=ft.Image(src=ENEMY_ART[edef.id], fit=ft.BoxFit.CONTAIN))
    return silhouette(size, accent, ENEMY_ICONS.get(edef.id, ft.Icons.PETS),
                      elite=edef.flags.get("elite", False), boss=edef.flags.get("boss", False))


# ------------------------------------------------------------------- app
class App:
    MAX_WIDTH = 600
    RECORDS_KEY = "capitower.records"
    HAND_CARD = (118, 176)
    HAND_LIFT = 26

    def __init__(self, page: ft.Page):
        self.page = page
        self.run: Run | None = None
        self.combat: Combat | None = None
        self.combats_played = 0
        self.selected: int | None = None  # carta da mão selecionada (toque 1 seleciona, toque 2 joga)
        self.banner: tuple[str, str] | None = None
        self.busy = False       # animação em curso: toques na mão / inimigos são ignorados
        self.gen = 0            # sobe a cada tela nova; tarefas de fundo param quando muda
        self._prev_hand: list = []          # (carta, left, top, ângulo) da última mão desenhada
        self._hand_ctrls: dict = {}         # índice na mão -> container da carta no leque
        self._hand_geom = (118, 176, 26, 400)
        self._enemy_sprites: dict = {}      # índice do inimigo -> container do sprite
        self._pending_show = None
        self._reroll_idx: int | None = None
        # recordes persistidos no aparelho (shared_preferences)
        self.records = {"best_floor": 0, "total_points": 0, "runs": 0, "wins": 0}

        page.title = "CapiTower"
        page.bgcolor = INK
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 0
        page.fonts = {FONT: "fonts/LuckiestGuy-Regular.ttf"}
        page.window.width = 430
        page.window.height = 860
        page.window.min_width = 360

        # coluna central com largura máxima: no celular ocupa tudo, no desktop fica centrada.
        # root = tela atual (anima fade/slide na troca); curtain = cortina da passagem de andar
        self.root = ft.Container(expand=True, clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                 animate_opacity=A(160, IN), animate_offset=A(160, IN))
        self.curtain = ft.Container(left=0, top=0, right=0, bottom=0, bgcolor=INK, visible=False, opacity=0,
                                    alignment=ft.Alignment.CENTER, animate_opacity=A(240, IN))
        # sem expand: o Row estica na vertical e a largura vem só de `width` (senão o expand ganha)
        self.frame = ft.Container(width=self._fit_width(), clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                  content=ft.Stack([self.root, self.curtain], expand=True))
        outer = ft.Row([self.frame], alignment=ft.MainAxisAlignment.CENTER,
                       vertical_alignment=ft.CrossAxisAlignment.STRETCH, expand=True)
        page.add(ft.SafeArea(content=outer, expand=True))
        page.on_resize = self._on_resize
        page.on_error = lambda e: self.show_error(str(e.data))
        self._guard_handlers()

    # ------------------------------------------------------- erros na tela
    HANDLER_PREFIXES = ("show_", "pick_", "reroll", "enter_", "next_", "do_", "resolve_", "start_",
                        "select_", "tap_", "play_", "end_", "take_")

    def _guard_handlers(self):
        """Embrulha todo handler de tela: exceção vira painel com traceback em vez de app mudo."""
        for name in dir(App):
            if name.startswith(self.HANDLER_PREFIXES) and name != "show_error":
                fn = getattr(self, name)
                if callable(fn):
                    setattr(self, name, self._guarded(fn))

    def _guarded(self, fn):
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def awrapper(*a, **kw):
                try:
                    return await fn(*a, **kw)
                except Exception:
                    self.busy = False
                    self.show_error(traceback.format_exc())
            return awrapper

        @functools.wraps(fn)
        def wrapper(*a, **kw):
            try:
                return fn(*a, **kw)
            except Exception:
                self.busy = False
                self.show_error(traceback.format_exc())
        return wrapper

    def task(self, coro_fn, *args):
        """Roda uma coroutine em segundo plano com o mesmo tratamento de erro dos handlers."""
        return self.page.run_task(self._guarded(coro_fn), *args)

    def show_error(self, text: str):
        self.busy = False
        self._pending_show = None
        self.show(self.scene([
            display("Deu ruim", 28, HP),
            txt("Um erro de código travou a tela. Copie o texto abaixo e mande pro desenvolvedor.", 12, MUTED),
            panel(ft.Text(text, size=10, color=TEXT, font_family="monospace", selectable=True), padding=8),
            wide(button("Voltar ao menu", self.show_menu, icon=ft.Icons.HOME)),
        ], bg=MENU_BG, shade=0.7), fade=False)

    def _fit_width(self) -> float:
        return min(self.page.width or 430, self.MAX_WIDTH)

    def _on_resize(self, e=None):
        w = getattr(e, "width", None) or self.page.width or 430
        self.frame.width = min(w, self.MAX_WIDTH)
        self.page.update()

    # -------------------------------------------------------- recordes
    async def load_records(self):
        try:
            raw = await self.page.shared_preferences.get(self.RECORDS_KEY)
            if raw:
                self.records.update(json.loads(raw))
        except Exception:
            pass
        self.show_menu()

    async def save_records(self):
        try:
            await self.page.shared_preferences.set(self.RECORDS_KEY, json.dumps(self.records))
        except Exception:
            pass

    def record_run(self, run: Run):
        r = self.records
        r["best_floor"] = max(r["best_floor"], run.floor)
        r["total_points"] += run.meta_points()
        r["runs"] += 1
        r["wins"] += 1 if run.victory else 0
        self.page.run_task(self.save_records)

    # ------------------------------------------------------------ util
    def theme(self) -> dict:
        if self.run and self.run.floor:
            return BLOCK_THEMES[self.run.current()["block"]]
        return BLOCK_THEMES[0]

    # --------------------------------------------------- troca de tela
    def show(self, control: ft.Control, fade=True, stage: Stage | None = None, floor: tuple | None = None):
        """Coloca a tela nova. `fade` faz a atual sumir e a nova entrar deslizando; `floor` usa a
        cortina de passagem de andar; `stage` toca as entradas dos elementos da tela nova."""
        self.gen += 1
        if not fade and not floor:
            self.root.content = control
            self.root.opacity, self.root.offset = 1, ft.Offset(0, 0)
            self.page.update()
            if stage:
                self.task(stage.play, self.page)
            return
        self._pending_show = (control, stage, floor)
        if not self._transitioning:
            self.task(self._transition)

    _transitioning = False

    async def _transition(self):
        self._transitioning = True
        self.busy = True
        try:
            while self._pending_show:
                control, stage, floor = self._pending_show
                self._pending_show = None
                if floor:
                    await self._floor_curtain(control, stage, floor)
                else:
                    await self._fade_swap(control, stage)
        finally:
            self._transitioning = False
            self.busy = False

    async def _fade_swap(self, control, stage):
        root = self.root
        root.animate_opacity, root.animate_offset = A(150, IN), A(150, IN)
        root.opacity, root.offset = 0, ft.Offset(0, 0.02)
        self.page.update()
        await asyncio.sleep(0.16)
        root.content = control
        root.offset = ft.Offset(0, -0.025)
        self.page.update()
        await asyncio.sleep(0.03)
        root.animate_opacity, root.animate_offset = A(320, OUT), A(360, OUT)
        root.opacity, root.offset = 1, ft.Offset(0, 0)
        self.page.update()
        if stage:
            await stage.play(self.page, lead=0.06)
        else:
            await asyncio.sleep(0.2)

    async def _floor_curtain(self, control, stage, floor):
        """Cortina escura sobe, mostra 'Andar N · bloco' e abre na tela nova."""
        n, block, accent = floor
        st = Stage()
        label = st.enter(ft.Column([
            ft.Icon(ft.Icons.STAIRS, color=accent, size=44),
            display(f"Andar {n}", 44, ACCENT, align=ft.TextAlign.CENTER),
            display(block, 20, accent, align=ft.TextAlign.CENTER),
        ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            dy=0.35, scale=0.7, ms=480, curve=BACK, delay=120)
        self.curtain.content = label
        self.curtain.visible, self.curtain.opacity = True, 0
        self.page.update()
        await asyncio.sleep(0.03)
        self.curtain.animate_opacity = A(260, IN)
        self.curtain.opacity = 1
        self.page.update()
        await st.play(self.page, lead=0.05)
        self.root.content = control
        self.root.opacity, self.root.offset = 1, ft.Offset(0, 0)
        self.page.update()
        await asyncio.sleep(0.55)
        self.curtain.animate_opacity = A(380, OUT)
        self.curtain.opacity = 0
        self.page.update()
        if stage:
            await stage.play(self.page, lead=0.08)
        await asyncio.sleep(0.3)
        self.curtain.visible = False
        self.curtain.content = None
        self.page.update()

    def rise(self, st: Stage, controls: list, delay=0, step=55, dy=0.22, ms=420) -> list:
        """Entrada padrão de uma tela: cada bloco sobe e aparece, um atrás do outro."""
        out = []
        for c in controls:
            if isinstance(c, ft.Container) and c.expand and c.content is None:
                out.append(c)  # espaçador
                continue
            out.append(st.enter(c, dy=dy, ms=ms, delay=delay))
            delay += step
        return out

    def typed(self, text: str, size=13, color=TEXT, delay=0.25, cps=55, align=None) -> Typewriter:
        """Texto que aparece aos poucos depois que a tela entra (pula com toque no painel)."""
        tw = Typewriter(text, size, color, cps=cps, align=align)
        g = self.gen + 1  # o show() que vem a seguir incrementa
        self.task(self._type_later, tw, g, delay)
        return tw

    async def _type_later(self, tw: Typewriter, g: int, delay: float):
        await asyncio.sleep(delay)
        await tw.run(alive=lambda: self.gen == g)

    async def _idle_bob(self, control: ft.Control, g: int, dy=0.035, period=1.5):
        """Balanço lento contínuo (logo do menu) enquanto a tela for a mesma."""
        control.animate_offset = A(int(period * 1000), INOUT)
        up = False
        await asyncio.sleep(0.9)
        while self.gen == g:
            control.offset = ft.Offset(0, dy if up else 0)
            up = not up
            try:
                control.update()
            except Exception:
                return
            await asyncio.sleep(period)

    def scene(self, controls: list, bg: str | None = None, scroll=True, padding=12, shade=0.45) -> ft.Control:
        """Cenário ao fundo, véu escuro por cima (mais forte embaixo) e o conteúdo na frente."""
        bg = bg or self.theme()["bg"]
        column = ft.Column(controls, spacing=10, expand=True,
                           horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                           scroll=ft.ScrollMode.AUTO if scroll else None)
        return ft.Stack([
            ft.Image(src=bg, fit=ft.BoxFit.COVER, left=0, top=0, right=0, bottom=0),
            ft.Container(left=0, top=0, right=0, bottom=0, gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                colors=[alpha(INK, shade * 0.5), alpha(INK, shade), alpha(INK, min(0.92, shade + 0.35))],
                stops=[0.0, 0.55, 1.0])),
            ft.Container(left=0, top=0, right=0, bottom=0, padding=padding, content=column),
        ], expand=True)

    def screen(self, controls: list, scroll=True) -> ft.Control:
        return self.scene(controls, scroll=scroll)

    def header(self, subtitle: str | None = None, right: ft.Control | None = None):
        run = self.run
        left = []
        if run and run.floor:
            left.append(ft.Row([
                display(f"Andar {run.floor}", 18),
                txt(f"/ {len(run.floors)}", 11, MUTED),
                txt("·", 11, MUTED),
                txt(run.block_info()["name"], 12, self.theme()["accent"], ft.FontWeight.BOLD),
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.END))
        else:
            left.append(display("CapiTower", 20))
        if subtitle:
            left.append(txt(subtitle, 12, MUTED))
        head = ft.Row([ft.Column(left, spacing=2, expand=True)] + ([right] if right else []),
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        if run and run.floor:
            head = ft.Column([head, bar(run.floor / len(run.floors), self.theme()["accent"], 4)], spacing=4)
        return ft.Container(content=head, bgcolor=alpha(INK, 0.6), border_radius=ft.BorderRadius.all(10),
                            padding=ft.Padding.symmetric(horizontal=10, vertical=6))

    def status_line(self):
        run = self.run
        chips = [
            chip("hp", f"{run.hp}/{run.max_hp}"),
            chip("level", run.level, label=f"{run.cls['ability']} nível {run.level}"),
            chip("deck", len(run.full_deck())),
        ]
        for m in run.modifiers:
            name, effect = content.MODIFIERS[m]
            chips.append(ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.GPP_GOOD, color=GOOD, size=15), txt(name, 11, GOOD)], spacing=3, tight=True),
                tooltip=effect,
            ))
        return panel(ft.Row(chips, spacing=12, wrap=True), padding=8)

    def dialog(self, title_text: str, body: ft.Control):
        dlg = ft.AlertDialog(
            title=display(title_text, 18),
            content=ft.Container(content=body, width=360, height=460),
            bgcolor="#1a2620",
            actions=[ft.TextButton(content=txt("Fechar", 13, ACCENT), on_click=lambda e: self.page.pop_dialog())],
        )
        self.page.show_dialog(dlg)

    def show_deck(self, e=None):
        run = self.run
        cards = sorted(run.full_deck(), key=lambda c: (c.arch, c.cost, c.name))
        rows = ft.Column([card_view(c, width=150, height=224) for c in cards], spacing=8,
                         scroll=ft.ScrollMode.AUTO, wrap=True, run_spacing=8)
        self.dialog(f"Deck ({len(cards)} cartas)", rows)

    # ------------------------------------------------------------ menu
    def show_menu(self, e=None):
        self.run = None
        self.combat = None
        st = Stage()
        r = self.records
        records = panel(ft.Row([
            chip("floor", r["best_floor"], label="Melhor andar"),
            chip("runs", r["runs"]),
            chip("wins", r["wins"]),
            chip("points", r["total_points"]),
        ], spacing=16, wrap=True, alignment=ft.MainAxisAlignment.CENTER)) if r["runs"] else ft.Container()
        logo = ft.Container(content=ft.Image(src="logo.png", fit=ft.BoxFit.CONTAIN), height=120,
                            padding=ft.Padding.symmetric(horizontal=16))
        st.enter(logo, dy=-0.5, scale=1.35, ms=650, curve=BACK)
        body = self.rise(st, [
            txt("Tower crawler roguelike de deck building.", 13, TEXT, align=ft.TextAlign.CENTER),
            ft.Container(expand=True),
            panel(txt("Uma família de capivaras caiu num poço de esteroides e virou uma trupe maligna "
                      "de super capivaras. A torre delas tem 50 andares, e no topo está a Soberana "
                      "Gertrudes. Você sobe, elas não gostam.", 12)),
            panel(ft.Column([
                icon_line(ft.Icons.BOLT, "3 de Ação por turno, mão de 5 cartas.", size=11, icon_color=ACCENT),
                icon_line(ft.Icons.STYLE, "Deck começa com 10 cartas e só cresce por recompensa.", size=11, icon_color=ACCENT),
                icon_line(ft.Icons.MILITARY_TECH, "Elite ou chefe: carta nova OU +1 nível da habilidade.", size=11, icon_color=ACCENT),
                icon_line(ft.Icons.STAIRS, "Permadeath. O andar alcançado vira pontos de meta.", size=11, icon_color=ACCENT),
            ], spacing=4)),
            records,
            wide(button("Nova run", self.show_class_select, icon=ft.Icons.PLAY_ARROW)),
        ], delay=200, step=80)
        self.show(self.scene([ft.Container(height=6), logo, *body, ft.Container(height=4)],
                             bg=MENU_BG, scroll=False, shade=0.25), stage=st)
        self.task(self._idle_bob, logo, self.gen, 0.045, 1.6)

    # ------------------------------------------------------ escolher classe
    def show_class_select(self, e=None):
        st = Stage()
        items = []
        for k, (cid, c) in enumerate(content.CLASSES.items()):
            portrait = ft.Container(
                content=ft.Image(src=c["image"], fit=ft.BoxFit.CONTAIN), width=104, height=104,
                bgcolor=alpha(ACCENT, 0.12), border_radius=ft.BorderRadius.all(52),
                border=ft.Border.all(2, alpha(ACCENT, 0.6)),
            )
            st.enter(portrait, scale=0.4, ms=520, curve=BACK, delay=160 + k * 110)
            items.append(st.enter(panel(
                ft.Row([
                    portrait,
                    ft.Column([
                        display(c["name"], 20),
                        txt(c["tagline"], 11, MUTED),
                        txt(c["mechanic"], 11, TEXT, max_lines=4),
                        ft.Row([ft.Icon(ft.Icons.MILITARY_TECH, color=ACCENT, size=14), txt(c["ability"], 11, ACCENT)], spacing=4),
                    ], spacing=3, expand=True),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                on_click=lambda e, cid=cid: self.pick_class(cid), padding=12,
            ), dx=0.35 if k % 2 == 0 else -0.35, ms=460, delay=80 + k * 110))
        self.show(self.scene([
            self.header("Escolha sua capivara"),
            *items,
            ft.Container(expand=True),
            st.enter(button("Voltar", self.show_menu, icon=ft.Icons.ARROW_BACK, primary=False), dy=0.4, delay=450),
        ], bg=MENU_BG, shade=0.55), stage=st)

    def pick_class(self, cid: str):
        if self.busy:
            return
        self.run = Run(cid)
        self._reroll_idx = None
        self.show_starting_draw()

    # ----------------------------------------------------- sorteio inicial
    def show_starting_draw(self, e=None):
        run = self.run
        st = Stage()
        hint = (icon_line(ft.Icons.REFRESH, "Toque numa carta para trocar (uma vez só). Cada carta entra em 2 cópias.", MUTED, 11)
                if not run.rerolled else icon_line(ft.Icons.CHECK, "Troca usada. Cada carta entra em 2 cópias.", MUTED, 11))
        fresh = self._reroll_idx is None
        views = []
        for i, c in enumerate(run.starting):
            v = card_view(c, on_click=(None if run.rerolled else (lambda e, i=i: self.reroll(i))), width=130, height=194)
            if fresh:
                st.enter(v, dy=1.4, scale=0.5, rotate=-0.5, ms=520, curve=BACK, delay=200 + i * 90)
            elif i == self._reroll_idx:
                st.enter(v, scale=0.2, rotate=0.8, ms=520, curve=BACK, delay=60)
            views.append(v)
        self._reroll_idx = None
        cards = ft.Row(views, wrap=True, spacing=8, run_spacing=8, alignment=ft.MainAxisAlignment.CENTER)
        ability = panel(ft.Column([
            heading(ft.Icons.MILITARY_TECH, f"{run.cls['ability']} nível 1", size=14),
            txt(run.cls["ability_text"][1], 12),
        ], spacing=3))
        go = wide(button("Entrar na torre", self.enter_tower, icon=ft.Icons.STAIRS))
        back = button("Voltar", self.show_class_select, icon=ft.Icons.ARROW_BACK, primary=False)
        if fresh:
            self.rise(st, [ability, go, back], delay=650, step=90)
        self.show(self.scene([
            self.header(f"{run.cls['name']} · sorteio inicial"),
            hint, cards, ability, go, back,
        ], bg=BLOCK_THEMES[0]["bg"]), stage=st, fade=fresh)

    def reroll(self, idx: int):
        if self.busy:
            return
        self.run.reroll(idx)
        self._reroll_idx = idx
        self.show_starting_draw()

    def enter_tower(self, e=None):
        if self.busy:
            return
        self.run.build_starting_deck()
        self.next_floor()

    # ------------------------------------------------------------- andar
    def next_floor(self, e=None):
        if self.busy:
            return
        run = self.run
        if run.is_last_floor():
            return self.show_end()
        run.advance()
        self.show_floor_preview(run.current())

    def show_floor_preview(self, f: dict):
        run = self.run
        t = f["type"]
        icon, label, desc = FLOOR[t]
        block = run.block_info()
        accent = self.theme()["accent"]
        st = Stage()
        lines = [heading(icon, label), txt(desc, 12, MUTED)]
        preview = None
        if "enemies" in f:
            sprites = []
            for k, eid in enumerate(dict.fromkeys(f["enemies"])):
                ed = content.ENEMIES[eid]
                n = f["enemies"].count(eid)
                name = ed.name + (f" ×{n}" if n > 1 else "")
                sprite = enemy_sprite(ed, 96 if ed.flags.get("boss") else 72, accent)
                st.enter(sprite, dy=-0.6, scale=0.6, ms=560, curve=ft.AnimationCurve.BOUNCE_OUT, delay=250 + k * 140)
                sprites.append(ft.Column([
                    sprite,
                    txt(name, 11, ACCENT if ed.flags.get("boss") else TEXT, ft.FontWeight.BOLD,
                        align=ft.TextAlign.CENTER, max_lines=2),
                    txt(ed.note, 10, MUTED, align=ft.TextAlign.CENTER, max_lines=2) if ed.note else ft.Container(),
                ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=110))
            preview = ft.Row(sprites, spacing=8, alignment=ft.MainAxisAlignment.CENTER,
                             vertical_alignment=ft.CrossAxisAlignment.END, wrap=True)
        if t == "challenge":
            lines.append(icon_line(ft.Icons.WARNING_AMBER, content.CHALLENGES[f["challenge"]], HP, 12))

        actions = []
        if t in ("combat", "elite", "boss", "final"):
            actions.append(button("Lutar", lambda e: self.start_combat(f["enemies"]), icon=ft.Icons.SPORTS_MMA, expand=True))
        elif t == "challenge":
            actions.append(button("Aceitar", lambda e: self.start_combat(f["enemies"], f["challenge"]), icon=ft.Icons.FLAG, expand=True))
            actions.append(button("Pular", self.next_floor, icon=ft.Icons.SKIP_NEXT, primary=False, expand=True))
        elif t == "rest":
            actions.append(button("Descansar", self.do_rest, icon=ft.Icons.HOTEL, expand=True))
        elif t == "event":
            actions.append(button("Ver o que é", lambda e: self.show_event(f["event"]), icon=ft.Icons.HELP_OUTLINE, expand=True))

        head = [self.header(), self.status_line(),
                panel(ft.Column([txt(block["name"], 13, accent, ft.FontWeight.BOLD), txt(block["desc"], 11, MUTED)], spacing=2), padding=8)]
        foot = self.rise(st, [panel(ft.Column(lines, spacing=6)), ft.Row(actions, spacing=8),
                              button("Ver deck", self.show_deck, icon=ft.Icons.STYLE, primary=False)], delay=500, step=90)
        self.show(self.scene([
            *self.rise(st, head, delay=300, step=70, dy=-0.3),
            ft.Container(content=preview, expand=True, alignment=ft.Alignment.BOTTOM_CENTER) if preview else ft.Container(expand=True),
            *foot,
        ], scroll=False), stage=st, floor=(run.floor, block["name"], accent))

    def do_rest(self, e=None):
        if self.busy:
            return
        before = self.run.hp
        self.run.heal_pct(0.30)
        st = Stage()
        heal = st.enter(ft.Row([ft.Icon(ft.Icons.HEALING, color=GOOD, size=18),
                                display(f"+{self.run.hp - before} de vida", 16, GOOD)], spacing=6),
                        scale=0.3, ms=600, curve=BACK, delay=350)
        self.show(self.scene([
            self.header(),
            self.status_line(),
            ft.Container(expand=True),
            *self.rise(st, [panel(ft.Column([heading(ft.Icons.HOTEL, "Descanso"), heal], spacing=6)),
                            wide(button("Continuar", self.next_floor, icon=ft.Icons.ARROW_UPWARD))], delay=150),
        ], scroll=False), stage=st)

    # ------------------------------------------------------------ eventos
    def show_event(self, ev: dict):
        if self.busy:
            return
        st = Stage()
        tw = self.typed(ev["text"], 13, delay=0.45)
        choices = [wide(button(label, lambda e, k=key: self.resolve_event(ev, k), primary=False))
                   for label, key in ev["choices"]]
        story = panel(ft.Column([heading(ft.Icons.HELP_OUTLINE, ev["title"]), tw.control], spacing=6),
                      on_click=lambda e: tw.finish())
        self.show(self.scene([
            self.header(),
            self.status_line(),
            ft.Container(expand=True),
            *self.rise(st, [story, *choices], delay=150, step=140),
        ], scroll=False), stage=st)

    def resolve_event(self, ev: dict, key: str):
        if self.busy:
            return
        run = self.run
        msg = "Nada acontece."
        if key == "heal20_risk":
            run.heal_pct(0.20)
            if run.rng.random() < 0.5:
                run.weak_next_combat = 2
                msg = "Cura 20%... e a barriga reclama. Fraqueza no próximo combate."
            else:
                msg = "Cura 20%. Água boa, no fim das contas."
        elif key == "heal10_later":
            run.heal_pct(0.10)
            run.heal_after_combat = int(run.max_hp * 0.10)
            msg = "Cura 10% agora e mais 10% depois do próximo combate."
        elif key == "strength_for_hp":
            run.hp = max(1, run.hp - 8)
            run.perm_strength += 1
            msg = "Perde 8 de vida. +1 de Força permanente na run."
        elif key == "temp_card":
            c = run.random_temp_card()
            run.temp_cards.append(c)
            msg = f"Achou {c.name}. Fica no deck até o próximo chefe."
        elif key == "heal15":
            run.heal_pct(0.15)
            msg = "Cura 15%. O cheiro você leva junto."
        st = Stage()
        tw = self.typed(msg, 13, delay=0.4)
        self.show(self.scene([
            self.header(),
            self.status_line(),
            ft.Container(expand=True),
            *self.rise(st, [panel(ft.Column([heading(ft.Icons.HELP_OUTLINE, ev["title"]), tw.control], spacing=6),
                                  on_click=lambda e: tw.finish()),
                            wide(button("Continuar", self.next_floor, icon=ft.Icons.ARROW_UPWARD))], delay=150, step=200),
        ], scroll=False), stage=st)

    # ------------------------------------------------------------ combate
    def start_combat(self, enemies: list[str], challenge: str | None = None):
        if self.busy:
            return
        self.combat = Combat(self.run, enemies, challenge)
        self.combats_played += 1
        self.selected = None
        self._prev_hand = []
        t = self.run.current()["type"]
        if t in ("boss", "final", "elite"):
            names = " & ".join(dict.fromkeys(content.ENEMIES[e].name for e in enemies))
            self.banner = ("Elite" if t == "elite" else "Chefe", names)
        self.render_combat(entering=True)

    def player_chips(self, c: Combat) -> list[ft.Control]:
        chips = [chip("def", c.block), chip("action", c.actions)]
        if c.cls == "capimaga":
            chips.append(chip("minions", f"{c.minions}/{content.MINION_CAP}"))
        elif c.cls == "brutamontes":
            chips.append(chip("adren", f"{c.adrenaline}/{c.adren_cap}"))
        else:
            chips.append(chip("impulso", c.played_this_turn))
        for key, val in (("strength", c.strength), ("weak", c.weak), ("frail", c.frail), ("poison", c.poison),
                         ("evasion", c.evasion)):
            if val:
                chips.append(chip(key, val, 12))
        if c.retaliation:
            chips.append(chip("retaliation", f"{c.retaliation} ({c.retaliation_turns}t)", 12))
        if c.next_free:
            chips.append(chip("free", "0", 12))
        return chips

    # números flutuantes: o que mudou entre antes e depois de uma ação
    def _snapshot(self) -> dict:
        c = self.combat
        return {"enemies": [(e.hp, e.block, e.alive) for e in c.enemies], "hp": c.hp, "block": c.block}

    def _diff(self, before: dict) -> dict:
        c = self.combat
        fx = {}
        for i, e in enumerate(c.enemies):
            hp0, bl0, alive0 = before["enemies"][i]
            items = []
            if e.hp < hp0:
                items.append((f"-{hp0 - e.hp}", HP))
            elif e.hp > hp0:
                items.append((f"+{e.hp - hp0}", GOOD))
            if e.block > bl0:
                items.append((f"+{e.block - bl0}", DEF))
            if items:
                fx[("enemy", i)] = items
            if alive0 and not e.alive:
                fx[("died", i)] = True
        items = []
        if c.hp < before["hp"]:
            items.append((f"-{before['hp'] - c.hp}", HP))
        elif c.hp > before["hp"]:
            items.append((f"+{c.hp - before['hp']}", GOOD))
        if c.block > before["block"]:
            items.append((f"+{c.block - before['block']}", DEF))
        if items:
            fx[("player",)] = items
        return fx

    def _fx_layer(self, items: list, width: float, base_top: float) -> list[ft.Control]:
        """Números que pipocam, sobem e somem; animados depois do primeiro update."""
        out = []
        for k, (label, color) in enumerate(items):
            t = ft.Container(
                left=0, top=base_top - k * 22, width=width, alignment=ft.Alignment.CENTER,
                content=display(label, 26 if color == HP else 22, color),
                scale=0.5,
                animate_offset=A(1100, OUT), animate_opacity=A(1100, IN), animate_scale=A(260, BACK),
            )
            self._fx.append(t)
            out.append(t)
        return out

    async def _animate_fx(self, fx: list, shakes: list, flashes: list, punches: list, vignette):
        await asyncio.sleep(0.05)
        for t in fx:
            t.offset = ft.Offset(0, -1.6)
            t.opacity = 0
            t.scale = 1.0
        for f in flashes:
            f.opacity = 0.75
        for p in punches:
            p.scale = 1.14
        if vignette is not None:
            vignette.opacity = 1
        for s in shakes:
            s.offset = ft.Offset(0.06, 0)
        every = fx + flashes + punches + shakes + ([vignette] if vignette is not None else [])
        flush(self.page, every)
        for k, dx in enumerate((-0.06, 0.04, 0)):
            await asyncio.sleep(0.07)
            for s in shakes:
                s.offset = ft.Offset(dx, 0)
            if k == 0:
                for f in flashes:
                    f.opacity = 0
                for p in punches:
                    p.scale = 1.0
                if vignette is not None:
                    vignette.opacity = 0
            flush(self.page, every if k == 0 else shakes)

    async def _fade_after(self, control: ft.Control, g: int, delay: float, ms: int = 600):
        await asyncio.sleep(delay)
        if self.gen != g:
            return  # tela ja trocou: o controle esta fora da arvore e o flush cairia num page.update inteiro
        control.opacity = 0
        flush(self.page, [control])
        await asyncio.sleep(ms / 1000)
        if self.gen != g:
            return
        # opacidade 0 nao basta: o overlay continua no Stack engolindo os toques
        control.visible = False
        flush(self.page, [control])

    async def _finish_later(self, delay: float):
        await asyncio.sleep(delay)
        self.finish_combat()

    def render_combat(self, fx: dict | None = None, entering=False, toast: str | None = None):
        c = self.combat
        run = self.run
        fx = fx or {}
        over = c.status != "ongoing"
        if over and not fx and not entering:
            return self.finish_combat()
        self._fx: list[ft.Control] = []
        shakes: list[ft.Control] = []
        flashes: list[ft.Control] = []
        punches: list[ft.Control] = []
        st = Stage()
        W = self.frame.width or 430
        accent = self.theme()["accent"]

        # ---- palco: inimigos em pé no cenário
        n = max(1, len(c.enemies))
        ew = min(160, (W - 24 - 6 * (n - 1)) / n)
        self._enemy_sprites = {}
        views = [self.enemy_view(i, e, ew, accent, fx, shakes, flashes, punches, st) for i, e in enumerate(c.enemies)]
        if entering:
            for k, v in enumerate(views):
                st.enter(v, dx=0.7, dy=-0.15, ms=520, curve=BACK, delay=150 + k * 120)
        enemies = ft.Row(views, spacing=6, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.END)
        stage = ft.Container(content=enemies, expand=True, alignment=ft.Alignment.BOTTOM_CENTER,
                             padding=ft.Padding.only(bottom=6))

        # ---- jogador
        powers = ft.Row([
            ft.Container(content=ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, color=KIND_COLORS["Poder"], size=14),
                                         txt(POWER_NAMES[p], 11, "#c9a7ee")], spacing=3, tight=True),
                         tooltip="Poder em campo")
            for p in c.powers
        ], spacing=8, wrap=True) if c.powers else None
        player_fx = fx.get(("player",), [])
        hit = any(col == HP for _, col in player_fx)
        blocked = any(col == DEF for _, col in player_fx)
        ring = ft.Container(width=72, height=72, bgcolor=alpha(ACCENT, 0.15), border_radius=ft.BorderRadius.all(36),
                            border=ft.Border.all(2, alpha(DEF if blocked else ACCENT, 0.9 if blocked else 0.7)),
                            content=ft.Image(src=run.cls["image"], fit=ft.BoxFit.CONTAIN),
                            animate_scale=A(200, BACK))
        portrait_layers = [ring]
        if hit:
            flash = ft.Container(width=72, height=72, bgcolor=HP, border_radius=ft.BorderRadius.all(36), opacity=0,
                                 animate_opacity=A(120, OUT))
            portrait_layers.append(flash)
            flashes.append(flash)
        if player_fx and not hit:
            punches.append(ring)
        if player_fx:
            portrait_layers += self._fx_layer(player_fx, 72, 10)
        portrait = ft.Stack(portrait_layers, width=72, height=72)
        if hit:
            portrait.animate_offset = A(70, OUT)
            shakes.append(portrait)
        if over and c.status == "lost":
            portrait.animate_rotation, portrait.animate_opacity = A(700, IN), A(700, IN)
            st.add(portrait, delay=200, rotate=0.6, opacity=0.3)
        info = [
            ft.Row([display(run.cls["name"], 15), ft.Container(expand=True),
                    hp_bar(c.hp, c.max_hp, min(150, W * 0.38))],
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row(self.player_chips(c), spacing=10, wrap=True),
        ]
        if powers:
            info.append(powers)
        player = panel(ft.Row([portrait, ft.Column(info, spacing=4, expand=True)],
                              spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=8)

        # ---- faixa do meio: carta selecionada (com botão jogar) ou o log
        if self.selected is not None and self.selected < len(c.hand) and not over:
            card = c.hand[self.selected]
            cost = c.cost_of(card)
            reason = c.block_reason(card)
            info = [
                ft.Row([chip("action", cost, 12), display(card.name, 14, KIND_COLORS[card.kind]),
                        txt(card.arch, 10, MUTED)], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                txt(card.text, 11, TEXT, max_lines=3),
            ]
            if reason is not None:
                info.append(txt(reason, 10, MUTED))
            middle = panel(ft.Row([
                ft.Column(info, spacing=2, expand=True),
                button("Jogar", lambda e, i=self.selected: self.play_card(i), icon=ft.Icons.TOUCH_APP,
                       disabled=not c.can_play(card)),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=8, border_color=alpha(ACCENT, 0.6))
            st.enter(middle, dy=0.25, ms=220)
        else:
            lines = [l for l in c.log if not l.startswith("---")][-2:] or ["..."]
            if self.combats_played == 1 and c.turn == 1 and not over:
                lines = ["Toque num inimigo para mirar. Toque numa carta para ver, toque de novo para jogar."]
            middle = panel(ft.Column([txt(line, 11, MUTED, max_lines=1) for line in lines], spacing=1), padding=8)

        # ---- mão em leque
        hand = self.hand_view(c, W, st)

        footer = ft.Row([
            ft.Row([chip("draw", len(c.draw_pile), 11, bold=False), chip("discard", len(c.discard), 11, bold=False)], spacing=10),
            button("Encerrar turno", self.end_turn, icon=ft.Icons.SKIP_NEXT, disabled=over),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        if entering:
            st.enter(player, dy=0.6, ms=450, delay=350)
            st.enter(middle, dy=0.6, ms=450, delay=420)
            st.enter(footer, dy=0.8, ms=450, delay=500)

        layers = [self.scene([
            self.header(right=chip("turn", c.turn, 12, bold=False)),
            stage,
            player,
            middle,
            hand,
            footer,
        ], scroll=False, shade=0.3)]

        # ---- vinheta vermelha quando o jogador apanha
        vignette = None
        if hit:
            vignette = ft.Container(left=0, right=0, top=0, bottom=0, opacity=0, animate_opacity=A(140, OUT),
                                    gradient=ft.RadialGradient(colors=[alpha(HP, 0.0), alpha(HP, 0.55)], radius=0.95))
            layers.append(vignette)

        # ---- aviso de turno novo
        if toast:
            pill = ft.Container(
                top=64, left=0, right=0, alignment=ft.Alignment.CENTER,
                content=ft.Container(content=display(toast, 22), bgcolor=alpha(INK, 0.85),
                                     padding=ft.Padding.symmetric(horizontal=18, vertical=6),
                                     border=ft.Border.all(2, ACCENT), border_radius=ft.BorderRadius.all(14)),
                animate_opacity=A(400, IN),
            )
            st.enter(pill, dy=-0.8, scale=0.6, ms=450, curve=BACK)
            layers.append(pill)
            # gen + 1: o show() no fim deste metodo incrementa self.gen (mesmo padrao de typed())
            self.task(self._fade_after, pill, self.gen + 1, 1.0, 400)

        # ---- banner de chefe / elite
        if self.banner:
            kind, names = self.banner
            self.banner = None
            banner = ft.Container(
                left=0, right=0, top=0, bottom=0, alignment=ft.Alignment.CENTER,
                animate_opacity=A(600, IN),
                content=st.enter(ft.Container(
                    bgcolor=alpha(INK, 0.85), padding=ft.Padding.symmetric(horizontal=24, vertical=16),
                    border=ft.Border.all(3, ACCENT), border_radius=ft.BorderRadius.all(16),
                    content=ft.Column([
                        display(kind, 18, MUTED, align=ft.TextAlign.CENTER),
                        display(names, 30, ACCENT, align=ft.TextAlign.CENTER, max_lines=2),
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                ), scale=0.4, dy=0.3, ms=650, curve=BACK, delay=250),
            )
            layers.append(banner)
            self.task(self._fade_after, banner, self.gen + 1, 1.7)

        self.show(ft.Stack(layers, expand=True), fade=entering, stage=st)
        if self._fx or shakes or flashes or punches:
            self.task(self._animate_fx, list(self._fx), shakes, flashes, punches, vignette)
        if over:
            self.busy = True
            self.task(self._finish_later, 1.3 if c.status == "won" else 1.6)

    def enemy_view(self, idx: int, e: Enemy, ew: float, accent: str, allfx: dict, shakes: list,
                   flashes: list, punches: list, st: Stage):
        c = self.combat
        fx = allfx.get(("enemy", idx))
        died = allfx.get(("died", idx), False)
        targeted = idx == c.target and (e.alive or died)
        n = len(c.enemies)
        size = min(ew * 0.85, {1: 130, 2: 104}.get(n, 84) * (1.15 if e.is_boss else 1.0))
        if e.edef.id in ENEMY_ART:
            size = min(ew * 0.95, 170)
        statuses = [chip(k, v, 11) for k, v in (("strength", e.strength), ("weak", e.weak),
                                                 ("frail", e.frail), ("poison", e.poison)) if v]
        if e.block:
            statuses.insert(0, chip("def", e.block, 11))

        # intenção do próximo turno, num balão acima da cabeça
        if e.alive:
            parts = []
            for kind, short, desc in e.intent_parts():
                icon, color = INTENT[kind]
                parts.append(ft.Container(
                    content=ft.Row([ft.Icon(icon, color=color, size=16), txt(short, 12, color, ft.FontWeight.BOLD)],
                                   spacing=2, tight=True),
                    tooltip=desc,
                ))
            intent = ft.Container(content=ft.Row(parts, spacing=6, tight=True), bgcolor=alpha(INK, 0.85),
                                  padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                  border_radius=ft.BorderRadius.all(10), border=ft.Border.all(1, LINE),
                                  tooltip="Intenção do próximo turno")
            if fx:
                st.enter(intent, scale=0.5, dy=0.4, ms=380, curve=BACK, delay=350)
        else:
            intent = ft.Container(height=24)

        # sprite com anel de alvo no chão, flash de impacto e números flutuantes
        sprite = ft.Container(content=enemy_sprite(e.edef, size, accent), left=0, top=6, width=size, height=size,
                              opacity=1.0 if (e.alive or died) else 0.25,
                              animate_offset=A(70, OUT), animate_scale=A(200, BACK))
        self._enemy_sprites[idx] = sprite
        hit = bool(fx) and any(col == HP for _, col in fx)
        if hit:
            shakes.append(sprite)
            punches.append(sprite)
        if died:
            sprite.animate_opacity, sprite.animate_rotation, sprite.animate_offset = A(650, IN), A(650, IN), A(650, IN)
            st.add(sprite, delay=280, opacity=0.35, rotate=ft.Rotate(0.5, alignment=ft.Alignment.BOTTOM_CENTER),
                   offset=ft.Offset(0.1, 0.12))
        ring = ft.Container(left=size * 0.05, top=size * 0.86, width=size * 0.9, height=size * 0.24,
                            bgcolor=alpha(ACCENT if targeted else INK, 0.55 if targeted else 0.35),
                            border_radius=ft.BorderRadius.all(size),
                            border=ft.Border.all(2, ACCENT) if targeted else None)
        if targeted and e.alive:
            st.enter(ring, scale=0.7, opacity=None, ms=300, curve=BACK)
        layers = [ring, sprite]
        if hit:
            flash = ft.Container(left=0, top=6, width=size, height=size, bgcolor="#ffffff", opacity=0,
                                 border_radius=ft.BorderRadius.all(size * 0.3), animate_opacity=A(110, OUT))
            layers.append(flash)
            flashes.append(flash)
        if fx:
            layers += self._fx_layer(fx, size, size * 0.2)
        sprite_stack = ft.Stack(layers, width=size, height=size + 10)

        body = ft.Column([
            intent,
            sprite_stack,
            ft.Row([ft.Icon(ft.Icons.MY_LOCATION, color=ACCENT, size=13) if targeted else ft.Container(),
                    txt(e.name, 11, ACCENT if (e.is_boss or targeted) else TEXT, ft.FontWeight.BOLD,
                        align=ft.TextAlign.CENTER, max_lines=2)],
                   spacing=3, tight=True, alignment=ft.MainAxisAlignment.CENTER),
            hp_bar(e.hp, e.max_hp, ew - 8, height=14) if (e.alive or died) else txt("Derrotado", 11, MUTED),
            ft.Row(statuses, spacing=6, wrap=True, alignment=ft.MainAxisAlignment.CENTER) if statuses else ft.Container(),
        ], spacing=3, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        return ft.Container(
            content=body, width=ew, padding=ft.Padding.symmetric(horizontal=2, vertical=4),
            on_click=(lambda ev, i=idx: self.select_target(i)) if e.alive else None,
        )

    def hand_view(self, c: Combat, W: float, st: Stage) -> ft.Control:
        """Leque. Cartas que já estavam na mão deslizam da posição antiga; as novas saem da pilha
        de compra (canto inferior esquerdo) girando e crescendo."""
        cw, ch = self.HAND_CARD
        lift = self.HAND_LIFT
        n = len(c.hand)
        avail = W - 24
        self._hand_ctrls = {}
        self._hand_geom = (cw, ch, lift, avail)
        if n == 0:
            self._prev_hand = []
            return ft.Container(height=ch + lift, alignment=ft.Alignment.CENTER,
                                content=txt("Mão vazia" if c.status == "ongoing" else "", 12, MUTED))
        step = min(cw + 6, (avail - cw) / (n - 1)) if n > 1 else 0
        total = cw + step * (n - 1)
        x0 = (avail - total) / 2
        overlap = step < cw
        layers = []
        order = list(range(n))
        if self.selected is not None and self.selected in order:
            order.remove(self.selected)
            order.append(self.selected)  # selecionada por cima das outras
        prev = list(self._prev_hand)
        new_hand = []
        fresh = 0
        for i in order:
            card = c.hand[i]
            sel = i == self.selected
            angle = (i - (n - 1) / 2) * 0.05 if overlap else 0
            left, top = x0 + i * step, (0 if sel else lift)
            rot = ft.Rotate(0 if sel else angle, alignment=ft.Alignment.BOTTOM_CENTER)
            holder = ft.Container(
                left=left, top=top, rotate=rot,
                content=card_view(card, on_click=lambda e, i=i: self.tap_card(i), cost=c.cost_of(card),
                                  playable=c.can_play(card), reason=c.block_reason(card),
                                  width=cw, height=ch, raised=sel),
            )
            match = next((p for p in prev if p[0] == card), None)
            if match:
                prev.remove(match)
                _, pl, pt, pa = match
                if (pl, pt) != (left, top):
                    st.move(holder, pl, pt, ms=260)
                if pa != rot.angle:
                    holder.animate_rotation = A(260, OUT)
                    st.add(holder, rotate=rot)
                    holder.rotate = ft.Rotate(pa, alignment=ft.Alignment.BOTTOM_CENTER)
            else:
                st.move(holder, -cw * 0.4, ch + lift, ms=460, curve=BACK, delay=90 + fresh * 80)
                st.enter(holder, scale=0.45, rotate=-0.7, ms=460, curve=BACK, delay=90 + fresh * 80)
                fresh += 1
            self._hand_ctrls[i] = holder
            new_hand.append((card, left, top, rot.angle))
            layers.append(holder)
        self._prev_hand = new_hand
        return ft.Stack(layers, height=ch + lift, width=avail)

    def select_target(self, idx: int):
        if self.busy:
            return
        self.combat.select_target(idx)
        self.render_combat()

    def tap_card(self, idx: int):
        if self.busy:
            return
        # primeiro toque seleciona (mostra o texto inteiro), segundo toque joga
        if self.selected == idx and self.combat.can_play(self.combat.hand[idx]):
            return self.play_card(idx)
        self.selected = None if self.selected == idx else idx
        self.render_combat()

    def play_card(self, idx: int):
        if self.busy or not self.combat.can_play(self.combat.hand[idx]):
            return
        self.busy = True
        self.task(self._play_card, idx)

    async def _play_card(self, idx: int):
        """A carta sobe até o meio, cresce, e voa conforme o tipo: Ataque no alvo, Defesa no
        retrato, Poder explode em brilho, Utilidade sobe e some. Só então o efeito resolve."""
        c = self.combat
        card = c.hand[idx]
        holder = self._hand_ctrls.get(idx)
        if holder is not None:
            cw, ch, lift, avail = self._hand_geom
            holder.animate_position = A(240, OUT)
            holder.animate_scale = A(240, BACK)
            holder.animate_rotation = A(200, OUT)
            holder.left, holder.top = (avail - cw) / 2, -ch * 0.45
            holder.scale = 1.22
            holder.rotate = ft.Rotate(0, alignment=ft.Alignment.BOTTOM_CENTER)
            flush(self.page, [holder])
            await asyncio.sleep(0.27)
            holder.animate_offset = A(300, IN)
            holder.animate_scale = A(300, IN)
            holder.animate_opacity = A(260, IN)
            if card.kind == "Ataque":
                n = max(1, len(c.enemies))
                ew = min(160, ((self.frame.width or 430) - 24 - 6 * (n - 1)) / n)
                row_w = n * ew + 6 * (n - 1)
                tx = (avail - row_w) / 2 + c.target * (ew + 6) + ew / 2
                holder.offset = ft.Offset((tx - avail / 2) / cw, -2.6)
                holder.scale, holder.opacity = 0.35, 0
            elif card.kind == "Defesa":
                holder.offset = ft.Offset(-(avail / 2 - 48) / cw, -1.55)
                holder.scale, holder.opacity = 0.3, 0
            elif card.kind == "Poder":
                holder.animate_scale = A(340, OUT)
                holder.animate_rotation = A(340, OUT)
                holder.rotate = ft.Rotate(0.25, alignment=ft.Alignment.CENTER)
                holder.scale, holder.opacity = 1.8, 0
            else:
                holder.offset = ft.Offset(0, -1.2)
                holder.scale, holder.opacity = 0.85, 0
            flush(self.page, [holder])
            await asyncio.sleep(0.28)
        before = self._snapshot()
        c.play(idx)
        self.selected = None
        self.busy = False
        self.render_combat(self._diff(before))

    def end_turn(self, e=None):
        if self.busy or self.combat.status != "ongoing":
            return
        self.busy = True
        self.task(self._end_turn)

    async def _end_turn(self):
        """Mão vai pro descarte, cada inimigo avança e age na sua vez, veneno cai, mão nova."""
        c = self.combat
        self.selected = None
        # 1. descarte da mão: cartas voam pro canto inferior direito
        if self._hand_ctrls:
            cw, ch, lift, avail = self._hand_geom
            holders = sorted(self._hand_ctrls.values(), key=lambda h: h.left)
            for holder in holders:
                holder.animate_position = A(300, IN)
                holder.animate_scale = A(300, IN)
                holder.animate_opacity = A(240, IN)
                holder.animate_rotation = A(300, IN)
            for holder in holders:
                holder.left, holder.top = avail - cw * 0.6, ch + lift
                holder.scale, holder.opacity = 0.4, 0
                holder.rotate = ft.Rotate(0.6, alignment=ft.Alignment.BOTTOM_CENTER)
                flush(self.page, [holder])
                await asyncio.sleep(0.05)
            await asyncio.sleep(0.22)
        # 2. efeitos de fim de turno do jogador (lacaios, veneno, poderes)
        before = self._snapshot()
        alive = c.end_turn_start()
        self._prev_hand = []
        fx = self._diff(before)
        self.busy = True
        self.render_combat(fx or {("noop",): True})
        if not alive:
            return
        if fx:
            await asyncio.sleep(0.75)
        # 3. inimigos, um por vez: avança, age, números aparecem
        c.enemies_begin()
        for i, e in enumerate(c.enemies):
            if not e.alive or c.status != "ongoing":
                continue
            spr = self._enemy_sprites.get(i)
            if spr is not None:
                spr.animate_offset = A(170, IN)
                spr.animate_scale = A(170, IN)
                spr.offset, spr.scale = ft.Offset(0, 0.22), 1.1
                flush(self.page, [spr])
                await asyncio.sleep(0.19)
            before = self._snapshot()
            c.enemy_act(e)
            self.busy = True
            self.render_combat(self._diff(before) or {("noop",): True})
            if c.status != "ongoing":
                return
            await asyncio.sleep(0.7)
        # 4. veneno e estados dos inimigos
        before = self._snapshot()
        c.enemies_end()
        fx = self._diff(before)
        if fx:
            self.busy = True
            self.render_combat(fx)
            if c.status != "ongoing":
                return
            await asyncio.sleep(0.7)
        # 5. mão nova
        c.start_next_turn()
        self.busy = False
        self.render_combat(toast=f"Turno {c.turn}")

    # ----------------------------------------------------- pós-combate
    def finish_combat(self):
        c = self.combat
        run = self.run
        t = run.current()["type"]
        self.busy = False
        if c.status == "lost":
            run.dead = True
            return self.show_end()

        if run.heal_after_combat:
            run.heal(run.heal_after_combat)
            run.heal_after_combat = 0
        if t in ("boss", "final"):
            run.bosses_defeated += 1
            run.temp_cards = []
        if t == "final":
            run.victory = True
            return self.show_end()
        if t in ("elite", "boss"):
            return self.show_reward()
        if t == "challenge":
            return self.show_modifier_choice()
        self.show_combat_summary()

    def show_combat_summary(self):
        st = Stage()
        self.show(self.scene([
            self.header(),
            self.status_line(),
            ft.Container(expand=True),
            *self.rise(st, [panel(ft.Column([
                st.enter(heading(ft.Icons.CHECK_CIRCLE, "Sala limpa", GOOD), scale=0.5, ms=520, curve=BACK, delay=250),
                chip("turn", f"{self.combat.turn} turno(s)", 12, bold=False),
            ], spacing=6)), wide(button("Próximo andar", self.next_floor, icon=ft.Icons.ARROW_UPWARD))], delay=120, step=160),
        ], scroll=False), stage=st)

    def show_reward(self):
        run = self.run
        st = Stage()
        opts = run.reward_options()
        views = [card_view(c, on_click=lambda e, c=c: self.take_card(c), width=130, height=194) for c in opts]
        for i, v in enumerate(views):
            st.enter(v, dy=1.2, scale=0.5, rotate=-0.5, ms=520, curve=BACK, delay=350 + i * 110)
        cards = ft.Row(views, wrap=True, spacing=8, run_spacing=8, alignment=ft.MainAxisAlignment.CENTER)
        can_level = run.level < content.MAX_LEVEL
        next_text = run.cls["ability_text"].get(run.level + 1, "Nível máximo")
        self.show(self.scene([
            self.header(),
            self.status_line(),
            *self.rise(st, [heading(ft.Icons.REDEEM, "Recompensa"),
                            txt("Escolha uma: carta nova (entra em 1 cópia) ou +1 nível da habilidade.", 12, MUTED)], delay=150),
            cards if opts else txt("Você já tem todas as cartas da classe.", 12, MUTED),
            *self.rise(st, [panel(ft.Column([
                heading(ft.Icons.MILITARY_TECH,
                        f"{run.cls['ability']} {run.level} → {run.level + 1 if can_level else run.level}", size=14),
                txt(next_text, 12),
                wide(button("Subir a habilidade", self.take_level, icon=ft.Icons.ARROW_UPWARD, disabled=not can_level)),
            ], spacing=6))], delay=750),
        ]), stage=st)

    def take_card(self, card: CardDef):
        if self.busy:
            return
        self.run.add_card(card)
        self.next_floor()

    def take_level(self, e=None):
        if self.busy:
            return
        self.run.level_up()
        self.next_floor()

    def show_modifier_choice(self):
        run = self.run
        st = Stage()
        opts = run.modifier_options()
        items = [panel(ft.Row([
            ft.Icon(ft.Icons.GPP_GOOD, color=GOOD, size=26),
            ft.Column([
                display(content.MODIFIERS[m][0], 16),
                txt(content.MODIFIERS[m][1], 12),
            ], spacing=3, expand=True),
        ], spacing=10), on_click=lambda e, m=m: self.take_modifier(m)) for m in opts]
        self.show(self.scene([
            self.header(),
            self.status_line(),
            ft.Container(expand=True),
            *self.rise(st, [heading(ft.Icons.FLAG, "Desafio vencido"),
                            txt("Escolha um modificador de run. Vale até o fim.", 12, MUTED), *items], delay=150, step=110),
        ], scroll=False), stage=st)

    def take_modifier(self, m: str):
        if self.busy:
            return
        self.run.add_modifier(m)
        self.next_floor()

    # ---------------------------------------------------------------- fim
    def show_end(self):
        run = self.run
        won = run.victory
        self.record_run(run)
        st = Stage()
        head = "A torre é sua" if won else "Você caiu"
        body = ("A Soberana Gertrudes foi derrotada. O churrasco de família vai ter que esperar."
                if won else f"Chegou ao andar {run.floor}. Perder também avança.")
        tw = self.typed(body, 13, delay=0.9, align=ft.TextAlign.CENTER)
        title_row = st.enter(ft.Row([
            ft.Icon(ft.Icons.WORKSPACE_PREMIUM if won else ft.Icons.HEART_BROKEN, color=ACCENT if won else HP, size=40),
            display(head, 34, ACCENT if won else HP),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER), scale=0.3, dy=-0.4, ms=700, curve=BACK, delay=250)
        self.show(self.scene([
            ft.Container(expand=True),
            title_row,
            ft.Container(content=tw.control, on_click=lambda e: tw.finish()),
            *self.rise(st, [panel(ft.Column([
                ft.Row([display(run.cls["name"], 16),
                        chip("level", run.level, label=f"{run.cls['ability']} nível {run.level}")], spacing=10),
                ft.Row([
                    chip("floor", run.floor, label="Andar alcançado"),
                    chip("boss", run.bosses_defeated),
                    chip("deck", len(run.deck)),
                    chip("points", run.meta_points(), 15),
                ], spacing=16, wrap=True),
                chip("seed", run.seed, 11, bold=False),
            ], spacing=8)),
                button("Ver deck", self.show_deck, icon=ft.Icons.STYLE, primary=False),
                wide(button("Voltar ao menu", self.show_menu, icon=ft.Icons.HOME))], delay=1100, step=140),
        ], bg=MENU_BG if won else None, scroll=False, shade=0.55), stage=st)


async def main(page: ft.Page):
    await App(page).load_records()
