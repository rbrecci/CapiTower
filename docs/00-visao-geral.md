# 00. Visão geral

## Pitch

CapiTower é um tower crawler roguelike de deck building para navegador. O jogador escolhe uma das
três classes, monta um deck enxuto de 15 cartas ao longo de 50 andares e enfrenta os capangas da
Soberana Gertrudes a cada 10 andares.

O diferencial está na escolha entre **largura** e **profundidade**: a cada recompensa o jogador
decide entre ganhar uma carta nova (largura, mais opções de nicho) ou subir o nível da habilidade
da classe (profundidade, build especializada). Como o deck começa aleatório, cada run oferece um
ponto de partida diferente para essa decisão.

## Pilares de design

**1. As três classes são igualmente fortes, só que diferentes.**
Nenhuma classe é a escolha "certa". Escolher classe é escolher estilo de jogo, nunca poder bruto.
Toda proposta de carta ou habilidade passa pelo teste: isso quebra a paridade entre as classes?

**2. Deck pequeno, decisão grande.**
Começa com 10 cartas (5 sorteadas, 2 cópias de cada) e termina com 20. Sem remoção, sem upgrade
de carta, sem lixo. Cada carta ganha é 5% do deck, então toda recompensa importa e o jogador nunca
precisa "consertar" o deck.

**3. A run conta uma história de build.**
O deck inicial aleatório define a pergunta da run, e as 10 recompensas definem a resposta.
Começou com 3 cartas do mesmo arquétipo? Especialize. Começou espalhado? Vire generalista.

**4. Perder também avança.**
Permadeath, mas o andar alcançado vira progresso de meta. Nenhuma run é desperdício.

**5. Humor sem piada burra.**
Capivaras bombadas levadas a sério dentro do próprio universo. O tom é leve, as mecânicas não.

## Público e sessão

- Sessão alvo de uma run completa: 30 a 45 minutos.
- Jogador de deck builder que conhece o gênero, mas o onboarding assume que não conhece.
- Desktop primeiro. Layout responsivo fica para depois do MVP.

## Escopo do MVP

Dentro:
- 1 classe jogável completa (20 cartas em 4 arquétipos, habilidade com 10 níveis).
- Motor de combate por turnos com o recurso Ação.
- Torre de 50 andares com ordem de encontros embaralhada.
- Conta, save da run e retomada.
- Placeholders visuais, sem arte final.

Fora do MVP:
- Classes 2 e 3.
- Sistema de objetivos e desbloqueios completo.
- Eventos narrativos além de um punhado de exemplos.
- Arte, som e animação.
- Qualquer forma de ranking ou competição.

## Não objetivos

Deixado de fora por decisão, não por falta de tempo:

- **Economia de moeda e loja.** Recompensas são sempre diretas.
- **Remoção e upgrade de cartas.** A curva de poder vem da habilidade de classe.
- **Validação autoritativa de combate no servidor.** O jogo é single player, cheat prejudica apenas
  quem cheata. Isso só seria revisto se algum dia existir ranking.
- **Lacaios alvejáveis.** Lacaios são presença visual e efeito mecânico, nunca unidades no campo.
