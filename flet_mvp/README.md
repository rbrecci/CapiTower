# CapiTower MVP (Flet)

Versao alternativa e jogavel do CapiTower em Python + [Flet](https://flet.dev), independente da
stack PHP/MySQL do projeto principal. Serve para playtestar o design de `docs/` sem servidor,
banco ou build: roda direto do VS Code ou no celular pelo app do Flet.

Tudo roda no cliente. Nao ha conta nem save de run; so os recordes (melhor andar, runs, vitorias,
pontos de meta acumulados) ficam salvos no aparelho via `shared_preferences`.

## Rodando

Requisito: Python 3.10+ e Flet instalado.

```bash
pip install -r requirements.txt
```

**Desktop (VS Code):** abra `flet_mvp/main.py` e rode com o botao de play, ou:

```bash
python main.py
```

Com hot reload (recarrega ao salvar qualquer arquivo da pasta):

```bash
flet run -r main.py
```

**Celular (QR code):** instale o app **Flet** no telefone (Play Store ou App Store), deixe o PC
e o celular na mesma rede Wi-Fi e rode:

```bash
flet run --android main.py
```

ou `flet run --ios main.py`. O terminal mostra um QR code; escaneie com o app Flet e o jogo abre
no celular, com hot reload ao salvar.

**Navegador:**

```bash
flet run --web main.py
```

Todos os comandos devem ser rodados de dentro da pasta `flet_mvp/`.

**APK / site para distribuir:** `pyproject.toml` ja tem os metadados. `flet build apk` gera
`build/apk/app-release.apk` (instala direto no Android, fora da loja); `flet build web` gera
`build/web/` (site estatico, serve para GitHub Pages ou qualquer hospedagem). A primeira build
baixa o Flutter SDK e pode precisar do Android SDK com licencas aceitas (`flutter doctor`).

**Smoke test headless** (monta todas as telas com uma Page falsa, joga um combate com bot e
espera as animacoes terminarem; nao abre janela):

```bash
python tests/smoke_ui.py
```

## Estrutura

```
flet_mvp/
  main.py                 entrada: ft.run(main, assets_dir="assets")
  assets/
    bg_*.jpg              cenario de cada bloco + bg_menu.jpg (torre)
    frame_*.png           moldura de carta por tipo (Ataque, Defesa, Poder, Utilidade)
    logo.png              titulo do jogo
    capimaga.png ...      classes e gertrudes.png (512px, geradas de ../Assets)
    fonts/                LuckiestGuy (titulos, numeros de dano)
  capitower/
    cards.py              catalogo de cartas (dados + vocabulario de efeitos)
    content.py            classes, habilidades, inimigos, chefes, blocos, eventos, modificadores
    run.py                estado da run: deck, HP, nivel, geracao da torre com seed
    combat.py             motor de combate por turnos (resolvedor de efeitos, IA de intencao)
    anim.py               primitivos de animacao: Stage (entradas com stagger) e Typewriter
    ui.py                 telas em Flet (menu, classe, sorteio, andar, combate, recompensa, fim)
  tests/smoke_ui.py       percorre todas as telas sem abrir janela
```

## Animacao

O Flet so interpola uma propriedade (`offset`, `scale`, `opacity`, `rotate`, `left/top`) quando o
controle ja esta na tela com o valor antigo e recebe um valor novo num update seguinte. Toda
entrada e feita em dois passos por `anim.Stage`: `enter(...)`/`move(...)` deixam o controle no
estado inicial ao construir a tela, e `play()` aplica os estados finais em grupos de atraso
(stagger) usando `control.update()` em vez de `page.update()`, que numa tela grande custa caro.

- **Troca de tela** (`App.show`): a tela atual apaga e a nova entra deslizando; `floor=` usa a
  cortina escura com "Andar N · bloco". `show(fade=False)` e o redesenho instantaneo do combate.
- **Mao**: cartas novas saem da pilha de compra (canto inferior esquerdo) girando e crescendo;
  cartas que ja estavam deslizam da posicao antiga (`_prev_hand`) quando o leque reabre.
- **Jogar carta** (`_play_card`): sobe e cresce, depois voa conforme o tipo (Ataque no alvo,
  Defesa no retrato, Poder explode em brilho, Utilidade sobe e some) e so entao o efeito resolve.
- **Fim de turno** (`_end_turn`): a mao voa pro descarte, cada inimigo avanca e age na sua vez
  (`combat.enemy_act`), numeros flutuam, quem apanha treme e pisca, vinheta vermelha no jogador,
  veneno cai, toast "Turno N" e mao nova. O `Combat.end_turn()` continua existindo para bots.
- **Impacto**: flash branco + punch de escala no inimigo, retrato treme e pisca vermelho, morto
  tomba e apaga. Banner de chefe/elite entra com bounce.
- **Texto**: eventos, resultado e tela de fim usam `Typewriter` (toque no painel pula).
- `App.busy` bloqueia toques na mao/inimigos enquanto uma sequencia roda; `App.gen` sobe a cada
  tela e encerra tarefas de fundo (logo balancando, texto digitando) da tela anterior.
- Cartas mostram o arquetipo numa etiqueta na borda da caixa de texto (alem do tooltip).

Cartas e inimigos sao dados puros. Para adicionar uma carta, basta uma linha em `cards.py` usando o
vocabulario documentado no topo do arquivo; para um inimigo, uma linha em `content.ENEMIES` com o
padrao de intencoes.

## O que esta implementado

- As 3 classes (Capimaga, Brutamontes, Ligeira) com mecanica exclusiva, estado exclusivo e
  habilidade de 10 niveis seguindo as curvas de `docs/02-classes-e-arquetipos.md`.
- 12 cartas por classe (3 por arquetipo), incluindo as cartas exemplo dos docs.
- Torre de 51 andares: 5 blocos com 5 combates, 1 elite (posicao 3 a 8), 1 evento, 1 descanso,
  1 desafio opcional e chefe fixo no andar 10. Andar 51: Gertrudes com 3 fases.
- Os 5 chefes com suas mecanicas centrais (carregar/golpear, dupla acao, estados, gemeos com
  heranca de buff, Bloco por turno) e bestiario dos 5 blocos.
- Sorteio inicial de 5 cartas distintas com 1 re-roll, deck de 10 (2 copias). O sorteio garante
  pelo menos 2 cartas de Ataque (senao existe deck que nao consegue fechar combate).
- 10 pontos de recompensa (5 elites + 5 chefes): carta nova (1 entre 3) OU +1 nivel.
- Estados compartilhados: Defesa (o "Bloco" dos docs, renomeado no front por clareza), Forca,
  Fragilidade, Fraqueza, Veneno. Retaliacao e Evasao.
- Interface de jogo: cada tela e uma cena com o cenario do bloco ao fundo e HUD translucido por
  cima; menu com a torre e o logo; cartas com moldura por tipo (custo na gema, texto na caixa).
  No combate os inimigos ficam em pe no cenario com a intencao num balao acima da cabeca, o
  jogador embaixo com retrato e barra, e a mao em leque. Tocar numa carta seleciona (mostra o
  texto inteiro e o botao Jogar), tocar de novo joga. Dano e Defesa aparecem como numeros
  flutuantes, quem apanha treme, e elite/chefe entra com um banner.
- Chefes e elites ainda nao tem arte: sao silhuetas com icone (`ENEMY_ICONS` em `ui.py`),
  destacadas por cor e tamanho. Gertrudes e as classes usam a arte de `assets/`. Os prompts para
  gerar o resto estao em `docs/08-prompts-de-assets.md`.
- Icones nativos do Flet (Material) e tooltips com o nome por extenso (na carta, o tooltip traz
  o texto completo, util quando a caixa da moldura corta); textos do front com acentuacao (os
  docs continuam sem acento por convencao do repositorio).
- Os 3 eventos e os 5 modificadores de run dos docs. Desafio com 2 condicoes.
- Pontos de meta no fim da run (`andar + chefes*10 + 50 se venceu`) e seed da run para reproduzir.

## Desvios em relacao aos docs (todos `[ajustar]`)

| Item | Docs | MVP | Motivo |
| --- | --- | --- | --- |
| HP inicial | 70 | 80 | Simulacao com bot ganancioso morria no bloco 1 com 70. |
| Cartas por classe | 20 | 12 | Escopo. As 20 entram quando as cartas forem detalhadas. |
| Dano dos lacaios | nao definido | 2 por lacaio, alvo aleatorio, no fim do turno | Precisava de um valor base para o Enxame funcionar. |
| Sorteio inicial | 5 aleatorias | 5 aleatorias com >= 2 Ataques | Sem isso existe deck sem dano nenhum. |
| Atordoamento | no vocabulario | nao implementado | Nenhuma carta do MVP usa. |
| Pool inicial reduzido / desbloqueios | sim | nao | Sem meta progressao persistente neste MVP. |

## Estado do balanceamento

Simulacao com um bot ganancioso (defende quando vai levar dano, ataca o inimigo mais fraco),
40 runs por classe, escolhendo carta ou nivel ao acaso em cada recompensa:

| Classe | Andar mediano | Andar maximo |
| --- | --- | --- |
| Capimaga | 16 | 36 |
| Brutamontes | 15 | 26 |
| Ligeira | 24 | 46 |

A Ligeira ainda esta acima das outras duas: ela atravessa o bloco 1 quase sem perder vida (Evasao
anula golpes unicos), e o bot nao sabe jogar Brutamontes direito (nunca toma dano de proposito
para encher a Adrenalina). Do bloco 2 em diante as tres perdem vida parecido. E o primeiro ponto
a olhar no playtest com gente de verdade. Os numeros vivem em `content.py` e `cards.py`.
