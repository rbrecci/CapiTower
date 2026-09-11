"""Primitivos de animação por cima das animações implícitas do Flet.

O Flet só interpola uma propriedade quando o controle já está na tela com o valor antigo e
recebe um valor novo num update seguinte. Então toda "entrada" é feita em dois passos: o
controle é montado no estado inicial (fora da tela, transparente, pequeno...), a página é
atualizada, e um tique depois o estado final é aplicado. `Stage` guarda esses pares e toca
todos com o atraso pedido (stagger); `Typewriter` mostra um texto aos poucos.
"""

import asyncio

import flet as ft

OUT = ft.AnimationCurve.EASE_OUT_CUBIC
BACK = ft.AnimationCurve.EASE_OUT_BACK
IN = ft.AnimationCurve.EASE_IN_CUBIC
INOUT = ft.AnimationCurve.EASE_IN_OUT


def A(ms: int, curve=OUT) -> ft.Animation:
    return ft.Animation(ms, curve)


class Stage:
    """Fila de animações de entrada: `enter(...)` deixa o controle no estado inicial e anota o
    final; `play()` aplica os finais respeitando o `delay` de cada um."""

    def __init__(self):
        self.items: list[tuple[ft.Control, int, dict]] = []

    def add(self, control: ft.Control, delay: int = 0, **final):
        self.items.append((control, delay, final))

    def enter(self, control: ft.Control, dx=0.0, dy=0.0, scale=None, opacity=0.0, rotate=None,
              ms=380, curve=OUT, delay=0):
        """Anima o controle do estado dado até o estado em que ele foi construído."""
        final = {}
        if dx or dy:
            control.animate_offset = A(ms, curve)
            final["offset"] = control.offset or ft.Offset(0, 0)
            control.offset = ft.Offset(dx, dy)
        if scale is not None:
            control.animate_scale = A(ms, curve)
            final["scale"] = control.scale if control.scale is not None else 1.0
            control.scale = scale
        if opacity is not None:
            control.animate_opacity = A(min(ms, 280), ft.AnimationCurve.EASE_OUT)
            final["opacity"] = control.opacity if control.opacity is not None else 1.0
            control.opacity = opacity
        if rotate is not None:
            control.animate_rotation = A(ms, curve)
            cur = control.rotate
            if isinstance(cur, ft.Rotate):
                final["rotate"] = cur
                control.rotate = ft.Rotate(cur.angle + rotate, alignment=cur.alignment)
            else:
                final["rotate"] = cur or 0
                control.rotate = (cur or 0) + rotate
        self.add(control, delay, **final)
        return control

    def move(self, control: ft.Control, left_from: float, top_from: float, ms=320, curve=OUT, delay=0):
        """Controle posicionado num Stack: começa em (left_from, top_from) e desliza até onde foi criado."""
        control.animate_position = A(ms, curve)
        self.add(control, delay, left=control.left, top=control.top)
        control.left, control.top = left_from, top_from
        return control

    async def play(self, page: ft.Page, lead=0.04):
        """Aplica os estados finais em grupos de atraso. Atualiza só os controles tocados
        (`control.update()`), bem mais barato que `page.update()` numa tela grande."""
        if not self.items:
            return
        await asyncio.sleep(lead)
        t = 0
        touched: list[ft.Control] = []
        for control, delay, final in sorted(self.items, key=lambda x: x[1]):
            if delay > t:
                flush(page, touched)
                touched = []
                await asyncio.sleep((delay - t) / 1000)
                t = delay
            for k, v in final.items():
                setattr(control, k, v)
            touched.append(control)
        flush(page, touched)
        self.items = []


def flush(page: ft.Page, controls):
    """Manda as mudanças dos controles dados; se algum ainda não está na página, cai para o update geral."""
    try:
        for c in controls:
            c.update()
    except Exception:
        page.update()


class Typewriter:
    """Texto que aparece letra a letra. Um texto invisível igual reserva a altura para o layout
    não pular. `finish()` mostra tudo de uma vez (usado no toque para pular)."""

    def __init__(self, text: str, size=13, color=None, cps=55, align=None, weight=None, font=None,
                 on_done=None):
        self.full = text
        self.cps = cps
        self.done = False
        self.on_done = on_done
        kw = dict(size=size, color=color, text_align=align, weight=weight, font_family=font)
        self.shown = ft.Text("", **kw)
        ghost = ft.Text(text, **kw, opacity=0)
        self.control = ft.Stack([ghost, self.shown])

    async def run(self, alive=lambda: True):
        step = max(1, round(self.cps * 0.035))
        n = 0
        try:
            while n < len(self.full) and not self.done and alive():
                n += step
                self.shown.value = self.full[:n]
                self.shown.update()
                await asyncio.sleep(0.035)
        except Exception:
            return
        if alive():
            self.finish()

    def finish(self):
        if self.done:
            return
        self.done = True
        self.shown.value = self.full
        try:
            self.shown.update()
        except Exception:
            pass
        if self.on_done:
            self.on_done()
